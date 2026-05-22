<template>
  <div class="tx-shell tx-inventory-page">
    <div v-if="errorMsg" class="alert-danger" role="alert">{{ errorMsg }}</div>

    <div class="tx-header">
      <h2 class="tx-title">Networks</h2>
      <div class="tx-header-actions">
        <button type="button" class="tx-btn tx-btn-blue" @click="$emit('open-add')">Add Network</button>
        <button type="button" class="tx-btn tx-btn-help" title="Help" @click="helpOpen = true">?</button>
        <div class="tx-inline-search">
          <label class="tx-inline-search-label" for="txNetworkSearch">Search:</label>
          <input
            id="txNetworkSearch"
            v-model="searchQuery"
            type="search"
            class="tx-inline-search-input"
            autocomplete="off"
          />
        </div>
      </div>
    </div>

    <div class="tx-inventory-table-wrap">
      <table class="tx-inventory-table">
        <thead>
          <tr>
            <th
              v-for="(col, cIdx) in displayColumns"
              :key="col.field"
              class="tx-th-regular"
              :class="{ 'tx-th-sep-blue': cIdx > 0 }"
              :title="col.label"
              @click="toggleSort(col.field)"
            >
              <span class="tx-th-label-clip">{{ col.label }}</span>
              <span class="tx-sort-dt" aria-hidden="true">
                <svg width="10" height="14" viewBox="0 0 10 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M5 0L9.33 5H0.67L5 0Z" fill="currentColor" opacity="0.35" />
                  <path d="M5 14L0.67 9H9.33L5 14Z" fill="currentColor" opacity="0.35" />
                </svg>
              </span>
            </th>
            <th class="tx-th-regular tx-th-actions tx-th-sep-blue">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td :colspan="displayColumns.length + 1" style="text-align: center; padding: 2rem">Loading...</td>
          </tr>
          <tr v-else-if="pagedRows.length === 0">
            <td :colspan="displayColumns.length + 1" style="text-align: center; padding: 2rem; color: #999">
              No networks found.
            </td>
          </tr>
          <tr v-for="(row, idx) in pagedRows" :key="(row.name || '') + '-' + idx">
            <td
              v-for="(col, cIdx) in displayColumns"
              :key="col.field"
              :class="{ 'tx-td-sep-blue': cIdx > 0 }"
            >
              <template v-if="col.field === 'name'">
                <button
                  type="button"
                  class="tx-name-link tx-cell-ellipsis tx-cell-truncate-js"
                  :title="networkNameTitle(row.name)"
                  @click="$emit('open-edit', row.name)"
                >
                  {{ formatNetworkNameDisplay(row.name) }}
                </button>
              </template>
              <template v-else-if="col.field === 'dhcp'">
                <span :class="dhcpClass(row.dhcp)">{{ dhcpLabel(row.dhcp) }}</span>
              </template>
              <template v-else-if="col.field === 'dhcp_range_begin' || col.field === 'dhcp_range_end'">
                <div class="tx-network-range-cell">
                  <span v-if="!isEmpty(row[col.field])" class="tx-cell-ellipsis">{{ row[col.field] }}</span>
                  <span v-else class="tx-na-box">NOT AVAILABLE</span>
                </div>
              </template>
              <template v-else-if="isEmpty(row[col.field])">
                <span class="tx-na-box">NOT AVAILABLE</span>
              </template>
              <template v-else>
                <span class="tx-cell-ellipsis" :title="cellText(row[col.field])">{{
                  cellText(row[col.field])
                }}</span>
              </template>
            </td>
            <td class="tx-col-actions tx-td-sep-blue">
              <div class="tx-action-icons">
                <button
                  type="button"
                  class="tx-btn tx-btn-blue tx-btn-compact"
                  title="Check IP"
                  @click="$emit('open-ip-check', row.name)"
                >
                  Check IP
                </button>
                <button
                  type="button"
                  class="tx-btn tx-btn-outline-blue tx-btn-compact tx-btn-next-ip-inv"
                  title="Next IP"
                  :disabled="nextIpLoading === row.name"
                  :aria-busy="nextIpLoading === row.name"
                  @click="doNextIp(row.name)"
                >
                  Next IP
                </button>
                <button
                  type="button"
                  class="tx-icon-act tx-icon-link"
                  title="Reserved IPs"
                  @click="$emit('open-reserved', row.name)"
                >
                  <img :src="actionIcons.reserved" alt="Reserved" width="28" height="28" class="tx-icon-img" />
                </button>
                <button
                  type="button"
                  class="tx-icon-act tx-icon-danger"
                  title="Delete"
                  @click="$emit('open-delete', row.name)"
                >
                  <img :src="actionIcons.delete" alt="Delete" width="28" height="28" class="tx-icon-img" />
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
        <button
          type="button"
          class="tx-paging-arrow"
          :disabled="currentPage <= 1"
          aria-label="Previous page"
          @click="currentPage--"
        >
          &lt;
        </button>
        <span class="tx-paging-current">{{ pageLabel }}</span>
        <button
          type="button"
          class="tx-paging-arrow"
          :disabled="currentPage >= totalPages"
          aria-label="Next page"
          @click="currentPage++"
        >
          &gt;
        </button>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="helpOpen" class="tx-modal-overlay" @mousedown.self="helpOpen = false">
        <div class="tx-help-dialog" role="dialog" aria-labelledby="help-title-network">
          <button type="button" class="tx-modal-x" aria-label="Close" @click="helpOpen = false">&times;</button>
          <h2 id="help-title-network" class="tx-help-title">How to use this app</h2>
          <ul class="tx-help-list">
            <li><strong>Add Network</strong> — Create a new network definition.</li>
            <li><strong>Edit</strong> — Click a network name to update settings.</li>
            <li><strong>Check IP</strong> — Look up an address in a network.</li>
            <li><strong>Next IP</strong> — Show the next free address from Luna.</li>
            <li><strong>Reserved list</strong> — View reserved IPs and device names.</li>
            <li><strong>Delete</strong> — Remove a network.</li>
          </ul>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="nextIpDialog" class="tx-modal-overlay" @mousedown.self="nextIpDialog = ''">
        <div class="tx-help-dialog" role="dialog">
          <button type="button" class="tx-modal-x" aria-label="Close" @click="nextIpDialog = ''">&times;</button>
          <h2 class="tx-help-title">Next free IP</h2>
          <p style="margin-top: 0.75rem; font-size: 1rem">{{ nextIpDialog }}</p>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { fetchNetworks, fetchNextIp } from '@/api'
