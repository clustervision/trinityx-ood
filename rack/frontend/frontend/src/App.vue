<script setup lang="ts">
// Import the RackView directly to force it to show
import RackView from './views/RackView.vue';
</script>

<template>
  <main class="app-container">
    <RackView />
  </main>
</template>

<style>
/* Global Reset to ensure visibility */
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  background-color: #f0f2f5; /* Light grey background to see white racks */
}

.app-container {
  padding: 20px;
  font-family: sans-serif;
}
</style>