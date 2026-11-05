<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import HeaderBar from './components/HeaderBar.vue'
import BootOverview from './components/BootOverview.vue'
import BootProgress from './components/BootProgress.vue'
import NodesModal from './components/NodesModal.vue'
import ConsoleModal from './components/ConsoleModal.vue'
import NotBooted from './components/NotBooted.vue'
import NotBootedModal from './components/NotBootedModal.vue'
import { images, progress, apiError, startPolling, stopPolling } from './composables/useStatus.js'

const consoleNode = ref(null)
const selectedRow = ref(null)
const nodesModal = ref(null)
const nodesModalReturn = ref(null)
const notBootedModal = ref(null)
const notBootedReturn = ref(null)

function openConsoleFromModal(node) {
  nodesModalReturn.value = nodesModal.value
  nodesModal.value = null
  consoleNode.value = node
}

function openConsoleFromNotBooted(node) {
  notBootedReturn.value = notBootedModal.value
  notBootedModal.value = null
  consoleNode.value = node
}

function closeConsole() {
  consoleNode.value = null
  if (nodesModalReturn.value) {
    nodesModal.value = nodesModalReturn.value
    nodesModalReturn.value = null
  }
  if (notBootedReturn.value) {
    notBootedModal.value = notBootedReturn.value
    notBootedReturn.value = null
  }
}

function openNodesModal(image, group) {
  nodesModal.value = { imgName: image.name, group }
}

function isPaused() {
  return consoleNode.value !== null || nodesModal.value !== null || notBootedModal.value !== null
}

function onKeydown(event) {
  if (event.key === 'Escape') {
    consoleNode.value = null
    nodesModal.value = null
    nodesModalReturn.value = null
    notBootedModal.value = null
    notBootedReturn.value = null
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
        <BootOverview
          :images="images"
          :selected="selectedRow"
          @select="selectedRow = $event"
          @show-nodes="openNodesModal"
        />
        <BootProgress :images="images" :progress="progress" :selected="selectedRow" @select="selectedRow = $event" />
        <NotBooted
          :images="images"
          :progress="progress"
          :selected="selectedRow"
          @open-console="consoleNode = $event"
          @view-all="notBootedModal = { rows: $event }"
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

  <NotBootedModal
    v-if="notBootedModal"
    :rows="notBootedModal.rows"
    @close="notBootedModal = null"
    @open-console="openConsoleFromNotBooted"
  />

  <ConsoleModal
    v-if="consoleNode"
    :node-name="consoleNode"
    @close="closeConsole"
  />
</template>
