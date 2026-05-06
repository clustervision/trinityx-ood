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
                  type="button"
                  class="tx-icon-act tx-icon-link"
                  :title="row.chroot_session_url ? 'Lchroot session' : 'Lchroot not available (need path + kernel version)'"
                  :disabled="!row.chroot_session_url"
                  @click="row.chroot_session_url && openChroot(row.chroot_session_url)"
                >
                  <img :src="actionIcons.shell" alt="Shell" width="28" height="28" class="tx-icon-img" />
                </button>
                <button
                  type="button"
                  class="tx-icon-act tx-icon-clone"
                  title="Clone"
                  @click="$emit('open-clone', row.name)"
                >
                  <img :src="actionIcons.clone" alt="Clone" width="28" height="28" class="tx-icon-img" />
                </button>
                <button
                  type="button"
                  class="tx-icon-act tx-icon-pack"
                  title="Pack"
                  @click="doPack(row.name)"
                >
                  <img :src="actionIcons.pack" alt="Pack" width="28" height="28" class="tx-icon-img" />
                </button>
                <button
                  type="button"
                  class="tx-icon-act tx-icon-danger"
                  title="Delete"
                  @click="confirmDelete(row.name)"
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
      <div v-if="packOpen" class="tx-modal-overlay" @mousedown.self="closePackDialog">
        <div class="tx-help-dialog" role="dialog">
          <button type="button" class="tx-modal-x" aria-label="Close" @click="closePackDialog">&times;</button>
          <h2 class="tx-help-title">{{ packTitle }}</h2>
          <div style="max-height:360px;overflow:auto;background:#000;border-radius:8px;padding:12px;">
            <p
              v-for="(line, idx) in packLines"
              :key="`${idx}-${line}`"
              style="font-size:15px;line-height:1.5;color:#f1e600;margin:0 0 4px;"
            >{{ line }}</p>
            <p v-if="packRunning" style="font-size:15px;line-height:1.5;color:#9ec2ff;margin:8px 0 0;">Polling status...</p>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { fetchOsimages, fetchOsimageDetail, deleteOsimage, packOsimage, checkPackStatus } from '../api'
import { publicAssetUrl } from '../utils/publicAssets'
import { messageForDisplay } from '../utils/sanitizeUserMessage'
import { resolveChrootBaseUrl, rewriteIfShellOrigin } from '../utils/oodShell'

defineEmits(['open-add', 'open-edit', 'open-clone'])

const actionIcons = {
  shell: publicAssetUrl('icons/icon-shell.png'),
  clone: publicAssetUrl('icons/icon-clone.png'),
  pack: publicAssetUrl('icons/icon-pack.png'),
  delete: publicAssetUrl('icons/icon-delete.png'),
}

const FIELD_LABELS = {
  name: 'NAME',
  kernelversion: 'KERNEL VERSION',
  kerneldetails: 'KERNEL DETAILS',
  distribution: 'DISTRIBUTION',
  osrelease: 'OS RELEASE',
}

const DISPLAY_FIELDS = ['name', 'kernelversion', 'kerneldetails', 'distribution', 'osrelease']

const images = ref([])
/** API `chroot_base_url`, optionally rewritten for OOD port (see `VITE_OOD_SHELL_ORIGIN`). */
const chrootBaseUrl = ref('')
const enrichedNames = new Set()
const loading = ref(true)
const errorMsg = ref('')
const searchQuery = ref('')
const sortField = ref('')
const sortAsc = ref(true)
const currentPage = ref(1)
const pageSize = ref(10)
const pageSizeOptions = [10, 25, 50, 100]
const helpOpen = ref(false)
const packOpen = ref(false)
const packTitle = ref('Pack OS Image')
const packLines = ref([])
const packRunning = ref(false)
let packTimer = null
let activeRequestId = ''
const packSeen = new Set()

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

function recordNameFromRow(row) {
  const n = row?.name
  if (typeof n !== 'string') return ''
  return n.replace(/\s*\*\s*$/, '').trim()
}

function buildChrootSessionUrl(base, shellImage, path, kernelVersion) {
  if (!base || !path || kernelVersion == null || kernelVersion === '') return null
  if (String(kernelVersion).includes('>None<')) return null
  const im = shellImage || ''
  return `${base}/image=${im},path=${path},kernel_version=${kernelVersion}`
}

