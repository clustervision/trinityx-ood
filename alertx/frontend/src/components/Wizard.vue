<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import axios, { AxiosError } from 'axios';


const currentIndex = ref(0);
const tabs = ref<HTMLElement[]>([]);
const nextBtn = ref<HTMLButtonElement | null>(null);
const prevBtn = ref<HTMLButtonElement | null>(null);
const showValidation = ref(false);

function validateForm() {
  if (currentIndex.value === 0) {
    const ruleName = document.getElementById('rule_name') as HTMLInputElement;
    const ruleDescription = document.getElementById('rule_description') as HTMLTextAreaElement;
    const ruleFor = document.getElementById('rule_for') as HTMLInputElement;
    const ruleCategory = document.getElementById('rule_category') as HTMLSelectElement;
    const ruleStatus = document.getElementById('rule_status') as HTMLInputElement;
    const ruleSeverity = document.getElementById('rule_severity') as HTMLSelectElement;

    if (!ruleName.value || !ruleDescription.value || !ruleFor.value || !ruleCategory.value || !ruleSeverity.value) {
      // alert('Please fill all required fields in Step 1');
      showValidation.value = true;
      return false;
    }
    return true;
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
  tabs.value = Array.from(document.querySelectorAll<HTMLElement>('#wizardTabs .nav-link'));
  nextBtn.value = document.getElementById('nextBtn') as HTMLButtonElement;
  prevBtn.value = document.getElementById('prevBtn') as HTMLButtonElement;

  // Initialize tab state
  updateTab(false, currentIndex.value);
});

/**
 * Navigation: Previous
 */
function goPrev() {
  if (currentIndex.value > 0) {
    updateTab(true, currentIndex.value - 1);
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

    alert("Wizard Complete!");
  }
}

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


const props = defineProps({
  PrometheusServer: {
    type: String,
    required: true,
  },
  url: {
    type: String,
    required: true,
  },

});

const PrometheusServer = new URL(props.PrometheusServer);
const PrometheusTarget = new URL(PrometheusServer.toString());
PrometheusTarget.pathname = '/api/v1/targets';
PrometheusTarget.searchParams.set('scrapePool', '');
console.log('Prometheus Target URL:', PrometheusTarget);
const PrometheusMetric = new URL(PrometheusServer.toString());
PrometheusMetric.pathname = '/api/v1/query';


let exporters = ref<string[]>([]);
let luna_groups = ref<string[]>([]);
let hostnames = ref<string[]>([]);
let metrics = ref<string[]>([]);
const selectedCategory = ref('');
const selectedMetrics = ref('');
const selectedFilterKey = ref('');
const selectedGroup = ref('');
const selectedHostname = ref('');

