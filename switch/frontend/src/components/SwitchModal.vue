<script setup lang="ts">

import { ref, onMounted, onBeforeUnmount, watch, reactive, computed } from 'vue'
import type { AxiosInstance } from 'axios'
import BaseModal from './BaseModal.vue'
import TextEditorModal from './TextEditorModal.vue'
import { SWITCH_NAME_MAX_LENGTH, validateSwitchNameInput } from '@/constants/switchName'

interface NetworkListResponse {
  network_list?: {
    options?: string[]
    selected?: string | null
  }
  content?: {
    message?: string
  }
  status?: boolean
  status_code?: number
}

interface Switch {
  comment: string | null
  ipaddress: string | null
  // ipaddress_ipv6: string | null
  macaddress: string | null
  name: string
  network: string | null
  oid: string | null
  read: string | null
  rw: string | null
  uplinkports: string | null
  vendor: string | null
}

type SwitchData = Partial<Switch> & Record<string, unknown>

type SwitchFormMode = 'add' | 'update' | 'clone'

const props = withDefaults(defineProps<{
  mode: SwitchFormMode
  apiClient: AxiosInstance
  switchName?: string
  switchList?: string[]
  switchData?: SwitchData
}>(), {
  switchName: '',
  switchList: () => [],
  switchData: () => ({})
})

const emit = defineEmits<{
  (event: 'close'): void
  (event: 'saved'): void
}>()

const loading = ref(false)
const errorMsg = ref('')
const successMsg = ref('')
const fatalError = ref(false)
const networkLoading = ref(false)
const networkErrorMsg = ref('')
const advancedOpen = ref(false)
const networkOptions = ref<string[]>([])

let networkRequestId = 0
const renaming = ref(false)
const renameDraft = ref('')
const showCommentEditor = ref(false)

const isAdd = computed(() => props.mode === 'add')
const isUpdate = computed(() => props.mode === 'update')
const isClone = computed(() => props.mode === 'clone')

const modalTitle = computed(() => {
  if (isAdd.value) return 'Add Switch'
  if (isUpdate.value) return `Update Switch: ${props.switchName}`
  return `Clone Switch: ${props.switchName}`
})

const submitText = computed(() => {
  if (isAdd.value) return 'Add Switch'
  if (isUpdate.value) return 'Update Switch'
  return 'Clone Switch'
})

const savingText = computed(() => {
  if (isAdd.value) return 'Adding...'
  if (isUpdate.value) return 'Updating...'
  return 'Cloning...'
})

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function nameExists(name: string): boolean {
  const trimmedName = name.trim()
  if (!trimmedName) return false

  return props.switchList.some((existingName) => existingName.trim() === trimmedName)
}

function startRename() {
  renameDraft.value = form.name
  renaming.value = true
}

function cancelRename() {
  renaming.value = false
  renameDraft.value = ''
}

function resolveUpdateName(): string {
  const sourceName = props.switchName.trim()
  if (!renaming.value) return form.name.trim() || sourceName
  const trimmed = renameDraft.value.trim()
  if (!trimmed || trimmed === sourceName) {
    cancelRename()
    return sourceName
  }
  return trimmed
}

function getSourceSwitchData(): SwitchData {
  const data = props.switchData || {}
  const sourceName = props.switchName.trim()

  if (!isRecord(data)) return {}

  const directByName = data[sourceName]
  if (isRecord(directByName)) return directByName as SwitchData

  const Switch = data.switch
  if (isRecord(Switch) && isRecord(Switch[sourceName])) {
    return Switch[sourceName] as SwitchData
  }

  const config = data.config
  if (isRecord(config)) {
    const configSwitchSetup = config.switch
    if (isRecord(configSwitchSetup) && isRecord(configSwitchSetup[sourceName])) {
      return configSwitchSetup[sourceName] as SwitchData
    }
  }

  return data as SwitchData
}

const liveNameValidationMsg = computed(() => {
  const sourceName = props.switchName.trim()

  if (isAdd.value) {
    const name = form.name.trim()
    if (!name) return ''
    const check = validateSwitchNameInput(name)
    if (!check.ok) return check.message
    if (nameExists(name)) return `Switch "${name}" already exists.`
    return ''
  }

  if (isUpdate.value) {
    if (!renaming.value) return ''
    const updateName = renameDraft.value.trim()
    if (!updateName) return ''
    const check = validateSwitchNameInput(updateName)
    if (!check.ok) return check.message
    if (updateName !== sourceName && nameExists(updateName)) {
      return `Switch "${updateName}" already exists.`
    }
    return ''
  }

  if (isClone.value) {
    const cloneName = form.newswitchname.trim()
    if (!cloneName) return ''
    const check = validateSwitchNameInput(cloneName)
    if (!check.ok) return check.message
    if (cloneName === sourceName) {
      return 'Switch New Name must be different from the source name.'
    }
    if (nameExists(cloneName)) {
      return `Switch "${cloneName}" already exists.`
    }
    return ''
  }

  return ''
})

