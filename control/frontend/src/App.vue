<template>
  <div class="tx-app-layout">
    <AppHeader />
    <main class="tx-app-main">
      <ControlInventory
        :rows="rows"
        :selected="selectedNodes"
        :toasts="toasts"
        :power-loading-nodes="powerLoadingNodes"
        :nodes-loading="nodesLoading"
        :message="message"
        :message-ok="messageOk"
        @toggle-select="(v) => (selectedNodes = v)"
        @bulk="runBulk"
        @single="runSingle"
        @dismiss-toast="dismissToast"
        @load-page="loadPageStatus"
      />
    </main>
    <AppFooter :app-url="appUrl" />
    <SelLogModal
      :open="selLogOpen"
      :loading="selLogLoading"
      :entries="selLogEntries"
      :node-count="selLogNodeCount"
      :loading-detail="selLogLoadingDetail"
      @close="closeSelLogModal"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import ControlInventory from './components/ControlInventory.vue'
import SelLogModal from './components/SelLogModal.vue'
import {
  fetchNodeList,
  fetchPageStatusSnapshot,
  mergeActionBodyIntoRows,
  mergeRowUpdates,
  pollActionForResult,
  pollActionInBackground,
  rowsFromNodeList,
  startBackgroundStatusPoll,
  triggerAction,
} from './api'
import { TOAST_TTL_MS, useToasts } from './composables/useToasts'
import { appUrlFromRuntime, resetPowerNotification } from './utils'
import {
  extractSelListResults,
  isSelListResponseReady,
  orderSelLogEntries,
} from './utils/selLogDisplay'
import type { ControlStatusRow, SelLogEntry, StatusToast } from './types'

const rows = ref<ControlStatusRow[]>([])
const selectedNodes = ref<string[]>([])
const message = ref('')
const messageOk = ref(true)
const powerLoadingNodes = ref<Record<string, boolean>>({})
const nodesLoading = ref(true)
const appUrl = computed(() => appUrlFromRuntime())
const { toasts, pushToast, dismissToast, clearToasts } = useToasts()

let stopStatusPoll: (() => void) | null = null
let stopActionPoll: (() => void) | null = null
let stopSelListPoll: AbortController | null = null
let messageTimer: ReturnType<typeof setTimeout> | null = null
let pageStatusRequest = 0
let selListRequest = 0

const selLogOpen = ref(false)
const selLogLoading = ref(false)
const selLogEntries = ref<SelLogEntry[]>([])
const selLogNodeCount = ref(0)
const selLogLoadingDetail = ref('')
const SEL_LIST_BATCH_SIZE = 10

function closeSelLogModal(): void {
  selLogOpen.value = false
  selLogLoading.value = false
  stopSelListPoll?.abort()
  stopSelListPoll = null
}

function scheduleMessageClear(): void {
  if (messageTimer) clearTimeout(messageTimer)
  messageTimer = setTimeout(() => {
    message.value = ''
    messageTimer = null
  }, TOAST_TTL_MS)
}

function setBanner(text: string, ok: boolean): void {
  messageOk.value = ok
  message.value = text
  if (text) scheduleMessageClear()
}

function setPowerLoading(nodes: string[]): void {
  const next = { ...powerLoadingNodes.value }
  for (const node of nodes) next[node] = true
  powerLoadingNodes.value = next
}

function syncPowerLoading(rows: ControlStatusRow[], newToasts: StatusToast[]): void {
  const next = { ...powerLoadingNodes.value }
  for (const row of rows) {
    if (row.power !== 'PENDING') delete next[row.node]
  }
  for (const toast of newToasts) {
    if (toast.node) delete next[toast.node]
  }
  powerLoadingNodes.value = next
}

function clearPowerLoading(): void {
  powerLoadingNodes.value = {}
}

/** One notice → top banner; multiple → toast stack only (no duplicate banner). */
function presentNotices(items: StatusToast[], ok = false): void {
  if (items.length === 0) return
  if (items.length === 1) {
    const only = items[0]
    if (!only) return
    setBanner(only.message, ok)
    return
  }
  if (messageTimer) clearTimeout(messageTimer)
  message.value = ''
  for (const toast of items) pushToast(toast)
}

