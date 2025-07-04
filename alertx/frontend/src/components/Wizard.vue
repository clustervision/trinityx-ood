<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, toRaw, reactive } from 'vue';
import axios, { AxiosError } from 'axios';
import { Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale
} from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale);


interface activeTargets {
  discoveredLabels: {
    __address__: string;
    __meta_filepath: string;
    __metrics_path__: string;
    __scheme__: string;
    __scrape_interval__: string;
    __scrape_timeout__: string;
    exporter: string;
    hostname: string;
    job: string;
    luna_group: string;
  },
  labels: {
    exporter: string;
    hostname: string;
    instance: string;
    job: string;
    luna_group: string;
  },
  scrapePool: string;
  scrapeUrl: string;
  globalUrl: string;
  lastError: string;
  lastScrape: string;
  lastScrapeDuration: number;
  health: string;
  scrapeInterval: string;
  scrapeTimeout: string;
};

interface PrometheusMetrics {
  metric: {
    __name__: string;
  };
  value: [number, string];
}[];

interface WidgetForm {
  rule_name: string;
  rule_description: string;
  rule_for: string;
  rule_category: string;
  rule_status: boolean;
  rule_nhc: boolean;
  rule_severity: string;
  group_granularity?: string;
  grouping_operator?: string;
  aggregation_operator?: string;
  threshold?: number;
  selectedCategory?: string;
  selectedMetrics?: string;
  selectedFilterKey?: string;
  selectedGroup?: string;
  selectedHostname?: string;
}

const props = defineProps({

  PrometheusServer: {
    type: String,
    required: true,
  },
  url: {
    type: String,
    required: true,
  },
  configType: {
    type: String,
    required: true,
  },
  configuration: Object,
  save_configuration: {
    type: Function,
    required: true,
  },

});

const form = reactive<WidgetForm>({
  rule_name: '',
  rule_description: '',
  rule_for: '',
  rule_category: props.configType,
  rule_status: true,
  rule_nhc: false,
  rule_severity: 'info',
  group_granularity: '',
  grouping_operator: '',
  aggregation_operator: '',
  threshold: 0,
  selectedCategory: '',
  selectedMetrics: '',
  selectedFilterKey: '',
  selectedGroup: '',
  selectedHostname: '',
});

const currentIndex = ref(0);
const tabs = ref<HTMLElement[]>([]);
const nextBtn = ref<HTMLButtonElement | null>(null);
const prevBtn = ref<HTMLButtonElement | null>(null);
const showValidation = ref(false);
const validationResult = ref<{ valid: boolean; error?: string; data?: any } | null>(null);
const granularityMap: Record<string, string> = {
  'per-metric':   '',
  'per-hostname': 'hostname',
  'per-group':    'luna_group',
  'global':       '',
};

const chartData = ref<any>(null);
const chartOptions = ref<any>({
  responsive: true,
  plugins: {
    legend: { display: false },
    title: { display: true, text: 'Prometheus Query Result' }
  }
});
const error_message = ref('');

let exporters = ref<string[]>([]);
let luna_groups = ref<string[]>([]);
let hostnames = ref<string[]>([]);
let metrics = ref<string[]>([]);
let onModalHidden: (() => void) | null = null;

const PrometheusServer = new URL(props.PrometheusServer);
const PrometheusTarget = new URL(PrometheusServer.toString());
PrometheusTarget.pathname = '/api/v1/targets';
PrometheusTarget.searchParams.set('scrapePool', '');
const PrometheusMetric = new URL(PrometheusServer.toString());
PrometheusMetric.pathname = '/api/v1/query';


