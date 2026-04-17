<template>
  <div class="tx-shell tx-inventory-page">
    <div v-if="errorMsg" class="alert alert-danger" role="alert">{{ errorMsg }}</div>

    <div class="tx-header">
      <h2 class="tx-title">Nodes</h2>
      <div class="tx-header-actions">
        <a :href="resolvePath('/add')" class="tx-btn tx-btn-blue">Add Node</a>
        <button class="tx-btn tx-btn-help" title="Help" type="button" @click="helpOpen = true">?</button>
        <div class="tx-inline-search">
          <label class="tx-inline-search-label" for="txNodeSearch">Search:</label>
          <input
            id="txNodeSearch"
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
            <th v-if="hasInterfaces" colspan="3" rowspan="1" class="tx-iface-header-main">Interfaces</th>
            <th
              rowspan="2"
              class="tx-th-regular tx-th-actions"
              :class="{ 'tx-th-sep-orange-right': hasInterfaces, 'tx-th-sep-blue': !hasInterfaces }"
            >Actions</th>
          </tr>
          <tr v-if="hasInterfaces">
            <th class="tx-iface-sub tx-iface-sub-name" @click.stop="toggleSort('iface_name')">
              <span class="tx-th-label-clip">Name</span>
              <span class="tx-sort-dt tx-sort-dt-orange" aria-hidden="true">
                <svg width="10" height="14" viewBox="0 0 10 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M5 0L9.33 5H0.67L5 0Z" fill="currentColor" opacity="0.35" />
                  <path d="M5 14L0.67 9H9.33L5 14Z" fill="currentColor" opacity="0.35" />
                </svg>
              </span>
            </th>
            <th class="tx-iface-sub tx-iface-sub-mac" @click.stop="toggleSort('iface_mac')">
              <span class="tx-th-label-clip">MAC address</span>
              <span class="tx-sort-dt tx-sort-dt-orange" aria-hidden="true">
                <svg width="10" height="14" viewBox="0 0 10 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M5 0L9.33 5H0.67L5 0Z" fill="currentColor" opacity="0.35" />
                  <path d="M5 14L0.67 9H9.33L5 14Z" fill="currentColor" opacity="0.35" />
                </svg>
              </span>
            </th>
            <th class="tx-iface-sub tx-iface-sub-ip" @click.stop="toggleSort('iface_ip')">
              <span class="tx-th-label-clip">IP address</span>
              <span class="tx-sort-dt tx-sort-dt-orange" aria-hidden="true">
                <svg width="10" height="14" viewBox="0 0 10 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M5 0L9.33 5H0.67L5 0Z" fill="currentColor" opacity="0.35" />
                  <path d="M5 14L0.67 9H9.33L5 14Z" fill="currentColor" opacity="0.35" />
                </svg>
              </span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td :colspan="totalColspan" style="text-align:center;padding:2rem;">Loading...</td>
          </tr>
          <tr v-else-if="pagedRows.length === 0">
            <td :colspan="totalColspan" style="text-align:center;padding:2rem;color:#999;">No nodes found.</td>
          </tr>
          <tr v-for="(row, idx) in pagedRows" :key="(row.name || '') + '-' + idx">
            <td
              v-for="(col, cIdx) in regularColumns"
              :key="col.field"
              :class="{
                'tx-td-sep-blue': cIdx > 0,
                'tx-td-sep-before-iface': hasInterfaces && cIdx === regularColumns.length - 1,
              }"
            >
              <template v-if="col.field === 'name'">
                <a
                  class="tx-name-link tx-cell-ellipsis"
                  :title="String(row.name ?? '')"
                  :href="resolvePath('/edit/' + encodeURIComponent(canonicalName(row.name)))"
                >{{ row.name }}</a>
              </template>
              <template v-else-if="col.field === 'osimage'">
                <span v-if="isInvalidOs(row)" class="tx-os-invalid">!!Invalid!!</span>
                <span v-else-if="isEmpty(row[col.field])" class="tx-na-box">NOT AVAILABLE</span>
                <span v-else class="tx-cell-ellipsis" :title="cellText(row[col.field])">{{ cellText(row[col.field]) }}</span>
              </template>
              <template v-else-if="col.field === 'setupbmc'">
                <span :class="setupbmcClass(row[col.field])">{{ setupbmcLabel(row[col.field]) }}</span>
              </template>
              <template v-else-if="col.field === 'tpm_present'">
                <span :class="tpmClass(row[col.field])">{{ tpmLabel(row[col.field]) }}</span>
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
            <td v-if="hasInterfaces" class="tx-iface-cell tx-iface-mac tx-td-iface-between">
              <div
                v-for="(iface, iIdx) in (row.interfaces || [])"
                :key="'m-' + iIdx"
                class="tx-iface-entry tx-cell-ellipsis"
                :title="String(iface.macaddress || '')"
              >{{ iface.macaddress || '' }}</div>
            </td>
            <td v-if="hasInterfaces" class="tx-iface-cell tx-iface-ip tx-td-iface-edge-ip">
              <div
                v-for="(iface, iIdx) in (row.interfaces || [])"
                :key="'p-' + iIdx"
                class="tx-iface-entry tx-cell-ellipsis"
                :title="ifaceIp(iface)"
              >{{ ifaceIp(iface) }}</div>
            </td>
            <td
              class="tx-col-actions"
              :class="{ 'tx-td-sep-orange-right': hasInterfaces, 'tx-td-sep-blue': !hasInterfaces }"
            >
              <div class="tx-action-icons">
                <a
                  class="tx-icon-act tx-icon-clone"
                  title="Clone"
                  :href="resolvePath('/clone/' + encodeURIComponent(canonicalName(row.name)))"
                >
                  <svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor" aria-hidden="true"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>
                </a>
                <button
                  type="button"
                  class="tx-icon-act tx-icon-link"
                  title="Node detail (JSON)"
                  @click="openDetail(canonicalName(row.name))"
                >
                  <svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor"><path d="M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z"/></svg>
                </button>
                <a
                  class="tx-icon-act tx-icon-ospush"
                  title="OS Push"
                  :href="resolvePath('/ospush/' + encodeURIComponent(canonicalName(row.name)))"
                >
                  <svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor" aria-hidden="true"><path d="M9 16h6v-6h4l-7-7-7 7h4v6zm-4 2h14v2H5v-2z"/></svg>
                </a>
                <button
                  type="button"
                  class="tx-icon-act tx-icon-danger"
                  title="Delete"
                  @click="confirmDelete(row.name)"
                >
                  <svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor" aria-hidden="true"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
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
        <div class="tx-help-dialog" role="dialog" aria-labelledby="help-title-node">
          <button type="button" class="tx-modal-x" aria-label="Close" @click="helpOpen = false">&times;</button>
          <h2 id="help-title-node" class="tx-help-title">How to use this app</h2>
          <ul class="tx-help-list">
            <li><strong>Add Node</strong> — Opens the classic form to create a node.</li>
            <li><strong>Edit</strong> — Click a node name.</li>
            <li><strong>Clone / Detail / OS Push / Delete</strong> — Use the icons in the Actions column (detail loads JSON from the API).</li>
            <li><strong>Search</strong> — Filter the table as you type.</li>
            <li><strong>Sort</strong> — Click a column header to sort; click again to reverse.</li>
          </ul>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="detailOpen" class="tx-modal-overlay" @mousedown.self="detailOpen = false">
        <div class="tx-help-dialog" role="dialog" style="max-width:640px;">
          <button type="button" class="tx-modal-x" aria-label="Close" @click="detailOpen = false">&times;</button>
          <h2 class="tx-help-title">Node detail</h2>
          <p v-if="detailLoading" style="margin:1rem 0;">Loading…</p>
          <p v-else-if="detailError" class="alert alert-danger" role="alert">{{ detailError }}</p>
          <pre v-else class="tx-detail-pre">{{ detailPretty }}</pre>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { fetchNodes, fetchNodeDetail, deleteNode } from '../api.js'

