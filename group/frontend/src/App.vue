<script setup lang="ts">

import { ref, computed, onMounted, watch } from 'vue'

import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import EditGroupModal from '@/components/EditGroupModal.vue'
import AddGroupModal from '@/components/AddGroupModal.vue'
import CloneGroupModal from '@/components/CloneGroupModal.vue'
import PushOsModal from '@/components/PushOsModal.vue'
import DeleteConfirmModal from '@/components/DeleteConfirmModal.vue'
import { fetchGroups } from '@/services/api'
import { formatGroupNameDisplay, groupNameTitle } from '@/constants/groupName'
import { punAppAssetUrl } from '@/utils/publicAssets'

type ModalType = 'add' | 'edit' | 'clone' | 'ospush' | 'delete' | null
type GroupMap = Record<string, Group>

interface InventoryRefType {
  loadData?: () => void
}

interface InterfaceItem {
  interface: string
  network: string
}

interface Group {
  _override: boolean
  bmcsetupname: string | null
  bootmenu: boolean
  comment: string | null
  domain: string | null
  interfaces: InterfaceItem[]
  kerneloptions: string | null
  name: string
  netboot: boolean
  osimage: string | null
  osimagetagid: string | null
  partscript: string
  postscript: string
  prescript: string
  provision_fallback: string | null
  provision_interface: string | null
  provision_method: string | null
  roles: string | null
  scripts: string | null
  setupbmc: boolean
  unmanaged_bmc_users: string | null
}



const app_url = window.APP_URL || import.meta.env.VITE_APP_URL
const iconClone = punAppAssetUrl('icons/icon-clone.png')
const iconOspush = punAppAssetUrl('icons/icon-ospush.png')
const iconDelete = punAppAssetUrl('icons/icon-delete.png')
const errorMsg = ref('')
const httpError = ref('')
const helpOpen = ref(false)
const searchQuery = ref('')
const pageSize = ref(10)
const currentPage = ref(1)
const pageSizeOptions = [10, 25, 50, 100]
const regularColumns = [
  { field: 'name', label: 'Name' },
  { field: 'bmcsetupname', label: 'BMC Setup' },
  { field: 'osimage', label: 'OS IMage' },
  { field: 'scripts', label: 'Scripts' },
  { field: 'roles', label: 'Roles' },
]
const loading = ref(true);
const groups = ref<Group[]>([]);
const groupList = ref<string[]>([]);
const activeModal = ref<ModalType>(null);
const selectedGroup = ref<string>('');
// const sortField = ref<string>('')
const sortAsc = ref(true);
const inventoryRef = ref<InventoryRefType | null>(null);

const hasInterfaces = computed(() => groups.value.some((g) => g.interfaces?.length > 0))

const totalColspan = computed(() => {
  let count = regularColumns.length + 1
  if (hasInterfaces.value) count += 2
  return count
})

function ifaceSortKey(row: Group, key: 'interface' | 'network') {
  return (row.interfaces || []).map((i) => (i[key] || '').toLowerCase()).join('|')
}


type SortField = keyof Group | 'iface_name' | 'iface_network'
const sortField = ref<SortField | ''>('')
const filteredRows = computed<Group[]>(() => {
  let rows = groups.value

  const q = searchQuery.value.toLowerCase().trim()
  if (q) {
    rows = rows.filter((row) =>
      JSON.stringify(row).toLowerCase().includes(q)
    )
  }

  if (sortField.value) {
    // const sf = sortField.value as keyof Group
    const sf = sortField.value
    const asc = sortAsc.value

    rows = [...rows].sort((a, b) => {
      let va = ''
      let vb = ''

      if (sf === 'iface_name') {
        va = ifaceSortKey(a, 'interface')
        vb = ifaceSortKey(b, 'interface')
      } else if (sf === 'iface_network') {
        va = ifaceSortKey(a, 'network')
        vb = ifaceSortKey(b, 'network')
      } else {
        va = String(a[sf] ?? '').toLowerCase()
        vb = String(b[sf] ?? '').toLowerCase()
      }

      return asc ? va.localeCompare(vb) : vb.localeCompare(va)
    })
  }

  return rows
})



const totalPages = computed(() =>
  Math.max(1, Math.ceil(filteredRows.value.length / pageSize.value)),
)

const pagedRows = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredRows.value.slice(start, start + pageSize.value)
})

watch(searchQuery, () => (currentPage.value = 1))
watch(pageSize, () => (currentPage.value = 1))

watch([filteredRows, totalPages], () => {
  if (currentPage.value > totalPages.value) {
    currentPage.value = totalPages.value
  }
})
function toggleSort(field: string) {
  if (sortField.value === field) {
    sortAsc.value = !sortAsc.value
  } else {
    sortField.value = field as SortField
    sortAsc.value = true
  }
}

function isEmpty(val: unknown) {
  return val === null || val === undefined || val === ''
}

