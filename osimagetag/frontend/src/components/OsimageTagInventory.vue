<template>
  <div class="tx-shell tx-inventory-page">
    <div v-if="errorMsg" class="alert-danger" role="alert">{{ errorMsg }}</div>

    <div class="tx-header">
      <h2 class="tx-title">OS Image Tags</h2>
      <div class="tx-header-actions">
        <button class="tx-btn tx-btn-help" title="Help" type="button" @click="helpOpen = true">?</button>
        <button type="button" class="tx-btn tx-btn-blue" @click="$emit('open-add')">Add Tag</button>
        <div class="tx-inline-search">
          <label class="tx-inline-search-label" for="txOsimageTagSearch">Search:</label>
          <input
            id="txOsimageTagSearch"
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
            <td :colspan="displayColumns.length + 1" style="text-align:center;padding:2rem;">Loading...</td>
          </tr>
          <tr v-else-if="pagedRows.length === 0">
            <td :colspan="displayColumns.length + 1" style="text-align:center;padding:2rem;color:#999;">No OS image tags found.</td>
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
                  class="tx-name-link tx-cell-ellipsis"
                  :title="String(row.name ?? '')"
                  @click="$emit('open-detail', row.name)"
                >{{ row.name }}</button>
              </template>
              <template v-else-if="isEmpty(row[col.field])">
                <span class="tx-na-box">NONE</span>
              </template>
              <template v-else>
                <span class="tx-cell-ellipsis" :title="cellText(row[col.field])">{{ cellText(row[col.field]) }}</span>
              </template>
            </td>
            <td class="tx-col-actions tx-td-sep-blue">
              <div class="tx-action-icons">
                <button
                  type="button"
                  class="tx-icon-act tx-icon-link"
                  title="Detail"
                  @click="$emit('open-detail', row.name)"
                >
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#5376EA" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
                </button>
                <button
                  type="button"
                  class="tx-icon-act tx-icon-danger"
                  title="Delete"
                  @click="confirmDelete(row)"
                >
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#E74C3C" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
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
        <span class="tx-paging-current">{{ pageLabel }}</span>
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
        <div class="tx-help-dialog" role="dialog" aria-labelledby="help-title-osimagetag">
          <button type="button" class="tx-modal-x" aria-label="Close" @click="helpOpen = false">&times;</button>
          <h2 id="help-title-osimagetag" class="tx-help-title">How to use this app</h2>
          <ul class="tx-help-list">
            <li><strong>Add Tag</strong> — Opens the form to add a new tag to an OS image.</li>
            <li><strong>Detail</strong> — Click a tag name to see its details.</li>
            <li><strong>Delete</strong> — Remove a tag from an OS image.</li>
            <li><strong>Search</strong> — Filter the table as you type.</li>
            <li><strong>Sort</strong> — Click a column header to sort; click again to reverse.</li>
          </ul>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { fetchOsimageTags, deleteOsimageTag } from '../api'

defineEmits(['open-add', 'open-detail'])

const FIELD_LABELS = {
  osimage: 'OS IMAGE',
  name: 'TAG NAME',
  kernelfile: 'KERNEL FILE',
  initrdfile: 'INITRD FILE',
  imagefile: 'IMAGE FILE',
  path: 'PATH',
  nodes: 'NODES',
  groups: 'GROUPS',
}

const DISPLAY_FIELDS = ['osimage', 'name', 'kernelfile', 'initrdfile', 'imagefile', 'path', 'nodes', 'groups']

const tags = ref([])
const loading = ref(true)
const errorMsg = ref('')
const searchQuery = ref('')
const sortField = ref('')
const sortAsc = ref(true)
const currentPage = ref(1)
const pageSize = ref(10)
const pageSizeOptions = [10, 25, 50, 100]
const helpOpen = ref(false)

const displayColumns = computed(() =>
  DISPLAY_FIELDS.map((f) => ({
    field: f,
    label: FIELD_LABELS[f] || f.replace(/_/g, ' ').toUpperCase(),
  }))
)

const pageLabel = computed(() => String(currentPage.value).padStart(2, '0'))

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
  return false
}

function rowMatchesSearch(row, q) {
  return DISPLAY_FIELDS.some((key) => {
    const val = row[key]
    if (val == null) return false
    return String(val).toLowerCase().includes(q)
  })
}

const filteredRows = computed(() => {
  let rows = tags.value
  const q = searchQuery.value.toLowerCase().trim()
  if (q) {
    rows = rows.filter((row) => rowMatchesSearch(row, q))
  }
  if (sortField.value) {
    const sf = sortField.value
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
    const data = await fetchOsimageTags()
    if (data.error) errorMsg.value = String(data.error || '').trim() || 'Failed to load OS image tags.'
    tags.value = data.tags || []
  } catch (err) {
    errorMsg.value = String(err?.message || '').trim() || 'Network error while loading OS image tags.'
  } finally {
    loading.value = false
  }
}

async function confirmDelete(row) {
  if (!row?.osimage || !row?.name) return
  if (!window.confirm(`Delete tag "${row.name}" from "${row.osimage}"?`)) return
  try {
    await deleteOsimageTag(row.osimage, row.name)
    await loadData()
  } catch (e) {
    errorMsg.value = String(e?.message || '').trim() || 'Delete failed.'
  }
}

defineExpose({ loadData })

onMounted(loadData)
</script>
