<script setup lang="ts">

import { ref, onMounted, watch, reactive } from 'vue'
import type { AxiosInstance } from 'axios'
import BaseModal from './BaseModal.vue'

interface Controller {
  hostname: string
  ipaddress: string
  luna_config: string
  serverport: number
  status: string | null  // null in response
  vendor: string | null  // null in response
}

interface Cluster {
  name: string | null
  user: string | null
  domain_search: string | null
  nameserver_ip: string | null
  forwardserver_ip: string | null
  ntp_server: string | null
  technical_contacts: string | null
  provision_method: string | null
  provision_fallback: string | null
  debug: boolean
  security: boolean
  packing_bootpause: boolean
  createnode_ondemand: boolean
  createnode_macashost: boolean
  nextnode_discover: boolean
  controller: Controller

  // Allows keys such as "availability-one" and "availability-two"
  [key: string]: unknown
}

const props = defineProps<{
  apiClient: AxiosInstance
  cluster: Cluster | null
}>()

const emit = defineEmits(['close', 'saved'])



const loading = ref(false)
const errorMsg = ref('')
const successMsg = ref('')
const fatalError = ref(false)


const emptyController = (): Controller => ({
  hostname: '',
  ipaddress: '',
  luna_config: '',
  serverport: 7050,
  status: null,
  vendor: null
})

const form = reactive({
  name: '',
  user: '',
  domain_search: '',
  nameserver_ip: '',
  forwardserver_ip: '',
  ntp_server: '',
  technical_contacts: '',
  provision_method: '',
  provision_fallback: '',
  debug: false,
  security: false,
  packing_bootpause: false,
  createnode_ondemand: false,
  createnode_macashost: false,
  nextnode_discover: false,
  controller: emptyController(),
  availability_controllers: {} as Record<string, Controller>
})

function isController(value: unknown): value is Controller {
  return (
    typeof value === 'object' &&
    value !== null &&
    'hostname' in value &&
    'ipaddress' in value &&
    'serverport' in value &&
    'luna_config' in value
  )
}

watch(
  () => props.cluster,
  (cluster) => {
    form.name = cluster?.name ?? ''
    form.user = cluster?.user ?? ''
    form.domain_search = cluster?.domain_search ?? ''
    form.nameserver_ip = cluster?.nameserver_ip ?? ''
    form.forwardserver_ip = cluster?.forwardserver_ip ?? ''
    form.ntp_server = cluster?.ntp_server ?? ''
    form.technical_contacts = cluster?.technical_contacts ?? ''
    form.provision_method = cluster?.provision_method ?? ''
    form.provision_fallback = cluster?.provision_fallback ?? ''

    form.debug = cluster?.debug ?? false
    form.security = cluster?.security ?? false
    form.packing_bootpause = cluster?.packing_bootpause ?? false
    form.createnode_ondemand = cluster?.createnode_ondemand ?? false
    form.createnode_macashost = cluster?.createnode_macashost ?? false
    form.nextnode_discover = cluster?.nextnode_discover ?? false

    Object.assign(form.controller, cluster?.controller ?? emptyController())

    form.availability_controllers = {}

    if (cluster) {
      for (const [key, value] of Object.entries(cluster)) {
        if (key !== 'controller' && key.startsWith('availability-') && isController(value)) {
          form.availability_controllers[key] = { ...value }
        }
      }
    }
  },
  { immediate: true }
)


onMounted(async () => {


})
function emptyToNull(value: string): string | null {
  return value === '' ? null : value
}

function buildPayload() {
  const clusterPayload: Record<string, unknown> = {
    name: form.name,
    user: emptyToNull(form.user),
    domain_search: emptyToNull(form.domain_search),
    nameserver_ip: emptyToNull(form.nameserver_ip),
    forwardserver_ip: emptyToNull(form.forwardserver_ip),
    ntp_server: emptyToNull(form.ntp_server),
    technical_contacts: emptyToNull(form.technical_contacts),
    provision_method: emptyToNull(form.provision_method),
    provision_fallback: emptyToNull(form.provision_fallback),
    debug: form.debug,
    security: form.security,
    packing_bootpause: form.packing_bootpause,
    createnode_ondemand: form.createnode_ondemand,
    createnode_macashost: form.createnode_macashost,
    nextnode_discover: form.nextnode_discover,
    controller: { ...form.controller }
  }

  for (const [key, controller] of Object.entries(form.availability_controllers)) {
    clusterPayload[key] = { ...controller }
  }

  return {
    config: {
      cluster: clusterPayload
    }
  }
}

