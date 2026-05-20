<script setup lang="ts">

import { ref, onMounted, watch, computed } from 'vue'
import axios from 'axios'
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import { formatBMCNameDisplay, bmcNameTitle } from '@/constants/bmcName'

import BmcSetupModal from '@/components/BmcSetupModal.vue'
import MemberModal from './components/MemberModal.vue'
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

interface BMCSetup {
  comment: string | null
  mgmtchannel: number
  name: string
  netchannel: number
  password: string | null
  unmanaged_bmc_users: string | null
  userid: number
  username: string | null
}

const bmc_setups = ref<BMCSetup[]>([]);
const bmcList = ref<string[]>([]);
const errorMsg = ref('')
const httpError = ref('')
const helpOpen = ref(false)
const searchQuery = ref('')
const pageSize = ref(10)
const currentPage = ref(1)
const pageSizeOptions = [10, 25, 50, 100]
const regularColumns = [
  { field: 'name', label: 'Name' },
  { field: 'userid', label: 'User ID' },
  { field: 'netchannel', label: 'Net Channel' },
  { field: 'unmanaged_bmc_users', label: 'Unmanaged BMC Users' },
]

const loading = ref(true);

type BmcFormMode = 'add' | 'update' | 'clone'
type ModalType = BmcFormMode | 'member' | 'delete' | null

