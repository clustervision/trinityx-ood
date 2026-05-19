<script setup lang="ts">

import { ref, onMounted } from 'vue'
import axios from 'axios'
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import UpdateCluster from '@/components/UpdateCluster.vue'

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


interface Controller {
  hostname: string
  ipaddress: string
  luna_config: string
  serverport: number
  status: string | null  // null in response
  vendor: string | null  // null in response
}

interface Cluster {
  createnode_macashost: boolean
  createnode_ondemand: boolean
  debug: boolean
  domain_search: string | null
  forwardserver_ip: string | null
  name: string | null
  nameserver_ip: string | null
  nextnode_discover: boolean
  ntp_server: string | null
  packing_bootpause: boolean
  provision_fallback: string | null
  provision_method: string | null
  security: boolean
  technical_contacts: string | null
  user: string | null
  controller: Controller // single object, not array
  ha_controllers: Controller[]
}

const cluster = ref<Cluster | null>(null)
const ha_controllers = ref<Controller[]>([]);

const errorMsg = ref('')
const httpError = ref('')
const helpOpen = ref(false)

const loading = ref(true);
const activeModal = ref(false);

/** -----------------------
 * UI Actions
 * ---------------------- */
function openModal() {
  activeModal.value = true
}

function closeModal() {
  activeModal.value = false
}

