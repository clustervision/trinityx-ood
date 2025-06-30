<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import axios, { AxiosError } from 'axios';


const currentIndex = ref(0);
const tabs = ref<HTMLElement[]>([]);
const nextBtn = ref<HTMLButtonElement | null>(null);
const prevBtn = ref<HTMLButtonElement | null>(null);

/**
 * Sync tab display with current index
 */
function updateTab(index: number) {
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
  updateTab(currentIndex.value);
});

/**
 * Navigation: Previous
 */
function goPrev() {
  if (currentIndex.value > 0) {
    updateTab(currentIndex.value - 1);
  }
}

/**
 * Navigation: Next
 */
function goNext() {
  if (currentIndex.value < tabs.value.length - 1) {
    updateTab(currentIndex.value + 1);
  } else {
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
              <div class="tab-pane fade show active" id="step1" role="tabpanel">Step 1 content here.
                <!-- <h2 class="mb-4">Basic Rule Information</h2>
                <div class="row g-6">
                  <div class="col mb-0">
                    <label for="rule_name" class="form-label">Rule Name</label>
                    <input type="text" id="rule_name" class="form-control" placeholder="Enter Rule Name" required/>
                  </div>
                </div>
                <div class="row">
                  <div class="col mb-6">
                    <label for="rule_description" class="form-label">Rule Description</label>
                    <input type="text" id="rule_description" class="form-control" required placeholder="Enter Rule Description" />
                  </div>
                </div>
                <div class="row">
                  <div class="col mb-0">
                    <label for="rule_for" class="form-label">Rule For</label>
                    <input type="text" id="rule_for" class="form-control" placeholder="Enter Rule For"  />
                  </div>
                </div>
                <div class="row">
                  <div class="col mb-6">
                    <label for="rule_category" class="form-label">Rule Category</label>
                    <select id="rule_category" class="form-select">
                      <option class="btn-primary" value="">Set Category</option>
                      <option class="btn-info" value="generic">Generic</option>
                      <option class="btn-warning" value="service">Service</option>
                      <option class="btn-dark" value="hardware">Hardware</option>
                    </select>
                  </div>
                  <div class="col mb-0">
                    <label for="rule_status" class="form-label">Enable</label>
                    <div class="form-check form-switch ">
                      <input type="checkbox" id="rule_status" class="form-check-input" />
                      <label id="rule_status_label" for="rule_status" class="form-check-label">ON</label>
                    </div>
                  </div>
                  <div class="col mb-6">
                    <label for="rule_nhc" class="form-label">Rule NHC</label>
                    <div class="form-check form-switch ">
                      <input type="checkbox" id="rule_nhc" class="form-check-input" data-toggle="switch" true-value=true false-value=false />
                      <label id="rule_nhc_label" for="rule_nhc" class="form-check-label">ON</label>
                    </div>
                  </div>
                  <div class="col mb-6">
                    <label for="rule_severity" class="form-label">Set Severity</label>
                    <select id="rule_severity" class="form-select">
                      <option class="btn-primary" value="">Set Severity</option>
                      <option class="btn-dark" value="critical">Critical</option>
                      <option class="btn-danger" value="danger">Danger</option>
                      <option class="btn-warning" value="warning">Warning</option>
                      <option class="btn-info" value="info">Informational</option>
                    </select>
                  </div>
                </div>
                 -->
              </div>
              <div class="tab-pane fade" id="step2" role="tabpanel">Step 2 content here.</div>
              <div class="tab-pane fade" id="step3" role="tabpanel">Step 3 content here.</div>
              <div class="tab-pane fade" id="step4" role="tabpanel">Step 4 content here.</div>
              <div class="tab-pane fade" id="test" role="tabpanel">Test stage content.</div>
              <div class="tab-pane fade" id="finish" role="tabpanel">Finish content. You're done!</div>
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









          <!-- <div class="container">
            <h3 class="mb-4">Create Monitoring Rule</h3>
            <form>
              
              <div class="row mb-3">
                <div class="col-md-6">
                  <label class="form-label">Group Granularity</label>
                  <select class="form-select">
                    <option selected disabled value="">Select granularity</option>
                    <option value="per-metric">per-metric</option>
                    <option value="per-hostname">per-hostname</option>
                    <option value="per-group">per-group</option>
                    <option value="global">global</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Grouping Operator</label>
                  <select class="form-select">
                    <option selected disabled value="">Select operator</option>
                    <option value="max">max</option>
                    <option value="min">min</option>
                    <option value="avg">avg</option>
                    <option value="sum">sum</option>
                    <option value="count">count</option>
                  </select>
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">Select Category</label>
                <select v-model="selectedCategory" id="exporter" class="form-select" :disabled="!exporters.length" @change="() => fetchMetrics(selectedCategory)">
                    <option selected disabled value="">Select Category(Exporter)</option>
                    <option v-for="exporter in exporters" :key="exporter" :value="exporter">{{ exporter }}</option>
                  </select>
              </div>

              <div class="mb-3">
                <label class="form-label">Select Metric</label>
                <select v-if="metrics.length" v-model="selectedMetrics" id="metrics" class="form-select" :disabled="!metrics.length">
                    <option selected disabled value="">Select Metric</option>
                    <option v-for="metric in metrics" :key="metric" :value="metric">{{ metric }}</option>
                  </select>
              </div>

              <div class="row mb-3">
                <div class="col-md-6">
                  <label class="form-label">Filter Key</label>
                  <select v-model=selectedFilterKey class="form-select">
                    <option selected disabled value="">Select filter key</option>
                    <option value="luna_group">luna_group</option>
                    <option value="hostname">hostname</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Filter Value</label>
                  <select v-if="selectedFilterKey === 'luna_group'" v-model="selectedGroup" id="luna_group" class="form-select" :disabled="!luna_groups.length">
                    <option selected disabled value="">Select Filter Value</option>
                    <option v-for="group in luna_groups" :key="group" :value="group">{{ group }}</option>
                  </select>
                  <select v-if="selectedFilterKey === 'hostname'" v-model="selectedHostname" id="hostname" class="form-select" :disabled="!hostnames.length">
                    <option selected disabled value="">Select Filter Value</option>
                    <option v-for="hostname in hostnames" :key="hostname" :value="hostname">{{ hostname }}</option>
                  </select>
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">Select Operator</label>
                <select class="form-select">
                  <option selected disabled value="">Select comparison</option>
                  <option value=">">&gt;</option>
                  <option value="<">&lt;</option>
                  <option value=">=">&gt;=</option>
                  <option value="<=">&lt;=</option>
                  <option value="=">=</option>
                </select>
              </div>

              <div class="mb-3">
                <label class="form-label">Threshold</label>
                <input type="number" class="form-control" placeholder="Enter threshold value">
              </div>
              </form>
              </div> -->
        </div>
      </div>
    </div>
  </div>
</template>