async function fetchTarget() {
  try {
    const proxyUrl = `${props.url}/proxy?url=${PrometheusTarget}`;
    const response = await axios.get(proxyUrl);
    if (response.status === 200) {
      const activeTargets = response.data.data.activeTargets;
      console.log(proxyUrl);
      console.log(response.status);
      console.log(activeTargets);
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
      console.log(luna_groups.value);
      console.log(exporters.value);
      console.log(hostnames.value);
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
fetchTarget();


async function fetchMetrics(exporter: string) {
  metrics.value = [];
  PrometheusMetric.searchParams.set('query', `avg by (__name__) ({__name__=~".*", exporter="${exporter}"})`);
  try {
    const proxyUrl = `${props.url}/proxy?url=${PrometheusMetric}`;
    const response = await axios.get(proxyUrl);
    if (response.status === 200) {
      const result = response.data.data.result;
      console.log(proxyUrl);
      console.log(response.status);
      console.log(result);
      result.forEach((MetricsResult: PrometheusMetrics) => {
        const metric = MetricsResult.metric?.__name__;
        if (metric && !metrics.value.includes(metric)) {
          metrics.value.push(metric);
        }
      });
      console.log(luna_groups.value);
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
const form = reactive<WidgetForm>({
  rule_name: '',
  rule_description: '',
  rule_for: '',
  rule_category: '',
  rule_status: false,
  rule_nhc: false,
  rule_severity: '',
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
// });
function submitForm() {
  console.log(form); // full reactive object
  // Send via axios
  // axios.post('/api/rules', form)
  const query = constructQuery();
  console.log('Constructed Query:', query);
}


const granularityMap: Record<string, string> = {
  'per-metric': '',              // no group
  'per-hostname': 'hostname',
  'per-group': 'luna_group',
  'global': '',                  // treat as no `by (...)`
};


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
  <div class="modal fade" id="wizard_modal" tabindex="-1" >
    <div class="modal-dialog modal-xl" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="exampleModalLabel4">Rule Creation Wizard</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body container-fluid">
          <div class="">
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
            <div class="tab-content border border-top-0 p-3" id="wizardTabContent" style="height: 500px; overflow-y: auto;">
              <!-- class="needs-validation" novalidate -->
              <!-- <form id="wizardForm" > -->
              
              <div class="tab-pane fade show active" id="step1" role="tabpanel">
                <h2 class="mb-4">Basic Rule Information</h2>
                <div class="row g-6">
                  <div class="col mb-0">
                    <label for="rule_name" class="form-label">Rule Name</label>
                    <input type="text" v-model="form.rule_name" id="rule_name" class="form-control" :class="{ 'is-invalid': !form.rule_name && showValidation }" placeholder="Enter Rule Name" required/>
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
                    <input type="text" v-model="form.rule_for" id="rule_for" class="form-control" :class="{ 'is-invalid': !form.rule_for && showValidation }" placeholder="Enter Rule For"  />
                    <div class="invalid-feedback">Rule For is required.</div>
                  </div>
                </div>
                <div class="row">
                  <div class="col mb-6">
                    <label for="rule_category" class="form-label">Rule Category</label>
                    <select v-model="form.rule_category" id="rule_category" class="form-select">
                      <option class="btn-primary" value="">Set Category</option>
                      <option class="btn-info" value="generic">Generic</option>
                      <option class="btn-warning" value="service">Service</option>
                      <option class="btn-dark" value="hardware">Hardware</option>
                    </select>
                  </div>
                  <div class="col mb-0">
                    <label for="rule_status" class="form-label">Enable</label>
                    <div class="form-check form-switch ">
                      <input v-model="form.rule_status" type="checkbox" id="rule_status" class="form-check-input" />
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
                      <option class="btn-primary" value="">Set Severity</option>
                      <option class="btn-dark" value="critical">Critical</option>
                      <option class="btn-danger" value="danger">Danger</option>
                      <option class="btn-warning" value="warning">Warning</option>
                      <option class="btn-info" value="info">Informational</option>
                    </select>
                  </div>
                </div>
                
              </div>

              <div class="tab-pane fade" id="step2" role="tabpanel">
              <h2 class="mb-4">Grouping the Metrics</h2>
              <p class="text-muted mb-4">Optional</p>
                
                <div class="row mb-3">
                <div class="col-md-6">
                  <label class="form-label">Group Granularity</label>
                  <select v-model="form.group_granularity" class="form-select">
                    <option selected disabled value="">Select granularity</option>
                    <option value="per-metric">per-metric</option>
                    <option value="per-hostname">per-hostname</option>
                    <option value="per-group">per-group</option>
                    <option value="global">global</option>
                  </select>
                </div>
                <div class="col-md-6">
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

                <h2 class="mb-4">Select Metrics</h2>
                <p class="text-muted mb-4">Select the exporter and metric to monitor.</p>
                <div class="mb-3">
                  <label class="form-label">Select Category</label>
                  <select v-model="form.selectedCategory" id="exporter" class="form-select" :disabled="!exporters.length" @change="() => form.selectedCategory && fetchMetrics(form.selectedCategory)">
                      <option selected disabled value="">Select Category(Exporter)</option>
                      <option v-for="exporter in exporters" :key="exporter" :value="exporter">{{ exporter }}</option>
                    </select>
                </div>

                <div class="mb-3">
                  <label class="form-label">Select Metric</label>
                  <select v-if="metrics.length" v-model="form.selectedMetrics" id="metrics" class="form-select" :disabled="!metrics.length">
                      <option selected disabled value="">Select Metric</option>
                      <option v-for="metric in metrics" :key="metric" :value="metric">{{ metric }}</option>
                    </select>
                </div>
              </div>

            <!-- </form> -->
              <div class="tab-pane fade" id="step4" role="tabpanel">
                
                <h2 class="mb-4">Filter Metrics</h2>
                <p class="text-muted mb-4">Optional</p>
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="form-label">Filter Key</label>
                    <select v-model="form.selectedFilterKey" class="form-select">
                      <option selected disabled value="">Select filter key</option>
                      <option value="luna_group">luna_group</option>
                      <option value="hostname">hostname</option>
                    </select>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">Filter Value</label>
                    <select v-if="form.selectedFilterKey === 'luna_group'" v-model="form.selectedGroup" id="luna_group" class="form-select" :disabled="!luna_groups.length">
                      <option selected disabled value="">Select Filter Value</option>
                      <option v-for="group in luna_groups" :key="group" :value="group">{{ group }}</option>
                    </select>
                    <select v-if="form.selectedFilterKey === 'hostname'" v-model="form.selectedHostname" id="hostname" class="form-select" :disabled="!hostnames.length">
                      <option selected disabled value="">Select Filter Value</option>
                      <option v-for="hostname in hostnames" :key="hostname" :value="hostname">{{ hostname }}</option>
                    </select>
                  </div>
                </div>

                <div class="mb-3">
                  <label class="form-label">Grouping Operator</label>
                  <select v-model="form.grouping_operator" class="form-select">
                    <option selected disabled value="">Select Grouping Comparison</option>
                    <option value=">">&gt;</option>
                    <option value="<">&lt;</option>
                    <option value=">=">&gt;=</option>
                    <option value="<=">&lt;=</option>
                    <option value="=">=</option>
                  </select>
                </div>

                <div class="mb-3">
                  <label class="form-label">Threshold</label>
                  <input v-model="form.threshold" type="number" class="form-control" placeholder="Enter threshold value">
                </div>
              
              </div>


              <div class="tab-pane fade" id="test" role="tabpanel">
                
                <h2 class="mb-4">Test stage content.</h2>
                <p class="text-muted mb-4">Test the rule with the selected metrics and filters.</p>
              
              
              </div>


              <div class="tab-pane fade" id="finish" role="tabpanel">

                <h2 class="mb-4">Finish stage content.</h2>
                <p class="text-muted mb-4">You're done! Review your settings and save the rule.</p>
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
  </div>
</template>