const submitValidationMsg = computed(() => {
  if (isAdd.value && !form.name.trim()) {
    return 'Name is required.'
  }

  if (isUpdate.value && renaming.value && !renameDraft.value.trim()) {
    return 'Name is required.'
  }

  if (isClone.value && !form.newswitchname.trim()) {
    return 'Switch New Name is required for clone.'
  }

  return liveNameValidationMsg.value
})

const isSubmitDisabled = computed(() => {
  return loading.value || Boolean(submitValidationMsg.value)
})


const form = reactive<{
  name: string
  newswitchname: string
  ipaddress: string
  // ipaddress_ipv6: string
  macaddress: string
  network: string
  oid: string
  read: string
  rw: string
  uplinkports: string
  vendor: string
  comment: string
}>({
  name: '',
  newswitchname: '',
  ipaddress: '',
  // ipaddress_ipv6: '',
  macaddress: '',
  network: '',
  oid: '',
  read: '',
  rw: '',
  uplinkports: '',
  vendor: '',
  comment: ''
})

function handleEscKey(event: KeyboardEvent) {
  if (event.key === 'Escape' && !loading.value) {
    emit('close')
  }
}

function asString(value: unknown): string {
  return value === null || value === undefined ? '' : String(value)
}

function stripBase64Padding(value: string): string {
  return value.replace(/=+$/, '')
}

function encodeBase64Utf8(value: string): string {
  const bytes = new TextEncoder().encode(value)
  let binary = ''

  for (const byte of bytes) {
    binary += String.fromCharCode(byte)
  }

  return window.btoa(binary)
}

function tryDecodeBase64Utf8(value: string): string | null {
  const raw = value.trim()

  if (!raw) return null

  let normalized = raw
    .replace(/\s+/g, '')
    .replace(/-/g, '+')
    .replace(/_/g, '/')

  const remainder = normalized.length % 4

  if (remainder === 1) return null

  if (remainder > 0) {
    normalized = normalized.padEnd(normalized.length + (4 - remainder), '=')
  }

  const base64Pattern =
    /^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/

  if (!base64Pattern.test(normalized)) {
    return null
  }

  try {
    const binary = window.atob(normalized)
    const bytes = new Uint8Array(binary.length)

    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i)
    }

    const decoded = new TextDecoder('utf-8', { fatal: true }).decode(bytes)
    const reEncoded = encodeBase64Utf8(decoded)

    if (stripBase64Padding(reEncoded) !== stripBase64Padding(normalized)) {
      return null
    }

    return decoded
  } catch {
    return null
  }
}

function decodeCommentValue(value: unknown): string {
  const raw = asString(value)

  if (!raw) return ''

  return tryDecodeBase64Utf8(raw) ?? raw
}

function encodeCommentValue(value: string): string | null {
  if (value === '') return null

  return encodeBase64Utf8(value)
}


function emptyToNull(value: string): string | null {
  const trimmed = value.trim()
  return trimmed === '' ? null : trimmed
}

watch(
  () => [props.mode, props.switchData, props.switchName] as const,
  () => {
    renaming.value = false
    renameDraft.value = ''
    errorMsg.value = ''
    networkErrorMsg.value = ''
    successMsg.value = ''

    if (props.mode === 'add') {
      form.name = ''
      form.newswitchname = ''
      form.ipaddress = ''
      // form.ipaddress_ipv6 = ''
      form.macaddress = ''
      form.network = ''
      form.oid = ''
      form.read = ''
      form.rw = ''
      form.uplinkports = ''
      form.vendor = ''
      form.comment = ''
      networkOptions.value = []
      return
    }

    const switchData = getSourceSwitchData()

    form.name = asString(switchData.name ?? props.switchName)
    form.newswitchname = ''
    form.ipaddress = asString(switchData.ipaddress)
    // form.ipaddress_ipv6 = asString(switchData.ipaddress_ipv6)
    form.macaddress = asString(switchData.macaddress)
    form.network = asString(switchData.network)
    form.oid = asString(switchData.oid)
    form.read = asString(switchData.read)
    form.rw = asString(switchData.rw)
    form.uplinkports = asString(switchData.uplinkports)
    form.vendor = asString(switchData.vendor)
    form.comment = decodeCommentValue(switchData.comment)
  },
  { immediate: true, deep: true }
)