function validateForm(): boolean {
  const activePane = document.querySelector('.tab-pane.active');
  if (!activePane) return false;

  if (currentIndex.value === 0) {
    const ruleName = activePane.querySelector('#rule_name') as HTMLInputElement;
    const ruleFor = activePane.querySelector('#rule_for') as HTMLInputElement;
    if (!ruleName?.value || !ruleFor?.value) {
      showValidation.value = true;
      return false;
    }
  } else if (currentIndex.value === 2) {
    const selectedCategory = activePane.querySelector('#exporter') as HTMLSelectElement;
    const selectedMetrics = activePane.querySelector('#metrics') as HTMLSelectElement;
    if (!selectedCategory?.value || !selectedMetrics?.value) {
      showValidation.value = true;
      return false;
    }
  } else if (currentIndex.value === 3) {
    const filter_key = activePane.querySelector('#filter_key') as HTMLSelectElement;
    const grouping_operator = activePane.querySelector('#grouping_operator') as HTMLSelectElement;
    const threshold = activePane.querySelector('#threshold') as HTMLInputElement;
    if (!filter_key?.value) {
      showValidation.value = true;
      return false;
    } else {
      if (filter_key.value === 'luna_group') {
        const selectedGroup = activePane.querySelector('#luna_group') as HTMLSelectElement;
        if (!selectedGroup?.value) {
          showValidation.value = true;
          return false;
        }
      }
      if (filter_key.value === 'hostname') {
        const selectedHostname = activePane.querySelector('#hostname') as HTMLSelectElement;
        if (!selectedHostname?.value) {
          showValidation.value = true;
          return false;
        }
      }
    }

    if (!grouping_operator?.value || String(threshold.value) === '') {
      showValidation.value = true;
      return false;
    } 

  }
  showValidation.value = false;
  return true;
}

async function runQueryValidation() {
  validationResult.value = await validatePrometheusQuery();
}


async function validatePrometheusQuery() {
  const Query = constructQuery();
  if (!Query || Query.trim() === '') {
    return { valid: false, error: 'Query cannot be empty' };
  }
  try {
    const response = await axios.get(`${PrometheusMetric}`, {
      params: { Query },
    });
    if (response.data.status === 'success') {
      fetchGraphData();
      return { valid: true, data: response.data.data };
    } else {
      return { valid: false, error: response.data.error };
    }
  } catch (err) {
    let errorMsg = 'Unknown error';
    if (err instanceof Error) {
      errorMsg = err.message;
    } else if (typeof err === 'string') {
      errorMsg = err;
    }
    return { valid: false, error: errorMsg };
  }
}

/**
 * Fetch graph data from Prometheus
 */
async function fetchGraphData() {
  const now = Math.floor(Date.now() / 1000);
  const start = now - 300; // last 5 minutes
  const end = now;
  const step = 15; // 15s resolution
  const Query = constructQuery();
  if (!Query || Query.trim() === '') {
    return { valid: false, error: 'Query cannot be empty' };
  }

  try {
    const response = await axios.get(`${PrometheusServer}api/v1/query_range`, {
      params: { query: Query, start, end, step}
    });
    const result = response.data.data.result;

    if (result.length === 0) {
      chartData.value = {labels: [], datasets: []};
      return;
    }

    chartData.value = {
      labels: result[0].values.map(([timestamp, _]: [number, string]) => new Date(timestamp * 1000).toLocaleTimeString()),
      datasets: result.map((series: any) => ({
        label: series.metric.luna_group || 'group',
        data: series.values.map(([_, value]: [any, any]) => parseFloat(value)),
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.3,
        fill: true
      }))
    };
  } catch (error) {
    console.error('Prometheus query error:', error);
  }
}


/**
 * Sync tab display with current index
 */
