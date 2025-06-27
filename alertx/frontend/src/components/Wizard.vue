<script setup lang="ts">
import { ref } from 'vue';
import axios, { AxiosError } from 'axios';


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

<template>
  <div class="modal fade" id="wizard_modal" tabindex="-1" >
    <div class="modal-dialog modal-xl" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="exampleModalLabel4">Rule Wizard</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div class="container">
            <h3 class="mb-4">Create Monitoring Rule</h3>
            <form>
              <!-- per-metric -->
              <div class="mb-3">
                <label class="form-label">Per-Metric</label>
                <select class="form-select">
                  <option selected disabled value="">Select metric type</option>
                  <option value="per-GPU">per-GPU</option>
                  <option value="per-Disk">per-Disk</option>
                  <option value="per-NIC">per-NIC</option>
                </select>
              </div>

              <!-- group granularity & operator -->
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

              <!-- Select category -->
              <div class="mb-3">
                <label class="form-label">Select Category</label>
                <select v-model="selectedCategory" id="exporter" class="form-select" :disabled="!exporters.length" @change="() => fetchMetrics(selectedCategory)">
                    <option selected disabled value="">Select Category(Exporter)</option>
                    <option v-for="exporter in exporters" :key="exporter" :value="exporter">{{ exporter }}</option>
                  </select>
              </div>

              <!-- Select metric -->
              <div class="mb-3">
                <label class="form-label">Select Metric</label>
                <select v-if="metrics.length" v-model="selectedMetrics" id="metrics" class="form-select" :disabled="!metrics.length">
                    <option selected disabled value="">Select Metric</option>
                    <option v-for="metric in metrics" :key="metric" :value="metric">{{ metric }}</option>
                  </select>
              </div>

              <!-- Filter key & value -->
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

              <!-- Operator -->
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

              <!-- Threshold -->
              <div class="mb-3">
                <label class="form-label">Threshold</label>
                <input type="number" class="form-control" placeholder="Enter threshold value">
              </div>
              </form>
              </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Close</button>
          <button type="button" class="btn btn-primary">Save Rule</button>
        </div>
      </div>
    </div>
  </div>
</template>
