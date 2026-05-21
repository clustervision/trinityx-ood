<script setup lang="ts">

import { ref, onMounted, watch, computed } from 'vue'
import axios from 'axios'
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import { formatSWITCHNameDisplay, switchNameTitle } from '@/constants/switchName'

import SwitchModal from '@/components/SwitchModal.vue'
import DeleteModal from '@/components/DeleteModal.vue'


const app_url = window.APP_URL || import.meta.env.VITE_APP_URL;

const apiClient = axios.create({
  baseURL: String(app_url).replace(/\/$/, ''),
  headers: {Accept: 'application/json', 'X-Requested-With': 'XMLHttpRequest'}}
)

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error?.response?.data?.message || error?.response?.data?.error || error.message
    return Promise.reject(new Error(message))
  }
);

interface Switch {
  comment: string | null
  ipaddress: string | null
  ipaddress_ipv6: string | null
  macaddress: string | null
  name: string
  network: string | null
  oid: string | null
  read: string | null
  rw: string | null
  uplinkports: string | null
  vendor: string | null
}

const switches = ref<Switch[]>([]);
const switchList = ref<string[]>([]);
const errorMsg = ref('')
const httpError = ref('')
const helpOpen = ref(false)
const searchQuery = ref('')
const pageSize = ref(10)
const currentPage = ref(1)
const pageSizeOptions = [10, 25, 50, 100]
const regularColumns = [
  { field: 'name', label: 'Name' },
  { field: 'network', label: 'Network' },
  { field: 'oid', label: 'OID' },
  { field: 'read', label: 'READ' },
  { field: 'ipaddress', label: 'IP Address' },
]

const loading = ref(true);

type SwitchFormMode = 'add' | 'update' | 'clone'
type ModalType = SwitchFormMode | 'delete' | null

const activeModal = ref<ModalType>(null);
const switchFormMode = computed<SwitchFormMode>(() => {
  if (activeModal.value === 'add' || activeModal.value === 'update' || activeModal.value === 'clone') {
    return activeModal.value
  }
  return 'add'
})

const sortAsc = ref(true);
const totalColspan = computed(() => {
  const count = regularColumns.length + 1
  return count
})

type SortField = keyof Switch
const sortField = ref<SortField | ''>('')
const filteredRows = computed<Switch[]>(() => {
  let rows = switches.value
  const q = searchQuery.value.toLowerCase().trim()
  if (q) {
    rows = rows.filter((row) =>
      JSON.stringify(row).toLowerCase().includes(q)
    )
  }
  if (sortField.value) {
    const sf = sortField.value
    const asc = sortAsc.value
    rows = [...rows].sort((a, b) => {
      let va = ''
      let vb = ''
      va = String(a[sf] ?? '').toLowerCase()
      vb = String(b[sf] ?? '').toLowerCase()
      return asc ? va.localeCompare(vb) : vb.localeCompare(va)
    })
  }
  return rows
})

function toggleSort(field: string) {
  if (sortField.value === field) {
    sortAsc.value = !sortAsc.value
  } else {
    sortField.value = field as SortField
    sortAsc.value = true
  }
}

const totalPages = computed(() =>
  Math.max(1, Math.ceil(filteredRows.value.length / pageSize.value)),
)

const pagedRows = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredRows.value.slice(start, start + pageSize.value)
})


/** -----------------------
 * UI Actions
 * ---------------------- */
const selectedSwitch = ref<string>('');
const selectedSwitchData = ref<Switch | null>(null)
function openModal(type: ModalType, switchName?: string, switchData?: Switch) {
  selectedSwitch.value = switchName ?? ''
  activeModal.value = type
  selectedSwitchData.value = switchData || null
}

function closeModal() {
  activeModal.value = null
  selectedSwitch.value = ''
  selectedSwitchData.value = null
}

function onSaved() {
  closeModal()
  loadData()
}

