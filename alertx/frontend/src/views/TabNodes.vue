<!-- <script lang="ts">
import { ref, watch, computed, onMounted } from "vue";
import axios from "axios";

interface ToastItem {
  message: string;
  toastClassName: string;
}

interface resetObject {
  hostname: string;
  message: string;
  status: boolean;
}

interface NodeRules {
  alert: string;
  annotations: { description: string; };
  expr: string;
  for: string | null;
  labels: { severity: string; };
}

interface RuleTable {
  id: number;
  rule: string;
  severity: string;
  time: string;
  expr: string;
  description: string;
  hostname: string;
}

interface Node {
  hostname: string;
  status: boolean;
  message: string;
  data: {groups: [{rules: NodeRules[]}];};
  rules: NodeRules[];
  class: string;
}

interface HardwareMetric {
  luna_group: string;
  hostname: string;
  class: string;
  vendor: string;
  description: string;
  size: string;
  clock: string;
  serial: string;
  product: string;
  handle: string;
  physid: string;
  version: string;
  slot: string;
}

interface InventoryItem {
  id: number;
  luna_group: string;
  hostname: string;
  class: string;
  vendor: string;
  description: string;
  size: string;
  clock: string;
  serial: string;
  product: string;
  handle: string;
  physid: string;
  version: string;
  slot: string;
}

interface Hardware {
  metric: HardwareMetric;
}