const networkLookupName = computed(() => {
  if (isAdd.value) return ''
  return props.switchName.trim()
})

watch(
  () => networkLookupName.value,
  () => {
    void loadNetworkOptions()
  },
  { immediate: true }
)

async function loadNetworkOptions() {
  const lookupName = networkLookupName.value
  const requestId = ++networkRequestId

  networkErrorMsg.value = ''
  networkLoading.value = true

  try {
    const endpoint = lookupName
      ? `/api/v1/get_networks/${encodeURIComponent(lookupName)}`
      : '/api/v1/get_networks'

    const { data } = await props.apiClient.get<NetworkListResponse>(
      endpoint,
      { validateStatus: () => true }
    )

    if (requestId !== networkRequestId) return

    const options = data.network_list?.options ?? []
    const selected = data.network_list?.selected ?? null
    const sourceNetwork = asString(getSourceSwitchData().network)

    networkOptions.value = options

    if (isAdd.value) {
      // Add mode: show all networks, but do not preselect anything.
      form.network = ''
      return
    }

    // Update/clone: prefer API selected value, otherwise fall back to source data.
    form.network = selected || sourceNetwork || form.network || ''
  } catch (err: unknown) {
    if (requestId !== networkRequestId) return

    networkOptions.value = []
    form.network = ''

    networkErrorMsg.value =
      err instanceof Error ? err.message : 'Could not load switch networks.'
  } finally {
    if (requestId === networkRequestId) {
      networkLoading.value = false
    }
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleEscKey)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleEscKey)
})

function buildPayload(targetName?: string) {
  const sourceName = props.mode === 'add'
    ? form.name.trim()
    : (targetName || props.switchName.trim())

  const switchPayload: Record<string, unknown> = {
    name: sourceName,
    read: emptyToNull(form.read),
    rw: emptyToNull(form.rw),
    oid: emptyToNull(form.oid),
    network: emptyToNull(form.network),
    ipaddress: emptyToNull(form.ipaddress),
    // ipaddress_ipv6: emptyToNull(form.ipaddress_ipv6),
    macaddress: emptyToNull(form.macaddress),
    vendor: emptyToNull(form.vendor),
    uplinkports: emptyToNull(form.uplinkports),
    comment: encodeCommentValue(form.comment)
  }

  if (props.mode === 'clone') {
    switchPayload.newswitchname = form.newswitchname.trim()
  }

  return {
    config: {
      switch: {
        [sourceName]: switchPayload
      }
    }
  }
}

function buildRenamePayload(oldName: string, newswitchname: string) {
  return {
    config: {
      switch: {
        [oldName]: {
          name: oldName,
          newswitchname: newswitchname
        }
      }
    }
  }
}

async function cloneAppearsCreated(cloneName: string): Promise<boolean> {
  if (!cloneName) return false

  try {
    const verifyResponse = await props.apiClient.get('/api/v1/switches')
    const raw = verifyResponse.data?.content?.config?.switch as Record<string, unknown> | undefined
    return Boolean(raw && Object.prototype.hasOwnProperty.call(raw, cloneName))
  } catch {
    return false
  }
}