async function onSubmit() {
  errorMsg.value = ''
  successMsg.value = ''

  try {
    const payload = buildPayload()

    const { data } = await props.apiClient.put('/api/v1/update', payload)

    if (data.status === true) {
      successMsg.value = data.content?.message || 'Cluster updated successfully.'

      setTimeout(() => {
        emit('saved')
        emit('close')
      }, 1500)

      return
    }

    errorMsg.value = data.content?.message || 'Update failed.'
  } catch (err: unknown) {
    errorMsg.value = err instanceof Error ? err.message : 'Unknown error occurred.'
  }
}
</script>


<template>
  <BaseModal size="large" @close="$emit('close')">

    <div class="tx-form-page">
      <div v-if="errorMsg" class="alert alert-danger" role="alert">{{ errorMsg }}</div>
      <div v-if="successMsg" class="alert alert-success" role="alert">{{ successMsg }}</div>
      <p v-if="loading" class="tx-loading">Loading...</p>
      <template v-if="!loading && !fatalError">
        <div class="tx-header">
          <h2 class="tx-title"> Update Cluster</h2>
        </div>
        <form id="clusterForm" @submit.prevent="onSubmit">
          <div class="left-column">
            <!-- NAME field with mandatory indicator -->
            <div class="text-field mandatory">
              <label-part>
                <label>NAME:</label>
              </label-part>
              <input type="text" id="name" v-model="form.name">
              <svg class="edit-icon" viewBox="0 0 25 25" fill="none" xmlns="http://www.w3.org/2000/svg">
                <g clip-path="url(#clip0)">
                  <path d="M6.22774 17.4148C5.80661 17.4148 5.39292 17.2488 5.0907 16.9466C4.72903 16.5849 4.5581 16.0697 4.63489 15.5643L5.10556 12.4777L12.1235 5.45978L16.5627 9.89894L9.54472 16.9169L6.47546 17.3999C6.39371 17.4123 6.30949 17.4197 6.22774 17.4197V17.4148ZM6.96595 13.4166L6.67116 15.3587L8.60091 15.0565L13.7609 9.89646L12.1235 8.25902L6.96595 13.4166Z" fill="#5376EA"/>
                  <path d="M15.1284 11.3308L10.6892 6.8916L12.3192 5.2616C13.216 4.36485 14.675 4.36485 15.5718 5.2616L16.7609 6.45066C17.6576 7.34741 17.6576 8.80648 16.7609 9.70323L15.1308 11.3332L15.1284 11.3308ZM13.4909 6.8916L15.1284 8.52904L15.3587 8.29866C15.4826 8.1748 15.4826 7.97414 15.3587 7.85028L14.1697 6.66122C14.0458 6.53736 13.8452 6.53736 13.7213 6.66122L13.4909 6.8916Z" fill="#5376EA"/>
                  <path d="M19.8053 18.4329H5.1947V20.4147H19.8053V18.4329Z" fill="#5376EA"/>
                  <path d="M21.5319 25H3.46809C1.55569 25 0 23.4443 0 21.5319V3.46809C0 1.55569 1.55569 0 3.46809 0H21.5319C23.4443 0 25 1.55569 25 3.46809V21.5319C25 23.4443 23.4443 25 21.5319 25ZM3.46809 1.98177C2.64814 1.98177 1.98177 2.64814 1.98177 3.46809V21.5319C1.98177 22.3519 2.64814 23.0182 3.46809 23.0182H21.5319C22.3519 23.0182 23.0182 22.3519 23.0182 21.5319V3.46809C23.0182 2.64814 22.3519 1.98177 21.5319 1.98177H3.46809Z" fill="#5376EA"/>
                </g>
                <defs>
                  <clipPath id="clip0">
                    <rect width="25" height="25" fill="white"/>
                  </clipPath>
                </defs>
              </svg>
            </div>

            <!-- CONTROLLER info box -->
            <div class="from-controller-box">
              <div class="from-controller-header">
                <label>CONTROLLER:</label>
              </div>
              <div class="from-controller-content">
                <div class="from-controller-row single-line">
                  <label>hostname =</label>
                  <input type="text" id="ctrl_hostname" readonly="true" v-model="form.controller.hostname">
                </div>
                <div class="from-controller-row single-line">
                  <label>status =</label>
                  <input type="text" id="ctrl_status" readonly="true" v-model="form.controller.status">
                </div>
                <div class="from-controller-row single-line">
                  <label>serverport =</label>
                  <input type="text" id="ctrl_serverport" readonly="true" v-model.number="form.controller.serverport">
                </div>
                <div class="from-controller-row single-line">
                  <label>vendor =</label>
                  <input type="text" id="ctrl_vendor" readonly="true" v-model="form.controller.vendor">
                </div>
                <div class="from-controller-row single-line">
                  <label>ipaddress =</label>
                  <input type="text" id="ctrl_ipaddress" readonly="true" v-model="form.controller.ipaddress">
                </div>
                <div class="from-controller-row">
                  <label>luna_config =</label>
                  <input type="text" id="ctrl_luna_config" readonly="true" v-model="form.controller.luna_config">
                </div>
              </div>
            </div>
          </div>

          <div class="right-column">
            <!-- Row 1: TECHNICAL CONTACTS | USER | DEBUG -->
            <div class="row">
              <div class="text-field wide">
                <label-part>
                  <label>TECHNICAL CONTACTS:</label>
                </label-part>
                <input type="text" id="technicalContacts" v-model="form.technical_contacts">
              </div>
              <div class="text-field wide">
                <label-part>
                  <label>USER:</label>
                </label-part>
                <input type="text" id="user" v-model="form.user">
              </div>
              <div class="checkbox-field">
                <label-part>
                  <label for="debugCheckbox">DEBUG:</label>
                </label-part>
                <div class="checkbox-container">
                  <input id="debugCheckbox" class="cluster-checkbox" type="checkbox" v-model="form.debug" />
                </div>
              </div>
              <!-- <div class="checkbox-field">
                <label-part>
                  <label>DEBUG:</label>
                </label-part>
                <div class="checkbox-container">
                  <button type="button" id="debugCheckbox" class="checked" onclick="toggleCheckbox('debugCheckbox')"></button>
                </div>
              </div> -->
            </div>

            <!-- Row 2: PROVISIONING METHOD | PROVISION FALLBACK -->
            <div class="row">
              <div class="text-field wide">
                <label-part>
                  <label>PROVISIONING METHOD:</label>
                </label-part>
                <input type="text" id="provisioningMethod" v-model="form.provision_method">
              </div>
              <div class="text-field wide">
                <label-part>
                  <label>PROVISION FALLBACK:</label>
                </label-part>
                <input type="text" id="provisionFallback" v-model="form.provision_fallback">
              </div>
            </div>

            <!-- Row 3: DOMAIN SEARCH -->
            <div class="text-field">
              <label-part>
                <label>DOMAIN SEARCH:</label>
              </label-part>
              <input type="text" id="domainSearch" v-model="form.domain_search">
            </div>

            <!-- Row 4: NAMESERVER IP -->
            <div class="text-field">
              <label-part>
                <label>NAMESERVER IP:</label>
              </label-part>
              <input type="text" id="nameserverIp" v-model="form.nameserver_ip">
            </div>

            <!-- Row 5: FORWARDSERVER IP -->
            <div class="text-field">
              <label-part>
                <label>FORWARDSERVER IP:</label>
              </label-part>
              <input type="text" id="forwardserverIp" v-model="form.forwardserver_ip">
            </div>

            <!-- Row 6: NTP SERVER -->
            <div class="text-field">
              <label-part>
                <label>NTP SERVER:</label>
              </label-part>
              <input type="text" id="ntpServer" v-model="form.ntp_server">
            </div>

            <!-- Row 7: CREATE NODE ON DEMAND | CREATE NODE ON MACASHOST -->
            <!-- <div class="row">
              <div class="boolean-field">
                <label-part>
                  <label>CREATE NODE ON DEMAND:</label>
                </label-part>
                <div class="button-group">
                  <button type="button" class="true" :class="{ active: form.createnode_ondemand === true }" @click="form.createnode_ondemand = true">TRUE</button>
                  <button type="button" class="false" :class="{ active: form.createnode_ondemand === false }" @click="form.createnode_ondemand = false">FALSE</button>
                </div>
              </div>
              <div class="text-field wide" style="flex: 1;">
                <label-part>
                  <label>CREATE NODE ON MACASHOST:</label>
                </label-part>
                <input type="text" id="createNodeOnMacasHost" value="text field">
              </div>
            </div> -->
            <!-- Row 7: CREATE NODE ON DEMAND | CREATE NODE ON MACASHOST -->
            <div class="row">
              <div class="checkbox-field">
                <label-part>
                  <label for="createNodeOnDemand">CREATE NODE ON DEMAND:</label>
                </label-part>
                <div class="checkbox-container">
                  <input id="createNodeOnDemand" class="cluster-checkbox" type="checkbox" v-model="form.createnode_ondemand" />
                </div>
              </div>

              <div class="checkbox-field">
                <label-part>
                  <label for="createNodeOnMacasHost">CREATE NODE ON MACASHOST:</label>
                </label-part>
                <div class="checkbox-container">
                  <input id="createNodeOnMacasHost" class="cluster-checkbox" type="checkbox" v-model="form.createnode_macashost" />
                </div>
              </div>
            </div>

            <!-- Row 8: NEXT NODE DISCOVER | SECURITY | PACKING BOOTPAUSE | Save -->
            <div class="row row-wide">
              <div class="field-group">
                <div class="checkbox-field">
                  <label-part>
                    <label for="nextNodeDiscover">NEXT NODE DISCOVER:</label>
                  </label-part>
                  <div class="checkbox-container">
                    <input id="nextNodeDiscover" class="cluster-checkbox" type="checkbox" v-model="form.nextnode_discover" />
                  </div>
                </div>

                <div class="checkbox-field">
                  <label-part>
                    <label for="securityCheckbox">SECURITY:</label>
                  </label-part>
                  <div class="checkbox-container">
                    <input id="securityCheckbox" class="cluster-checkbox" type="checkbox" v-model="form.security"  />
                  </div>
                </div>

                <div class="checkbox-field">
                  <label-part>
                    <label for="packingBootpause">PACKING BOOTPAUSE:</label>
                  </label-part>
                  <div class="checkbox-container">
                    <input id="packingBootpause" class="cluster-checkbox" type="checkbox" v-model="form.packing_bootpause" />
                  </div>
                </div>
              </div>
              <!-- <div class="field-group">
                <div class="text-field" style="width: auto;">
                  <label-part>
                    <label>NEXT NODE DISCOVER:</label>
                  </label-part>
                  <input type="text" id="nextNodeDiscover" value="1" style="width: 80px;">
                </div>
                <div class="boolean-field">
                  <label-part>
                    <label>SECURITY:</label>
                  </label-part>
                  <div class="button-group">
                    <button type="button" class="true active" onclick="toggleBoolean('security', true)">TRUE</button>
                    <button type="button" class="false" onclick="toggleBoolean('security', false)">FALSE</button>
                  </div>
                </div>
                <div class="boolean-field">
                  <label-part>
                    <label>PACKING BOOTPAUSE:</label>
                  </label-part>
                  <div class="button-group">
                    <button type="button" class="true active" onclick="toggleBoolean('packingBootpause', true)">TRUE</button>
                    <button type="button" class="false" onclick="toggleBoolean('packingBootpause', false)">FALSE</button>
                  </div>
                </div>
              </div> -->
              <button type="submit">Save Changes</button>
            </div>
          </div>
        </form>
      </template>
    </div>

  </BaseModal>
</template>