function cellText(val: unknown) {
  if (typeof val === 'boolean') return val ? 'Yes' : 'No'
  return String(val ?? '')
}

function canonicalName(name: string) {
  return name
}


/** -----------------------
 * UI Actions
 * ---------------------- */
const selectedGroupData = ref<Group | null>(null)
function openModal(type: ModalType, groupName?: string, group?: Group) {
  selectedGroup.value = groupName ?? ''
  activeModal.value = type
  selectedGroupData.value = group || null
}

function closeModal() {
  activeModal.value = null
  selectedGroup.value = ''
}

function onSaved() {
  closeModal()
  loadData()
  inventoryRef.value?.loadData?.()
}

async function loadData() {
  loading.value = true
  errorMsg.value = ''

  try {
    const data = await fetchGroups()
    if (data.status === true && data.content?.config?.group) {
      const groups_data: GroupMap = data.content.config.group
      groups.value = Object.values(groups_data)
      for (const key in groups_data) { groupList.value.push(key) }

    } else {
      if (data.status_code === 404) {
        httpError.value = data.content?.message
      } else {
        errorMsg.value = data.content?.message
      }
    }
  } catch (err: unknown) {
    if (err instanceof Error) {
      errorMsg.value = err.message
    } else {
      errorMsg.value = 'Unknown error occurred'
    }
  } finally {
    loading.value = false
  }
}
defineExpose({ loadData })

onMounted(loadData)
// console.log(filteredRows.value);
</script>

