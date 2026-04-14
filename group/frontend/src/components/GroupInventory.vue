<template>
  <div class="tx-shell tx-inventory-page">
    <div v-if="errorMsg" class="alert alert-danger" role="alert">{{ errorMsg }}</div>

    <div class="tx-header">
      <h2 class="tx-title">Groups</h2>
      <div class="tx-header-actions">
        <button class="tx-btn tx-btn-help" title="Help" type="button">?</button>
        <button type="button" class="tx-btn tx-btn-blue" @click="$emit('open-add')">Add Group</button>
        <div class="tx-inline-search">
          <label class="tx-inline-search-label" for="txManualSearch">Search:</label>
          <input
            id="txManualSearch"
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
              v-for="col in regularColumns"
              :key="col.field"
              rowspan="2"
              class="tx-th-regular"
              :class="{ 'tx-th-sortable': true, 'tx-th-sorted': sortField === col.field }"
              @click="toggleSort(col.field)"
            >
              {{ col.label }}
              <span class="tx-sort-arrow">{{ sortField === col.field ? (sortAsc ? '\u25B2' : '\u25BC') : '\u25BC' }}</span>
            </th>
            <th v-if="hasInterfaces" colspan="2" rowspan="2" class="tx-iface-header">
              <div class="tx-iface-head-inner">
                <div class="tx-iface-head-title">Interfaces</div>
                <div class="tx-iface-head-subs">
                  <span
                    :class="{ 'tx-th-sorted': sortField === 'iface_name' }"
                    @click.stop="toggleSort('iface_name')"
                  >
                    Name
                    <span class="tx-sort-arrow">{{ sortField === 'iface_name' ? (sortAsc ? '\u25B2' : '\u25BC') : '\u25BC' }}</span>
                  </span>
                  <span
                    :class="{ 'tx-th-sorted': sortField === 'iface_network' }"
                    @click.stop="toggleSort('iface_network')"
                  >
                    Network
                    <span class="tx-sort-arrow">{{ sortField === 'iface_network' ? (sortAsc ? '\u25B2' : '\u25BC') : '\u25BC' }}</span>
                  </span>
                </div>
              </div>
            </th>
            <th rowspan="2" class="tx-th-regular tx-th-actions">Actions</th>
          </tr>
          <tr class="tx-iface-thead-spacer"></tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td :colspan="totalColspan" style="text-align:center;padding:2rem;">Loading...</td>
          </tr>
          <tr v-else-if="pagedRows.length === 0">
            <td :colspan="totalColspan" style="text-align:center;padding:2rem;color:#999;">No groups found.</td>
          </tr>
          <tr v-for="(row, idx) in pagedRows" :key="row.name + '-' + idx">
            <td
              v-for="col in regularColumns"
              :key="col.field"
            >
              <template v-if="col.field === 'name'">
                <button
                  type="button"
                  class="tx-name-link"
                  @click="$emit('open-edit', canonicalName(row.name))"
                >{{ row.name }}</button>
              </template>
              <template v-else-if="isEmpty(row[col.field])">
                <span class="tx-na-box">NOT AVAILABLE</span>
              </template>
              <template v-else>
                {{ cellText(row[col.field]) }}
              </template>
            </td>
            <td v-if="hasInterfaces" class="tx-iface-cell tx-iface-name">
              <div
                v-for="(iface, iIdx) in (row.interfaces || [])"
                :key="'n-' + iIdx"
                class="tx-iface-entry"
              >{{ iface.interface || '' }}</div>
            </td>
            <td v-if="hasInterfaces" class="tx-iface-cell tx-iface-network">
              <div
                v-for="(iface, iIdx) in (row.interfaces || [])"
                :key="'nw-' + iIdx"
                class="tx-iface-entry"
              >{{ iface.network || '' }}</div>
            </td>
            <td class="tx-col-actions">
              <div class="tx-action-icons">
                <button
                  type="button"
                  class="tx-icon-act tx-icon-clone"
                  title="Clone"
                  @click="$emit('clone', canonicalName(row.name))"
                >
                  <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>
                </button>
                <button
                  type="button"
                  class="tx-icon-act tx-icon-ospush"
                  title="OS Push"
                  @click="$emit('ospush', canonicalName(row.name))"
                >
                  <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M9 16h6v-6h4l-7-7-7 7h4v6zm-4 2h14v2H5v-2z"/></svg>
                </button>
                <button
                  type="button"
                  class="tx-icon-act tx-icon-danger"
                  title="Delete"
                  @click="handleDelete(canonicalName(row.name))"
                >
                  <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="tx-table-footer">
      <div class="tx-page-length">
        <select v-model.number="pageSize">
          <option v-for="n in pageSizeOptions" :key="n" :value="n">{{ n }}</option>
        </select>
        <span class="tx-page-length-label">Entries per Page</span>
      </div>
      <div class="tx-paging">
        <button
          class="tx-paging-btn"
          :disabled="currentPage <= 1"
          @click="currentPage--"
        >&lt;</button>
        <button
          v-for="p in visiblePages"
          :key="p"
          class="tx-paging-btn"
          :class="{ current: p === currentPage }"
          @click="currentPage = p"
        >{{ p }}</button>
        <button
          class="tx-paging-btn"
          :disabled="currentPage >= totalPages"
          @click="currentPage++"
        >&gt;</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { fetchGroups, deleteGroup } from '../api.js'