const FIELD_LABELS = {
  name: 'NAME',
  group: 'GROUP',
  osimage: 'OS IMAGE',
  osimagetag: 'OS IM. TAG',
  setupbmc: 'SETUP BMC',
  bmcsetup: 'BMC SETUP',
  status: 'STATUS',
  tpm_present: 'TPM PRESENT',
}

const fields = ref([])
const nodes = ref([])
const loading = ref(true)
const errorMsg = ref('')
const searchQuery = ref('')
const sortField = ref('')
const sortAsc = ref(true)
const currentPage = ref(1)
const pageSize = ref(10)
const pageSizeOptions = [10, 25, 50, 100]
const helpOpen = ref(false)

const detailOpen = ref(false)
const detailLoading = ref(false)
const detailError = ref('')
const detailJson = ref(null)

const hasInterfaces = computed(() => fields.value.includes('interfaces'))

const regularColumns = computed(() => {
  return fields.value
    .filter((f) => f !== 'interfaces')
    .map((f) => ({
      field: f,
      label: FIELD_LABELS[f] || f.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
    }))
})

const totalColspan = computed(() => {
  let count = regularColumns.value.length + 1
  if (hasInterfaces.value) count += 3
  return count
})

const pageLabel = computed(() => String(currentPage.value).padStart(2, '0'))