const activeModal = ref<ModalType>(null);
const bmcFormMode = computed<BmcFormMode>(() => {
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

type SortField = keyof BMCSetup
const sortField = ref<SortField | ''>('')
const filteredRows = computed<BMCSetup[]>(() => {
  let rows = bmc_setups.value
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
const selectedBMC = ref<string>('');
const selectedBMCData = ref<BMCSetup | null>(null)
function openModal(type: ModalType, bmcName?: string, bmc?: BMCSetup) {
  selectedBMC.value = bmcName ?? ''
  activeModal.value = type
  selectedBMCData.value = bmc || null
}

function closeModal() {
  activeModal.value = null
  selectedBMC.value = ''
  selectedBMCData.value = null
}

function onSaved() {
  closeModal()
  loadData()
}

async function loadData() {
  loading.value = true
  errorMsg.value = ''

  try {
    const { data } = await apiClient.get('/api/v1/bmcsetups')
    if (data.status === true && data.content?.config?.bmcsetup) {
      const raw = data.content.config.bmcsetup as Record<string, BMCSetup>
      bmc_setups.value = Object.entries(raw).map(([name, value]) => ({
        ...value,
        name: value.name || name
      }))
      bmcList.value = Object.keys(raw)
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
          <h2 class="tx-title">BMC Setup</h2>
          <div class="tx-header-actions">
            <button type="button" class="tx-btn tx-btn-blue" @click="openModal('add')">Add BMC Setup</button>
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
                    <button type="button" class="tx-name-link" :title="bmcNameTitle(row.name)" @click="openModal('update', canonicalName(row.name), row)">
                      <span class="tx-cell-ellipsis">{{ formatBMCNameDisplay(row.name) }}</span>
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
                    <button class="tx-icon-act flex items-center justify-center hover:opacity-70 transition-opacity" title="Delete" @click="openModal('delete', canonicalName(row.name))">
                        <svg width="23" height="27" viewBox="0 0 15 18" fill="none">
                            <g clip-path="url(#del-clip)">
                                <path d="M15 2.9983H12.0691V2.01601C12.0691 0.905158 11.1751 0.00515747 10.083 0.00515747H4.92719C3.83 0.00515747 2.94108 0.9103 2.94108 2.01601V2.9983H0V4.06287H1.78293V16.56C1.78293 17.3572 2.42296 18.0052 3.21029 18.0052H11.7897C12.577 18.0052 13.2171 17.3572 13.2171 16.56V4.06287H15V2.9983ZM12.1656 16.5549C12.1656 16.7657 11.998 16.9354 11.7897 16.9354H3.21029C3.00203 16.9354 2.83441 16.7657 2.83441 16.5549V4.21716H12.1656V16.5549ZM3.98239 2.01087C3.98239 1.4863 4.404 1.05944 4.92211 1.05944H10.0779C10.596 1.05944 11.0176 1.4863 11.0176 2.01087V2.99316H3.98239V2.01087Z" fill="#FF4416" />
                                <path d="M9.47847 6.30515H8.427V14.6931H9.47847V6.30515Z" fill="#FF4416" />
                                <path d="M6.57296 6.30515H5.52148V14.6931H6.57296V6.30515Z" fill="#FF4416" />
                            </g>
                        </svg>
                    </button>
                    <button class="tx-icon-act flex items-center justify-center hover:opacity-70 transition-opacity" title="Member" @click="openModal('member', canonicalName(row.name))">
                        <svg width="26" height="26" viewBox="0 0 17 17" fill="none">
                            <g clip-path="url(#edit-clip)">
                                <path d="M13.5999 4.58514H3.3999V5.96457H13.5999V4.58514Z" fill="#8971D9" />
                                <path d="M13.5999 7.81027H3.3999V9.1897H13.5999V7.81027Z" fill="#8971D9" />
                                <path d="M13.5999 11.0354H3.3999V12.4149H13.5999V11.0354Z" fill="#8971D9" />
                                <path d="M14.9843 17H2.01571C0.903429 17 0 16.0966 0 14.9843V2.01571C0 0.903429 0.903429 0 2.01571 0H14.9843C16.0966 0 17 0.903429 17 2.01571V14.9843C17 16.0966 16.0966 17 14.9843 17ZM2.01571 0.932571C1.41829 0.932571 0.927714 1.41829 0.927714 2.02057V14.9891C0.927714 15.5866 1.41343 16.0771 2.01571 16.0771H14.9843C15.5817 16.0771 16.0723 15.5914 16.0723 14.9891V2.01571C16.0723 1.41829 15.5866 0.927714 14.9843 0.927714H2.01571V0.932571Z" fill="#8971D9" />
                            </g>
                        </svg>
                    </button>
                    <button class="tx-icon-act flex items-center justify-center hover:opacity-70 transition-opacity" title="Copy" @click="openModal('clone', canonicalName(row.name), row)">
                        <svg width="26" height="26" viewBox="0 0 17 17" fill="none">
                            <g clip-path="url(#copy-clip)">
                                <path d="M7.78588 6.65973H6.43409V9.10212H4.00757V10.4853H6.43409V12.9374H7.78588V10.4853H10.2124V9.10212H7.78588V6.65973Z" fill="#4EBAE8" />
                                <path d="M14.8697 0.362732H4.91519C3.93598 0.362732 3.13829 1.17041 3.13829 2.16188V2.96472H2.13042C1.15121 2.96472 0.353516 3.7724 0.353516 4.76387V14.843C0.353516 15.8344 1.15121 16.6421 2.13042 16.6421H12.0849C13.0641 16.6421 13.8618 15.8344 13.8618 14.843V14.0401H14.8697C15.8489 14.0401 16.6466 13.2324 16.6466 12.241V2.16188C16.6466 1.17041 15.8489 0.362732 14.8697 0.362732ZM13.045 14.8381C13.045 15.3701 12.6151 15.8054 12.0897 15.8054H2.1352C1.60977 15.8054 1.17987 15.3701 1.17987 14.8381V4.75903C1.17987 4.22703 1.60977 3.79175 2.1352 3.79175H12.0897C12.6151 3.79175 13.045 4.22703 13.045 4.75903V14.8381ZM15.825 12.241C15.825 12.773 15.3951 13.2083 14.8697 13.2083H13.8618V4.75903C13.8618 3.76757 13.0641 2.95989 12.0849 2.95989H3.95987V2.15704C3.95987 1.62504 4.38976 1.18976 4.91519 1.18976H14.8697C15.3951 1.18976 15.825 1.62504 15.825 2.15704V12.2361V12.241Z" fill="#4EBAE8" />
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
              <button type="button" class="tx-modal-x" aria-label="Close" @click="helpOpen = false">&times;</button>
              <h2 id="help-title" class="tx-help-title">How to use this BMC Setup app</h2>

              <div class="tx-help-content">
                <p class="tx-help-intro">
                  Use this app to view, add, update, clone, rename, and delete BMC Setup profiles stored in the Luna2 daemon.
                  A BMC Setup defines how Luna should access a node's Baseboard Management Controller for out-of-band management.
                </p>

                <ul class="tx-help-list">
                  <li>
                    <strong>BMC Setup Name</strong> - The logical profile name for this BMC configuration.
                    Nodes can be linked to this setup so Luna knows which BMC credentials and channel settings to use.
                  </li>

                  <li>
                    <strong>User ID</strong> - The numeric BMC/IPMI user slot ID.
                    Many BMCs store users in numbered slots, for example <code>2</code> for an administrator user.
                    This is not the username itself; it is the BMC's internal user index.
                  </li>

                  <li>
                    <strong>User Name</strong> - The login name used to access the BMC.
                    This is usually an IPMI or Redfish-capable BMC account, such as <code>admin</code>.
                  </li>

                  <li>
                    <strong>Password</strong> - The password for the BMC user.
                    Handle this carefully: this account may allow power control, remote console access, and hardware-level management.
                  </li>

                  <li>
                    <strong>Network Channel</strong> - The BMC/IPMI network channel number used for LAN communication.
                    In IPMI, a “channel” is a logical interface inside the BMC. The network channel usually points to the LAN-capable BMC interface.
                    Typical values are vendor-dependent, but <code>1</code> is common on many systems.
                  </li>

                  <li>
                    <strong>Management Channel</strong> - The channel used for BMC management operations such as user access, privilege settings, or management commands.
                    On many platforms this may be the same as the network channel, but some vendors expose multiple channels for different management paths.
                  </li>

                  <li>
                    <strong>Uplink / BMC Network Port</strong> - The physical or logical network path used to reach the BMC from the management network.
                    This is usually the dedicated BMC/iDRAC/iLO/IPMI port, or a shared motherboard NIC if the server is configured for shared BMC networking.
                    The app stores channel values, not the physical switch port itself.
                  </li>

                  <li>
                    <strong>Unmanaged BMC Users</strong> - BMC users that should not be managed or overwritten by this setup.
                    Use this when certain accounts are maintained manually, by the hardware vendor, or by another operational process.
                  </li>

                  <li>
                    <strong>Comment</strong> - Free-form notes for this BMC Setup.
                    Use it for operational context, exceptions, vendor-specific notes, shared-NIC behaviour, channel assumptions, or migration remarks.
                    The comment editor can also load text from a file.
                  </li>

                  <li>
                    <strong>Members</strong> - Shows the nodes currently linked to this BMC Setup.
                    This helps confirm which nodes will be affected when a profile is updated.
                  </li>

                  <li>
                    <strong>Add</strong> - Creates a new BMC Setup.
                    The name must be unique.
                  </li>

                  <li>
                    <strong>Update</strong> - Updates an existing BMC Setup.
                    If you rename the setup, the app first performs a rename action and then saves the updated configuration.
                  </li>

                  <li>
                    <strong>Clone</strong> - Creates a new BMC Setup using an existing setup as the source.
                    The cloned setup is pre-filled with the source values, but the clone name must be unique.
                  </li>

                  <li>
                    <strong>Delete</strong> - Removes a BMC Setup.
                    Before deleting, check its members so you do not remove a profile still used by active nodes.
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
  <BmcSetupModal v-if="activeModal === 'add' || activeModal === 'update' || activeModal === 'clone'" :mode="bmcFormMode" :api-client="apiClient" :bmc-list="bmcList" :bmc-data="selectedBMCData || {}" :bmc-name="selectedBMC" @close="closeModal" @saved="onSaved" />
  <MemberModal v-if="activeModal === 'member'" :api-client="apiClient" :bmc-name="selectedBMC" @close="closeModal" />
  <DeleteModal v-if="activeModal === 'delete'" :apiClient="apiClient" :bmc-name="selectedBMC" @close="closeModal" @deleted="onSaved" />

</template>