export default {

  props: {
    isActive: {
      type: Boolean,
      required: true,
      default: false,
    },
    url: {
      type: String,
      required: true,
    },
    promQLurl: {
      type: String,
      required: true,
    },
  },

  setup(props) {
    const nodeStatus = ref(true);
    const nodeNHC = ref(true);
    const nodes = ref<Node[]>([]);
    const nodes_rules =  ref<RuleTable[]>([]);
    const inventory = ref<InventoryItem[]>([]);
    const rule_message = ref("");
    const hardware_message = ref("");
    const selectedIndices = ref<number[]>([]);
    const searchTerm = ref("");
    const currentFilter = ref("all");
    const toastQueue = ref<ToastItem[]>([]);
    const showToast = ref(false);
    const toastMessage = ref("");
    const error_message = ref<string[]>([]);
    const toastClass = ref("");

    function Toast(message: string, toastClassName: string) {
      toastQueue.value.push({ message, toastClassName });
      processQueue();
    };

    function processQueue() {
      if (!showToast.value && toastQueue.value.length > 0) {
        const nextToast = toastQueue.value.shift();
        if (nextToast) {
          const { message, toastClassName } = nextToast;
          toastMessage.value = message;
          toastClass.value = toastClassName;
          showToast.value = true;
          setTimeout(() => {
            showToast.value = false;
            processQueue();
          }, 3000);
        }
      }
    };

    const fetchNodes = async () => {
      try {
        const response = await axios.get(`${props.url}/get_nodes`);
        if (response.status === 200) {
          nodes.value = response.data.map((node: Node) => ({
            hostname: node.hostname,
            status: node.status,
            message: node.status ? '' : node.message,
            rules: node.data ? node.data.groups[0].rules : [],
            class: node.status ? "primary" : "secondary",
          }));
        } else {
          Toast(`Error fetching nodes: ${response.status}`, "bg-secondary");
        }
      } catch (error) {
        Toast("Failed to fetch nodes.", "bg-secondary");
        console.error("Error fetching nodes:", error);
      }
    };

    const filteredNodes = computed(() => {
      let filtered = nodes.value;
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase();
        filtered = filtered.filter((node) =>
          node.hostname.toLowerCase().includes(term)
        );
      }
      if (currentFilter.value === "secondary") {
        filtered = filtered.filter((node) => node.class === "secondary");
      }
      return filtered;
    });

    const toggleSelect = (index: number) => {

      const currentIndex = selectedIndices.value.indexOf(index);
      if (currentIndex === -1) {
        selectedIndices.value.push(index);
        showInventory(index);
        showRules(index);
      } else {
        selectedIndices.value.splice(currentIndex, 1);
        if (selectedIndices.value.length === 0){
          inventory.value = [];
          hardware_message.value = ``;
          nodes_rules.value = [];
          rule_message.value = ``;
        } else {
          showInventory(selectedIndices.value[selectedIndices.value.length - 1]);
          showRules(selectedIndices.value[selectedIndices.value.length - 1]);
        }
      }

    };

    const selectAllNodes = () => {
      selectedIndices.value = nodes.value.map((_, index) => index);
    };

    const revertSelection = () => {
      selectedIndices.value = [];
      inventory.value = [];
      hardware_message.value = ``;
      nodes_rules.value = [];
      rule_message.value = ``;
    };

    const selectFailedNodes = () => {
      selectedIndices.value = nodes.value
        .map((node, index) => (node.class === "secondary" ? index : -1))
        .filter((index) => index !== -1);
    };

    const resetSelectedNodes = async () => {
      error_message.value = [];
      if (selectedIndices.value.length === 0){
        Toast("Please select at least one node.", "bg-warning");
      } else {
        const selectedNodes = selectedIndices.value.map(
          (index) => nodes.value[index]
        );
        const payload = selectedNodes.map((node) => ({
          hostname: node.hostname,
          force: true,
        }));

        try {
          const response = await axios.post(`${props.url}/save_nodes`, payload);
          if (response.status === 200) {
            response.data.response.forEach((result: resetObject) => {
              if (result.status === true){
                // Toast(result.message, result.status ? "bg-success" : "bg-secondary");
                Toast(`SUCCESS[RESET] :: Node ${result.hostname} is Reset.`, "bg-success");
              } else {
                error_message.value.push(result.message.replace(/(.{200})/g, "$1\n"));
              }
            });
          }
        } catch (error) {
          Toast("Error saving selected nodes.", "bg-secondary");
          console.error("Error saving nodes:", error);
        }
        revertSelection();
        fetchNodes();
      }

    };

    const fetchGlobalSettings = async () => {
      try {
        const response = await axios.get(`${props.url}/get_global`);
        if (response.status === 200) {
          if (response.data.hw.disabled === false){
            nodeStatus.value = true;
          } else {
            nodeStatus.value = false;
          }
          if (response.data.hw.nhc === true){
            nodeNHC.value = true;
          } else {
            nodeNHC.value = false;
          }
        } else {
          Toast(`ERROR[Global Settings] :: ${response.status}`, "bg-secondary");
        }
      } catch (error) {
        Toast("Failed to fetch Global Settings.", "bg-secondary");
        console.error("Error fetching nodes:", error);
      }
    };
    // fetchGlobalSettings();

    const setGlobalSettings = async (event: Event) => {
      error_message.value = [];
      const target = event.target as HTMLInputElement;
      const checkboxName = target.name;
      let isChecked = target.checked;
      let name = "";
      let answer = false;
      let error_str = "";
      if (checkboxName === "disabled" && isChecked === true){
          isChecked = false;
          name = "Enable";
          answer = true;
      } else if (checkboxName === "disabled" && isChecked === false){
          isChecked = true;
          name = "Enable";
          answer = false;
      } else { name = "NHC"; answer = isChecked; }
      const payload = { hw: { [checkboxName]: isChecked } };
      try {
        const response = await axios.post(`${props.url}/set_global`, payload);
        if (response.status === 200) {
          error_str = response.data.response;
          if (response.data.response.length === 0){
            Toast(`Global[${name}] is set to [${answer}] for All Nodes.`, "bg-success");
          } else {
            response.data.response.forEach((result: resetObject) => {
              let message: string = '';
              let messageClass: string = '';
              if (result.status){
                message = `Global[${name}] for ${result.hostname} is set to [${answer}].`;
                messageClass = "bg-success";
                Toast(message, messageClass);
              } else {
                message = `ERROR :: Global[${name}] for ${result.hostname} is ${result.message}.`;
                messageClass = "bg-secondary";
                error_message.value.push(message);
              }

            });
          }
        }
      } catch (error) {
        Toast(`ERROR :: ${error_str} ${error}`, "bg-secondary");
        console.error("Error saving nodes:", error);
      }
    };


    const showInventory = async (index: number) =>  {
      const hostname = nodes.value[index].hostname;
      const inventoryURL = `${props.url}/proxy?url=${props.promQLurl}/api/v1/query?query=lshw_device%7Bhostname%3D%7E%22${hostname}%22%2C+id%3D%7E%22cpu%7Cdisplay%7Cnetwork%7Cdisk%7Cbank%3A.*%22%7D`;
      // const inventoryURL = `https://demo-controller1.cluster:9090/api/v1/query?query=lshw_device%7Bhostname%3D%7E%22${hostname}%22%2C+id%3D%7E%22cpu%7Cdisplay%7Cnetwork%7Cdisk%7Cbank%3A.*%22%7D`;
      try {
        const response = await axios.get(inventoryURL);
        if (response.status === 200) {
          inventory.value = response.data.data.result.map((hwd: Hardware, index: number) => ({
            id: index + 1,
            luna_group:   hwd.metric.luna_group ? hwd.metric.luna_group : "N/A",
            hostname:     hwd.metric.hostname ? hwd.metric.hostname : "N/A",
            class:        hwd.metric.class ? hwd.metric.class : "N/A",
            vendor:       hwd.metric.vendor ? hwd.metric.vendor : "N/A",
            description:  hwd.metric.description ? hwd.metric.description : "N/A",
            size:         hwd.metric.size ? hwd.metric.size : "N/A",
            clock:        hwd.metric.clock ? hwd.metric.clock : "N/A",
            serial:       hwd.metric.serial ? hwd.metric.serial : "N/A",
            product:      hwd.metric.product ? hwd.metric.product : "N/A",
            handle:       hwd.metric.handle ? hwd.metric.handle : "N/A",
            physid:       hwd.metric.physid ? hwd.metric.physid : "N/A",
            version:      hwd.metric.version ? hwd.metric.version : "N/A",
            slot:         hwd.metric.slot ? hwd.metric.slot : "N/A",
          }));
          if (inventory.value.length === 0){
            hardware_message.value = `There is no Hardware Configuration is available for ${hostname}.`;
          }
        } else {
          Toast(`Error fetching Hardware: ${response.status}`, "bg-secondary");
          hardware_message.value = `Error fetching Hardware: ${response.status} `;
        }
      } catch (error) {
        // Toast(`Failed to fetch Hardware Inventory for ${hostname}.`, "bg-secondary");
        console.error("Error fetching URL:", error);
        hardware_message.value = `Failed to fetch Hardware Inventory for ${hostname}: ${error}`;
      }
    };

  const showRules = async (index: number) =>  {
    const hostname = nodes.value[index].hostname;
    const nodeRules = nodes.value[index].rules;
    nodes_rules.value = nodeRules.map((Rule, index): RuleTable => ({
      id: index + 1,
      rule: Rule.alert,
      severity: Rule.labels.severity,
      time: Rule.for ?? "",
      expr: Rule.expr,
      description: Rule.annotations.description,
      hostname: hostname,
    }));
    if (nodes_rules.value.length === 0){
      rule_message.value = `There is no Rule Configuration is available for ${hostname}.`;
    }
  };

    watch(() => props.isActive, async (newValue) => {
      if (newValue) {
        fetchNodes();
        fetchGlobalSettings();
      }
    });

    onMounted(() => {
      if (props.isActive) {
        fetchNodes();
        fetchGlobalSettings();
      }

    });


    return {
      nodes,
      selectedIndices,
      searchTerm,
      toggleSelect,
      selectAllNodes,
      revertSelection,
      selectFailedNodes,
      resetSelectedNodes,
      filteredNodes,
      showToast,
      toastClass,
      toastMessage,
      processQueue,
      showRules,
      showInventory,
      nodeStatus,
      nodeNHC,
      inventory,
      hardware_message,
      nodes_rules,
      rule_message,
      fetchGlobalSettings,
      setGlobalSettings,
      error_message,
    };
  },
};
</script>

