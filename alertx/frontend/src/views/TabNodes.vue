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
  <div>
    <div class="row">
      <div class="col-md-1"><span class="nav_head">Global Settings: </span></div>

      <div class="col-md-1 d-flex align-items-center">
        <strong class="align-self-center">Enable</strong>
        <div class="form-check form-switch mb-2 ms-5 align-self-center">
          <input class="form-check-input" type="checkbox" checked data-toggle="switch" @change="triggerStatus()" v-model="nodeStatus" />
          <label class="form-check-label" :for="`rule_status_`">{{ nodeStatus ? 'ON' : 'OFF' }}</label>
        </div>
      </div>
      <div class="col-md-1"></div>
      <div class="col-md-1 d-flex align-items-center">
        <strong class="align-self-center">NHC</strong>
        <div class="form-check form-switch mb-2 ms-5 align-self-center">
          <input class="form-check-input" type="checkbox" checked data-toggle="switch" @change="triggerNHC()"  v-model="nodeNHC" />
          <label class="form-check-label" :for="`rule_nhc_`">{{ nodeNHC ? 'ON' : 'OFF' }}</label>
        </div>
      </div>

      <!-- <div class="col-md-1"><button type="button" class="btn btn-sm btn-info" @click="filterNodes('all')">All</button></div>
      <div class="col-md-1"><button type="button" class="btn btn-sm btn-warning" @click="filterNodes('secondary')">Failed</button></div> -->
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
          <span class="input-group-text"><box-icon name="search" color="blue" size="sm"></box-icon></span>
          <input type="text" class="form-control" placeholder="Search By Name" v-model="searchTerm" />
        </div>
      </div>
      <div class="col-md-2">
        <button type="button" class="btn btn-sm btn-success" @click="resetSelectedNodes">Reset Selected Nodes</button>
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
    <div class="col-md-6">
      <div class="table table-bordered table-striped table-hover table-responsive text-nowrap">
        <table class="table table-bordered table-striped table-hover caption-top">
          <thead>
            <tr>
              <th>#</th>
              <th>Rule</th>
              <th>State</th>
              <th>Severity</th>
              <th>NHC</th>
              <th>Event Time</th>
              <th>Affected</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>1</td>
              <td>asd</td>
              <td>sdcsdc</td>
              <td>dscsd</td>
              <td>sdcsdc</td>
              <td>sdcsdc</td>
              <td>sdc</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="col-md-6">
      <div v-if="inventory.length > 0" class="table table-bordered table-striped table-hover table-responsive text-nowrap">
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
  </div>



</template>

<script lang="ts">
import { ref, computed, onMounted } from "vue";
import axios from "axios";

interface ToastItem {
  message: string;
  toastClassName: string;
}

interface resetObject {
  message: string;
  status: string;
}

interface Node {
  hostname: string;
  status: boolean;
  message: string;
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
    const inventory = ref<InventoryItem[]>([]);
    const hardware_message = ref("");
    const selectedIndices = ref<number[]>([]);
    const searchTerm = ref("");
    const currentFilter = ref("all");