function updateTab(formtab: boolean, index: number) {
  if(formtab){
    const isValid = validateForm();
    if (!isValid) return;
  }
  
  if (index < 0 || index >= tabs.value.length) return;

  tabs.value[currentIndex.value].classList.remove('active');
  const currentTabPane = document.querySelector<HTMLElement>(tabs.value[currentIndex.value].dataset.bsTarget!);
  currentTabPane?.classList.remove('show', 'active');

  currentIndex.value = index;

  const currentTarget = tabs.value[currentIndex.value].dataset.bsTarget;
  if (currentTarget === '#test') {
    runQueryValidation();
  }

  tabs.value[currentIndex.value].classList.add('active');
  const nextTabPane = document.querySelector<HTMLElement>(tabs.value[currentIndex.value].dataset.bsTarget!);
  nextTabPane?.classList.add('show', 'active');

  // Set previous tabs color (#ffca2c) and reset others to default color
  tabs.value.forEach((tab, i) => {
    if (i < currentIndex.value) {
      tab.style.color = '#f8f9fa';  // Highlight previous tabs
      tab.style.backgroundColor = '#ffca2c';
    } else if (i === currentIndex.value) {
      tab.style.color = '#f8f9fa';  // Current tab color (original blue)
      tab.style.backgroundColor = '#0d6efd';
    } else {
      tab.style.color = '#f8f9fa'; // Reset to default (or inherit)
      tab.style.backgroundColor = '#5c636a';
    }
  });

  if (prevBtn.value) prevBtn.value.disabled = currentIndex.value === 0;
  if (nextBtn.value) nextBtn.value.innerText = currentIndex.value === tabs.value.length - 1 ? 'Finish' : 'Next';
}

/**
 * On DOM ready, bind buttons and load tabs
 */
onMounted(() => {
  const modalEl = document.getElementById(`wizard_modal_${props.configType}`);
  if (!modalEl) return;

  modalEl.addEventListener('show.bs.modal', () => {
    fetchTarget();
    tabs.value = Array.from(modalEl.querySelectorAll<HTMLElement>('#wizardTabs .nav-link'));
    nextBtn.value = document.getElementById('nextBtn') as HTMLButtonElement;
    prevBtn.value = document.getElementById('prevBtn') as HTMLButtonElement;
    updateTab(false, currentIndex.value);
  });

  onModalHidden = () => {
    resetForm();
  };
  modalEl.addEventListener('hidden.bs.modal', onModalHidden);

});


onBeforeUnmount(() => {
  const modalEl = document.getElementById(`wizard_modal_${props.configType}`);
  if (modalEl && onModalHidden) {
    modalEl.removeEventListener('hidden.bs.modal', onModalHidden);
  }
});

/**
 * Reset form to initial state
 */
function resetForm() {
  // Reset form fields
  Object.assign(form, {
    rule_name: '',
    rule_description: '',
    rule_for: '',
    rule_category: props.configType,
    rule_status: true,
    rule_nhc: false,
    rule_severity: 'info',
    group_granularity: '',
    grouping_operator: '',
    aggregation_operator: '',
    threshold: 0,
    selectedCategory: '',
    selectedMetrics: '',
    selectedFilterKey: '',
    selectedGroup: '',
    selectedHostname: '',
  });

  currentIndex.value = 0;
  showValidation.value = false;
  validationResult.value = null;
  chartData.value = null;

  // Reset tab visual state
  tabs.value.forEach((tab, i) => {
    tab.classList.remove('active');
    const pane = document.querySelector<HTMLElement>(tab.dataset.bsTarget!);
    pane?.classList.remove('show', 'active');
  });

  // Activate first tab only
  const firstTab = tabs.value[0];
  firstTab.classList.add('active');
  const firstPane = document.querySelector<HTMLElement>(firstTab.dataset.bsTarget!);
  firstPane?.classList.add('show', 'active');

  // Recolor tabs
  tabs.value.forEach((tab, i) => {
    if (i === 0) {
      tab.style.color = '#f8f9fa';
      tab.style.backgroundColor = '#0d6efd';
    } else {
      tab.style.color = '#f8f9fa';
      tab.style.backgroundColor = '#5c636a';
    }
  });

  // Reset buttons
  if (prevBtn.value) prevBtn.value.disabled = true;
  if (nextBtn.value) nextBtn.value.innerText = 'Next';
}


