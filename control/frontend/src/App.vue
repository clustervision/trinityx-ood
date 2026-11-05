<!--
  This code is part of the TrinityX software suite
  Copyright (C) 2026  ClusterVision Solutions b.v.

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <https://www.gnu.org/licenses/>

  @author      Yixin Zhang
  @copyright   Copyright 2026, Luna2 Project[OOD]
  @license     GPL
  @version     2.0
  @maintainer  Yixin Zhang
  @email       yixin.zhang@clustervision.com
  @status      Development
-->

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
        @hold-toast="holdToast"
        @release-toast="releaseToast"
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
import { appUrlFromRuntime, filterSelHostlist, resetPowerNotification } from './utils'
import {
  extractSelListResults,
  isSelListResponseReady,
  orderSelLogEntries,
} from './utils/selLogDisplay'
import type { ControlStatusRow, SelLogEntry, StatusField, StatusToast } from './types'

const rows = ref<ControlStatusRow[]>([])
const selectedNodes = ref<string[]>([])
const message = ref('')
const messageOk = ref(true)
const powerLoadingNodes = ref<Record<string, boolean>>({})
const nodesLoading = ref(true)
const appUrl = computed(() => appUrlFromRuntime())
const { toasts, pushToast, dismissToast, clearToasts, holdToast, releaseToast } = useToasts()

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

/** One notice → top banner; multiple → one expandable toast (no stack spam). */
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

  const fieldCounts = new Map<string, number>()
  for (const item of items) {
    fieldCounts.set(item.field, (fieldCounts.get(item.field) ?? 0) + 1)
  }
  const fieldLabel = [...fieldCounts.keys()].sort().join('/')
  const summary = `${items.length} errors${fieldLabel ? ` · ${fieldLabel}` : ''}`
  pushToast({
    id: `batch:${fieldLabel || 'mixed'}`,
    node: '',
    field: (items[0]?.field ?? 'power') as StatusField,
    message: summary,
    details: items.map((t) => t.message),
  })
}

function setupbmcByNodeMap(): Record<string, boolean | undefined> {
  const map: Record<string, boolean | undefined> = {}
  for (const row of rows.value) map[row.node] = row.setupbmc
  return map
}

function resolveActionHostlist(system: string, hostlist: string[]): string[] | null {
  if (system !== 'sel') return hostlist
  const { enabled, skipped } = filterSelHostlist(hostlist, setupbmcByNodeMap())
  if (enabled.length === 0) {
    setBanner(
      skipped.length === 1
        ? `${skipped[0]} has setupbmc=false; SEL is unavailable.`
        : `SEL is unavailable because setupbmc is false for the selected node(s).`,
      false,
    )
    return null
  }
  if (skipped.length > 0) {
    setBanner(
      `Skipping SEL for ${skipped.length} node(s) with setupbmc=false: ${skipped.join(', ')}.`,
      true,
    )
  }
  return enabled
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
    const nodes = await fetchNodeList()
    rows.value = rowsFromNodeList(nodes)
  } finally {
    nodesLoading.value = false
  }
}

async function loadPageStatus(hostlist: string[]) {
  if (hostlist.length === 0) return
  const requestId = ++pageStatusRequest
  stopStatusPoll?.()
  setPowerLoading(hostlist)
  const setupbmcMap = setupbmcByNodeMap()
  rows.value = mergeRowUpdates(
    rows.value,
    rowsFromNodeList(hostlist, setupbmcMap as Record<string, boolean>),
  )

  try {
    const snapshot = await fetchPageStatusSnapshot(hostlist)
    if (requestId !== pageStatusRequest) return
    rows.value = mergeRowUpdates(rows.value, snapshot.rows)
    presentNotices(snapshot.toasts)
    syncPowerLoading(snapshot.rows, snapshot.toasts)
    const rowByNode = new Map(rows.value.map((r) => [r.node.toLowerCase(), r]))
    const pageRows = hostlist.map((node) => {
      const row = rowByNode.get(node.toLowerCase())
      if (row) return row
      const created = rowsFromNodeList([node], setupbmcMap as Record<string, boolean>)
      return created[0]!
    })
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
  const hostlist = resolveActionHostlist(system, selectedNodes.value)
  if (!hostlist) return
  await runAction(system, action, hostlist)
}

async function runSingle(system: string, action: string, node: string) {
  const hostlist = resolveActionHostlist(system, [node])
  if (!hostlist) return
  await runAction(system, action, hostlist)
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

        // Ignore intermediate PENDING updates from pollActionInBackground startup.
        const field = (['power', 'sel', 'chassis', 'redfish'] as const).find((f) => f === system)
        if (field) {
          const stillPending = hostlist.some((node) => {
            const row = updated.find((r) => r.node.toLowerCase() === node.toLowerCase())
            return !row || row[field] === 'PENDING'
          })
          if (stillPending) return
        }

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
