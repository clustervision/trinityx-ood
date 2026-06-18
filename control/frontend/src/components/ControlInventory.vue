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
  <div class="tx-shell tx-inventory-page">
    <div v-if="message" :class="messageOk ? 'alert-success' : 'alert-danger'" role="alert">{{ message }}</div>

    <div class="tx-header">
      <h2 class="tx-title">Available Nodes</h2>
      <div class="tx-header-actions">
        <button type="button" class="tx-btn tx-btn-help" title="Help" @click="helpOpen = true">?</button>
        <div class="tx-inline-search">
          <label class="tx-inline-search-label" for="txControlSearch">Search:</label>
          <input
            id="txControlSearch"
            v-model="searchQuery"
            type="search"
            class="tx-inline-search-input"
            autocomplete="off"
          />
        </div>
      </div>
    </div>

    <div class="tx-control-layout">
      <aside class="tx-control-sidebar" aria-label="Bulk actions">
        <label class="tx-control-sidebar-head">
          <input
            type="checkbox"
            :checked="allPageSelected"
            :title="`Select all ${pagedRows.length} nodes on this page`"
            @change="togglePageSelection"
          />
          <span class="tx-control-sidebar-head-text">
            <span>ACTIONS FOR SELECTED NODES</span>
            <span class="tx-control-selected-count">{{ selectedCountLabel }}</span>
          </span>
        </label>

        <section class="tx-control-section">
          <h3 class="tx-control-section-title">POWER</h3>
          <div class="tx-control-section-actions">
            <div class="tx-control-power-row">
              <PowerStatusDot
                :power="sidebarPowerDisplay"
                :loading="sidebarPowerLoading"
                :disabled="props.selected.length === 0"
                size="sidebar"
                label="selected nodes"
                @click="onSidebarPowerToggle"
              />
              <button type="button" class="tx-btn tx-btn-orange tx-btn-sidebar" @click="emitBulk('power', 'reset')">
                RESET
              </button>
            </div>
          </div>
        </section>

        <section class="tx-control-section">
          <h3 class="tx-control-section-title">SEL</h3>
          <div class="tx-control-section-actions tx-control-section-actions--row">
            <button type="button" class="tx-btn tx-btn-outline-blue tx-btn-sidebar" @click="emitBulk('sel', 'clear')">
              CLEAR
            </button>
            <button type="button" class="tx-btn tx-btn-outline-blue tx-btn-sidebar" @click="emitBulk('sel', 'list')">
              LIST
            </button>
          </div>
        </section>

        <section class="tx-control-section">
          <h3 class="tx-control-section-title">CHASSIS</h3>
          <div class="tx-control-section-actions tx-control-section-actions--row">
            <button type="button" class="tx-btn tx-btn-outline-blue tx-btn-sidebar" @click="emitBulk('chassis', 'identify')">
              IDENTIFY
            </button>
            <button type="button" class="tx-btn tx-btn-outline-blue tx-btn-sidebar" @click="emitBulk('chassis', 'noidentify')">
              NO IDENTIFY
            </button>
          </div>
        </section>

        <section class="tx-control-section">
          <h3 class="tx-control-section-title">REDFISH</h3>
          <div class="tx-control-section-actions tx-control-section-actions--row">
            <button type="button" class="tx-btn tx-btn-outline-blue tx-btn-sidebar tx-btn-inactive" disabled>
              SETTINGS
            </button>
            <button type="button" class="tx-btn tx-btn-outline-blue tx-btn-sidebar tx-btn-inactive" disabled>
              UPLOAD
            </button>
          </div>
        </section>
      </aside>

      <div class="tx-control-table-area">
        <aside v-if="toasts.length" class="tx-toast-stack" aria-live="polite" aria-label="Luna status messages">
          <div v-for="toast in toasts" :key="toast.id" class="tx-toast" role="status">
            <span class="tx-toast-text">{{ toast.message }}</span>
            <button type="button" class="tx-toast-close" aria-label="Dismiss" @click="emit('dismissToast', toast.id)">
              &times;
            </button>
          </div>
        </aside>

        <div
          class="tx-inventory-table-wrap"
          :class="{ 'tx-inventory-table-wrap--loading': nodesLoading && rows.length === 0 }"
        >
          <div v-if="nodesLoading && rows.length === 0" class="tx-table-loading-overlay" aria-live="polite">
            <span class="tx-table-loading-spinner" aria-hidden="true" />
            <span class="tx-table-loading-text">Loading nodes…</span>
          </div>
          <table class="tx-inventory-table">
            <thead>
              <tr>
                <th class="tx-th-regular tx-col-check" />
                <th class="tx-th-regular tx-col-name">NAME</th>
                <th class="tx-th-regular">POWER ACTIONS</th>
                <th class="tx-th-regular">SEL ACTIONS</th>
                <th class="tx-th-regular">CHASSIS ACTIONS</th>
                <th class="tx-th-regular">REDFISH ACTIONS</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!nodesLoading && filteredRows.length === 0">
                <td colspan="6" class="tx-empty-cell">
                  {{ rows.length === 0 ? 'No nodes available.' : 'No nodes match your search.' }}
                </td>
              </tr>
              <tr v-for="row in pagedRows" :key="row.node">
                <td class="tx-col-check">
                  <input type="checkbox" :checked="selectedSet.has(row.node)" @change="toggleOne(row.node)" />
                </td>
                <td class="tx-td-name tx-col-name">
                  <span class="tx-name-link"><span class="tx-cell-ellipsis">{{ row.node }}</span></span>
                </td>
                <td class="tx-td-actions">
                  <div class="tx-control-cell-actions tx-control-cell-actions--row">
                    <PowerStatusDot
                      :power="row.power"
                      :loading="isPowerRowLoading(row.node)"
                      :label="row.node"
                      @click="onRowPowerToggle(row)"
                    />
                    <template v-if="isPowerRowLoading(row.node)">
                      <span class="tx-power-loading-spinner" aria-hidden="true" />
                      <span class="tx-status-text tx-status-loading-text" aria-live="polite">Loading…</span>
                    </template>
                    <button type="button" class="tx-btn tx-btn-orange tx-btn-cell" @click="emitSingle('power', 'reset', row.node)">
                      RESET
                    </button>
                  </div>
                </td>
                <td class="tx-td-actions">
                  <div class="tx-control-cell-actions">
                    <button type="button" class="tx-btn tx-btn-outline-blue tx-btn-cell" @click="emitSingle('sel', 'clear', row.node)">
                      CLEAR
                    </button>
                    <button type="button" class="tx-btn tx-btn-outline-blue tx-btn-cell" @click="emitSingle('sel', 'list', row.node)">
                      LIST
                    </button>
                  </div>
                </td>
                <td class="tx-td-actions">
                  <div class="tx-control-cell-actions">
                    <button type="button" class="tx-btn tx-btn-outline-blue tx-btn-cell" @click="emitSingle('chassis', 'identify', row.node)">
                      IDENTIFY
                    </button>
                    <button type="button" class="tx-btn tx-btn-outline-blue tx-btn-cell" @click="emitSingle('chassis', 'noidentify', row.node)">
                      NO IDENTIFY
                    </button>
                  </div>
                </td>
                <td class="tx-td-actions">
                  <div class="tx-control-cell-actions">
                    <button type="button" class="tx-btn tx-btn-outline-blue tx-btn-cell tx-btn-inactive" disabled>
                      SETTINGS
                    </button>
                    <button type="button" class="tx-btn tx-btn-outline-blue tx-btn-cell tx-btn-inactive" disabled>
                      UPLOAD
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="tx-table-footer">
          <div class="tx-page-length-box">
            <select v-model.number="pageSize">
              <option v-for="n in pageSizeOptions" :key="n" :value="n">{{ n }}</option>
            </select>
            <span class="tx-page-length-label">Entries per Page</span>
          </div>
          <div class="tx-paging">
            <button type="button" class="tx-paging-arrow" :disabled="page <= 1" aria-label="Previous page" @click="page--">
              &lt;
            </button>
            <span class="tx-paging-current">{{ page }}</span>
            <button type="button" class="tx-paging-arrow" :disabled="page >= totalPages" aria-label="Next page" @click="page++">
              &gt;
            </button>
          </div>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="helpOpen" class="tx-modal-overlay" @mousedown.self="helpOpen = false">
        <div class="tx-help-dialog" role="dialog" aria-labelledby="control-help-title">
          <button type="button" class="tx-modal-x" aria-label="Close" @click="helpOpen = false">&times;</button>
          <h2 id="control-help-title" class="tx-help-title">How to use Control</h2>
          <h3 class="tx-help-section-title">Overview</h3>
          <ul class="tx-help-list">
            <li>Control lets you run BMC actions against nodes in your cluster from one inventory table.</li>
            <li>Status for the current page loads automatically when you open a page or change search or pagination.</li>
          </ul>
          <h3 class="tx-help-section-title">Power</h3>
          <ul class="tx-help-list">
            <li><strong>Green power icon</strong> — node power is on. Click the icon to turn power off.</li>
            <li><strong>Red power icon</strong> — node power is off. Click the icon to turn power on.</li>
            <li><strong>Grey power icon</strong> — power status is not yet known. Click the icon to turn power on.</li>
            <li><strong>RESET</strong> — hard reset the node without using the power icon.</li>
            <li>While a power action runs, a spinner appears next to the icon until Luna reports the new state.</li>
          </ul>
          <h3 class="tx-help-section-title">Bulk actions</h3>
          <ul class="tx-help-list">
            <li>Select one or more nodes with the checkboxes, then use the left panel.</li>
            <li>The header checkbox selects or clears every node on the <em>current page</em> only.</li>
            <li>The power icon in the sidebar applies to all selected nodes: green when all are on (click to turn off), red when any are off (click to turn all on).</li>
            <li>SEL, Chassis, and other bulk buttons run the same action on every selected node.</li>
          </ul>
          <h3 class="tx-help-section-title">Row actions</h3>
          <ul class="tx-help-list">
            <li>Each table row has the same actions as the sidebar, scoped to that node only.</li>
            <li><strong>SEL → LIST</strong> opens a log viewer for the System Event Log.</li>
            <li><strong>SEL → CLEAR</strong> clears the SEL for that node.</li>
            <li><strong>CHASSIS → IDENTIFY</strong> / <strong>NO IDENTIFY</strong> toggles chassis locate LED behaviour.</li>
          </ul>
          <h3 class="tx-help-section-title">Search and pagination</h3>
          <ul class="tx-help-list">
            <li><strong>Search</strong> filters the table by node name as you type.</li>
            <li>Use <strong>Entries per Page</strong> and the page arrows to move through large node lists.</li>
          </ul>
          <h3 class="tx-help-section-title">Messages</h3>
          <ul class="tx-help-list">
            <li>Success and error banners appear at the top of the page after an action.</li>
            <li>Failed nodes may also show a toast in the upper-right corner with Luna error details.</li>
          </ul>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import PowerStatusDot from '@/components/PowerStatusDot.vue'
