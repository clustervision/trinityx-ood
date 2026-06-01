<template>
  <div class="tx-app">
    <AppHeader />
    <main class="tx-main">
      <div v-if="message" :class="messageOk ? 'alert-success' : 'alert-danger'">{{ message }}</div>
      <ControlInventory
        :rows="rows"
        :selected="selectedNodes"
        @toggle-select="(v) => (selectedNodes = v)"
        @bulk="runBulk"
        @single="runSingle"
      />
    </main>
    <AppFooter />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import ControlInventory from './components/ControlInventory.vue'
import { fetchControlStatus, pollRequestDone, triggerAction } from './api'
import type { ControlStatusRow } from './types'

const rows = ref<ControlStatusRow[]>([])
const selectedNodes = ref<string[]>([])
const message = ref('')
const messageOk = ref(true)

async function refresh() {
  const status = await fetchControlStatus()
  rows.value = status.rows
}

async function runBulk(system: string, action: string) {
  if (selectedNodes.value.length === 0) {
    messageOk.value = false
    message.value = 'Please select at least one node.'
    return
  }
  await runAction(system, action, selectedNodes.value)
}

async function runSingle(system: string, action: string, node: string) {
  await runAction(system, action, [node])
}

async function runAction(system: string, action: string, hostlist: string[]) {
  message.value = ''
  try {
    const requestId = await triggerAction(system, action, hostlist)
    if (requestId) await pollRequestDone(requestId)
    await refresh()
    messageOk.value = true
    message.value = `${system}/${action} completed for ${hostlist.join(', ')}`
  } catch (e) {
    messageOk.value = false
    message.value = e instanceof Error ? e.message : 'Operation failed.'
  }
}

onMounted(async () => {
  try {
    await refresh()
  } catch (e) {
    messageOk.value = false
    message.value = e instanceof Error ? e.message : 'Failed to load control nodes.'
  }
})
</script>