<template>
  <div class="tx-app-layout">
    <AppHeader :app_url="app_url"/>

    <main class="tx-app-main">

      <div class="tx-shell tx-inventory-page">
        <div v-if="errorMsg" class="alert alert-danger" role="alert">{{ errorMsg }}</div>

        <div class="tx-header">
          <h2 class="tx-title">Groups</h2>
          <div class="tx-header-actions">
            <button type="button" class="tx-btn tx-btn-blue" @click="openModal('add')">Add Group</button>
            <button class="tx-btn tx-btn-help" title="Help" type="button" @click="helpOpen = true">?</button>
            <div class="tx-inline-search">
              <label class="tx-inline-search-label" for="txManualSearch">Search:</label>
              <input id="txManualSearch" v-model="searchQuery" type="search" class="tx-inline-search-input" autocomplete="off" />
            </div>
          </div>
        </div>

        <div class="tx-inventory-table-wrap">
          <table class="tx-inventory-table">
            <thead>
              <tr>
                <th v-for="(col, cIdx) in regularColumns" :key="col.field" rowspan="2" class="tx-th-regular" :class="{'tx-th-sep-blue': cIdx > 0, 'tx-th-sep-before-iface': hasInterfaces && cIdx === regularColumns.length - 1,}" :title="col.label" @click="toggleSort(col.field)">
                  <span class="tx-th-label-clip">{{ col.label }}</span>
                  <span class="tx-sort-dt" aria-hidden="true">
                    <svg width="10" height="14" viewBox="0 0 10 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M5 0L9.33 5H0.67L5 0Z" fill="currentColor" opacity="0.35" />
                      <path d="M5 14L0.67 9H9.33L5 14Z" fill="currentColor" opacity="0.35" />
                    </svg>
                  </span>
                </th>
                <th v-if="hasInterfaces" colspan="2" rowspan="1" class="tx-iface-header-main">Interfaces</th>
                <th rowspan="2" class="tx-th-regular tx-th-actions" :class="{ 'tx-th-sep-orange-right': hasInterfaces, 'tx-th-sep-blue': !hasInterfaces }">Actions</th>
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
                <th class="tx-iface-sub tx-iface-sub-network" @click.stop="toggleSort('iface_network')">
                  <span class="tx-th-label-clip">Network</span>
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
                <td :colspan="totalColspan" style="text-align: center; padding: 2rem">Loading...</td>
              </tr>
              <tr v-else-if="pagedRows.length === 0">
                <td :colspan="totalColspan" style="text-align: center; padding: 2rem; color: #999">{{ httpError }}</td>
              </tr>
              <tr v-for="row in pagedRows" :key="row.name">
                <!-- {{ row }} -->
                <!-- {{ regularColumns }} -->
                <td v-for="(col, cIdx) in regularColumns" :key="col.field" :class="{'tx-td-sep-blue': cIdx > 0, 'tx-td-sep-before-iface': hasInterfaces && cIdx === regularColumns.length - 1, 'tx-td-name': col.field === 'name',}">
                  <template v-if="col.field === 'name'">
                    <button type="button" class="tx-name-link" :title="groupNameTitle(row.name)" @click="openModal('edit', canonicalName(row.name), row)">
                      <span class="tx-cell-ellipsis">{{ formatGroupNameDisplay(row.name) }}</span>
                    </button>
                  </template>
                  <template v-else-if="isEmpty((row as any)[col.field])">
                    <span class="tx-na-box">NOT AVAILABLE</span>
                  </template>
                  <template v-else>
                    <span class="tx-cell-ellipsis" :title="cellText((row as any)[col.field])">{{ cellText((row as any)[col.field]) }}</span>
                  </template>
                </td>
                <td v-if="hasInterfaces" class="tx-iface-cell tx-iface-name tx-td-iface-edge">
                  <div v-for="(iface, iIdx) in row.interfaces || []" :key="'n-' + iIdx" class="tx-iface-entry tx-cell-ellipsis" :title="String(iface.interface || '')">
                    {{ iface.interface || '' }}
                  </div>
                </td>
                <td v-if="hasInterfaces" class="tx-iface-cell tx-iface-network tx-td-iface-between">
                  <div v-for="(iface, iIdx) in row.interfaces || []" :key="'nw-' + iIdx" class="tx-iface-entry tx-cell-ellipsis" :title="String(iface.network || '')">
                    {{ iface.network || '' }}
                  </div>
                </td>
                <td class="tx-col-actions" :class="{ 'tx-td-sep-orange-right': hasInterfaces, 'tx-td-sep-blue': !hasInterfaces }">
                  <div class="tx-action-icons">
                    <button type="button" class="tx-icon-act tx-icon-clone" title="Clone" @click="openModal('clone', canonicalName(row.name), row)">
                      <img :src="iconClone" alt="Clone" width="28" height="28" onerror="this.style.display = 'none' this.nextElementSibling.style.display = 'inline'" />
                      <svg style="display: none" viewBox="0 0 24 24" width="28" height="28" fill="currentColor">
                        <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z" />
                      </svg>
                    </button>
                    <button type="button" class="tx-icon-act tx-icon-ospush" title="OS Push" @click="openModal('ospush', canonicalName(row.name))">
                      <img :src="iconOspush" alt="OS Push" width="28" height="28" onerror="this.style.display = 'none' this.nextElementSibling.style.display = 'inline'"/>
                      <svg style="display: none" viewBox="0 0 24 24" width="28" height="28" fill="currentColor">
                        <path d="M9 16h6v-6h4l-7-7-7 7h4v6zm-4 2h14v2H5v-2z" />
                      </svg>
                    </button>
                    <button type="button" class="tx-icon-act tx-icon-danger" title="Delete" @click="openModal('delete', canonicalName(row.name))">
                      <img :src="iconDelete" alt="Delete" width="28" height="28" onerror="this.style.display = 'none' this.nextElementSibling.style.display = 'inline'" />
                      <svg style="display: none" viewBox="0 0 24 24" width="28" height="28" fill="currentColor">
                        <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z" />
                      </svg>
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
            <button type="button" class="tx-paging-arrow" :disabled="currentPage <= 1" aria-label="Previous page" @click="currentPage--">&lt;</button>
            <span class="tx-paging-current">{{ currentPage }}</span>
            <button type="button" class="tx-paging-arrow" :disabled="currentPage >= totalPages" aria-label="Next page" @click="currentPage++">&gt;</button>
          </div>
        </div>

        <Teleport to="body">
          <div v-if="helpOpen" class="tx-modal-overlay" @mousedown.self="helpOpen = false">
            <div class="tx-help-dialog" role="dialog" aria-labelledby="help-title">
              <button type="button" class="tx-modal-x" aria-label="Close" @click="helpOpen = false">
                &times;
              </button>
              <h2 id="help-title" class="tx-help-title">How to use this app</h2>
              <ul class="tx-help-list">
                <li><strong>Add Group</strong> — Use the button to create a new group.</li>
                <li><strong>Edit</strong> — Click an underlined group name.</li>
                <li><strong>Clone / OS Push / Delete</strong> — Use the icons in the Actions column.</li>
                <li><strong>Search</strong> — Filter the table as you type.</li>
                <li><strong>Sort</strong> — Click a column header (or Name / Network under Interfaces) to sort; click again to reverse. </li>
              </ul>
            </div>
          </div>
        </Teleport>
      </div>
    </main>

    <AppFooter :app_url="app_url"/>
  </div>

  <!-- Modals -->
  <EditGroupModal v-if="activeModal === 'edit'" :groupList="groupList" :group="selectedGroupData || {}" :group-name="selectedGroup" @close="closeModal" @saved="onSaved" />

  <AddGroupModal v-if="activeModal === 'add'" :groupList="groupList" @close="closeModal" @saved="onSaved" />

  <CloneGroupModal v-if="activeModal === 'clone'" :groupList="groupList" :group="selectedGroupData || {}" :group-name="selectedGroup" @close="closeModal" @saved="onSaved" />

  <PushOsModal v-if="activeModal === 'ospush'" :group-name="selectedGroup" :group="selectedGroupData || {}" @close="closeModal" @saved="onSaved" />

  <DeleteConfirmModal v-if="activeModal === 'delete'" :group-name="selectedGroup" @close="closeModal" @deleted="onSaved" />
</template>
