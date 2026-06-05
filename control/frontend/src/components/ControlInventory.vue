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
              <span class="tx-status-dot tx-status-ok" aria-hidden="true" />
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
            <button type="button" class="tx-btn tx-btn-outline-blue tx-btn-sidebar" @click="emitBulk('redfish', 'setting')">
              SETTINGS
            </button>
            <button type="button" class="tx-btn tx-btn-outline-blue tx-btn-sidebar" @click="emitBulk('redfish', 'upload')">
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
                <td class="tx-td-name tx-col-name">{{ row.node }}</td>
                <td class="tx-td-actions">
                  <div class="tx-control-cell-actions tx-control-cell-actions--row">
                    <span :class="powerStatusDotClass(row.power)" aria-hidden="true" />
                    <template v-if="isPowerRowLoading(row.node)">
                      <span class="tx-power-loading-spinner" aria-hidden="true" />
                      <span class="tx-status-text tx-status-loading-text" aria-live="polite">Loading…</span>
                    </template>
                    <span v-else :class="powerStatusTextClass(row.power)">{{ powerStatusLabel(row.power) }}</span>
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
                    <button type="button" class="tx-btn tx-btn-outline-blue tx-btn-cell" @click="emitSingle('redfish', 'setting', row.node)">
                      SETTINGS
                    </button>
                    <button type="button" class="tx-btn tx-btn-outline-blue tx-btn-cell" @click="emitSingle('redfish', 'upload', row.node)">
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
          <ul class="tx-help-list">
            <li>Select nodes with checkboxes, then use the left panel for bulk actions.</li>
            <li>Or use the action buttons in each row for a single node.</li>
            <li><strong>Search</strong> filters the table as you type.</li>
          </ul>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import type { ControlStatusRow, StatusToast } from '@/types'
import { powerStatusDotClass, powerStatusLabel, powerStatusTextClass } from '@/utils'
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