async function loadData() {
  loading.value = true
  errorMsg.value = ''

  try {
    const { data } = await apiClient.get('/api/v1/switches')
    if (data.status === true && data.content?.config?.switch) {
      const raw = data.content.config.switch as Record<string, Switch>
      switches.value = Object.entries(raw).map(([name, value]) => ({
        ...value,
        name: value.name || name
      }))
      switchList.value = Object.keys(raw)
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
watch(searchQuery, () => (currentPage.value = 1))
defineExpose({ loadData })

onMounted(loadData)

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

</script>

<template>
  <div class="tx-app-layout">
    <AppHeader :app_url="app_url"/>
    <main class="tx-app-main">
      <div class="tx-shell tx-inventory-page">
        <div v-if="errorMsg" class="alert alert-danger" role="alert">{{ errorMsg }}</div>
        <div class="tx-header">
          <h2 class="tx-title">Switch</h2>
          <div class="tx-header-actions">
            <button type="button" class="tx-btn tx-btn-blue" @click="openModal('add')">Add Switch</button>
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
                <th v-for="(col) in regularColumns" :key="col.field" rowspan="2" class="tx-th-regular tx-th-sep-blue" @click="toggleSort(col.field)">
                  <span class="tx-th-label-clip">{{ col.label }}</span>
                  <span class="tx-sort-dt" aria-hidden="true">
                    <svg width="10" height="14" viewBox="0 0 10 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M5 0L9.33 5H0.67L5 0Z" fill="currentColor" opacity="0.35" />
                      <path d="M5 14L0.67 9H9.33L5 14Z" fill="currentColor" opacity="0.35" />
                    </svg>
                  </span>
                </th>
                <th rowspan="2" class="tx-th-regular tx-th-actions tx-th-sep-blue">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading"><td :colspan="totalColspan" style="text-align: center; padding: 2rem">Loading...</td></tr>
              <tr v-else-if="pagedRows.length === 0"><td :colspan="totalColspan" style="text-align: center; padding: 2rem; color: #999">{{ httpError }}</td></tr>
              <tr v-for="row in pagedRows" :key="row.name">
                <td v-for="(col) in regularColumns" :key="col.field" style="text-align: center;" class="tx-td-sep-blue">
                  <template v-if="col.field === 'name'">
                    <button type="button" class="tx-name-link" :title="switchNameTitle(row.name)" @click="openModal('update', canonicalName(row.name), row)">
                      <span class="tx-cell-ellipsis">{{ formatSWITCHNameDisplay(row.name) }}</span>
                    </button>
                  </template>
                  <template v-else-if="isEmpty((row as any)[col.field])">
                    <span class="tx-na-box">NOT AVAILABLE</span>
                  </template>
                  <template v-else>
                    <span class="tx-cell-ellipsis" :title="cellText((row as any)[col.field])">{{ cellText((row as any)[col.field]) }}</span>
                  </template>
                </td>
                <td class="tx-col-actions tx-td-sep-blue" >
                  <div class="tx-action-icons">
                    <button class="tx-icon-act flex items-center justify-center hover:opacity-70 transition-opacity" title="Copy" @click="openModal('clone', canonicalName(row.name), row)">
                        <svg width="26" height="26" viewBox="0 0 17 17" fill="none">
                            <g clip-path="url(#copy-clip)">
                                <path d="M7.78588 6.65973H6.43409V9.10212H4.00757V10.4853H6.43409V12.9374H7.78588V10.4853H10.2124V9.10212H7.78588V6.65973Z" fill="#4EBAE8" />
                                <path d="M14.8697 0.362732H4.91519C3.93598 0.362732 3.13829 1.17041 3.13829 2.16188V2.96472H2.13042C1.15121 2.96472 0.353516 3.7724 0.353516 4.76387V14.843C0.353516 15.8344 1.15121 16.6421 2.13042 16.6421H12.0849C13.0641 16.6421 13.8618 15.8344 13.8618 14.843V14.0401H14.8697C15.8489 14.0401 16.6466 13.2324 16.6466 12.241V2.16188C16.6466 1.17041 15.8489 0.362732 14.8697 0.362732ZM13.045 14.8381C13.045 15.3701 12.6151 15.8054 12.0897 15.8054H2.1352C1.60977 15.8054 1.17987 15.3701 1.17987 14.8381V4.75903C1.17987 4.22703 1.60977 3.79175 2.1352 3.79175H12.0897C12.6151 3.79175 13.045 4.22703 13.045 4.75903V14.8381ZM15.825 12.241C15.825 12.773 15.3951 13.2083 14.8697 13.2083H13.8618V4.75903C13.8618 3.76757 13.0641 2.95989 12.0849 2.95989H3.95987V2.15704C3.95987 1.62504 4.38976 1.18976 4.91519 1.18976H14.8697C15.3951 1.18976 15.825 1.62504 15.825 2.15704V12.2361V12.241Z" fill="#4EBAE8" />
                            </g>
                        </svg>
                    </button>
                    <button class="tx-icon-act flex items-center justify-center hover:opacity-70 transition-opacity" title="Delete" @click="openModal('delete', canonicalName(row.name))">
                        <svg width="23" height="27" viewBox="0 0 15 18" fill="none">
                            <g clip-path="url(#del-clip)">
                                <path d="M15 2.9983H12.0691V2.01601C12.0691 0.905158 11.1751 0.00515747 10.083 0.00515747H4.92719C3.83 0.00515747 2.94108 0.9103 2.94108 2.01601V2.9983H0V4.06287H1.78293V16.56C1.78293 17.3572 2.42296 18.0052 3.21029 18.0052H11.7897C12.577 18.0052 13.2171 17.3572 13.2171 16.56V4.06287H15V2.9983ZM12.1656 16.5549C12.1656 16.7657 11.998 16.9354 11.7897 16.9354H3.21029C3.00203 16.9354 2.83441 16.7657 2.83441 16.5549V4.21716H12.1656V16.5549ZM3.98239 2.01087C3.98239 1.4863 4.404 1.05944 4.92211 1.05944H10.0779C10.596 1.05944 11.0176 1.4863 11.0176 2.01087V2.99316H3.98239V2.01087Z" fill="#FF4416" />
                                <path d="M9.47847 6.30515H8.427V14.6931H9.47847V6.30515Z" fill="#FF4416" />
                                <path d="M6.57296 6.30515H5.52148V14.6931H6.57296V6.30515Z" fill="#FF4416" />
                            </g>
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

              <h2 id="help-title" class="tx-help-title">How to use this Switch app</h2>

              <div class="tx-help-content">
                <p class="tx-help-intro">
                  Use this app to view, add, update, clone, rename, and delete switch definitions stored in the Luna2 daemon.
                  A switch definition tells Luna how a physical or logical network switch is identified, reached, and associated with a Luna network.
                </p>

                <ul class="tx-help-list">
                  <li>
                    <strong>Switch Name</strong> — The logical name of the switch inside Luna.
                    This name is used when viewing, updating, cloning, renaming, or deleting the switch entry.
                    The name must be unique.
                  </li>

                  <li>
                    <strong>Read</strong> — The SNMP read community or read credential used for read-only switch queries.
                    This is typically used when Luna or an administrator needs to inspect switch information without changing configuration.
                  </li>

                  <li>
                    <strong>RW</strong> — The SNMP read-write community or write-capable credential.
                    This should be handled carefully because it may allow configuration changes on the switch.
                  </li>

                  <li>
                    <strong>OID</strong> — The Object Identifier used for SNMP-based switch queries.
                    An OID points to a specific value or object in the switch’s SNMP tree, for example system, interface, or port information.
                  </li>

                  <li>
                    <strong>Network</strong> — The Luna network associated with this switch.
                    In add mode, no network is selected by default. In update or clone mode, the app selects the source switch network if one is available.
                    The available values are loaded from the network API.
                  </li>

                  <li>
                    <strong>IP Address</strong> — The management IP address used to reach the switch.
                    This is normally the switch’s management interface address, not a node-facing data-plane address.
                  </li>

                  <li>
                    <strong>MAC Address</strong> — The switch MAC address, when known.
                    This can help identify the physical device, especially where multiple switches have similar names or IP ranges.
                  </li>

                  <li>
                    <strong>Vendor</strong> — The switch vendor or platform family, for example Cisco, Mellanox/NVIDIA, HPE, Dell, or another supported vendor.
                    This is useful for operational context and vendor-specific behaviour.
                  </li>

                  <li>
                    <strong>Uplink Ports</strong> — The switch ports that connect upstream to another switch, router, core fabric, or aggregation layer.
                    Enter them as a simple list such as <code>1,2,3,4</code> if your environment uses numeric port references.
                  </li>

                  <li>
                    <strong>Comment</strong> — Free-form notes for operational context.
                    Use this for physical location, rack position, uplink notes, vendor-specific quirks, maintenance remarks, or migration notes.
                    The comment editor can also load text from a file.
                  </li>

                  <li>
                    <strong>Advanced</strong> — Expands additional switch fields such as network, IP address, MAC address, vendor, uplink ports, and comment.
                    It is closed by default so the common fields stay clean and easy to edit.
                  </li>

                  <li>
                    <strong>Add</strong> — Creates a new switch entry.
                    The switch name must be unique.
                  </li>

                  <li>
                    <strong>Update</strong> — Updates an existing switch entry.
                    If you rename the switch, the app first performs the rename action and then saves the updated switch configuration.
                  </li>

                  <li>
                    <strong>Clone</strong> — Creates a new switch using an existing switch as the source.
                    The cloned switch is pre-filled with source values, but the clone name must be unique.
                  </li>

                  <li>
                    <strong>Delete</strong> — Removes a switch entry.
                    Before deleting, check whether the switch is still referenced by active networks, nodes, or operational documentation.
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </Teleport>
      </div>
    </main>

    <AppFooter :app_url="app_url"/>
  </div>

  <!-- Modals -->
  <SwitchModal v-if="activeModal === 'add' || activeModal === 'update' || activeModal === 'clone'" :mode="switchFormMode" :api-client="apiClient" :switch-list="switchList" :switch-data="selectedSwitchData || {}" :switch-name="selectedSwitch" @close="closeModal" @saved="onSaved" />
  <DeleteModal v-if="activeModal === 'delete'" :apiClient="apiClient" :switch-name="selectedSwitch" @close="closeModal" @deleted="onSaved" />

</template>
