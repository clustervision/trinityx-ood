import { ref, watch, triggerRef, onMounted, onUnmounted } from 'vue';
import axios from 'axios';
import { isSessionExpired } from '@/utils/connectionStatus';
import type { Device } from '@/types/rack';

interface PrometheusResult {
  metric: { hostname: string; [key: string]: any; };
  value: [number, string];
}

interface PrometheusResponse {
  status: string;
  data: { resultType: string; result: PrometheusResult[]; };
}

/** max = scale for normalization (≥ any sample; use 1 when all samples are 0). */
export interface MetricRange {
  min: number;
  max: number;
  hasData: boolean;
  peak: number;
  avg: number;
}

const EMPTY_RANGE: MetricRange = { min: 0, max: 1, hasData: false, peak: 0, avg: 0 };

/**
 * Same shape as your browser URL query=… string: `+` means space in x-www-form-urlencoded.
 * We store `+` in source so it matches pasted URLs; convert to real PromQL before calling Prometheus.
 */
const QUERY_MAP: Record<string, string> = {
  'System Load': 'avg+by+(hostname,+luna_group)+(node_load5)',
  'Temperature':
    'max+by+(hostname,+luna_group)+(ipmi_temperature_celsius{+name=~"[cC][pP][uU].*[tT][eE][mM][pP].*"+})',
  'Power Consumption': 'avg+by+(hostname,+luna_group)+(ipmi_dcmi_power_consumption_watts)',
  'GPU Temperature': 'avg+by+(hostname,+luna_group)+(nvidia_smi_temperature_gpu)',
};

function plusFormToPromQL(plusForm: string): string {
  return plusForm.replace(/\+/g, ' ');
}

/** Encode like your working URLs: spaces → `+` (not `%20`) inside the query param value. */
function encodeQueryParamValue(value: string): string {
  return encodeURIComponent(value).replace(/%20/g, '+');
}

function prometheusInstantQueryParams(query: string): string {
  return `query=${encodeQueryParamValue(query)}`;
}


export function useRackMetrics() {
  //@ts-ignore
  const prome_url = window.PROMETHEUS_URL;
  const metric1 = ref<string | null>(null);
  const metric2 = ref<string | null>(null);
  const metricDataMap = ref<Record<string, Record<string, number>>>({});

  const metric1Range = ref<MetricRange>({ ...EMPTY_RANGE });
  const metric2Range = ref<MetricRange>({ ...EMPTY_RANGE });

  let refreshTimer: ReturnType<typeof setInterval> | null = null;

  const calculateColor = (value: number, max: number) => {
    if (max <= 0) return 'hsl(120, 100%, 45%)';
    let ratio = value / max;
    if (ratio > 1) ratio = 1;
    const hue = (1 - ratio) * 120;
    return `hsl(${hue}, 100%, 45%)`;
  };

  const fetchSingleMetric = async (metricType: string, rangeRef: typeof metric1Range) => {
    const query = QUERY_MAP[metricType];
    if (!query) return;

    rangeRef.value = { ...EMPTY_RANGE };

    try {
      const promql = plusFormToPromQL(query);
      const response = await axios.get<PrometheusResponse>(
        `${prome_url}/api/v1/query?${prometheusInstantQueryParams(promql)}`
      );

      if (response.data.status !== 'success') return;

      const results = response.data.data.result;

      if (!results.length) {
        rangeRef.value = { ...EMPTY_RANGE };
        triggerRef(metricDataMap);
        return;
      }

      let maxVal = 0;
      let sum = 0;
      let count = 0;

      results.forEach((item) => {
        const rawHostname = item.metric.hostname;
        if (!rawHostname) return;
        const parts = rawHostname.split('.');
        const hostname = parts[0];
        if (!hostname) return;
        const value = parseFloat(item.value[1]);
        if (!Number.isFinite(value)) return;
        if (value > maxVal) maxVal = value;
        sum += value;
        count += 1;

        if (!metricDataMap.value[hostname]) metricDataMap.value[hostname] = {};
        metricDataMap.value[hostname][metricType] = value;
      });

      if (count === 0) {
        rangeRef.value = { ...EMPTY_RANGE };
        triggerRef(metricDataMap);
        return;
      }

      const avg = sum / count;
      const scaleMax = maxVal === 0 ? 1 : maxVal;

      rangeRef.value = {
        min: 0,
        max: scaleMax,
        hasData: true,
        peak: maxVal,
        avg,
      };
      triggerRef(metricDataMap);
    } catch (e) {
      console.error(`Fetch error ${metricType}`, e);
      rangeRef.value = { ...EMPTY_RANGE };
    }
  };

  const fetchMetricData = async () => {
    if (isSessionExpired.value) return;
    const m1Active = metric1.value && metric1.value !== 'No Scale';
    const m2Active = metric2.value && metric2.value !== 'No Scale';

    if (m1Active) await fetchSingleMetric(metric1.value!, metric1Range);
    if (m2Active) await fetchSingleMetric(metric2.value!, metric2Range);
  };
  const getMetricForDevice = (device: Device | null, type: string | null, isMetric1: boolean) => {
    if (!device || !type || type === 'No Scale') return undefined;
    const deviceMetrics = metricDataMap.value[device.name];

    if (deviceMetrics && deviceMetrics[type] !== undefined) {
      const val = deviceMetrics[type];
      const range = isMetric1 ? metric1Range.value : metric2Range.value;
      const color = calculateColor(val, range.max);
      return {
        value: Number(val.toFixed(2)),
        color: color
      };
    }
    return undefined;
  };

  const startAutoRefresh = () => {
    stopAutoRefresh();
    refreshTimer = setInterval(() => {
      console.log('Auto-refreshing metrics...');
      fetchMetricData();
    }, 30000);
  };

  const stopAutoRefresh = () => {
    if (refreshTimer) {
      clearInterval(refreshTimer);
      refreshTimer = null;
    }
  };

  onMounted(() => {
    startAutoRefresh();
  });

  onUnmounted(() => {
    stopAutoRefresh();
  });

  watch([metric1, metric2], fetchMetricData);
  watch(isSessionExpired, (expired) => {
    if (expired) stopAutoRefresh();
  });

  return { metric1, metric2, metric1Range, metric2Range, getMetricForDevice, fetchMetricData };
}
