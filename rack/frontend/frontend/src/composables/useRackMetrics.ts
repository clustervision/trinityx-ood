import { ref, watch, triggerRef, onMounted, onUnmounted } from 'vue'; // Added onMounted, onUnmounted
import axios from 'axios';
import type { Device } from '@/types/rack';

interface PrometheusResult {
  metric: { hostname: string; [key: string]: any; };
  value: [number, string];
}

interface PrometheusResponse {
  status: string;
  data: { resultType: string; result: PrometheusResult[]; };
}

interface MetricRange {
  min: number;
  max: number;
}

const QUERY_MAP: Record<string, string> = {
  'System Load': 'avg by (hostname, luna_group) (node_load5)',
  'Temperature': 'max by (hostname, luna_group) (ipmi_temperature_celsius{name=~"[cC][pP][uU].*[tT][eE][mM][pP].*"})',
  'Power Consumption': 'avg by (hostname, luna_group) (ipmi_dcmi_power_consumption_watts)',
  'GPU Temperature': 'avg by (hostname, luna_group) (nvidia_smi_temperature_gpu)',
};


export function useRackMetrics() {
  const prome_url = 'https://yixin3-dev-ctrl001:9090';
  const metric1 = ref<string | null>('No Scale');
  const metric2 = ref<string | null>('No Scale');
  const metricDataMap = ref<Record<string, Record<string, number>>>({});

  const metric1Range = ref<MetricRange>({ min: 0, max: 100 });
  const metric2Range = ref<MetricRange>({ min: 0, max: 100 });

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

    try {
      const response = await axios.get<PrometheusResponse>(`${prome_url}/api/v1/query`, {
        params: { query: query }
      });

      if (response.data.status !== 'success') return;

      const results = response.data.data.result;

      let maxVal = 0;

      results.forEach((item) => {
        const rawHostname = item.metric.hostname;
        if (!rawHostname) return;
        const parts = rawHostname.split('.');
        const hostname = parts[0];
        if (!hostname) return;
        const value = parseFloat(item.value[1]) || 0;
        if (value > maxVal) maxVal = value;

        if (!metricDataMap.value[hostname]) metricDataMap.value[hostname] = {};
        metricDataMap.value[hostname][metricType] = value;
      });
      rangeRef.value = { min: 0, max: maxVal === 0 ? 100 : maxVal };
      triggerRef(metricDataMap);
    } catch (e) {
      console.error(`Fetch error ${metricType}`, e);
    }
  };

  const fetchMetricData = async () => {
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

  return { metric1, metric2, metric1Range, metric2Range, getMetricForDevice, fetchMetricData };
}