    const toastQueue = ref<ToastItem[]>([]);
    const showToast = ref(false);
    const toastMessage = ref("");
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
            message: node.message,
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
      } else {
        selectedIndices.value.splice(currentIndex, 1);
        if (selectedIndices.value.length === 0){
          inventory.value = [];
          hardware_message.value = ``;
        } else {
          showInventory(selectedIndices.value[selectedIndices.value.length - 1]);
        }
      }

      // Need a logic here inventory.value = [];
    };

    const selectAllNodes = () => {
      selectedIndices.value = nodes.value.map((_, index) => index);
    };

    const revertSelection = () => {
      selectedIndices.value = [];
    };

    const selectFailedNodes = () => {
      selectedIndices.value = nodes.value
        .map((node, index) => (node.class === "secondary" ? index : -1))
        .filter((index) => index !== -1);
    };

    const resetSelectedNodes = async () => {
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
            Toast(result.message, result.status ? "bg-success" : "bg-secondary");
          });
        }
      } catch (error) {
        Toast("Error saving selected nodes.", "bg-secondary");
        console.error("Error saving nodes:", error);
      }
      revertSelection();
    };

    const triggerNHC = async () => {
      const payload = nodes.value.map((node) => ({
        hostname: node.hostname,
        force: false,
        nhc: nodeNHC.value,
      }));
      try {
        const response = await axios.post(`${props.url}/save_nodes`, payload);
        if (response.status === 200) {
          response.data.response.forEach((result: resetObject) => {
            Toast(result.message, result.status ? "bg-success" : "bg-secondary");
          });
        }
      } catch (error) {
        Toast("Error saving selected nodes.", "bg-secondary");
        console.error("Error saving nodes:", error);
      }
    };

    const triggerStatus = async () => {
      let status = false;
      if (nodeStatus.value === true){
        status = false;
      } else {
        status = true;
      }
      const payload = nodes.value.map((node) => ({
        hostname: node.hostname,
        force: false,
        disabled: status,
      }));
      console.log(payload);
      try {
        const response = await axios.post(`${props.url}/save_nodes`, payload);
        if (response.status === 200) {
          console.log(response.data.response);
          response.data.response.forEach((result: resetObject) => {
            Toast(result.message, result.status ? "bg-success" : "bg-secondary");
          });
        }
      } catch (error) {
        Toast("Error saving selected nodes.", "bg-secondary");
        console.error("Error saving nodes:", error);
      }
    };

    const showInventory = async (index: number) =>  {
      const hostname = nodes.value[index].hostname;
      // const inventoryURL = `${props.promQLurl}/api/v1/query?query=lshw_device%7Bhostname%3D%7E%22${hostname}%22%2C+id%3D%7E%22cpu%7Cdisplay%7Cnetwork%7Cdisk%7Cbank%3A.*%22%7D`;
      const inventoryURL = `https://demo-controller1.cluster:9090/api/v1/query?query=lshw_device%7Bhostname%3D%7E%22${hostname}%22%2C+id%3D%7E%22cpu%7Cdisplay%7Cnetwork%7Cdisk%7Cbank%3A.*%22%7D`;
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
          Toast(`Error fetching nodes: ${response.status}`, "bg-secondary");
          hardware_message.value = `Error fetching nodes: ${response.status}`;
        }
      } catch (error) {
        Toast("Failed to fetch nodes.", "bg-secondary");
        console.error("Error fetching nodes:", error);
        hardware_message.value = `Error fetching nodes: ${error}`;
      }
    };

    const showRules = async (index: number) =>  {
      const hostname = nodes.value[index].hostname;
      // const inventoryURL = `${props.promQLurl}/api/v1/query?query=lshw_device%7Bhostname%3D%7E%22${hostname}%22%2C+id%3D%7E%22cpu%7Cdisplay%7Cnetwork%7Cdisk%7Cbank%3A.*%22%7D`;
      const inventoryURL = `https://demo-controller1.cluster:9090/api/v1/query?query=lshw_device%7Bhostname%3D%7E%22${hostname}%22%2C+id%3D%7E%22cpu%7Cdisplay%7Cnetwork%7Cdisk%7Cbank%3A.*%22%7D`;
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
          Toast(`Error fetching nodes: ${response.status}`, "bg-secondary");
          hardware_message.value = `Error fetching nodes: ${response.status}`;
        }
      } catch (error) {
        Toast("Failed to fetch nodes.", "bg-secondary");
        console.error("Error fetching nodes:", error);
        hardware_message.value = `Error fetching nodes: ${error}`;
      }
    };

    // Lifecycle hook
    onMounted(() => {
      fetchNodes();
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
      triggerNHC,
      triggerStatus,
      inventory,
      hardware_message,
    };
  },
};
</script>
