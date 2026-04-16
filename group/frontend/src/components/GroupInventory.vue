<template>
  <div class="tx-shell tx-inventory-page">
    <div v-if="errorMsg" class="alert alert-danger" role="alert">{{ errorMsg }}</div>

    <div class="tx-header">
      <h2 class="tx-title">Groups</h2>
      <div class="tx-header-actions">
        <button type="button" class="tx-btn tx-btn-blue" @click="$emit('open-add')">Add Group</button>
        <button class="tx-btn tx-btn-help" title="Help" type="button" @click="helpOpen = true">?</button>
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
              v-for="(col, cIdx) in regularColumns"
              :key="col.field"
              rowspan="2"
              class="tx-th-regular"
              :class="{
                'tx-th-sep-blue': cIdx > 0,
                'tx-th-sep-before-iface': hasInterfaces && cIdx === regularColumns.length - 1,
              }"
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
            <th v-if="hasInterfaces" colspan="2" rowspan="2" class="tx-iface-header">
              <div class="tx-iface-head-inner">
                <div class="tx-iface-head-title">Interfaces</div>
                <div class="tx-iface-head-subs">
                  <span @click.stop="toggleSort('iface_name')">
                    Name
                    <span class="tx-sort-dt tx-sort-dt-orange" aria-hidden="true">
                      <svg width="10" height="14" viewBox="0 0 10 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M5 0L9.33 5H0.67L5 0Z" fill="currentColor" opacity="0.35" />
                        <path d="M5 14L0.67 9H9.33L5 14Z" fill="currentColor" opacity="0.35" />
                      </svg>
                    </span>
                  </span>
                  <span @click.stop="toggleSort('iface_network')">
                    Network
                    <span class="tx-sort-dt tx-sort-dt-orange" aria-hidden="true">
                      <svg width="10" height="14" viewBox="0 0 10 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M5 0L9.33 5H0.67L5 0Z" fill="currentColor" opacity="0.35" />
                        <path d="M5 14L0.67 9H9.33L5 14Z" fill="currentColor" opacity="0.35" />
                      </svg>
                    </span>
                  </span>
                </div>
              </div>
            </th>
            <th rowspan="2" class="tx-th-regular tx-th-actions" :class="{ 'tx-th-sep-orange-right': hasInterfaces, 'tx-th-sep-blue': !hasInterfaces }">Actions</th>
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
              v-for="(col, cIdx) in regularColumns"
              :key="col.field"
              :class="{
                'tx-td-sep-blue': cIdx > 0,
                'tx-td-sep-before-iface': hasInterfaces && cIdx === regularColumns.length - 1,
              }"
            >
              <template v-if="col.field === 'name'">
                <button
                  type="button"
                  class="tx-name-link tx-cell-ellipsis"
                  :title="String(row.name ?? '')"
                  @click="$emit('open-edit', canonicalName(row.name))"
                >{{ row.name }}</button>
              </template>
              <template v-else-if="isEmpty(row[col.field])">
                <span class="tx-na-box">NOT AVAILABLE</span>
              </template>
              <template v-else>
                <span class="tx-cell-ellipsis" :title="cellText(row[col.field])">{{ cellText(row[col.field]) }}</span>
              </template>
            </td>
            <td v-if="hasInterfaces" class="tx-iface-cell tx-iface-name tx-td-iface-edge">
              <div
                v-for="(iface, iIdx) in (row.interfaces || [])"
                :key="'n-' + iIdx"
                class="tx-iface-entry tx-cell-ellipsis"
                :title="String(iface.interface || '')"
              >{{ iface.interface || '' }}</div>
            </td>
            <td v-if="hasInterfaces" class="tx-iface-cell tx-iface-network tx-td-iface-between">
              <div
                v-for="(iface, iIdx) in (row.interfaces || [])"
                :key="'nw-' + iIdx"
                class="tx-iface-entry tx-cell-ellipsis"
                :title="String(iface.network || '')"
              >{{ iface.network || '' }}</div>
            </td>
            <td class="tx-col-actions" :class="{ 'tx-td-sep-orange-right': hasInterfaces, 'tx-td-sep-blue': !hasInterfaces }">
              <div class="tx-action-icons">
                <button
                  type="button"
                  class="tx-icon-act tx-icon-clone"
                  title="Clone"
                  @click="$emit('clone', canonicalName(row.name))"
                >
                  <img src="/icons/icon-clone.png" alt="Clone" width="28" height="28"
                    onerror="this.style.display='none';this.nextElementSibling.style.display='inline'"
                  />
                  <svg style="display:none" viewBox="0 0 24 24" width="28" height="28" fill="currentColor"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>
                </button>
                <button
                  type="button"
                  class="tx-icon-act tx-icon-ospush"
                  title="OS Push"
                  @click="$emit('ospush', canonicalName(row.name))"
                >
                  <img src="/icons/icon-ospush.png" alt="OS Push" width="28" height="28"
                    onerror="this.style.display='none';this.nextElementSibling.style.display='inline'"
                  />
                  <svg style="display:none" viewBox="0 0 24 24" width="28" height="28" fill="currentColor"><path d="M9 16h6v-6h4l-7-7-7 7h4v6zm-4 2h14v2H5v-2z"/></svg>
                </button>
                <button
                  type="button"
                  class="tx-icon-act tx-icon-danger"
                  title="Delete"
                  @click="$emit('delete', canonicalName(row.name))"
                >
                  <img src="/icons/icon-delete.png" alt="Delete" width="28" height="28"
                    onerror="this.style.display='none';this.nextElementSibling.style.display='inline'"
                  />
                  <svg style="display:none" viewBox="0 0 24 24" width="28" height="28" fill="currentColor"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
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
        >&lt;</button>
        <span class="tx-paging-current">{{ currentPage }}</span>
        <button
          type="button"
          class="tx-paging-arrow"
          :disabled="currentPage >= totalPages"
          aria-label="Next page"
          @click="currentPage++"
        >&gt;</button>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="helpOpen" class="tx-modal-overlay" @mousedown.self="helpOpen = false">
        <div class="tx-help-dialog" role="dialog" aria-labelledby="help-title">
          <button type="button" class="tx-modal-x" aria-label="Close" @click="helpOpen = false">&times;</button>
          <h2 id="help-title" class="tx-help-title">How to use this app</h2>
          <ul class="tx-help-list">
            <li><strong>Add Group</strong> — Use the button to create a new group.</li>
            <li><strong>Edit</strong> — Click an underlined group name.</li>
            <li><strong>Clone / OS Push / Delete</strong> — Use the icons in the Actions column.</li>
            <li><strong>Search</strong> — Filter the table as you type.</li>
            <li><strong>Sort</strong> — Click a column header (or Name / Network under Interfaces) to sort; click again to reverse.</li>
          </ul>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { fetchGroups } from '../api.js'

const emit = defineEmits(['open-add', 'open-edit', 'clone', 'ospush', 'delete'])

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
const helpOpen = ref(false)

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

function ifaceSortKey(row, key) {
  const list = row.interfaces || []
  return list
    .map((item) => String((item && item[key]) || '').toLowerCase())
    .join('\u0001')
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
      let va
      let vb
      if (sf === 'iface_name') {
        va = ifaceSortKey(a, 'interface')
        vb = ifaceSortKey(b, 'interface')
      } else if (sf === 'iface_network') {
        va = ifaceSortKey(a, 'network')
        vb = ifaceSortKey(b, 'network')
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

watch(searchQuery, () => { currentPage.value = 1 })
watch(pageSize, () => { currentPage.value = 1 })
watch([filteredRows, totalPages], () => {
  if (currentPage.value > totalPages.value) currentPage.value = Math.max(1, totalPages.value)
})

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

defineExpose({ loadData })

onMounted(loadData)
</script>
