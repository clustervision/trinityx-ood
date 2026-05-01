<template>
  <div class="tx-shell tx-inventory-page">
    <div v-if="errorMsg" class="alert-danger" role="alert">{{ errorMsg }}</div>

    <div class="tx-header">
      <h2 class="tx-title">OS Images</h2>
      <div class="tx-header-actions">
        <button class="tx-btn tx-btn-help" title="Help" type="button" @click="helpOpen = true">?</button>
        <button type="button" class="tx-btn tx-btn-blue" @click="$emit('open-add')">Add OS Image</button>
        <div class="tx-inline-search">
          <label class="tx-inline-search-label" for="txOsimageSearch">Search:</label>
          <input
            id="txOsimageSearch"
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
            <td :colspan="displayColumns.length + 1" style="text-align:center;padding:2rem;color:#999;">No OS images found.</td>
          </tr>
          <tr v-for="(row, idx) in pagedRows" :key="(row.name || '') + '-' + idx">
            <td
              v-for="(col, cIdx) in displayColumns"
              :key="col.field"
              :class="{
                'tx-td-sep-blue': cIdx > 0,
                'tx-td-kernel-details': col.field === 'kerneldetails',
              }"
            >
              <template v-if="col.field === 'name'">
                <button
                  type="button"
                  class="tx-name-link tx-cell-ellipsis"
                  :title="String(row.name ?? '')"
                  @click="$emit('open-edit', row.name)"
                >{{ row.name }}</button>
              </template>
              <template v-else-if="col.field === 'kerneldetails'">
                <div
                  v-if="kernelDetailsHtml(row)"
                  class="tx-kernel-details-cell tx-kernel-details-html"
                  v-html="kernelDetailsHtml(row)"
                ></div>
                <div v-else-if="hasKernelDetails(row)" class="tx-kernel-details-cell">
                  <div v-if="row.initrdfile"><strong>Initrd File:</strong>&nbsp; {{ row.initrdfile }}</div>
                  <div v-if="row.kernelfile"><strong>Kernel File:</strong>&nbsp; {{ row.kernelfile }}</div>
                  <div v-if="row.imagefile"><strong>Image File:</strong>&nbsp; {{ row.imagefile }}</div>
                  <div v-if="row.path"><strong>Path:</strong>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {{ row.path }}</div>
                </div>
                <span v-else class="tx-na-box">NONE</span>
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
                  v-if="row.chroot_session_url"
                  type="button"
                  class="tx-icon-act tx-icon-link"
                  title="Lchroot Session"
                  @click="openChroot(row.chroot_session_url)"
                >
                  <svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor"><path d="M20 3H4c-1.1 0-2 .9-2 2v11c0 1.1.9 2 2 2h3l-1 1v2h12v-2l-1-1h3c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 13H4V5h16v11z"/></svg>
                </button>
                <button
                  type="button"
                  class="tx-icon-act tx-icon-clone"
                  title="Clone"
                  @click="$emit('open-clone', row.name)"
                >
                  <svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>
                </button>
                <button
                  type="button"
                  class="tx-icon-act tx-icon-pack"
                  title="Pack"
                  @click="doPack(row.name)"
                >
                  <svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor"><path d="M20 2H4c-1.1 0-2 .9-2 2v3h20V4c0-1.1-.9-2-2-2zM2 22h20c0 1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2zM2 9v11h20V9H2zm8 1.5h4v2h-4v-2z"/></svg>
                </button>
                <button
                  type="button"
                  class="tx-icon-act tx-icon-danger"
                  title="Delete"
                  @click="confirmDelete(row.name)"
                >
                  <svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
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

    <!-- Help dialog -->
    <Teleport to="body">
      <div v-if="helpOpen" class="tx-modal-overlay" @mousedown.self="helpOpen = false">
        <div class="tx-help-dialog" role="dialog" aria-labelledby="help-title-osimage">
          <button type="button" class="tx-modal-x" aria-label="Close" @click="helpOpen = false">&times;</button>
          <h2 id="help-title-osimage" class="tx-help-title">How to use this app</h2>
          <ul class="tx-help-list">
            <li><strong>Add OS Image</strong> — Opens the form to create a new OS image.</li>
            <li><strong>Edit</strong> — Click an image name to open the edit form.</li>
            <li><strong>Clone</strong> — Duplicate an existing OS image with a new name.</li>
            <li><strong>Pack</strong> — Pack the OS image for deployment.</li>
            <li><strong>Delete</strong> — Remove an OS image.</li>
            <li><strong>Search</strong> — Filter the table as you type.</li>
            <li><strong>Sort</strong> — Click a column header to sort; click again to reverse.</li>
          </ul>
        </div>
      </div>
    </Teleport>

    <!-- Pack status dialog -->
    <Teleport to="body">
      <div v-if="packStatus" class="tx-modal-overlay" @mousedown.self="packStatus = null">
        <div class="tx-help-dialog" role="dialog">
          <button type="button" class="tx-modal-x" aria-label="Close" @click="packStatus = null">&times;</button>
          <h2 class="tx-help-title">Pack OS Image</h2>
          <p style="font-size:15px;line-height:1.6;color:#111;">{{ packStatus }}</p>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { fetchOsimages, deleteOsimage, packOsimage } from '../api.js'