const emit = defineEmits(['open-add', 'open-edit', 'clone', 'ospush'])

const fields = ref([])
const groups = ref([])
const loading = ref(true)
const errorMsg = ref('')
const searchQuery = ref('')
const sortField = ref('')
const sortAsc = ref(true)
const currentPage = ref(1)
const pageSize = ref(10)
const pageSizeOptions = [10, 25, 50, 100]

const hasInterfaces = computed(() => fields.value.includes('interfaces'))

const regularColumns = computed(() => {
  return fields.value
    .filter((f) => f !== 'interfaces')
    .map((f) => ({
      field: f,
      label: f.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
    }))
})

const totalColspan = computed(() => {
  let count = regularColumns.value.length + 1
  if (hasInterfaces.value) count += 2
  return count
})

function canonicalName(displayName) {
  return String(displayName || '').replace(/\s+\*$/, '').trim()
}

function cellText(val) {
  if (val == null) return ''
  if (typeof val === 'object') {
    try { return JSON.stringify(val) } catch { return String(val) }
  }
  return String(val)
}

function isEmpty(val) {
  if (val == null) return true
  if (typeof val === 'string' && val.trim() === '') return true
  if (Array.isArray(val) && val.length === 0) return true
  return false
}

const filteredRows = computed(() => {
  let rows = groups.value
  const q = searchQuery.value.toLowerCase().trim()
  if (q) {
    rows = rows.filter((row) => {
      return Object.values(row).some((val) => {
        if (val == null) return false
        if (typeof val === 'string') return val.toLowerCase().includes(q)
        if (Array.isArray(val)) {
          return val.some((item) =>
            Object.values(item || {}).some((v) =>
              String(v || '').toLowerCase().includes(q)
            )
          )
        }
        return String(val).toLowerCase().includes(q)
      })
    })
  }
  if (sortField.value) {
    const sf = sortField.value
    const asc = sortAsc.value
    rows = [...rows].sort((a, b) => {
      let va, vb
      if (sf === 'iface_name') {
        va = (a.interfaces?.[0]?.interface || '').toLowerCase()
        vb = (b.interfaces?.[0]?.interface || '').toLowerCase()
      } else if (sf === 'iface_network') {
        va = (a.interfaces?.[0]?.network || '').toLowerCase()
        vb = (b.interfaces?.[0]?.network || '').toLowerCase()
      } else {
        va = a[sf] != null ? String(a[sf]).toLowerCase() : ''
        vb = b[sf] != null ? String(b[sf]).toLowerCase() : ''
      }
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

const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value
  const delta = 2
  for (let i = Math.max(1, current - delta); i <= Math.min(total, current + delta); i++) {
    pages.push(i)
  }
  return pages
})

watch(searchQuery, () => { currentPage.value = 1 })
watch(pageSize, () => { currentPage.value = 1 })

function toggleSort(field) {
  if (sortField.value === field) {
    sortAsc.value = !sortAsc.value
  } else {
    sortField.value = field
    sortAsc.value = true
  }
}

async function loadData() {
  loading.value = true
  errorMsg.value = ''
  try {
    const data = await fetchGroups()
    if (data.error) errorMsg.value = data.error
    fields.value = data.fields || []
    groups.value = data.groups || []
  } catch (err) {
    errorMsg.value = err.message || 'Network error while loading groups.'
  } finally {
    loading.value = false
  }
}

async function handleDelete(name) {
  if (!name || !confirm(`Delete group "${name}"?`)) return
  try {
    await deleteGroup(name)
    await loadData()
  } catch (err) {
    alert(err.message || 'Delete failed')
  }
}

defineExpose({ loadData })

onMounted(loadData)
</script>