import type { ControlStatusRow, StatusToast } from '@/types'
import {
  bulkPowerToggleAction,
  bulkPowerToggleVisualState,
  powerToggleAction,
} from '@/utils'
import { computed, ref, watch } from 'vue'

const props = defineProps<{
  rows: ControlStatusRow[]
  selected: string[]
  toasts?: StatusToast[]
  powerLoadingNodes?: Record<string, boolean>
  nodesLoading?: boolean
  message?: string
  messageOk?: boolean
}>()

const emit = defineEmits<{
  bulk: [system: string, action: string]
  single: [system: string, action: string, node: string]
  toggleSelect: [next: string[]]
  dismissToast: [id: string]
  loadPage: [nodes: string[]]
}>()

const toasts = computed(() => props.toasts ?? [])
const nodesLoading = computed(() => Boolean(props.nodesLoading))
const rows = computed(() => props.rows)

function isPowerRowLoading(node: string): boolean {
  return Boolean(props.powerLoadingNodes?.[node])
}

const sidebarPowerLoading = computed(() =>
  props.selected.some((node) => isPowerRowLoading(node)),
)

const sidebarPowerDisplay = computed(() => {
  const visual = bulkPowerToggleVisualState(
    props.selected,
    props.rows,
    props.powerLoadingNodes ?? {},
  )
  if (visual === 'on') return 'ON'
  if (visual === 'off') return 'OFF'
  if (visual === 'loading') return 'PENDING'
  return 'UNKNOWN'
})