defineEmits(['open-add', 'open-edit', 'open-clone'])

const FIELD_LABELS = {
  name: 'NAME',
  kernelversion: 'KERNEL VERSION',
  kerneldetails: 'KERNEL DETAILS',
  distribution: 'DISTRIBUTION',
  osrelease: 'OS RELEASE',
}

const DISPLAY_FIELDS = ['name', 'kernelversion', 'kerneldetails', 'distribution', 'osrelease']

const images = ref([])
const loading = ref(true)
const errorMsg = ref('')
const searchQuery = ref('')
const sortField = ref('')
const sortAsc = ref(true)
const currentPage = ref(1)
const pageSize = ref(10)
const pageSizeOptions = [10, 25, 50, 100]
const helpOpen = ref(false)
const packStatus = ref(null)

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

function hasKernelDetails(row) {
  return row.initrdfile || row.kernelfile || row.imagefile || row.path
}

/** Backend may send preformatted HTML in `kerneldetails` (legacy list field). */
function kernelDetailsHtml(row) {
  const k = row.kerneldetails
  if (k == null) return ''
  const s = String(k).trim()
  return s || ''
}

function openChroot(url) {
  if (url) window.open(url, '_blank')
}

function rowMatchesSearch(row, q) {
  return DISPLAY_FIELDS.some((key) => {
    const val = row[key]
    if (val == null) return false
    return String(val).toLowerCase().includes(q)
  })
}

const filteredRows = computed(() => {
  let rows = images.value
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
    const data = await fetchOsimages()
    if (data.error) errorMsg.value = data.error
    images.value = data.images || []
  } catch (err) {
    errorMsg.value = err.message || 'Network error while loading OS images.'
  } finally {
    loading.value = false
  }
}

async function confirmDelete(name) {
  if (!name) return
  if (!window.confirm(`Delete OS Image "${name}"?`)) return
  try {
    await deleteOsimage(name)
    await loadData()
  } catch (e) {
    errorMsg.value = e.message || 'Delete failed.'
  }
}

async function doPack(name) {
  if (!name) return
  packStatus.value = `Packing "${name}"...`
  try {
    const result = await packOsimage(name)
    if (result.data && result.data.message) {
      packStatus.value = result.data.message
    } else if (result.data && result.data.request_id) {
      packStatus.value = `Pack initiated. Request ID: ${result.data.request_id}`
    } else {
      packStatus.value = result.ok ? `Pack request sent for "${name}".` : `Pack failed for "${name}".`
    }
  } catch (e) {
    packStatus.value = e.message || 'Pack failed.'
  }
}

defineExpose({ loadData })

onMounted(loadData)
</script>
