<template>
  <div class="tx-app-layout">
    <AppHeader />
    <main class="tx-app-main">
      <NodeInventory ref="inventoryRef" />
    </main>
    <AppFooter />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import NodeInventory from './components/NodeInventory.vue'

const inventoryRef = ref(null)
</script>