function applyPageRowUpdate(updatedPageRows: ControlStatusRow[], newToasts: StatusToast[]) {
  rows.value = mergeRowUpdates(rows.value, updatedPageRows)
  syncPowerLoading(updatedPageRows, newToasts)
  presentNotices(newToasts)
}

function beginBackgroundPollForPage(
  hostlist: string[],
  pageRows: ControlStatusRow[],
  requestIds: { power: string; sel: string; chassis: string },
) {
  stopStatusPoll?.()
  setPowerLoading(hostlist)
  stopStatusPoll = startBackgroundStatusPoll(pageRows, requestIds, applyPageRowUpdate, {
    onPowerPollComplete: clearPowerLoading,
    hostlist,
  })
}

async function loadNodes() {
  nodesLoading.value = true
  try {
    const names = await fetchNodeList()
    rows.value = rowsFromNodeList(names)
  } finally {
    nodesLoading.value = false
  }
}

async function loadPageStatus(hostlist: string[]) {
  if (hostlist.length === 0) return
  const requestId = ++pageStatusRequest
  stopStatusPoll?.()
  setPowerLoading(hostlist)
  rows.value = mergeRowUpdates(rows.value, rowsFromNodeList(hostlist))

  try {
    const snapshot = await fetchPageStatusSnapshot(hostlist)
    if (requestId !== pageStatusRequest) return
    rows.value = mergeRowUpdates(rows.value, snapshot.rows)
    presentNotices(snapshot.toasts)
    syncPowerLoading(snapshot.rows, snapshot.toasts)
    const pageRows = rows.value.filter((r) => hostlist.includes(r.node))
    beginBackgroundPollForPage(hostlist, pageRows, snapshot.requestIds)
  } catch (e) {
    if (requestId !== pageStatusRequest) return
    clearPowerLoading()
    setBanner(e instanceof Error ? e.message : 'Failed to load page status.', false)
  }
}

async function runBulk(system: string, action: string) {
  if (selectedNodes.value.length === 0) {
    setBanner('Please select at least one node.', false)
    return
  }
  await runAction(system, action, selectedNodes.value)
}

async function runSingle(system: string, action: string, node: string) {
  await runAction(system, action, [node])
}

async function fetchSelListBatch(
  batch: string[],
  requestId: number,
): Promise<SelLogEntry[]> {
  const { requestId: actionRequestId, immediateToasts, body: immediateBody } = await triggerAction(
    'sel',
    'list',
    batch,
  )
  if (requestId !== selListRequest) return []

  if (immediateToasts.length > 0) {
    return batch.map((node) => {
      const toast = immediateToasts.find((t) => t.node === node) ?? immediateToasts[0]
      return {
        node,
        text: toast?.message ?? 'SEL list failed to start.',
        error: true,
      }
    })
  }

  let body = immediateBody
  if (actionRequestId && !isSelListResponseReady(immediateBody, batch)) {
    const polled = await pollActionForResult(actionRequestId, batch, 'sel', 'list', {
      signal: stopSelListPoll?.signal,
    })
    if (requestId !== selListRequest) return []
    body = polled.body
    if (polled.timedOut) {
      return extractSelListResults(body, batch).map((entry) =>
        entry.text.trim()
          ? entry
          : { ...entry, text: 'Timed out waiting for SEL log.', error: true },
      )
    }
  }

  const { rows: updatedRows } = mergeActionBodyIntoRows(rows.value, body, batch, 'sel', 'list')
  rows.value = mergeRowUpdates(rows.value, updatedRows)
  return extractSelListResults(body, batch)
}