async function onSubmit() {
  errorMsg.value = ''
  successMsg.value = ''

  if (submitValidationMsg.value) {
  errorMsg.value = submitValidationMsg.value
  return
}

  const sourceName = props.mode === 'add'
    ? form.name.trim()
    : props.switchName.trim()

  const updateName = props.mode === 'update' ? resolveUpdateName() : form.name.trim()
  const newswitchname = form.newswitchname.trim()

  if (!sourceName) {
    errorMsg.value = 'Name is required.'
    return
  }

  if (props.mode === 'add') {
    const check = validateSwitchNameInput(form.name)
    if (!check.ok) {
      errorMsg.value = check.message
      return
    }
  }


  if (props.mode === 'update') {
    if (renaming.value) {
      const check = validateSwitchNameInput(renameDraft.value)
      if (!check.ok) {
        errorMsg.value = check.message
        return
      }
    }
    if (renaming.value && !updateName) {
      errorMsg.value = 'Name is required.'
      return
    }


  }

  if (props.mode === 'clone') {
    if (!newswitchname) {
      errorMsg.value = 'Switch New Name is required for clone.'
      return
    }

    if (newswitchname === sourceName) {
      errorMsg.value = 'Switch New Name must be different from the source name.'
      return
    }


  }

  loading.value = true

  try {
    let data
    const cloneName = form.newswitchname.trim()

    if (props.mode === 'add') {
      const response = await props.apiClient.post('/api/v1/add', buildPayload())
      data = response.data
    } else if (props.mode === 'clone') {
      const response = await props.apiClient.post('/api/v1/clone', buildPayload())
      data = response.data
    } else {
      const renamed = updateName !== sourceName
      const finalName = renamed ? updateName : sourceName

      if (renamed) {
        const renameResponse = await props.apiClient.patch(
          '/api/v1/rename',
          buildRenamePayload(sourceName, updateName)
        )

        if (renameResponse.data.status !== true) {
          errorMsg.value = renameResponse.data.content?.message || 'Switch rename failed.'
          return
        }
      }

      const updateResponse = await props.apiClient.put(
        '/api/v1/update',
        buildPayload(finalName)
      )

      data = updateResponse.data
    }

    if (data.status === true) {
      successMsg.value =
        data.content?.message ||
        (props.mode === 'add'
          ? 'Switch added successfully.'
          : props.mode === 'update'
            ? 'Switch updated successfully.'
            : 'Switch cloned successfully.')
      emit('saved')

      setTimeout(() => {
        emit('close')
      }, 800)

      return
    }

    if (props.mode === 'clone' && cloneName && await cloneAppearsCreated(cloneName)) {
      successMsg.value = `Switch "${cloneName}" has been created successfully.`
      emit('saved')
      setTimeout(() => {
        emit('close')
      }, 800)
      return
    }

    errorMsg.value = data.content?.message || 'Switch save failed.'
  } catch (err: unknown) {
    const cloneName = form.newswitchname.trim()
    if (props.mode === 'clone' && cloneName && await cloneAppearsCreated(cloneName)) {
      successMsg.value = `Switch "${cloneName}" has been created successfully.`
      emit('saved')
      setTimeout(() => {
        emit('close')
      }, 800)
      return
    }
    errorMsg.value = err instanceof Error ? err.message : 'Unknown error occurred.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <BaseModal size="large" :close-disabled="loading" @close="emit('close')">
    <div class="tx-form-page switch-modal-page">
       <div v-if="liveNameValidationMsg || errorMsg || networkErrorMsg" class="alert-danger" role="alert">
        {{ liveNameValidationMsg || errorMsg || networkErrorMsg }}
      </div>
      <div v-if="successMsg" class="alert-success" role="alert">{{ successMsg }}</div>

      <template v-if="!fatalError">
        <div class="switch-header switch-modal-header">
          <h2 class="switch-title">{{ modalTitle }}</h2>
        </div>

        <p v-if="loading" class="tx-loading">Saving...</p>

        <form id="switchForm" class="switch-form" @submit.prevent="onSubmit">
          <div class="switch-form-container">

            <div class="switch-form-row">
              <div v-if="!isClone" class="switch-form-field mandatory">
                <label class="switch-field-label" for="switch-name">NAME:</label>

                <div class="switch-name-wrapper">
                  <input
                    v-if="isAdd"
                    id="switch-name"
                    v-model.trim="form.name"
                    type="text"
                    autocomplete="off"
                    required
                    class="switch-input"
                    :maxlength="SWITCH_NAME_MAX_LENGTH"
                    :class="{ 'switch-input-error': liveNameValidationMsg }"
                  >
                  <div v-else-if="isUpdate" class="tx-name-input-wrap switch-name-rename-wrap">
                    <template v-if="!renaming">
                      <input
                        id="switch-name"
                        type="text"
                        class="tx-name-input-readonly"
                        :value="form.name"
                        readonly
                      >
                      <button
                        type="button"
                        class="tx-btn-rename"
                        title="Edit name"
                        aria-label="Edit name"
                        @click="startRename"
                      >
                        <svg viewBox="0 0 25 25" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" width="20" height="20">
                          <g clip-path="url(#switch-edit-name-clip)">
                            <path d="M6.22774 17.4148C5.80661 17.4148 5.39292 17.2488 5.0907 16.9466C4.72903 16.5849 4.5581 16.0697 4.63489 15.5643L5.10556 12.4777L12.1235 5.45978L16.5627 9.89894L9.54472 16.9169L6.47546 17.3999C6.39371 17.4123 6.30949 17.4197 6.22774 17.4197V17.4148ZM6.96595 13.4166L6.67116 15.3587L8.60091 15.0565L13.7609 9.89646L12.1235 8.25902L6.96595 13.4166Z" fill="#5376EA"/>
                            <path d="M15.1284 11.3308L10.6892 6.8916L12.3192 5.2616C13.216 4.36485 14.675 4.36485 15.5718 5.2616L16.7609 6.45066C17.6576 7.34741 17.6576 8.80648 16.7609 9.70323L15.1308 11.3332L15.1284 11.3308ZM13.4909 6.8916L15.1284 8.52904L15.3587 8.29866C15.4826 8.1748 15.4826 7.97414 15.3587 7.85028L14.1697 6.66122C14.0458 6.53736 13.8452 6.53736 13.7213 6.66122L13.4909 6.8916Z" fill="#5376EA"/>
                            <path d="M19.8053 18.4329H5.1947V20.4147H19.8053V18.4329Z" fill="#5376EA"/>
                            <path d="M21.5319 25H3.46809C1.55569 25 0 23.4443 0 21.5319V3.46809C0 1.55569 1.55569 0 3.46809 0H21.5319C23.4443 0 25 1.55569 25 3.46809V21.5319C25 23.4443 23.4443 25 21.5319 25ZM3.46809 1.98177C2.64814 1.98177 1.98177 2.64814 1.98177 3.46809V21.5319C1.98177 22.3519 2.64814 23.0182 3.46809 23.0182H21.5319C22.3519 23.0182 23.0182 22.3519 23.0182 21.5319V3.46809C23.0182 2.64814 22.3519 1.98177 21.5319 1.98177H3.46809Z" fill="#5376EA"/>
                          </g>
                          <defs>
                            <clipPath id="switch-edit-name-clip">
                              <rect width="25" height="25" fill="white"/>
                            </clipPath>
                          </defs>
                        </svg>
                      </button>
                    </template>
                    <template v-else>
                      <input
                        id="switch-name"
                        v-model.trim="renameDraft"
                        type="text"
                        class="tx-name-input-editing"
                        :maxlength="SWITCH_NAME_MAX_LENGTH"
                        aria-label="Switch name"
                        @keyup.escape="cancelRename"
                      >
                      <button
                        type="button"
                        class="tx-btn-rename tx-btn-rename-cancel-char"
                        title="Stop editing name"
                        aria-label="Stop editing name"
                        @click="cancelRename"
                      >
                        ×
                      </button>
                    </template>
                  </div>
                </div>
              </div>

              <div v-if="isClone" class="switch-form-field mandatory">
                <label class="switch-field-label" for="switch-new-name">CLONE NAME:</label>
                <input id="switch-new-name" v-model.trim="form.newswitchname" type="text" class="switch-input" autocomplete="off" :maxlength="SWITCH_NAME_MAX_LENGTH" :class="{ 'switch-input-error': liveNameValidationMsg }" required>
              </div>

              <div class="switch-form-field">
                <label class="switch-field-label" for="switch-read">READ:</label>
                <input id="switch-read" v-model.trim="form.read" type="text" class="switch-input" autocomplete="off">
              </div>
            </div>

            <div class="switch-form-row">
              <div class="switch-form-field">
                <label class="switch-field-label" for="switch-rw">RW:</label>
                <input id="switch-rw" v-model.trim="form.rw" type="text" class="switch-input" autocomplete="off">
              </div>

              <div class="switch-form-field">
                <label class="switch-field-label" for="switch-oid">OID:</label>
                <input id="switch-oid" v-model.trim="form.oid" type="text" class="switch-input" autocomplete="off">
              </div>
            </div>

            <button type="button" class="switch-advanced-btn" :class="{ 'is-open': advancedOpen }" @click="advancedOpen = !advancedOpen">Advanced
              <svg width="10" height="6" viewBox="0 0 10 6" fill="none" aria-hidden="true">
                <path :d="advancedOpen ? 'M9.52628 5.25L4.76314 0L0 5.25' : 'M4.58969e-07 0L4.76314 5.25L9.52628 8.32814e-07'" stroke="currentColor" stroke-width="2" />
              </svg>
            </button>

            <div v-if="advancedOpen" class="switch-advanced-section">
              <div class="switch-form-row">
                <div class="switch-form-field">
                  <label class="switch-field-label" for="switch-network">NETWORK:</label>

                  <div class="switch-select-wrapper">
                    <select id="switch-network" v-model="form.network" class="switch-select" :class="{ 'switch-select-placeholder': !form.network }" :disabled="networkLoading">
                      <option value="">--- Select ---</option>
                      <option v-for="network in networkOptions" :key="network" :value="network">{{ network }}</option>
                    </select>

                    <svg class="switch-select-icon" width="10" height="6" viewBox="0 0 10 6" fill="none" aria-hidden="true">
                      <path d="M4.58969e-07 0L4.76314 5.25L9.52628 8.32814e-07" stroke="#5376EA" stroke-width="2"/>
                    </svg>
                  </div>
                </div>

                <div class="switch-form-field">
                  <label class="switch-field-label" for="switch-ipaddress">IP ADDRESS:</label>
                  <input id="switch-ipaddress" v-model.trim="form.ipaddress" type="text" class="switch-input" autocomplete="off">
                </div>
              </div>

              <div class="switch-form-row">
                <div class="switch-form-field">
                  <label class="switch-field-label" for="switch-macaddress">MAC ADDRESS:</label>
                  <input id="switch-macaddress" v-model.trim="form.macaddress" type="text" class="switch-input" autocomplete="off">
                </div>

                <div class="switch-form-field">
                  <label class="switch-field-label" for="switch-vendor">VENDOR:</label>
                  <input id="switch-vendor" v-model.trim="form.vendor" type="text" class="switch-input" autocomplete="off">
                </div>
              </div>

              <div class="switch-form-row full-width">
                <div class="switch-form-field">
                  <label class="switch-field-label" for="switch-uplinkports">UPLINK PORTS:</label>
                  <input id="switch-uplinkports" v-model.trim="form.uplinkports" type="text" class="switch-input" autocomplete="off" placeholder="Example: 1,2,3,4">
                </div>
              </div>

              <div class="switch-comment-section">
                <div class="switch-comment-header">
                  <label for="switch-comment">COMMENT:</label>
                </div>

                <div class="switch-comment-body">
                  <textarea id="switch-comment" v-model="form.comment" class="switch-textarea switch-textarea-with-edit-icon" rows="3" />
                  <button type="button" class="switch-edit-icon-btn switch-comment-edit-btn" aria-label="Open comment editor" title="Open comment editor" @click="showCommentEditor = true">
                    <svg viewBox="0 0 25 25" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                  <g clip-path="url(#switch-open-comment-clip)">
                    <path d="M21.5319 25H3.46809C1.55569 25 0 23.4443 0 21.5319V3.46809C0 1.55569 1.55569 0 3.46809 0H21.5319C23.4443 0 25 1.55569 25 3.46809V21.5319C25 23.4443 23.4443 25 21.5319 25ZM3.46809 1.98177C2.64814 1.98177 1.98177 2.64814 1.98177 3.46809V21.5319C1.98177 22.3519 2.64814 23.0182 3.46809 23.0182H21.5319C22.3519 23.0182 23.0182 22.3519 23.0182 21.5319V3.46809C23.0182 2.64814 22.3519 1.98177 21.5319 1.98177H3.46809Z" fill="#5376EA" />
                    <path d="M6.2 7.1C6.2 6.55 6.65 6.1 7.2 6.1H12.65V8.1H8.2V16.8H16.9V12.35H18.9V17.8C18.9 18.35 18.45 18.8 17.9 18.8H7.2C6.65 18.8 6.2 18.35 6.2 17.8V7.1Z" fill="#5376EA" />
                    <path d="M14.05 5.1H19.9V10.95H17.9V8.52L12.25 14.17L10.83 12.75L16.48 7.1H14.05V5.1Z" fill="#5376EA" />
                  </g>
                  <defs>
                    <clipPath id="switch-open-comment-clip">
                      <rect width="25" height="25" fill="white"/>
                    </clipPath>
                  </defs>
                </svg>

                  </button>
                </div>
              </div>
            </div>

            <TextEditorModal v-if="showCommentEditor" v-model="form.comment" title="Edit Switch Comment" @close="showCommentEditor = false" />

            <div class="switch-button-container">
              <button type="submit" class="switch-submit-btn" :disabled="isSubmitDisabled" :class="{ 'switch-submit-btn-disabled': isSubmitDisabled }">{{ loading ? savingText : submitText }}</button>
            </div>

          </div>
        </form>
      </template>
    </div>
  </BaseModal>
</template>