/**
 * Navigation: Previous
 */
function goPrev() {
  if (currentIndex.value > 0) {
    updateTab(false, currentIndex.value - 1);
  }
}

/**
 * Navigation: Next
 */
function goNext() {
  if (currentIndex.value < tabs.value.length - 1) {
    updateTab(true, currentIndex.value + 1);
  } else {
    submitForm();
  }
}
/**
 * Submit the form and save the configuration
 */
function submitForm() {
  // Centralized state for rule data
  const ruleData = reactive({
    alert: form.rule_name,
    annotations: { description: form.rule_description },
    for: form.rule_for,
    expr: constructQuery() || '',
    labels: {
      category: form.rule_category === 'generic' ? 'generic' : 'service',
      disabled: !form.rule_status,
      nhc: form.rule_nhc || false,
      severity: form.rule_severity || 'info'
    },
  });

  const rule = toRaw(ruleData);
  const add_rule_config = JSON.parse(JSON.stringify(props.configuration));
  if (add_rule_config?.groups?.[0]?.rules) {
    add_rule_config.groups[0].rules.push(rule);
  } else {
    console.error('Cannot add row: Invalid configuration structure');
  }
  props.save_configuration(props.configType, add_rule_config, `wizard_modal_${props.configType}`)
}

async function fetchTarget() {
  try {
    const proxyUrl = `${props.url}/proxy?url=${PrometheusTarget}`;
    const response = await axios.get(proxyUrl);
    if (response.status === 200) {
      const activeTargets = response.data.data.activeTargets;
      activeTargets.forEach((target: activeTargets) => {
        const group = target.labels?.luna_group;
        const exporter = target.labels?.exporter;
        const hostname = target.labels?.hostname;
        if (group && !luna_groups.value.includes(group)) {
          luna_groups.value.push(group);
        }
        if (exporter && !exporters.value.includes(exporter)) {
          exporters.value.push(exporter);
        }
        if (hostname && !hostnames.value.includes(hostname)) {
          hostnames.value.push(hostname);
        }
      });
    }
  } catch (error: unknown) {
    if (error instanceof AxiosError) {
      error_message.value = `<strong>[Prometheus Server] :: Could not read from Prometheus Server. \n\t URL: ${PrometheusTarget}`;
      error_message.value += `\n\t Please ensure Prometheus Server service is running and the port can be reachable.</strong>`;
    } else if (error instanceof Error) {
      error_message.value = `<strong>[Prometheus Server] :: ${error.message}</strong>`;
    }else {
      error_message.value = `<strong>[Prometheus Server] :: ${error}</strong>`;
    }
  }
}

async function fetchMetrics(exporter: string) {
  metrics.value = [];
  PrometheusMetric.searchParams.set('query', `avg by (__name__) ({__name__=~".*", exporter="${exporter}"})`);
  try {
    const proxyUrl = `${props.url}/proxy?url=${PrometheusMetric}`;
    const response = await axios.get(proxyUrl);
    if (response.status === 200) {
      const result = response.data.data.result;
      result.forEach((MetricsResult: PrometheusMetrics) => {
        const metric = MetricsResult.metric?.__name__;
        if (metric && !metrics.value.includes(metric)) {
          metrics.value.push(metric);
        }
      });
    }
  } catch (error: unknown) {
    if (error instanceof AxiosError) {
      console.log(error.code);
      console.log(error.message);
    } else if (error instanceof Error) {
      console.log(error.message);
    }else {
      console.log(error);
    }
  }

}