async function runSelList(hostlist: string[]) {
  if (messageTimer) clearTimeout(messageTimer)
  message.value = ''
  clearToasts()
  stopSelListPoll?.abort()
  stopSelListPoll = new AbortController()

  const requestId = ++selListRequest
  selLogOpen.value = true
  selLogLoading.value = true
  selLogEntries.value = []
  selLogNodeCount.value = hostlist.length
  selLogLoadingDetail.value = `Fetching system event log (0/${hostlist.length})…`

  try {
    const merged: SelLogEntry[] = []
    const batches: string[][] = []
    for (let i = 0; i < hostlist.length; i += SEL_LIST_BATCH_SIZE) {
      batches.push(hostlist.slice(i, i + SEL_LIST_BATCH_SIZE))
    }

    for (let index = 0; index < batches.length; index += 1) {
      const batch = batches[index]
      if (!batch || batch.length === 0) continue
      if (requestId !== selListRequest) return

      const doneBefore = index * SEL_LIST_BATCH_SIZE
      selLogLoadingDetail.value = `Fetching system event log (${doneBefore}/${hostlist.length})…`
      const batchEntries = await fetchSelListBatch(batch, requestId)
      if (requestId !== selListRequest) return

      merged.push(...batchEntries)
      selLogEntries.value = orderSelLogEntries(merged, hostlist)
      selLogLoadingDetail.value = `Fetching system event log (${merged.length}/${hostlist.length})…`
    }

    selLogEntries.value = orderSelLogEntries(merged, hostlist)
    selLogNodeCount.value = hostlist.length
  } catch (e) {
    if (requestId !== selListRequest) return
    selLogEntries.value = [{
      node: hostlist.length === 1 ? (hostlist[0] ?? 'node') : `${hostlist.length} nodes`,
      nodes: hostlist.length > 1 ? hostlist : undefined,
      text: e instanceof Error ? e.message : 'Failed to load SEL log.',
      error: true,
    }]
  } finally {
    if (requestId === selListRequest) {
      selLogLoading.value = false
      selLogLoadingDetail.value = ''
    }
  }
}

async function runAction(system: string, action: string, hostlist: string[]) {
  if (system === 'sel' && action === 'list') {
    await runSelList(hostlist)
    return
  }
  if (messageTimer) clearTimeout(messageTimer)
  message.value = ''
  clearToasts()

  try {
    const { requestId, immediateToasts } = await triggerAction(system, action, hostlist)
    let hadFailures = immediateToasts.length > 0
    if (hadFailures) presentNotices(immediateToasts)

    if (!requestId) {
      if (!hadFailures) {
        setBanner(`${system}/${action} did not start for ${hostlist.join(', ')}.`, false)
      }
      return
    }

    if (system === 'power') setPowerLoading(hostlist)

    stopActionPoll?.()
    stopActionPoll = pollActionInBackground(
      requestId,
      rows.value,
      hostlist,
      (updated, newToasts) => {
        rows.value = mergeRowUpdates(rows.value, updated)
        syncPowerLoading(updated, newToasts)
        if (newToasts.length > 0) {
          hadFailures = true
          presentNotices(newToasts)
          return
        }
        if (hadFailures) return
        if (system === 'power' && action === 'reset') {
          const resetMsg = resetPowerNotification(updated, hostlist)
          if (resetMsg) {
            setBanner(resetMsg, true)
            return
          }
        }
        if (system === 'power' && (action === 'on' || action === 'off')) {
          const verb = action === 'on' ? 'powered on' : 'powered off'
          setBanner(`${hostlist.join(', ')} ${verb}.`, true)
          return
        }
        setBanner(`${system}/${action} completed for ${hostlist.join(', ')}.`, true)
      },
      system,
      action,
    )
  } catch (e) {
    setBanner(e instanceof Error ? e.message : 'Operation failed.', false)
  }
}

onMounted(async () => {
  try {
    await loadNodes()
  } catch (e) {
    setBanner(e instanceof Error ? e.message : 'Failed to load control nodes.', false)
  }
})

onBeforeUnmount(() => {
  if (messageTimer) clearTimeout(messageTimer)
  stopStatusPoll?.()
  stopActionPoll?.()
  stopSelListPoll?.abort()
})
</script>