function onRowPowerToggle(row: ControlStatusRow) {
  const action = powerToggleAction(row.power, isPowerRowLoading(row.node))
  if (!action) return
  emitSingle('power', action, row.node)
}

function onSidebarPowerToggle() {
  const action = bulkPowerToggleAction(
    props.selected,
    props.rows,
    props.powerLoadingNodes ?? {},
  )
  if (!action) return
  emitBulk('power', action)
}

const searchQuery = ref('')
const helpOpen = ref(false)
const page = ref(1)
const pageSize = ref(10)
const pageSizeOptions = [10, 25, 50]

const selectedSet = computed(() => new Set(props.selected))
/** True when every node on the current page is selected. */
const allPageSelected = computed(
  () => pagedRows.value.length > 0 && pagedRows.value.every((r) => selectedSet.value.has(r.node)),
)

const selectedCountLabel = computed(() => {
  const count = props.selected.length
  if (count === 0) return 'No nodes selected'
  if (count === 1) return '1 node selected'
  return `${count} nodes selected`
})

const filteredRows = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return props.rows
  return props.rows.filter((r) => r.node.toLowerCase().includes(q))
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredRows.value.length / pageSize.value)))

const pagedRows = computed(() => {
  const start = (page.value - 1) * pageSize.value
  return filteredRows.value.slice(start, start + pageSize.value)
})

watch([searchQuery, pageSize], () => {
  page.value = 1
})

function emitCurrentPageLoad(): void {
  emit('loadPage', pagedRows.value.map((r) => r.node))
}

watch([page, pageSize, searchQuery], emitCurrentPageLoad, { flush: 'post' })

watch(
  () => props.rows.length,
  (len, prev) => {
    if (len > 0 && prev === 0) emitCurrentPageLoad()
  },
  { flush: 'post' },
)

function toggleOne(node: string) {
  const next = new Set(selectedSet.value)
  if (next.has(node)) next.delete(node)
  else next.add(node)
  emit('toggleSelect', [...next])
}

function togglePageSelection() {
  const pageNodes = pagedRows.value.map((r) => r.node)
  const pageSet = new Set(pageNodes)
  if (allPageSelected.value) {
    emit(
      'toggleSelect',
      [...selectedSet.value].filter((node) => !pageSet.has(node)),
    )
    return
  }
  // Replace selection with current page only (do not keep nodes from other pages).
  emit('toggleSelect', pageNodes)
}

function emitBulk(system: string, action: string) {
  emit('bulk', system, action)
}

function emitSingle(system: string, action: string, node: string) {
  emit('single', system, action, node)
}

</script>