<style lang="css">
.node-box{
  padding-bottom: 0.2rem;
  padding-right: 0.2rem;
}
.node-box:hover {
  cursor: pointer;
}
.node-body {
  padding-left: 0.5rem;
  padding-bottom: 0.2rem;
  padding-top: 0.2rem;
}

.selected {
  border: 2px solid rgb(17, 0, 255);
  background-color: #f8f9fa;
  color: black;
  padding: 0rem;
  border-radius: 12px;
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
}
.selected .card-text{
  font-weight: bold;
}

.selected .card-text{
  font-weight: bold;
}

.nav_head {
  font-weight: bold;
}

.node_pan {
  background-color: antiquewhite;
  padding-top: 0.8rem;
  padding-bottom: 0.8rem;
}
</style>

<template>
  <h4 class="fw-bold py-3 mb-4">
    <span class="text-muted fw-light"> Monitoring /</span> Node Hardware
  </h4>
  <div v-if="error_message.length">
    <div v-for="message in error_message" :key="message" class="alert alert-danger alert-dismissible" role="alert">
      <pre>{{ message }}</pre>
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
  </div>

  <div>
    <div class="row">
      <div class="col-md-1"><span class="nav_head">Global Settings: </span></div>

      <div class="col-md-1 d-flex align-items-center">
        <strong class="align-self-center">Enable</strong>
        <div class="form-check form-switch mb-2 ms-5 align-self-center">
          <input class="form-check-input" type="checkbox" checked data-toggle="switch" name="disabled" @change="setGlobalSettings($event)" v-model="nodeStatus" />
          <label class="form-check-label" :for="`rule_status_`">{{ nodeStatus ? 'ON' : 'OFF' }}</label>
        </div>
      </div>
      <div class="col-md-1"></div>
      <div class="col-md-1 d-flex align-items-center">
        <strong class="align-self-center">NHC</strong>
        <div class="form-check form-switch mb-2 ms-5 align-self-center">
          <input class="form-check-input" type="checkbox" checked data-toggle="switch" name="nhc" @change="setGlobalSettings($event)"  v-model="nodeNHC" />
          <label class="form-check-label" :for="`rule_nhc_`">{{ nodeNHC ? 'ON' : 'OFF' }}</label>
        </div>
      </div>
    </div>
    <br />
    <div class="row">
      <div class="col-md-1"><span class="nav_head">Filter:</span></div>
      <div class="col-md-1">
        <button type="button" class="btn btn-sm btn-primary" @click="selectAllNodes">Select All</button>
      </div>
      <div class="col-md-1">
        <button type="button" class="btn btn-sm btn-secondary" @click="selectFailedNodes">Select Failed</button>
      </div>
      <div class="col-md-1">
        <button type="button" class="btn btn-sm btn-dark" @click="revertSelection">Deselect All</button>
      </div>
      <div class="col-md-4">
        <div class="input-group input-group-sm">
          <span class="input-group-text"><i class="bx bx-search" style="font-size:24px; color:blue;"></i></span>
          <input type="text" class="form-control" placeholder="Filter By Name" v-model="searchTerm" />
        </div>
      </div>
    </div>
    <br />
    <div class="row">
      <div class="col-md-1"><span class="nav_head">Actions: </span></div>

      <div class="col-md-4 d-flex align-items-center">
        <strong class="align-self-center">Reset Selected Nodes</strong>
        <div class="form-check form-switch mb-2 ms-5 align-self-center">
          <button type="button" class="btn btn-sm btn-warning" @click="resetSelectedNodes"><strong>Reset Nodes</strong></button>
        </div>
      </div>
    </div>
    <br />

    <div class="row node_pan">
      <div v-for="(node, index) in filteredNodes" :key="index" class="col-md-1 node-box" :class="{ selected: selectedIndices.includes(index) }" @click="toggleSelect(index)">
        <div class="card text-white" :class="`bg-${node.class}`">
          <div class="card-body node-body"><p class="card-text">{{ node.hostname }}</p></div>
        </div>
      </div>
    </div>
  </div>
  <div v-if="showToast" :class="`bs-toast toast toast-placement-ex m-2 fade ${toastClass} top-0 end-0 show`" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="3000">
    <div class="toast-header">
      <i class="bx bx-bell me-2"></i>
      <div class="me-auto fw-medium">Configuration</div>
      <small>Just now</small>
      <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close" @click="showToast = false; processQueue()"></button>
    </div>
    <div class="toast-body">{{ toastMessage }}</div>
  </div>
  <br />

  <div class="row">
    <div v-if="nodes_rules.length > 0" class="table table-bordered table-striped table-hover table-responsive text-nowrap">
      <h3>Rules Configurations for {{ nodes_rules[nodes_rules.length - 1].hostname }}</h3>
      <table class="table table-bordered table-striped table-hover caption-top">
        <thead>
          <tr>
            <th>#</th>
            <th>Rule</th>
            <th>Severity</th>
            <th>For Time</th>
            <th>Expr</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="Rule in nodes_rules" :key="Rule.id">
            <td>{{ Rule.id }}</td>
            <td>{{ Rule.rule }}</td>
            <td>{{ Rule.severity }}</td>
            <td>{{ Rule.time }}</td>
            <td>{{ Rule.expr }}</td>
            <td>{{ Rule.description }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else-if="rule_message" class="alert alert-danger" role="alert">{{ rule_message }}</div>
  </div>
  <div class="row">
    <div v-if="inventory.length > 0" class="table table-bordered table-striped table-hover table-responsive text-nowrap">
      <h3>Hardware Inventory for {{ inventory[inventory.length - 1].hostname }}</h3>
      <table class="table table-bordered table-striped table-hover caption-top">
        <thead>
          <tr>
            <th>#</th>
            <th>Luna Group</th>
            <th>Hostname</th>
            <th>Class</th>
            <th>Vendor</th>
            <th>Description</th>
            <th>Size</th>
            <th>Clock</th>
            <th>Serial</th>
            <th>Product</th>
            <th>Handle</th>
            <th>Physid</th>
            <th>Version</th>
            <th>Slot</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="hwd in inventory" :key="hwd.id">
            <td>{{ hwd.id }}</td>
            <td>{{ hwd.luna_group }}</td>
            <td>{{ hwd.hostname }}</td>
            <td>{{ hwd.class }}</td>
            <td>{{ hwd.vendor }}</td>
            <td>{{ hwd.description }}</td>
            <td>{{ hwd.size }}</td>
            <td>{{ hwd.clock }}</td>
            <td>{{ hwd.serial }}</td>
            <td>{{ hwd.product }}</td>
            <td>{{ hwd.handle }}</td>
            <td>{{ hwd.physid }}</td>
            <td>{{ hwd.version }}</td>
            <td>{{ hwd.slot }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else-if="hardware_message" class="alert alert-danger" role="alert">{{ hardware_message }}</div>
</div>

</template> -->


<script lang="ts">
import { ref, watch, computed, onMounted, onBeforeUnmount } from "vue";
import axios from "axios";

interface ToastItem {
  message: string;
  toastClassName: string;
}

interface resetObject {
  hostname: string;
  message: string;
  status: boolean;
}

interface NodeRules {
  alert: string;
  annotations: { description: string };
  expr: string;
  for: string | null;
  labels: { severity: string };
}

interface RuleTable {
  id: number;
  rule: string;
  severity: string;
  time: string;
  expr: string;
  description: string;
  hostname: string;
}

interface Node {
  hostname: string;
  status: boolean;
  message: string;
  data?: { groups: { rules: NodeRules[] }[] };
  rules: NodeRules[];
  class: string;
}

interface NodeBatchItem {
  hostname: string;
  status: boolean;
  message?: string;
  data?: { groups: { rules: NodeRules[] }[] };
}

interface HardwareMetric {
  luna_group: string;
  hostname: string;
  class: string;
  vendor: string;
  description: string;
  size: string;
  clock: string;
  serial: string;
  product: string;
  handle: string;
  physid: string;
  version: string;
  slot: string;
}

interface InventoryItem {
  id: number;
  luna_group: string;
  hostname: string;
  class: string;
  vendor: string;
  description: string;
  size: string;
  clock: string;
  serial: string;
  product: string;
  handle: string;
  physid: string;
  version: string;
  slot: string;
}

interface Hardware {
  metric: HardwareMetric;
}

export default {
  props: {
    isActive: {
      type: Boolean,
      required: true,
      default: false,
    },
    url: {
      type: String,
      required: true,
    },
    promQLurl: {
      type: String,
      required: true,
    },
  },

  setup(props) {
    const nodeStatus = ref(true);
    const nodeNHC = ref(true);
    const nodes = ref<Node[]>([]);
    const nodes_rules = ref<RuleTable[]>([]);
    const inventory = ref<InventoryItem[]>([]);
    const rule_message = ref("");
    const hardware_message = ref("");
    const selectedHostnames = ref<string[]>([]);
    const activeHostname = ref("");
    const searchTerm = ref("");
    const currentFilter = ref("all");
    const toastQueue = ref<ToastItem[]>([]);
    const showToast = ref(false);
    const toastMessage = ref("");
    const error_message = ref<string[]>([]);
    const toastClass = ref("");
    const isFetchingNodes = ref(false);
    const nodeFetchProgress = ref("");

    let nodeEventSource: EventSource | null = null;

    const apiBaseUrl = computed(() => props.url.replace(/\/$/, ""));
    const promBaseUrl = computed(() => props.promQLurl.replace(/\/$/, ""));

    function Toast(message: string, toastClassName: string) {
      toastQueue.value.push({ message, toastClassName });
      processQueue();
    }

    function processQueue() {
      if (!showToast.value && toastQueue.value.length > 0) {
        const nextToast = toastQueue.value.shift();

        if (nextToast) {
          const { message, toastClassName } = nextToast;
          toastMessage.value = message;
          toastClass.value = toastClassName;
          showToast.value = true;

          setTimeout(() => {
            showToast.value = false;
            processQueue();
          }, 3000);
        }
      }
    }

    const parseSsePayload = (event: Event) => {
      return JSON.parse((event as MessageEvent).data);
    };

    const closeNodeStream = () => {
      if (nodeEventSource) {
        nodeEventSource.close();
        nodeEventSource = null;
      }

      isFetchingNodes.value = false;
    };

    const clearNodeDetails = () => {
      inventory.value = [];
      hardware_message.value = "";
      nodes_rules.value = [];
      rule_message.value = "";
    };

    const upsertNodes = (batch: NodeBatchItem[]) => {
      const updatedNodes = [...nodes.value];

      const indexByHostname = new Map(
        updatedNodes.map((node, index) => [node.hostname, index])
      );

      batch.forEach((item) => {
        const nodeItem: Node = {
          hostname: item.hostname,
          status: item.status,
          message: item.status ? "" : item.message || "",
          rules: [],
          class: item.status ? "primary" : "secondary",
        };

        const existingIndex = indexByHostname.get(item.hostname);

        if (existingIndex !== undefined) {
          updatedNodes[existingIndex] = {
            ...updatedNodes[existingIndex],
            ...nodeItem,
          };
        } else {
          updatedNodes.push(nodeItem);
        }
      });

      nodes.value = updatedNodes;
    };

    const fetchNodes = () => {
      closeNodeStream();

      nodes.value = [];
      selectedHostnames.value = [];
      activeHostname.value = "";
      clearNodeDetails();
      error_message.value = [];

      isFetchingNodes.value = true;
      nodeFetchProgress.value = "Loading nodes...";

      nodeEventSource = new EventSource(`${apiBaseUrl.value}/get_nodes/`);

      nodeEventSource.addEventListener("meta", (event: Event) => {
        const payload = parseSsePayload(event);
        nodeFetchProgress.value = `Loading nodes: 0/${payload.total}`;
      });

      nodeEventSource.addEventListener("batch", (event: Event) => {
        const payload = parseSsePayload(event);

        if (Array.isArray(payload.data)) {
          upsertNodes(payload.data);
        }

        nodeFetchProgress.value = `Loading nodes: ${payload.processed}/${payload.total}`;
      });

      nodeEventSource.addEventListener("batch_error", (event: Event) => {
        const payload = parseSsePayload(event);

        if (Array.isArray(payload.nodes)) {
          upsertNodes(
            payload.nodes.map((hostname: string) => ({
              hostname,
              status: false,
              message: "Failed to load node hardware status.",
            }))
          );
        }

        Toast(
          `Failed to load one node batch: ${payload.nodes?.join(", ") || "unknown batch"}`,
          "bg-secondary"
        );

        nodeFetchProgress.value = `Loading nodes: ${payload.processed}/${payload.total}`;
      });

      nodeEventSource.addEventListener("done", (event: Event) => {
        const payload = parseSsePayload(event);

        nodeFetchProgress.value = `Loaded ${payload.processed}/${payload.total} nodes`;
        closeNodeStream();
      });

      nodeEventSource.addEventListener("error", (event: Event) => {
        const messageEvent = event as MessageEvent;

        if (typeof messageEvent.data === "string") {
          try {
            const payload = JSON.parse(messageEvent.data);
            Toast(payload.message || "Node stream failed.", "bg-secondary");
          } catch {
            Toast("Node stream failed.", "bg-secondary");
          }
        } else {
          Toast("Node stream interrupted.", "bg-secondary");
        }

        closeNodeStream();
      });
    };

    const filteredNodes = computed(() => {
      let filtered = nodes.value;

      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase();

        filtered = filtered.filter((node) =>
          node.hostname.toLowerCase().includes(term)
        );
      }

      if (currentFilter.value === "secondary") {
        filtered = filtered.filter((node) => node.class === "secondary");
      }

      return filtered;
    });

    const showInventory = async (hostname: string) => {
      const requestedHostname = hostname;

      inventory.value = [];
      hardware_message.value = `Loading Hardware Inventory for ${hostname}...`;

      const query = `lshw_device{hostname=~"${hostname}", id=~"cpu|display|network|disk|bank:.*"}`;
      const prometheusURL = `${promBaseUrl.value}/api/v1/query?query=${encodeURIComponent(query)}`;
      const inventoryURL = `${apiBaseUrl.value}/proxy?url=${encodeURIComponent(prometheusURL)}`;

      try {
        const response = await axios.get(inventoryURL);

        if (activeHostname.value !== requestedHostname) {
          return;
        }

        if (response.status === 200) {
          const result = response.data?.data?.result || [];

          inventory.value = result.map((hwd: Hardware, index: number) => ({
            id: index + 1,
            luna_group: hwd.metric.luna_group || "N/A",
            hostname: hwd.metric.hostname || "N/A",
            class: hwd.metric.class || "N/A",
            vendor: hwd.metric.vendor || "N/A",
            description: hwd.metric.description || "N/A",
            size: hwd.metric.size || "N/A",
            clock: hwd.metric.clock || "N/A",
            serial: hwd.metric.serial || "N/A",
            product: hwd.metric.product || "N/A",
            handle: hwd.metric.handle || "N/A",
            physid: hwd.metric.physid || "N/A",
            version: hwd.metric.version || "N/A",
            slot: hwd.metric.slot || "N/A",
          }));

          hardware_message.value =
            inventory.value.length === 0
              ? `There is no Hardware Configuration available for ${hostname}.`
              : "";
        } else {
          hardware_message.value = `Error fetching Hardware: ${response.status}`;
        }
      } catch (error) {
        if (activeHostname.value !== requestedHostname) {
          return;
        }

        console.error("Error fetching Hardware Inventory:", error);
        hardware_message.value = `Failed to fetch Hardware Inventory for ${hostname}: ${error}`;
      }
    };

    const showRules = async (hostname: string) => {
      const requestedHostname = hostname;

      nodes_rules.value = [];
      rule_message.value = `Loading Rule Configuration for ${hostname}...`;

      try {
        const response = await axios.get(
          `${apiBaseUrl.value}/get_nodes/${encodeURIComponent(hostname)}`
        );

        if (activeHostname.value !== requestedHostname) {
          return;
        }

        if (response.status !== 200) {
          rule_message.value = `Error fetching Rule Configuration for ${hostname}: ${response.status}`;
          return;
        }

        const nodeResponse = Array.isArray(response.data)
          ? response.data[0]
          : response.data;

        const nodeRules: NodeRules[] =
          nodeResponse?.data?.groups?.[0]?.rules || [];

        nodes_rules.value = nodeRules.map((Rule, index): RuleTable => ({
          id: index + 1,
          rule: Rule.alert,
          severity: Rule.labels.severity,
          time: Rule.for ?? "",
          expr: Rule.expr,
          description: Rule.annotations.description,
          hostname,
        }));

        const nodeIndex = nodes.value.findIndex(
          (node) => node.hostname === hostname
        );

        if (nodeIndex !== -1) {
          nodes.value[nodeIndex] = {
            ...nodes.value[nodeIndex],
            rules: nodeRules,
          };
        }

        rule_message.value =
          nodes_rules.value.length === 0
            ? `There is no Rule Configuration available for ${hostname}.`
            : "";
      } catch (error) {
        if (activeHostname.value !== requestedHostname) {
          return;
        }

        console.error("Error fetching Rule Configuration:", error);
        rule_message.value = `Failed to fetch Rule Configuration for ${hostname}: ${error}`;
      }
    };

    const showNodeDetails = async (hostname: string) => {
      activeHostname.value = hostname;
      clearNodeDetails();

      await Promise.all([
        showInventory(hostname),
        showRules(hostname),
      ]);
    };

    const toggleSelect = (node: Node) => {
      const hostname = node.hostname;
      const currentIndex = selectedHostnames.value.indexOf(hostname);

      if (currentIndex === -1) {
        selectedHostnames.value.push(hostname);
        showNodeDetails(hostname);
        return;
      }

      selectedHostnames.value.splice(currentIndex, 1);

      if (selectedHostnames.value.length === 0) {
        activeHostname.value = "";
        clearNodeDetails();
        return;
      }

      const lastHostname =
        selectedHostnames.value[selectedHostnames.value.length - 1];

      showNodeDetails(lastHostname);
    };

    const selectAllNodes = () => {
      selectedHostnames.value = nodes.value.map((node) => node.hostname);
    };

    const revertSelection = () => {
      selectedHostnames.value = [];
      activeHostname.value = "";
      clearNodeDetails();
    };

    const selectFailedNodes = () => {
      selectedHostnames.value = nodes.value
        .filter((node) => node.class === "secondary")
        .map((node) => node.hostname);
    };

    const resetSelectedNodes = async () => {
      error_message.value = [];

      if (selectedHostnames.value.length === 0) {
        Toast("Please select at least one node.", "bg-warning");
        return;
      }

      const payload = selectedHostnames.value.map((hostname) => ({
        hostname,
        force: true,
      }));

      try {
        const response = await axios.post(`${apiBaseUrl.value}/save_nodes`, payload);

        if (response.status === 200) {
          response.data.response.forEach((result: resetObject) => {
            if (result.status === true) {
              Toast(
                `SUCCESS[RESET] :: Node ${result.hostname} is Reset.`,
                "bg-success"
              );
            } else {
              error_message.value.push(
                result.message.replace(/(.{200})/g, "$1\n")
              );
            }
          });
        }
      } catch (error) {
        Toast("Error saving selected nodes.", "bg-secondary");
        console.error("Error saving nodes:", error);
      }

      revertSelection();
      fetchNodes();
    };

    const fetchGlobalSettings = async () => {
      try {
        const response = await axios.get(`${apiBaseUrl.value}/get_global`);

        if (response.status === 200) {
          nodeStatus.value = response.data.hw.disabled === false;
          nodeNHC.value = response.data.hw.nhc === true;
        } else {
          Toast(`ERROR[Global Settings] :: ${response.status}`, "bg-secondary");
        }
      } catch (error) {
        Toast("Failed to fetch Global Settings.", "bg-secondary");
        console.error("Error fetching Global Settings:", error);
      }
    };

    const setGlobalSettings = async (event: Event) => {
      error_message.value = [];

      const target = event.target as HTMLInputElement;
      const checkboxName = target.name;

      let isChecked = target.checked;
      let name = "";
      let answer = false;
      let error_str = "";

      if (checkboxName === "disabled" && isChecked === true) {
        isChecked = false;
        name = "Enable";
        answer = true;
      } else if (checkboxName === "disabled" && isChecked === false) {
        isChecked = true;
        name = "Enable";
        answer = false;
      } else {
        name = "NHC";
        answer = isChecked;
      }

      const payload = { hw: { [checkboxName]: isChecked } };

      try {
        const response = await axios.post(
          `${apiBaseUrl.value}/set_global`,
          payload
        );

        if (response.status === 200) {
          error_str = response.data.response;

          if (response.data.response.length === 0) {
            Toast(
              `Global[${name}] is set to [${answer}] for All Nodes.`,
              "bg-success"
            );
          } else {
            response.data.response.forEach((result: resetObject) => {
              let message = "";
              let messageClass = "";

              if (result.status) {
                message = `Global[${name}] for ${result.hostname} is set to [${answer}].`;
                messageClass = "bg-success";
                Toast(message, messageClass);
              } else {
                message = `ERROR :: Global[${name}] for ${result.hostname} is ${result.message}.`;
                messageClass = "bg-secondary";
                error_message.value.push(message);
              }
            });
          }
        }
      } catch (error) {
        Toast(`ERROR :: ${error_str} ${error}`, "bg-secondary");
        console.error("Error saving Global Settings:", error);
      }
    };

    watch(
      () => props.isActive,
      async (newValue) => {
        if (newValue) {
          fetchNodes();
          fetchGlobalSettings();
        } else {
          closeNodeStream();
        }
      }
    );

    onMounted(() => {
      if (props.isActive) {
        fetchNodes();
        fetchGlobalSettings();
      }
    });

    onBeforeUnmount(() => {
      closeNodeStream();
    });

    return {
      nodes,
      selectedHostnames,
      searchTerm,
      toggleSelect,
      selectAllNodes,
      revertSelection,
      selectFailedNodes,
      resetSelectedNodes,
      filteredNodes,
      showToast,
      toastClass,
      toastMessage,
      processQueue,
      showRules,
      showInventory,
      nodeStatus,
      nodeNHC,
      inventory,
      hardware_message,
      nodes_rules,
      rule_message,
      fetchGlobalSettings,
      setGlobalSettings,
      error_message,
      isFetchingNodes,
      nodeFetchProgress,
    };
  },
};
</script>

<style lang="css">
.node-box {
  padding-bottom: 0.2rem;
  padding-right: 0.2rem;
}

.node-box:hover {
  cursor: pointer;
}

.node-body {
  padding-left: 0.5rem;
  padding-bottom: 0.2rem;
  padding-top: 0.2rem;
  padding-right: 0rem;
}

.selected {
  border: 2px solid rgb(17, 0, 255);
  background-color: #f8f9fa;
  color: black;
  padding: 0rem;
  border-radius: 12px;
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
}

.selected .card-text {
  font-weight: bold;
}

.nav_head {
  font-weight: bold;
}

.node_pan {
  background-color: antiquewhite;
  padding-top: 0.8rem;
  padding-bottom: 0.8rem;
}
</style>

<template>
  <h4 class="fw-bold py-3 mb-4">
    <span class="text-muted fw-light"> Monitoring /</span> Node Hardware
  </h4>

  <div v-if="error_message.length">
    <div
      v-for="message in error_message"
      :key="message"
      class="alert alert-danger alert-dismissible"
      role="alert"
    >
      <pre>{{ message }}</pre>
      <button
        type="button"
        class="btn-close"
        data-bs-dismiss="alert"
        aria-label="Close"
      ></button>
    </div>
  </div>

  <div>
    <div class="row">
      <div class="col-md-1">
        <span class="nav_head">Global Settings: </span>
      </div>

      <div class="col-md-1 d-flex align-items-center">
        <strong class="align-self-center">Enable</strong>
        <div class="form-check form-switch mb-2 ms-5 align-self-center">
          <input
            class="form-check-input"
            type="checkbox"
            checked
            data-toggle="switch"
            name="disabled"
            @change="setGlobalSettings($event)"
            v-model="nodeStatus"
          />
          <label class="form-check-label" :for="`rule_status_`">
            {{ nodeStatus ? "ON" : "OFF" }}
          </label>
        </div>
      </div>

      <div class="col-md-1"></div>

      <div class="col-md-1 d-flex align-items-center">
        <strong class="align-self-center">NHC</strong>
        <div class="form-check form-switch mb-2 ms-5 align-self-center">
          <input
            class="form-check-input"
            type="checkbox"
            checked
            data-toggle="switch"
            name="nhc"
            @change="setGlobalSettings($event)"
            v-model="nodeNHC"
          />
          <label class="form-check-label" :for="`rule_nhc_`">
            {{ nodeNHC ? "ON" : "OFF" }}
          </label>
        </div>
      </div>
    </div>

    <br />

    <div class="row">
      <div class="col-md-1">
        <span class="nav_head">Filter:</span>
      </div>

      <div class="col-md-1">
        <button
          type="button"
          class="btn btn-sm btn-primary"
          @click="selectAllNodes"
        >
          Select All
        </button>
      </div>

      <div class="col-md-1">
        <button
          type="button"
          class="btn btn-sm btn-secondary"
          @click="selectFailedNodes"
        >
          Select Failed
        </button>
      </div>

      <div class="col-md-1">
        <button
          type="button"
          class="btn btn-sm btn-dark"
          @click="revertSelection"
        >
          Deselect All
        </button>
      </div>

      <div class="col-md-4">
        <div class="input-group input-group-sm">
          <span class="input-group-text">
            <i class="bx bx-search" style="font-size: 24px; color: blue;"></i>
          </span>
          <input
            type="text"
            class="form-control"
            placeholder="Filter By Name"
            v-model="searchTerm"
          />
        </div>
      </div>
    </div>

    <br />

    <div class="row">
      <div class="col-md-1">
        <span class="nav_head">Actions: </span>
      </div>

      <div class="col-md-4 d-flex align-items-center">
        <strong class="align-self-center">Reset Selected Nodes</strong>
        <div class="form-check form-switch mb-2 ms-5 align-self-center">
          <button
            type="button"
            class="btn btn-sm btn-warning"
            @click="resetSelectedNodes"
          >
            <strong>Reset Nodes</strong>
          </button>
        </div>
      </div>
    </div>

    <br />

    <div v-if="isFetchingNodes" class="alert alert-info" role="alert">
      {{ nodeFetchProgress }}
    </div>

    <div class="row node_pan">
      <div
        v-for="node in filteredNodes"
        :key="node.hostname"
        class="col-md-1 node-box"
        :class="{ selected: selectedHostnames.includes(node.hostname) }"
        @click="toggleSelect(node)"
      >
        <div class="card text-white" :class="`bg-${node.class}`">
          <div class="card-body node-body">
            <p class="card-text">{{ node.hostname }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div
    v-if="showToast"
    :class="`bs-toast toast toast-placement-ex m-2 fade ${toastClass} top-0 end-0 show`"
    role="alert"
    aria-live="assertive"
    aria-atomic="true"
    data-bs-delay="3000"
  >
    <div class="toast-header">
      <i class="bx bx-bell me-2"></i>
      <div class="me-auto fw-medium">Configuration</div>
      <small>Just now</small>
      <button
        type="button"
        class="btn-close"
        data-bs-dismiss="toast"
        aria-label="Close"
        @click="
          showToast = false;
          processQueue();
        "
      ></button>
    </div>
    <div class="toast-body">{{ toastMessage }}</div>
  </div>

  <br />

  <div class="row">
    <div
      v-if="nodes_rules.length > 0"
      class="table table-bordered table-striped table-hover table-responsive text-nowrap"
    >
      <h3>Rules Configurations for {{ nodes_rules[nodes_rules.length - 1].hostname }}</h3>

      <table class="table table-bordered table-striped table-hover caption-top">
        <thead>
          <tr>
            <th>#</th>
            <th>Rule</th>
            <th>Severity</th>
            <th>For Time</th>
            <th>Expr</th>
            <th>Description</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="Rule in nodes_rules" :key="Rule.id">
            <td>{{ Rule.id }}</td>
            <td>{{ Rule.rule }}</td>
            <td>{{ Rule.severity }}</td>
            <td>{{ Rule.time }}</td>
            <td>{{ Rule.expr }}</td>
            <td>{{ Rule.description }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else-if="rule_message" class="alert alert-danger" role="alert">
      {{ rule_message }}
    </div>
  </div>

  <div class="row">
    <div
      v-if="inventory.length > 0"
      class="table table-bordered table-striped table-hover table-responsive text-nowrap"
    >
      <h3>Hardware Inventory for {{ inventory[inventory.length - 1].hostname }}</h3>

      <table class="table table-bordered table-striped table-hover caption-top">
        <thead>
          <tr>
            <th>#</th>
            <th>Luna Group</th>
            <th>Hostname</th>
            <th>Class</th>
            <th>Vendor</th>
            <th>Description</th>
            <th>Size</th>
            <th>Clock</th>
            <th>Serial</th>
            <th>Product</th>
            <th>Handle</th>
            <th>Physid</th>
            <th>Version</th>
            <th>Slot</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="hwd in inventory" :key="hwd.id">
            <td>{{ hwd.id }}</td>
            <td>{{ hwd.luna_group }}</td>
            <td>{{ hwd.hostname }}</td>
            <td>{{ hwd.class }}</td>
            <td>{{ hwd.vendor }}</td>
            <td>{{ hwd.description }}</td>
            <td>{{ hwd.size }}</td>
            <td>{{ hwd.clock }}</td>
            <td>{{ hwd.serial }}</td>
            <td>{{ hwd.product }}</td>
            <td>{{ hwd.handle }}</td>
            <td>{{ hwd.physid }}</td>
            <td>{{ hwd.version }}</td>
            <td>{{ hwd.slot }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else-if="hardware_message" class="alert alert-danger" role="alert">
      {{ hardware_message }}
    </div>
  </div>
</template>