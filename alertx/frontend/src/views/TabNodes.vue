<!-- <script setup lang="ts"></script> -->

<style>

.node-box{
  padding-bottom: 0.2rem;
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

<script lang="ts">

import { ref, computed } from "vue";
import axios from 'axios';


interface node {
  hostname: string;
  status: string;
  message: string;
  class: string;
};

const currentFilter = ref("all");
const searchTerm = ref("");
const selectedIndices = ref<number[]>([]);

export default {
  props: {
    url: {
      type: String,
      required: true,
    },
  },

  // data() {
  //   return {
  //     nodes: [] as nodeHW[],
  //     nodeList: [] as { hostname: string; status: string; message: string; class: string; }[],
  //   //   selectedIndices,
  //   // toggleSelect,
  //   // selectAllNodes,
  //   // searchTerm,
  //   // revertSelection,
  //   // selectFailedNodes,
  //   // filteredNodes,
  //   // resetSelectedNodes,
  //   };
  // },

  // async mounted() {
  //   try {
  //     const response = await axios.get(this.url +"/get_nodes");
  //     if (response.status === 200) {
  //       console.log(response.status);
  //       console.log(response.data);
  //       this.nodeList.forEach((node) => {
  //         this.nodes.push({hostname: node.hostname, status: node.status, message: node.message, class: node.status ? "primary" : "danger" });
  //       });
  //     } else {
  //       console.error("Error fetching rules:", response.status, response.data);
  //     }
  //   } catch (error) {
  //     console.error("Error fetching status:", error);
  //   }
  //   console.log(this.nodes);
  // },

  setup(props) {
    const nodes = ref<{ hostname: string; status: boolean; message: string; class: string }[]>([]);
    const nodeList = ref<{ hostname: string; status: boolean; message: string }[]>([]);

    const fetchNodes = async () => {
      try {
        const response = await axios.get(`${props.url}/get_nodes`);
        if (response.status === 200) {
          nodeList.value = response.data;
          nodes.value = nodeList.value.map((node) => ({
            hostname: node.hostname,
            status: node.status,
            message: node.message,
            class: node.status ? "primary" : "danger",
          }));
        } else {
          console.error("Error fetching nodes:", response.status, response.data);
        }
      } catch (error) {
        console.error("Error fetching status:", error);
      }
      // console.log(nodes.value);
    };

    // Fetch nodes when the component is mounted
    fetchNodes();
    const asd = fetchNodes();
    console.log(asd);
    // const emit = defineEmits(['toast']);




    function toggleSelect(index: number) {
      const currentIndex = selectedIndices.value.indexOf(index);
      if (currentIndex === -1) {
        selectedIndices.value.push(index);
      } else {
        selectedIndices.value.splice(currentIndex, 1);
      }
    }

    const selectAllNodes = () => {
      selectedIndices.value = nodes.value.map((_, index) => index);
    };

    const revertSelection = () => {
      selectedIndices.value = [];
    };

    const selectFailedNodes = () => {
      selectedIndices.value = nodes.value
        .map((node, index) => (node.class === "danger" ? index : -1))
        .filter((index) => index !== -1);
    };

    const filteredNodes = computed(() => {
      if (searchTerm.value){
        const term = searchTerm.value.toLowerCase();
        return nodes.value.filter((node) => node.name.toLowerCase().includes(term));
      }

      if (currentFilter.value === "all") {
        return nodes.value;
      }
      return nodes.value.filter((node) => node.class === currentFilter.value);
    });

    // function filterNodes(filter: string) {
    //   currentFilter.value = filter;
    // };

    const resetSelectedNodes = async () => {
      const selectedNodes = selectedIndices.value.map(
        (index) => nodes.value[index]
      );
      const payload:Array<object> = [];
      console.log("Selected Nodes:", selectedNodes);
      selectedNodes.forEach(node => {
        console.log(" Nodes:", node.name);
        payload.push({"hostname": node.name, "force": true })
      });
      console.log(" payload:", payload);

      // const response = await saveNode(payload);
      // if (response.status === 200){

      //   response.message.forEach((host: object) => {
      //     console.log(host.message);
      //     emit('toast', {message: host.message, toastClass: 'bg-danger'});
      //   });

      // }
      // console.log(response);
    };

    async function saveNode(payload: object) {
      try {
        const response = await axios.post(props.url +"/save_nodes", payload);
        return {"status": response.status, "message": response.data.response};
      } catch (error: unknown) {
        if (axios.isAxiosError(error)) {
          return {
            status: error.response?.status || 500,
            message: error.response?.data || 'An error occurred during the request.',
          };
        } else {
          return {
            status: 500,
            message: 'An unknown error occurred.',
          };
        }
      }
    };

  return {
    nodes,
    selectedIndices,
    toggleSelect,
    selectAllNodes,
    searchTerm,
    revertSelection,
    selectFailedNodes,
    filteredNodes,
    resetSelectedNodes,
  };
},
};

</script>

<template>
  <div class="row">
    <div class="col-md-1"><span class="nav_head">Filter: </span></div>
    <div class="col-md-1"><button type="button" class="btn btn-sm btn-dark" @click="revertSelection">DeSelection</button></div>
    <div class="col-md-1"><button type="button" class="btn btn-sm btn-primary" @click="selectAllNodes">Select All</button></div>
    <div class="col-md-1"><button type="button" class="btn btn-sm btn-danger" @click="selectFailedNodes">Select Failed</button></div>
    <div class="col-md-4">
      <div class="input-group input-group-sm">
          <span class="input-group-text"><box-icon name='search' color="blue" size="sm" ></box-icon></span>
          <input type="text" class="form-control" placeholder="Search By Name" v-model="searchTerm" />
        </div>
    </div>
    <div class="col-md-2"><button type="button" class="btn btn-sm btn-success" @click="resetSelectedNodes">Reset Selected Nodes</button><span style="color: red; font-weight: bold;"> ---- I AM A API</span></div>
  </div>

  <!-- <div class="row">
    <div class="col-md-1"><span class="nav_head">Show: </span></div>
    <div class="col-md-1"><button type="button" class="btn btn-sm btn-info" @click="filterNodes('all')">All</button></div>
    <div class="col-md-1"><button type="button" class="btn btn-sm btn-warning" @click="filterNodes('danger')">Failed</button></div>
  </div> -->

<br />

    <div class="row node_pan">
      <span style="color: red; font-weight: bold;"> FAKE DATA; Need a API to show Data</span>
      <div v-for="(node, index) in filteredNodes" :key="index" class="col-md-1 node-box" :class="{ selected: selectedIndices.includes(index) }" @click="toggleSelect(index)">
        <div class="card text-white" :class="`bg-${node.class}`">
          <div class="card-body node-body">
            <p class="card-text">{{ node.hostname }}</p>
          </div>
        </div>
      </div>

    </div>

</template>