function constructQuery() {
  if (!form.selectedMetrics) return '';

  // Build filter
  let filters = '';
  if (form.selectedFilterKey && form.selectedGroup) {
    filters = `{${form.selectedFilterKey}="${form.selectedGroup}"}`;
  } else if (form.selectedFilterKey && form.selectedHostname) {
    filters = `{${form.selectedFilterKey}="${form.selectedHostname}"}`;
  }

  // Default to no aggregation if not selected
  const aggFn = form.aggregation_operator || ''; // e.g., avg, sum
  const operator = form.grouping_operator || ''; // e.g., >=
  const threshold = form.threshold ?? '';        // allow 0 and blank

  // Grouping key map
  const groupKey = granularityMap[form.group_granularity || ''] || '';
  const byClause = groupKey ? ` by (${groupKey})` : '';

  // If aggregation operator is missing, skip wrapping the metric
  const metricWithFilters = `${form.selectedMetrics}${filters}`;
  const leftExpr = aggFn ? `${aggFn}(${metricWithFilters})${byClause}` : metricWithFilters;

  // Final query with optional threshold/operator
  const query = operator && threshold !== '' ? `${leftExpr} ${operator} ${threshold}` : leftExpr;

  return query;
}


</script>
<style>
#wizardTabs {
  border-bottom: none;
  overflow-x: hidden;
}

.wizard-step-first {
  position: relative;
  background-color: #f8f9fa;
  color: #0d6efd;
  border: 1px solid #dee2e6;
  border-right: none;
  border-radius: 0;
  padding: 10px 25px 10px 15px;
  margin-right: -1px;
  clip-path: polygon(0 0, 90% 0, 100% 50%, 90% 100%, 0 100%);
  z-index: 1;
}

.wizard-step {
  position: relative;
  background-color: #f8f9fa;
  color: #0d6efd;
  border: 1px solid #dee2e6;
  border-right: none;
  border-radius: 0;
  padding: 10px 25px 10px 15px;
  margin-right: -1px;
  clip-path: polygon(0 0, 90% 0, 100% 50%, 90% 100%, 0 100%, 10% 50%);
  z-index: 1;
}

.wizard-step-last {
  position: relative;
  background-color: #f8f9fa;
  color: #0d6efd;
  border: 1px solid #dee2e6;
  border-right: none;
  border-radius: 0;
  padding: 10px 25px 10px 15px;
  margin-right: -1px;
  clip-path: polygon(0 0, 100% 0, 100% 100%, 10% 100%, 0 100%, 10% 50%);
  z-index: 1;
}

.nav-pills .nav-link {
  border-radius: 0;
}

