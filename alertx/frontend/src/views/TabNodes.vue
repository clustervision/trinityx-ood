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

export default {
  setup() {

    const nodes = ref([
      { name: "Node001", class: "primary" },
      { name: "Node002", class: "danger" },
      { name: "Node003", class: "primary" },
      { name: "Node004", class: "danger" },
      { name: "Node005", class: "danger" },
      { name: "Node006", class: "primary" },
      { name: "Node007", class: "danger" },
      { name: "Node008", class: "primary" },
      { name: "Node009", class: "danger" },
      { name: "Node010", class: "danger" },
      { name: "Node011", class: "danger" },
      { name: "Node012", class: "primary" },
      { name: "Node013", class: "primary" },
      { name: "Node014", class: "danger" },
      { name: "Node015", class: "danger" },
      { name: "Node016", class: "primary" },
      { name: "Node017", class: "primary" },
      { name: "Node018", class: "danger" },
      { name: "Node019", class: "primary" },
      { name: "Node020", class: "danger" },
    ]);


    const currentFilter = ref("all");
    const searchTerm = ref("");
    const selectedIndices = ref<number[]>([]);

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

    const resetSelectedNodes = () => {
      const selectedNodes = selectedIndices.value.map(
        (index) => nodes.value[index]
      );
      console.log("Selected Nodes:", selectedNodes);

      // Logic to process or send the selected nodes
      // Example: send them to a server using an API
      /*
      axios.post('/reset-nodes', selectedNodes)
        .then(response => console.log('Nodes reset successfully'))
        .catch(error => console.error('Error resetting nodes:', error));
      */
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
            <p class="card-text">{{ node.name }}</p>
          </div>
        </div>
      </div>

    </div>

</template>

