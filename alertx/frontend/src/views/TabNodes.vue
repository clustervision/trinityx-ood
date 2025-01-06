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
</style>

<script setup lang="ts">

import { ref } from "vue";
const nodes = ref([
  { name: "Node001", class: "primary" },
  { name: "Node002", class: "danger" },
  { name: "Node003", class: "secondary" },
  { name: "Node004", class: "dark" },
  { name: "Node005", class: "danger" },
  { name: "Node006", class: "primary" },
  { name: "Node007", class: "dark" },
  { name: "Node008", class: "secondary" },
  { name: "Node009", class: "warning" },
  { name: "Node010", class: "danger" },
  { name: "Node011", class: "danger" },
  { name: "Node012", class: "info" },
  { name: "Node013", class: "secondary" },
  { name: "Node014", class: "warning" },
  { name: "Node015", class: "danger" },
  { name: "Node016", class: "info" },
  { name: "Node017", class: "secondary" },
  { name: "Node018", class: "warning" },
  { name: "Node019", class: "primary" },
  { name: "Node020", class: "secondary" },
]);

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
          <input type="text" class="form-control" placeholder="Search By Name" />
        </div>
    </div>
    <div class="col-md-2"><button type="button" class="btn btn-sm btn-secondary">Reset Selected Nodes</button></div>
  </div>

  <div class="row">
    <div class="col-md-1"><span class="nav_head">Show: </span></div>
    <div class="col-md-1"><button type="button" class="btn btn-sm btn-info" @click="selectAllNodes">All</button></div>
    <div class="col-md-1"><button type="button" class="btn btn-sm btn-warning" @click="selectFailedNodes">Failed</button></div>
  </div>

<br />

    <div class="row">

      <div v-for="(node, index) in nodes" :key="index" class="col-md-1 node-box" :class="{ selected: selectedIndices.includes(index) }" @click="toggleSelect(index)">
        <div class="card text-white" :class="`bg-${node.class}`">
          <div class="card-body node-body">
            <p class="card-text">{{ node.name }}</p>
          </div>
        </div>
      </div>

    </div>

</template>