</style>
<template>
  <div class="modal fade" :id="`wizard_modal_${props.configType}`" tabindex="-1">
    <div class="modal-dialog modal-xl" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h2 class="modal-title">Rule Creation Wizard</h2>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        
        <div class="modal-body container-fluid">
          <div v-if="error_message">
            <div class="alert alert-danger alert-dismissible" role="alert">
              <pre v-html="error_message" style="font-size: larger; margin-bottom: 0rem;"></pre>
              </div>
          </div>
            <!-- Tab navigation (full width) -->
            <div class="nav nav-pills nav-fill" id="wizardTabs" role="tablist">
              <button class="wizard-step-first nav-link active" disabled id="step1-tab" data-bs-toggle="tab" data-bs-target="#step1" type="button" role="tab">Step 1</button>
              <button class="wizard-step nav-link" disabled id="step2-tab" data-bs-toggle="tab" data-bs-target="#step2" type="button" role="tab">Step 2</button>
              <button class="wizard-step nav-link" disabled id="step3-tab" data-bs-toggle="tab" data-bs-target="#step3" type="button" role="tab">Step 3</button>
              <button class="wizard-step nav-link" disabled id="step4-tab" data-bs-toggle="tab" data-bs-target="#step4" type="button" role="tab">Step 4</button>
              <button class="wizard-step nav-link" disabled id="test-tab"  data-bs-toggle="tab" data-bs-target="#test" type="button" role="tab">Test</button>
              <button class="wizard-step-last nav-link" disabled id="finish-tab" data-bs-toggle="tab" data-bs-target="#finish" type="button" role="tab">Finish</button>
            </div>

            <!-- Tab content with fixed height -->
            <div class="tab-content border border-top-0 p-3" id="wizardTabContent" style="overflow-y: auto;">
 
              <div class="tab-pane fade show active" id="step1" role="tabpanel">
                <h5 class="mb-4">Basic Rule Information</h5>
                <div class="row g-6">
                  <div class="col mb-0">
                    <label for="rule_name" class="form-label">Rule Name</label>
                    <input type="text" v-model="form.rule_name" id="rule_name" autocomplete="off" class="form-control" :class="{ 'is-invalid': !form.rule_name && showValidation }" placeholder="Enter Rule Name" required/>
                    <div class="invalid-feedback">Rule name is required.</div>
                  </div>
                </div>
                <div class="row">
                  <div class="col mb-6">
                    <label for="rule_description" class="form-label">Rule Description</label>
                    <textarea v-model="form.rule_description" id="rule_description" class="form-control" rows="3" required placeholder="Enter Rule Description"></textarea>
                  </div>
                </div>
                <div class="row">
                  <div class="col mb-0">
                    <label for="rule_for" class="form-label">Rule For</label>
                    <input type="text" v-model="form.rule_for" id="rule_for" autocomplete="off" class="form-control" :class="{ 'is-invalid': !form.rule_for && showValidation }" placeholder="Enter Rule For"  />
                    <div class="invalid-feedback">Rule For is required.</div>
                  </div>
                </div>
                <div class="row">
                  <div class="col mb-6">
                    <label for="rule_category" class="form-label">Rule Category</label>
                    <select v-model="form.rule_category" id="rule_category" class="form-select">
                      <option class="btn-primary" disabled value="">Set Category</option>
                      <option class="btn-info" selected value="generic">Generic</option>
                      <option class="btn-warning" value="service">Service</option>
                    </select>
                  </div>
                  <div class="col mb-0">
                    <label for="rule_status" class="form-label">Enable</label>
                    <div class="form-check form-switch ">
                      <input v-model="form.rule_status" type="checkbox" id="rule_status" class="form-check-input" checked />
                      <label id="rule_status_label" for="rule_status" class="form-check-label">{{ form.rule_status ? 'ON' : 'OFF' }}</label>
                    </div>
                  </div>
                  <div class="col mb-6">
                    <label for="rule_nhc" class="form-label">Rule NHC</label>
                    <div class="form-check form-switch ">
                      <input v-model="form.rule_nhc" type="checkbox" id="rule_nhc" class="form-check-input"/>
                      <label id="rule_nhc_label" for="rule_nhc" class="form-check-label">{{ form.rule_nhc ? 'ON' : 'OFF' }}</label>
                    </div>
                  </div>
                  <div class="col mb-6">
                    <label for="rule_severity" class="form-label">Set Severity</label>
                    <select v-model="form.rule_severity" id="rule_severity" class="form-select">
                      <option class="btn-primary" disabled value="">Set Severity</option>
                      <option class="btn-dark" value="critical">Critical</option>
                      <option class="btn-danger" value="danger">Danger</option>
                      <option class="btn-warning" value="warning">Warning</option>
                      <option class="btn-info" selected value="info">Informational</option>
                    </select>
                  </div>
                </div>
              </div>

              <div class="tab-pane fade" id="step2" role="tabpanel">
              <h5 class="mb-4">Grouping the Metrics</h5>
              <p class="text-muted mb-4">Grouping is Optional</p>
                <div class="row mb-3">
                  <div class="col-md-12">
                    <label class="form-label">Group Granularity</label>
                    <select v-model="form.group_granularity" class="form-select">
                      <option selected disabled value="">Select granularity</option>
                      <option value="per-metric">per-metric</option>
                      <option value="per-hostname">per-hostname</option>
                      <option value="per-group">per-group</option>
                      <option value="global">global</option>
                    </select>
                  </div>
                </div>
                <div class="row mb-3">
                  <div class="col-md-12">
                    <label class="form-label">Grouping Aggregation Operator</label>
                    <select v-model="form.aggregation_operator" class="form-select">
                      <option selected disabled value="">Select Aggregation Operator</option>
                      <option value="max">max</option>
                      <option value="min">min</option>
                      <option value="avg">avg</option>
                      <option value="sum">sum</option>
                      <option value="count">count</option>
                    </select>
                  </div>
                </div>
              </div>

              <div class="tab-pane fade" id="step3" role="tabpanel">
                <h5 class="mb-4">Select Metrics</h5>
                <p class="text-muted mb-4">Select the exporter and metric to monitor.</p>
                <div class="mb-3">
                  <label class="form-label">Select Category</label>
                  <select v-model="form.selectedCategory" id="exporter" class="form-select" :class="{ 'is-invalid': !form.selectedCategory && showValidation }" :disabled="!exporters.length" @change="() => form.selectedCategory && fetchMetrics(form.selectedCategory)">
                      <option selected disabled value="">Select Category(Exporter)</option>
                      <option v-for="exporter in exporters" :key="exporter" :value="exporter">{{ exporter }}</option>
                    </select>
                    <div class="invalid-feedback">Category selection is madatory to build a rule.</div>
                </div>

                <div class="mb-3">
                  <label class="form-label">Select Metric</label>
                  <select v-model="form.selectedMetrics" id="metrics" class="form-select" :class="{ 'is-invalid': !form.selectedMetrics && showValidation }" :disabled="!metrics.length">
                      <option selected disabled value="">Select Metric</option>
                      <option v-for="metric in metrics" :key="metric" :value="metric">{{ metric }}</option>
                    </select>
                    <div class="invalid-feedback">Metric selection is madatory to build a rule.</div>
                </div>
              </div>

              <div class="tab-pane fade" id="step4" role="tabpanel">
                <h5 class="mb-4">Filter Metrics</h5>
                <p class="text-muted mb-4">Please select the filter criteria for the metrics.</p>
                <div class="row mb-3">
                  <div class="col-md-12">
                    <label class="form-label">Filter Key</label>
                    <select v-model="form.selectedFilterKey" id="filter_key" class="form-select" :class="{ 'is-invalid': !form.selectedFilterKey && showValidation }">
                      <option selected disabled value="">Select filter key</option>
                      <option value="luna_group">luna_group</option>
                      <option value="hostname">hostname</option>
                    </select>
                    <div class="invalid-feedback">Filter Key selection is madatory to build a rule.</div>
                  </div>
                  </div>
                  <div class="row mb-3">
                  <div class="col-md-12">
                    <label class="form-label">Filter Value</label>
                    <select v-if="form.selectedFilterKey === 'luna_group'" v-model="form.selectedGroup" id="luna_group" class="form-select" :class="{ 'is-invalid': !form.selectedGroup && showValidation }" :disabled="!luna_groups.length">
                      <option selected disabled value="">Select Filter Value</option>
                      <option v-for="group in luna_groups" :key="group" :value="group">{{ group }}</option>
                    </select>
                    <select v-else-if="form.selectedFilterKey === 'hostname'" v-model="form.selectedHostname" id="hostname" class="form-select" :class="{ 'is-invalid': !form.selectedHostname && showValidation }" :disabled="!hostnames.length">
                      <option selected disabled value="">Select Filter Value</option>
                      <option v-for="hostname in hostnames" :key="hostname" :value="hostname">{{ hostname }}</option>
                    </select>
                    <select v-else class="form-select" disabled>
                      <option selected disabled value="">Select Filter Value</option>
                    </select>
                    <div class="invalid-feedback">Filter Value selection is madatory to build a rule.</div>
                  </div>
                </div>

                <div class="mb-3">
                  <label class="form-label">Grouping Operator</label>
                  <select v-model="form.grouping_operator" id="grouping_operator" class="form-select" :class="{ 'is-invalid': !form.grouping_operator && showValidation }">
                    <option selected disabled value="">Select Grouping Comparison</option>
                    <option value=">">&gt;</option>
                    <option value="<">&lt;</option>
                    <option value=">=">&gt;=</option>
                    <option value="<=">&lt;=</option>
                    <option value="=">=</option>
                  </select>
                  <div class="invalid-feedback">Grouping Operator selection is madatory to build a rule.</div>
                </div>

                <div class="mb-3">
                  <label class="form-label">Threshold</label>
                  <input v-model="form.threshold" type="number" id="threshold" autocomplete="off" class="form-control" :class="{ 'is-invalid': String(form.threshold) === '' && showValidation }" placeholder="Enter threshold value">
                  <div class="invalid-feedback">Threshold is madatory to build a rule.</div>
                </div>
              </div>

              <div class="tab-pane fade" id="test" role="tabpanel">
                <h5 class="mb-4">Test stage content.</h5>
                <div class="alert alert-info" role="alert"><strong>Constructed Query: <i>{{ constructQuery() }}</i></strong></div>

                <div v-if="validationResult">
                  <div v-if="!validationResult.valid" class="alert alert-warning" role="alert"><strong>Test Fails ❌: Status: <i>{{ validationResult.error }}</i></strong></div>
                  <div v-if="validationResult.valid" class="alert alert-success" role="alert"><strong>Test Pass ✅: <i>Constructed Queery is a valid Prometheus Query.</i></strong></div>
                  <div v-if="validationResult.valid" class="p-3">
                    <Line v-if="chartData" :data="chartData" :options="chartOptions" />
                    <div v-else>Loading chart...</div>
                  </div>
                </div>
              </div>

              <div class="tab-pane fade" id="finish" role="tabpanel">
                <h5 class="mb-4">Finish stage content.</h5>
                <p class="text-muted mb-4">Review Rule settings and save the rule.</p>
                <table class="table table-bordered table-striped">
                  <thead>
                    <tr>
                      <th scope="col">Key</th>
                      <th scope="col">Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <th scope="col">Rule Name</th>
                      <td scope="col">{{ form.rule_name }}</td>
                    </tr>
                    <tr>
                      <th scope="col">Rule Description</th>
                      <td scope="col">{{ form.rule_description }}</td>
                    </tr>
                    <tr>
                      <th scope="col">Rule For</th>
                      <td scope="col">{{ form.rule_for }}</td>
                    </tr>
                    <tr>
                      <th scope="col">Rule Category</th>
                      <td scope="col">{{ form.rule_category }}</td>
                    </tr>
                    <tr>
                      <th scope="col">Rule Status</th>
                      <td scope="col">{{ form.rule_status ? 'Enabled' : 'Disabled' }}</td>
                    </tr>
                    <tr>
                      <th scope="col">Rule NHC</th>
                      <td scope="col">{{ form.rule_nhc ? 'Enabled' : 'Disabled' }}</td>
                    </tr>
                    <tr>
                      <th scope="col">Rule Severity</th>
                      <td scope="col">{{ form.rule_severity }}</td>
                    </tr> 
                    <tr>
                      <th scope="col">Rule Exprestion</th>
                      <td scope="col" class="table-info">{{ constructQuery() }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Navigation buttons -->
            <div class="modal-footer">
              <div class="mt-3 d-flex justify-content-between" style="float: right;">
                <button type="button" class="btn btn-outline-secondary me-2" data-bs-dismiss="modal">Close</button>
                <button v-if="currentIndex !== 0" id="prevBtn" class="btn btn-secondary me-2" @click="goPrev">Previous (Step {{ currentIndex }})</button>
                <button id="nextBtn" class="btn btn-primary" @click="goNext">{{ currentIndex === 5 ? 'Save Rule' : 'Next' }}</button>
              </div>
            </div>
        </div>
      </div>
    </div>
  </div>
</template>