import { formatNetworkNameDisplay, networkNameTitle } from '@/constants/networkName'
import { punAppAssetUrl } from '@/utils'
import type { NetworkInventoryRow } from '@/types'

defineEmits<{
  'open-add': []
  'open-edit': [name: string]
  'open-delete': [name: string]
  'open-reserved': [name: string]
  'open-ip-check': [name: string]
}>()

const actionIcons = {
  reserved: punAppAssetUrl('icons/icon-reserved.png'),
  delete: punAppAssetUrl('icons/icon-delete.png'),
}

const FIELD_LABELS: Record<string, string> = {
  name: 'NAME',
  network: 'NETWORK',
  type: 'TYPE',
  dhcp: 'DHCP',
  dhcp_range_begin: 'DHCP_RANGE_BEGIN',
  dhcp_range_end: 'DHCP_RANGE_END',
}

const DISPLAY_FIELDS = [
  'name',
  'network',
  'type',
  'dhcp',
  'dhcp_range_begin',
  'dhcp_range_end',
] as const

const networks = ref<NetworkInventoryRow[]>([])
const loading = ref(true)
const errorMsg = ref('')
const searchQuery = ref('')
const sortField = ref('')
const sortAsc = ref(true)
const currentPage = ref(1)
const pageSize = ref(10)
const pageSizeOptions = [10, 25, 50, 100]
const helpOpen = ref(false)
const nextIpLoading = ref('')
const nextIpDialog = ref('')

const displayColumns = computed(() =>
  DISPLAY_FIELDS.map((f) => ({
    field: f,
    label: FIELD_LABELS[f] || f.replace(/_/g, ' ').toUpperCase(),
  })),
)

const pageLabel = computed(() => String(currentPage.value).padStart(2, '0'))

function cellText(val: unknown): string {
  if (val == null) return ''
  return String(val)
}

function isEmpty(val: unknown): boolean {
  if (val == null) return true
  if (typeof val === 'string' && val.trim() === '') return true
  return false
}

function dhcpLabel(val: unknown): string {
  if (val === true || val === 'true') return 'TRUE'
  return 'FALSE'
}

function dhcpClass(val: unknown): string {
  if (val === true || val === 'true') return 'tx-pill tx-pill-true'
  return 'tx-pill tx-pill-false'
}

function rowMatchesSearch(row: NetworkInventoryRow, q: string): boolean {
  return DISPLAY_FIELDS.some((key) => {
    const val = row[key]
    if (val == null) return false
    return String(val).toLowerCase().includes(q)
  })
}

const filteredRows = computed(() => {
  let rows = networks.value
  const q = searchQuery.value.toLowerCase().trim()
  if (q) rows = rows.filter((row) => rowMatchesSearch(row, q))
  if (sortField.value) {
    const sf = sortField.value as keyof NetworkInventoryRow
    const asc = sortAsc.value
    rows = [...rows].sort((a, b) => {
      const va = a[sf] != null ? String(a[sf]).toLowerCase() : ''
      const vb = b[sf] != null ? String(b[sf]).toLowerCase() : ''
      if (va < vb) return asc ? -1 : 1
      if (va > vb) return asc ? 1 : -1
      return 0
    })
  }
  return rows
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredRows.value.length / pageSize.value)))

const pagedRows = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredRows.value.slice(start, start + pageSize.value)
})

watch(searchQuery, () => {
  currentPage.value = 1
})
watch(pageSize, () => {
  currentPage.value = 1
})
watch([filteredRows, totalPages], () => {
  if (currentPage.value > totalPages.value) currentPage.value = Math.max(1, totalPages.value)
})

function toggleSort(field: string) {
  if (sortField.value === field) sortAsc.value = !sortAsc.value
  else {
    sortField.value = field
    sortAsc.value = true
  }
}

async function loadData() {
  loading.value = true
  errorMsg.value = ''
  try {
    const data = await fetchNetworks()
    if (data.error) errorMsg.value = data.error
    networks.value = data.networks || []
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : 'Failed to load networks.'
  } finally {
    loading.value = false
  }
}

async function doNextIp(name: string) {
  if (!name) return
  nextIpLoading.value = name
  try {
    const ip = await fetchNextIp(name)
    nextIpDialog.value = ip
      ? `Next free IP for ${name}: ${ip}`
      : `No free IP returned for ${name}.`
  } catch (e) {
    nextIpDialog.value = e instanceof Error ? e.message : 'Next IP request failed.'
  } finally {
    nextIpLoading.value = ''
  }
}

defineExpose({ loadData })

onMounted(loadData)
</script>
