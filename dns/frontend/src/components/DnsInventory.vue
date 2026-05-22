<template>
  <div class="tx-shell tx-inventory-page">
    <div v-if="errorMsg" class="alert-danger" role="alert">{{ errorMsg }}</div>

    <div class="tx-header">
      <h2 class="tx-title">DNS Entries</h2>
      <div class="tx-header-actions">
        <button type="button" class="tx-btn tx-btn-blue" @click="$emit('open-add')">Add New DNS</button>
        <button class="tx-btn tx-btn-help" type="button" title="Help" @click="helpOpen = true">?</button>
        <div class="tx-inline-search">
          <label class="tx-inline-search-label" for="txDnsSearch">Search:</label>
          <input
            id="txDnsSearch"
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
            <th class="tx-th-regular">Network</th>
            <th class="tx-th-regular tx-th-sep-blue">Host</th>
            <th class="tx-th-regular tx-th-sep-blue">IP Address</th>
            <th class="tx-th-regular tx-th-actions tx-th-sep-blue">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="4" style="text-align: center; padding: 2rem">Loading...</td>
          </tr>
          <tr v-else-if="pagedRows.length === 0">
            <td colspan="4" style="text-align: center; padding: 2rem; color: #999">No DNS entries found.</td>
          </tr>
          <tr v-for="(row, idx) in pagedRows" :key="row.network + '::' + row.host + '-' + idx">
            <td>
              <span class="tx-cell-ellipsis" :title="dnsLabelTitle(row.network)">{{
                formatDnsLabelDisplay(row.network)
              }}</span>
            </td>
            <td class="tx-td-sep-blue">
              <button
                type="button"
                class="tx-name-link tx-cell-ellipsis"
                :title="dnsLabelTitle(row.host)"
                @click="$emit('open-update', row.network, row.host)"
              >
                {{ formatDnsLabelDisplay(row.host) }}
              </button>
            </td>
            <td class="tx-td-sep-blue">
              <span class="tx-cell-ellipsis" :title="row.ipaddress">{{ row.ipaddress }}</span>
            </td>
            <td class="tx-col-actions tx-td-sep-blue">
              <div class="tx-action-icons">
                <button
                  type="button"
                  class="tx-icon-act tx-icon-danger"
                  title="Delete"
                  @click="$emit('open-delete', row.network, row.host)"
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
        <div class="tx-help-dialog" role="dialog">
          <button type="button" class="tx-modal-x" aria-label="Close" @click="helpOpen = false">&times;</button>
          <h2 class="tx-help-title">How to use this app</h2>
          <ul class="tx-help-list">
            <li><strong>Add New DNS</strong> — Create a host record on a network.</li>
            <li><strong>Update</strong> — Click the host name.</li>
            <li><strong>Delete</strong> — Remove a DNS entry.</li>
          </ul>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { fetchDnsEntries } from '@/api'
import { punAppAssetUrl } from '@/utils'
import {
  dnsLabelTitle,
  formatDnsLabelDisplay,
} from '@/constants/dnsName'
import type { DnsEntryRow } from '@/types'

defineEmits<{
  'open-add': []
  'open-update': [network: string, host: string]
  'open-delete': [network: string, host: string]
}>()

const actionIcons = {
  delete: punAppAssetUrl('icons/icon-delete.png'),
}

const rows = ref<DnsEntryRow[]>([])
const loading = ref(true)
const errorMsg = ref('')
const searchQuery = ref('')
const helpOpen = ref(false)
const pageSizeOptions = [10, 25, 50, 100]
const pageSize = ref(10)
const currentPage = ref(1)

const filteredRows = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return rows.value
  return rows.value.filter((r) => {
    const hay = `${r.network} ${r.host} ${r.ipaddress}`.toLowerCase()
    return hay.includes(q)
  })
})

const totalPages = computed(() =>
  Math.max(1, Math.ceil(filteredRows.value.length / pageSize.value)),
)

const pagedRows = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredRows.value.slice(start, start + pageSize.value)
})

const pageLabel = computed(() => {
  if (filteredRows.value.length === 0) return '0'
  return String(currentPage.value)
})

watch([searchQuery, pageSize], () => {
  currentPage.value = 1
})

watch(totalPages, (tp) => {
  if (currentPage.value > tp) currentPage.value = tp
})

async function loadData() {
  loading.value = true
  errorMsg.value = ''
  try {
    rows.value = await fetchDnsEntries()
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : 'Failed to load DNS entries.'
    rows.value = []
  } finally {
    loading.value = false
  }
}

function handleEscKey(event: KeyboardEvent) {
  if (event.key === 'Escape' && helpOpen.value) {
    helpOpen.value = false
  }
}

defineExpose({ loadData })

onMounted(() => {
  loadData()
  window.addEventListener('keydown', handleEscKey)
})
onUnmounted(() => {
  window.removeEventListener('keydown', handleEscKey)
})
</script>
