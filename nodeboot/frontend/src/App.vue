<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import HeaderBar from './components/HeaderBar.vue'
import ImagesTable from './components/ImagesTable.vue'
import NodesModal from './components/NodesModal.vue'
import ConsoleModal from './components/ConsoleModal.vue'
import { images, apiError, startPolling, stopPolling } from './composables/useStatus.js'

const consoleNode = ref(null)
const nodesModal = ref(null)
const nodesModalReturn = ref(null)

function openConsole(node) {
  nodesModalReturn.value = nodesModal.value
  nodesModal.value = null
  consoleNode.value = node
}

function openConsoleFromModal(node) {
  nodesModalReturn.value = nodesModal.value
  nodesModal.value = null
  consoleNode.value = node
}

function closeConsole() {
  consoleNode.value = null
  if (nodesModalReturn.value) {
    nodesModal.value = nodesModalReturn.value
    nodesModalReturn.value = null
  }
}

function openNodesModal(image, group) {
  nodesModal.value = { imgName: image.name, group }
}

function isPaused() {
  return consoleNode.value !== null || nodesModal.value !== null
}

function onKeydown(event) {
  if (event.key === 'Escape') {
    consoleNode.value = null
    nodesModal.value = null
    nodesModalReturn.value = null
  }
}

onMounted(() => {
  startPolling(isPaused)
  window.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  stopPolling()
  window.removeEventListener('keydown', onKeydown)
})
</script>

<template>
  <div class="tx-app-layout">
    <AppHeader />
    <main class="tx-app-main">
      <div class="app-shell">
        <HeaderBar :images="images" />
        <div v-if="apiError" class="alert alert-danger" role="alert">
          <strong>API error ::</strong> {{ apiError }}
        </div>
        <ImagesTable
          :images="images"
          @open-console="openConsole"
          @see-all="openNodesModal"
        />
      </div>
    </main>
    <AppFooter />
  </div>

  <NodesModal
    v-if="nodesModal"
    :img-name="nodesModal.imgName"
    :group="nodesModal.group"
    @close="nodesModal = null"
    @open-console="openConsoleFromModal"
  />

  <ConsoleModal
    v-if="consoleNode"
    :node-name="consoleNode"
    @close="closeConsole"
  />
</template>