function onSaved() {
  closeModal()
  loadData()
  // inventoryRef.value?.loadData?.()
}
const CLUSTER_STATIC_KEYS = new Set([
  'name', 'user', 'domain_search', 'nameserver_ip', 'forwardserver_ip',
  'ntp_server', 'technical_contacts', 'provision_method', 'provision_fallback',
  'debug', 'security', 'packing_bootpause', 'createnode_ondemand',
  'createnode_macashost', 'nextnode_discover', 'controller'
])
async function loadData() {
  loading.value = true
  errorMsg.value = ''

  try {
    const { data } = await apiClient.get('/api/v1/cluster')
    if (data.status === true && data.content?.config?.cluster) {
      const raw: Cluster = data.content.config.cluster
    cluster.value = raw
    ha_controllers.value = Object.entries(raw).filter(([key]) => !CLUSTER_STATIC_KEYS.has(key)).map(([, value]) => value as Controller)
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

function boolLabel(value: boolean | string | null | undefined): string {
  if (value === true || value === 'true') return 'TRUE'
  if (value === false || value === 'false') return 'FALSE'
  return 'NONE'
}

function boolBadge(value: boolean | string | null | undefined): string {
  if (value === true || value === 'true') return 'badge-true'
  if (value === false || value === 'false') return 'badge-false'
  return 'badge-none'
}

</script>

<template>
  <div class="tx-app-layout">
    <AppHeader :app_url="app_url"/>

    <main class="tx-app-main">

      <div class="tx-shell tx-inventory-page">
        <div v-if="errorMsg" class="alert alert-danger" role="alert">{{ errorMsg }}</div>

        <div class="tx-header">
          <h2 class="tx-title">Cluster</h2>
          <div class="tx-header-actions">
            <button type="button" class="tx-btn tx-btn-blue" @click="openModal()">Update Cluster</button>
            <button class="tx-btn tx-btn-help" title="Help" type="button" @click="helpOpen = true">?</button>
          </div>
        </div>

        <div class="tx-inventory-table-wrap">
          <!-- Form Content -->
            <div class="form-content">
                <!-- Row 1: NAME | TECHNICAL CONTACTS | USER | DEBUG -->
                <div class="form-row">
                    <div class="field field-name">
                        <div class="field-label">NAME:</div>
                        <div class="field-input">{{ cluster?.name }}</div>
                    </div>
                    <div class="form-row-inline">
                        <div class="field flex-1">
                            <div class="field-label">TECHNICAL CONTACTS:</div>
                            <div class="field-input">{{ cluster?.technical_contacts }}</div>
                        </div>
                        <div class="field flex-1">
                            <div class="field-label">USER:</div>
                            <div class="field-input">{{ cluster?.user }}</div>
                        </div>
                        <div class="field-bool">
                            <label class="field-label">DEBUG:</label>
                            <div role="status" aria-label="DEBUG: TRUE">
                              <span :class="['badge', boolBadge(cluster?.debug)]">{{ boolLabel(cluster?.debug) }}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Row 2: Controller (left) + Fields (right) -->
                <div class="form-row-two-col">


                    <!-- Controller Box -->
                  <div class="controller-box">
                  <div class="controller-box">

                    <!-- Primary controller -->
                    <div class="controller-header">CONTROLLER:</div>
                    <div class="controller-content">
                        <p>Hostname = {{ cluster?.controller.hostname }}</p>
                        <div class="inline-row">
                            <span>Status =</span>
                            <span :class="['badge', boolBadge(cluster?.controller.status)]">{{ boolLabel(cluster?.controller.status) }}</span>
                        </div>
                        <p>Server Port = {{ cluster?.controller.serverport }}</p>
                        <div class="inline-row">
                            <span>Vendor =</span>
                            <span :class="['badge', boolBadge(cluster?.controller.vendor)]">{{ boolLabel(cluster?.controller.vendor) }}</span>
                        </div>
                        <p>IPAddress = {{ cluster?.controller.ipaddress }}</p>
                        <p>Luna Config = {{ cluster?.controller.luna_config }}</p>
                    </div>

                    <!-- HA Controllers -->
                    <div v-for="node in ha_controllers" :key="node.hostname" class="controller-block">
                        <div class="controller-header">{{ node.hostname.toUpperCase() }}:</div>
                        <div class="controller-content">
                            <p>Hostname = {{ node.hostname }}</p>
                            <div class="inline-row">
                                <span>Status =</span>
                                <span :class="['badge', boolBadge(node.status)]">{{ boolLabel(node.status) }}</span>
                            </div>
                            <p>Server Port = {{ node.serverport }}</p>
                            <div class="inline-row">
                                <span>Vendor =</span>
                                <span :class="['badge', boolBadge(node.vendor)]">{{ boolLabel(node.vendor) }}</span>
                            </div>
                            <p>IPAddress = {{ node.ipaddress }}</p>
                            <p>Luna Config = {{ node.luna_config }}</p>
                        </div>
                    </div>
                </div>
                </div>

                    <!-- Right-side fields -->
                    <div class="right-fields">
                        <!-- PROVISIONING METHOD | PROVISION FALLBACK -->
                        <div class="form-row-inline">
                            <div class="field flex-1">
                                <div class="field-label">PROVISIONING METHOD:</div>
                                <div class="field-input">{{ cluster?.provision_method }}</div>
                            </div>
                            <div class="field flex-1">
                                <div class="field-label">PROVISION FALLBACK:</div>
                                <div class="field-input">{{ cluster?.provision_fallback }}</div>
                            </div>
                        </div>

                        <!-- DOMAIN SEARCH -->
                        <div class="field">
                            <div class="field-label">DOMAIN SEARCH:</div>
                            <div class="field-input">{{ cluster?.domain_search }}</div>
                        </div>

                        <!-- NAMESERVER IP -->
                        <div class="field">
                            <div class="field-label">NAMESERVER IP:</div>
                            <div class="field-input">{{ cluster?.nameserver_ip }}</div>
                        </div>

                        <!-- FORWARDSERVER IP -->
                        <div class="field">
                            <div class="field-label">FORWARDSERVER IP:</div>
                            <div class="field-input">{{ cluster?.forwardserver_ip }}</div>
                        </div>

                        <!-- NTP SERVER -->
                        <div class="field">
                            <div class="field-label">NTP SERVER:</div>
                            <div class="field-input">{{ cluster?.ntp_server }}</div>
                        </div>

                        <!-- CREATE NODE ON DEMAND | CREATE NODE ON MACASHOST (read-only status) -->
                        <div class="form-row-inline">
                            <div class="field-bool">
                                <label class="field-label">CREATE NODE ON DEMAND:</label>
                                <div role="status" aria-label="CREATE NODE ON DEMAND: TRUE">
                                    <span :class="['badge', boolBadge(cluster?.createnode_ondemand)]">{{ boolLabel(cluster?.createnode_ondemand) }}</span>
                                </div>
                            </div>
                            <div class="field-bool">
                                <label class="field-label">CREATE NODE ON MACASHOST:</label>
                                <div role="status" aria-label="CREATE NODE ON MACASHOST: NONE">
                                    <span :class="['badge', boolBadge(cluster?.createnode_macashost)]">{{ boolLabel(cluster?.createnode_macashost) }}</span>
                                </div>
                            </div>
                        </div>

                        <!-- NEXT NODE DISCOVER | SECURITY | PACKING BOOTPAUSE (read-only status) -->
                        <div class="form-row-inline">
                            <div class="field-bool">
                                <label class="field-label">NEXT NODE DISCOVER:</label>
                                <div role="status" aria-label="NEXT NODE DISCOVER: TRUE">
                                  <span :class="['badge', boolBadge(cluster?.nextnode_discover)]">{{ boolLabel(cluster?.nextnode_discover) }}</span>
                                </div>
                            </div>
                            <div class="field-bool">
                                <label class="field-label">SECURITY:</label>
                                <div role="status" aria-label="SECURITY: TRUE">
                                    <span :class="['badge', boolBadge(cluster?.security)]">{{ boolLabel(cluster?.security) }}</span>
                                </div>
                            </div>
                            <div class="field-bool">
                                <label class="field-label">PACKING BOOTPAUSE:</label>
                                <div role="status" aria-label="PACKING BOOTPAUSE: TRUE">
                                    <span :class="['badge', boolBadge(cluster?.packing_bootpause)]">{{ boolLabel(cluster?.packing_bootpause) }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <Teleport to="body">
          <div v-if="helpOpen" class="tx-modal-overlay" @mousedown.self="helpOpen = false">
            <div class="tx-help-dialog" role="dialog" aria-labelledby="help-title">
              <button type="button" class="tx-modal-x" aria-label="Close" @click="helpOpen = false">
                &times;
              </button>

              <h2 id="help-title" class="tx-help-title">How to use this Cluster app</h2>

              <div class="tx-help-content">
                <p class="tx-help-intro">
                  Use this app to view and update the Luna cluster configuration stored in the Luna2 daemon.
                  These fields map to <code>luna cluster change</code>.
                </p>

                <ul class="tx-help-list">
                  <li><strong>Cluster Name</strong> — The logical name of the Luna cluster.</li>
                  <li><strong>Controller IP</strong> — The IP address of the cluster controller. Maps to <code>--controller</code>.</li>
                  <li><strong>Controller Network</strong> — Network name used when changing the controller IP outside the current network scope. Maps to <code>--controller_network</code>.</li>
                  <li><strong>User</strong> — The cluster user value stored in Luna.</li>
                  <li><strong>NTP Server</strong> — Time synchronisation server used by the cluster. Important for logs, certificates, authentication, and troubleshooting.</li>
                  <li><strong>Name Server IP</strong> — DNS server used by cluster nodes. Often the controller IP.</li>
                  <li><strong>Forward Server IP</strong> — Upstream DNS resolver used to forward external DNS requests.</li>
                  <li><strong>Technical Contacts</strong> — Contact details for the people responsible for the cluster.</li>
                  <li><strong>Provision Method</strong> — Main node provisioning method, for example <code>torrent</code> or <code>http</code>.</li>
                  <li><strong>Provision Fallback</strong> — Backup provisioning method if the primary method is unavailable.</li>
                  <li><strong>Domain Search</strong> — Comma-separated DNS search domains, for example <code>cluster,ib,ipmi</code>.</li>
                  <li><strong>Packing Bootpause</strong> — Pauses node booting until OS image packing has finished.</li>
                  <li><strong>Create Node On Demand</strong> — Allows Luna to create node entries automatically when nodes are discovered.</li>
                  <li><strong>Create Node On MAC as Host</strong> — Uses the MAC address as hostname for newly created on-demand nodes.</li>
                  <li><strong>Next Node Discover</strong> — Enables discovery of the next node when adding or detecting new nodes.</li>
                  <li><strong>Security</strong> — Enables or disables Luna security mode. Change carefully.</li>
                  <li><strong>Debug</strong> — Enables verbose troubleshooting mode. Disable after investigation.</li>
                  <li><strong>Update</strong> — Saves the changed values to the Luna2 daemon.</li>
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
  <UpdateCluster v-if="activeModal === true" :apiClient="apiClient" :cluster="cluster" @close="closeModal" @saved="onSaved" />
</template>