function patchAllChrootSessionUrls() {
  const base = chrootBaseUrl.value
  if (!base) return
  images.value = images.value.map((r) => {
    const u = buildChrootSessionUrl(
      base,
      r._shellImageName || recordNameFromRow(r),
      r.path,
      r.kernelversion
    )
    return u ? { ...r, chroot_session_url: u } : r
  })
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
  if (!url) return
  window.open(rewriteIfShellOrigin(url), '_blank')
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

watch(chrootBaseUrl, () => {
  patchAllChrootSessionUrls()
})

watch(
  pagedRows,
  async (rows) => {
    for (const row of rows) {
      const key = recordNameFromRow(row)
      if (!key || enrichedNames.has(key)) continue
      enrichedNames.add(key)
      try {
        const res = await fetchOsimageDetail(key)
        if (res?.error) {
          enrichedNames.delete(key)
          continue
        }
        const o = res.osimage || {}
        const idx = images.value.findIndex((r) => recordNameFromRow(r) === key)
        if (idx === -1) continue
        const cur = images.value[idx]
        const next = { ...cur }
        for (const k of ['initrdfile', 'kernelfile', 'imagefile', 'path']) {
          if (o[k] != null && o[k] !== '') next[k] = o[k]
        }
        if (o.kerneldetails != null && String(o.kerneldetails).trim() !== '') {
          next.kerneldetails = o.kerneldetails
        }
        next._shellImageName = o.name != null && o.name !== '' ? o.name : key
        const u = buildChrootSessionUrl(
          chrootBaseUrl.value,
          next._shellImageName,
          next.path,
          next.kernelversion
        )
        if (u) next.chroot_session_url = u
        images.value[idx] = next
      } catch {
        enrichedNames.delete(key)
      }
    }
  },
  { flush: 'post' }
)

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
  enrichedNames.clear()
  try {
    const data = await fetchOsimages()
    if (data.error) errorMsg.value = messageForDisplay(data.error)
    chrootBaseUrl.value = resolveChrootBaseUrl(data)
    images.value = data.images || []
    patchAllChrootSessionUrls()
  } catch (err) {
    errorMsg.value = messageForDisplay(err.message || 'Network error while loading OS images.')
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
    errorMsg.value = messageForDisplay(e.message || 'Delete failed.')
  }
}

async function doPack(name) {
  if (!name) return
  closePackDialog()
  packOpen.value = true
  packTitle.value = `Packing OS Image >> ${name}...`
  packLines.value = []
  packRunning.value = true
  pushPackLine(`starting pack for ${name}`)
  try {
    const result = await packOsimage(name)
    const data = result.data || {}
    if (data.message) pushPackLine(String(data.message))
    const rid = String(data.request_id || '').trim()
    if (!rid) {
      packRunning.value = false
      if (!result.ok) pushPackLine(`pack failed for ${name}`)
      return
    }
    activeRequestId = rid
    pushPackLine(`queued pack osimage ${name} with id ${rid}`)
    await pollPackStatus(name, rid)
  } catch (e) {
    pushPackLine(e.message || 'pack failed.')
    packRunning.value = false
  }
}

function normalizePackLines(data) {
  const out = []
  if (typeof data === 'string') {
    out.push(...data.split('\n'))
    return out
  }
  if (!data || typeof data !== 'object') return out
  const d = data
  if (typeof d.message === 'string') out.push(...d.message.split('\n'))
  if (typeof d.content === 'string') out.push(...d.content.split('\n'))
  if (typeof d.log === 'string') out.push(...d.log.split('\n'))
  return out
}

function pushPackLine(line) {
  const s = messageForDisplay(String(line || '')).trim()
  if (!s || packSeen.has(s)) return
  packSeen.add(s)
  packLines.value.push(s)
}

function closePackDialog() {
  packOpen.value = false
  packRunning.value = false
  activeRequestId = ''
  if (packTimer) {
    clearTimeout(packTimer)
    packTimer = null
  }
  packSeen.clear()
}

async function pollPackStatus(name, rid) {
  const doneRe = /\b(finished|done|success|failed|error|complete|completed)\b/i
  const tick = async () => {
    if (!packRunning.value || activeRequestId !== rid) return
    try {
      const status = await checkPackStatus(rid)
      const lines = normalizePackLines(status.data)
      lines.forEach(pushPackLine)
      if (!status.ok) pushPackLine(`status check http ${status.status}`)
      const merged = lines.join(' ')
      if (doneRe.test(merged)) {
        packRunning.value = false
        return
      }
    } catch (e) {
      pushPackLine(e.message || 'status check failed')
    }
    packTimer = setTimeout(tick, 2000)
  }
  await tick()
}

defineExpose({ loadData })

onMounted(loadData)
</script>