const detailPretty = computed(() => {
  if (!detailJson.value) return ''
  try {
    return JSON.stringify(detailJson.value, null, 2)
  } catch {
    return String(detailJson.value)
  }
})

function resolvePath(path) {
  const b = (typeof window !== 'undefined' && window.APP_URL) ? window.APP_URL.replace(/\/$/, '') : ''
  return b ? `${b}${path}` : path
}

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

function ifaceIp(iface) {
  if (!iface || typeof iface !== 'object') return ''
  const parts = []
  if (iface.ipaddress) parts.push(String(iface.ipaddress))
  if (iface.ipaddress_ipv6) parts.push(String(iface.ipaddress_ipv6))
  if (iface.dhcp === true) parts.push('[DHCP]')
  return parts.join(' ') || ''
}

function isInvalidOs(row) {
  const v = row.osimage
  if (v != null && typeof v === 'string' && /invalid/i.test(v)) return true
  return false
}

function setupbmcLabel(val) {
  if (val === true || val === 'true' || val === 'True') return 'YES'
  if (val === false || val === 'false' || val === 'False') return 'NO'
  const s = val != null ? String(val).toLowerCase() : ''
  if (s.includes('inherit')) return 'INHERITED'
  return cellText(val) || '—'
}

function setupbmcClass(val) {
  const s = val != null ? String(val).toLowerCase() : ''
  if (s.includes('inherit')) return 'tx-pill tx-pill-inherited'
  if (val === true || val === 'true' || val === 'True') return 'tx-pill tx-pill-yes'
  if (val === false || val === 'false' || val === 'False') return 'tx-pill tx-pill-no'
  return 'tx-pill tx-pill-no'
}

function tpmLabel(val) {
  if (val === true || val === 'true' || val === 'True') return 'TRUE'
  if (val === false || val === 'false' || val === 'False') return 'FALSE'
  return cellText(val) || '—'
}

function tpmClass(val) {
  if (val === true || val === 'true' || val === 'True') return 'tx-pill tx-pill-true'
  if (val === false || val === 'false' || val === 'False') return 'tx-pill tx-pill-false'
  return 'tx-pill tx-pill-false'
}

function ifaceSortKey(row, key) {
  const list = row.interfaces || []
  if (key === 'ip') {
    return list
      .map((item) => ifaceIp(item).toLowerCase())
      .join('\u0001')
  }
  return list
    .map((item) => String((item && item[key]) || '').toLowerCase())
    .join('\u0001')
}

const filteredRows = computed(() => {
  let rows = nodes.value
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
      } else if (sf === 'iface_mac') {
        va = ifaceSortKey(a, 'macaddress')
        vb = ifaceSortKey(b, 'macaddress')
      } else if (sf === 'iface_ip') {
        va = ifaceSortKey(a, 'ip')
        vb = ifaceSortKey(b, 'ip')
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
    const data = await fetchNodes()
    if (data.error) errorMsg.value = data.error
    fields.value = data.fields || []
    nodes.value = data.nodes || []
  } catch (err) {
    errorMsg.value = err.message || 'Network error while loading nodes.'
  } finally {
    loading.value = false
  }
}

async function openDetail(name) {
  detailOpen.value = true
  detailLoading.value = true
  detailError.value = ''
  detailJson.value = null
  try {
    const data = await fetchNodeDetail(name)
    if (data.error) detailError.value = data.error
    else detailJson.value = data.node || {}
  } catch (e) {
    detailError.value = e.message || 'Request failed'
  } finally {
    detailLoading.value = false
  }
}

async function confirmDelete(displayName) {
  const c = canonicalName(displayName)
  if (!c) return
  if (!window.confirm(`Delete node ${c}?`)) return
  try {
    await deleteNode(c)
    await loadData()
  } catch (e) {
    errorMsg.value = e.message || 'Delete failed.'
  }
}

defineExpose({ loadData })

onMounted(loadData)
</script>
