<script setup lang="ts">

import { ref, onMounted, onBeforeUnmount, watch, reactive, computed } from 'vue'
import type { AxiosInstance } from 'axios'
import BaseModal from './BaseModal.vue'
import TextEditorModal from './TextEditorModal.vue'
import { OTHER_DEV_NAME_MAX_LENGTH, validateOtherdevNameInput } from '@/constants/otherdevName'

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

interface OtherDev {
  comment: string | null
  ipaddress: string | null
  macaddress: string | null
  name: string
  network: string | null
  vendor: string | null
}

type OtherDevData = Partial<OtherDev> & Record<string, unknown>

type OtherDevFormMode = 'add' | 'update' | 'clone'

const props = withDefaults(defineProps<{
  mode: OtherDevFormMode
  apiClient: AxiosInstance
  otherdevName?: string
  otherdevList?: string[]
  otherdevData?: OtherDevData
}>(), {
  otherdevName: '',
  otherdevList: () => [],
  otherdevData: () => ({})
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
  if (isAdd.value) return 'Add Other Device'
  if (isUpdate.value) return `Update Other Device: ${props.otherdevName}`
  return `Clone Other Device: ${props.otherdevName}`
})

const submitText = computed(() => {
  if (isAdd.value) return 'Add Other Device'
  if (isUpdate.value) return 'Update Other Device'
  return 'Clone Other Device'
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

  return props.otherdevList.some((existingName) => existingName.trim() === trimmedName)
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
  const sourceName = props.otherdevName.trim()
  if (!renaming.value) return form.name.trim() || sourceName
  const trimmed = renameDraft.value.trim()
  if (!trimmed || trimmed === sourceName) {
    cancelRename()
    return sourceName
  }
  return trimmed
}

function getSourceOtherDevData(): OtherDevData {
  const data = props.otherdevData || {}
  const sourceName = props.otherdevName.trim()

  if (!isRecord(data)) return {}

  const directByName = data[sourceName]
  if (isRecord(directByName)) return directByName as OtherDevData

  const OtherDev = data.otherdev
  if (isRecord(OtherDev) && isRecord(OtherDev[sourceName])) {
    return OtherDev[sourceName] as OtherDevData
  }

  const config = data.config
  if (isRecord(config)) {
    const configOtherDevSetup = config.otherdev
    if (isRecord(configOtherDevSetup) && isRecord(configOtherDevSetup[sourceName])) {
      return configOtherDevSetup[sourceName] as OtherDevData
    }
  }

  return data as OtherDevData
}

const liveNameValidationMsg = computed(() => {
  const sourceName = props.otherdevName.trim()

  if (isAdd.value) {
    const name = form.name.trim()
    if (!name) return ''
    const check = validateOtherdevNameInput(name)
    if (!check.ok) return check.message
    if (nameExists(name)) return `Other Device "${name}" already exists.`
    return ''
  }

  if (isUpdate.value) {
    if (!renaming.value) return ''
    const updateName = renameDraft.value.trim()
    if (!updateName) return ''
    const check = validateOtherdevNameInput(updateName)
    if (!check.ok) return check.message
    if (updateName !== sourceName && nameExists(updateName)) {
      return `Other Device "${updateName}" already exists.`
    }
    return ''
  }

  if (isClone.value) {
    const cloneName = form.newotherdevname.trim()
    if (!cloneName) return ''
    const check = validateOtherdevNameInput(cloneName)
    if (!check.ok) return check.message
    if (cloneName === sourceName) {
      return 'Other Device New Name must be different from the source name.'
    }
    if (nameExists(cloneName)) {
      return `Other Device "${cloneName}" already exists.`
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

  if (isClone.value && !form.newotherdevname.trim()) {
    return 'Other Device New Name is required for clone.'
  }

  return liveNameValidationMsg.value
})

const isSubmitDisabled = computed(() => {
  return loading.value || Boolean(submitValidationMsg.value)
})


const form = reactive<{
  name: string
  newotherdevname: string
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
  newotherdevname: '',
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
  if (event.key === 'Escape') {
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
  () => [props.mode, props.otherdevData, props.otherdevName] as const,
  () => {
    renaming.value = false
    renameDraft.value = ''
    errorMsg.value = ''
    networkErrorMsg.value = ''
    successMsg.value = ''

    if (props.mode === 'add') {
      form.name = ''
      form.newotherdevname = ''
      form.ipaddress = ''
      form.macaddress = ''
      form.network = ''
      form.vendor = ''
      form.comment = ''
      networkOptions.value = []
      return
    }

    const otherdevData = getSourceOtherDevData()

    form.name = asString(otherdevData.name ?? props.otherdevName)
    form.newotherdevname = ''
    form.ipaddress = asString(otherdevData.ipaddress)
    form.macaddress = asString(otherdevData.macaddress)
    form.network = asString(otherdevData.network)
    form.vendor = asString(otherdevData.vendor)
    form.comment = decodeCommentValue(otherdevData.comment)
  },
  { immediate: true, deep: true }
)


const networkLookupName = computed(() => {
  if (isAdd.value) return ''
  return props.otherdevName.trim()
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
    const sourceNetwork = asString(getSourceOtherDevData().network)

    networkOptions.value = options

    if (isAdd.value) {
      form.network = ''
      return
    }

    form.network = selected || sourceNetwork || form.network || ''
  } catch (err: unknown) {
    if (requestId !== networkRequestId) return

    networkOptions.value = []
    form.network = ''

    networkErrorMsg.value =
      err instanceof Error ? err.message : 'Could not load other device networks.'
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
    : (targetName || props.otherdevName.trim())

  const otherdevPayload: Record<string, unknown> = {
    name: sourceName,
    network: emptyToNull(form.network),
    ipaddress: emptyToNull(form.ipaddress),
    macaddress: emptyToNull(form.macaddress),
    vendor: emptyToNull(form.vendor),
    comment: encodeCommentValue(form.comment)
  }

  if (props.mode === 'clone') {
    otherdevPayload.newotherdevname = form.newotherdevname.trim()
  }

  return {
    config: {
      otherdev: {
        [sourceName]: otherdevPayload
      }
    }
  }
}

function buildRenamePayload(oldName: string, newotherdevname: string) {
  return {
    config: {
      otherdev: {
        [oldName]: {
          name: oldName,
          newotherdevname: newotherdevname
        }
      }
    }
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
    : props.otherdevName.trim()

  const updateName = props.mode === 'update' ? resolveUpdateName() : form.name.trim()
  const newotherdevname = form.newotherdevname.trim()

  if (!sourceName) {
    errorMsg.value = 'Name is required.'
    return
  }

  if (props.mode === 'add') {
    const check = validateOtherdevNameInput(form.name)
    if (!check.ok) {
      errorMsg.value = check.message
      return
    }
  }


  if (props.mode === 'update') {
    if (renaming.value) {
      const check = validateOtherdevNameInput(renameDraft.value)
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
    if (!newotherdevname) {
      errorMsg.value = 'Other Device New Name is required for clone.'
      return
    }

    if (newotherdevname === sourceName) {
      errorMsg.value = 'Other Device New Name must be different from the source name.'
      return
    }


  }

  loading.value = true

  try {
    let data

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
          errorMsg.value = renameResponse.data.content?.message || 'Other Device rename failed.'
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
          ? 'Other Device added successfully.'
          : props.mode === 'update'
            ? 'Other Device updated successfully.'
            : 'Other Device cloned successfully.')

      setTimeout(() => {
        emit('saved')
        emit('close')
      }, 3000)

      return
    }

    errorMsg.value = data.content?.message || 'Other Device save failed.'
  } catch (err: unknown) {
    errorMsg.value = err instanceof Error ? err.message : 'Unknown error occurred.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <BaseModal size="large" @close="emit('close')">
    <div class="tx-form-page otherdev-modal-page">
       <div v-if="liveNameValidationMsg || errorMsg" class="alert-danger" role="alert">
          {{ liveNameValidationMsg || errorMsg }}
        </div>
      <div v-if="successMsg" class="alert-success" role="alert">{{ successMsg }}</div>

      <template v-if="!fatalError">
        <div class="otherdev-header otherdev-modal-header">
          <h2 class="otherdev-title">{{ modalTitle }}</h2>
        </div>

        <p v-if="loading" class="tx-loading">Saving...</p>

        <form id="otherdevForm" class="otherdev-form" @submit.prevent="onSubmit">
          <div class="otherdev-form-container">

            <div class="otherdev-form-row">
              <div v-if="!isClone" class="otherdev-form-field mandatory">
                <label class="otherdev-field-label" for="otherdev-name">NAME:</label>

                <div class="otherdev-name-wrapper">
                  <input
                    v-if="isAdd"
                    id="otherdev-name"
                    v-model.trim="form.name"
                    type="text"
                    autocomplete="off"
                    required
                    class="otherdev-input"
                    :maxlength="OTHER_DEV_NAME_MAX_LENGTH"
                    :class="{ 'otherdev-input-error': liveNameValidationMsg }"
                  >
                  <div v-else-if="isUpdate" class="tx-name-input-wrap otherdev-name-rename-wrap">
                    <template v-if="!renaming">
                      <input
                        id="otherdev-name"
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
                          <g clip-path="url(#otherdev-edit-name-clip)">
                            <path d="M6.22774 17.4148C5.80661 17.4148 5.39292 17.2488 5.0907 16.9466C4.72903 16.5849 4.5581 16.0697 4.63489 15.5643L5.10556 12.4777L12.1235 5.45978L16.5627 9.89894L9.54472 16.9169L6.47546 17.3999C6.39371 17.4123 6.30949 17.4197 6.22774 17.4197V17.4148ZM6.96595 13.4166L6.67116 15.3587L8.60091 15.0565L13.7609 9.89646L12.1235 8.25902L6.96595 13.4166Z" fill="#5376EA"/>
                            <path d="M15.1284 11.3308L10.6892 6.8916L12.3192 5.2616C13.216 4.36485 14.675 4.36485 15.5718 5.2616L16.7609 6.45066C17.6576 7.34741 17.6576 8.80648 16.7609 9.70323L15.1308 11.3332L15.1284 11.3308ZM13.4909 6.8916L15.1284 8.52904L15.3587 8.29866C15.4826 8.1748 15.4826 7.97414 15.3587 7.85028L14.1697 6.66122C14.0458 6.53736 13.8452 6.53736 13.7213 6.66122L13.4909 6.8916Z" fill="#5376EA"/>
                            <path d="M19.8053 18.4329H5.1947V20.4147H19.8053V18.4329Z" fill="#5376EA"/>
                            <path d="M21.5319 25H3.46809C1.55569 25 0 23.4443 0 21.5319V3.46809C0 1.55569 1.55569 0 3.46809 0H21.5319C23.4443 0 25 1.55569 25 3.46809V21.5319C25 23.4443 23.4443 25 21.5319 25ZM3.46809 1.98177C2.64814 1.98177 1.98177 2.64814 1.98177 3.46809V21.5319C1.98177 22.3519 2.64814 23.0182 3.46809 23.0182H21.5319C22.3519 23.0182 23.0182 22.3519 23.0182 21.5319V3.46809C23.0182 2.64814 22.3519 1.98177 21.5319 1.98177H3.46809Z" fill="#5376EA"/>
                          </g>
                          <defs>
                            <clipPath id="otherdev-edit-name-clip">
                              <rect width="25" height="25" fill="white"/>
                            </clipPath>
                          </defs>
                        </svg>
                      </button>
                    </template>
                    <template v-else>
                      <input
                        id="otherdev-name"
                        v-model.trim="renameDraft"
                        type="text"
                        class="tx-name-input-editing"
                        :maxlength="OTHER_DEV_NAME_MAX_LENGTH"
                        aria-label="Other device name"
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

              <div v-if="isClone" class="otherdev-form-field mandatory">
                <label class="otherdev-field-label" for="otherdev-new-name">CLONE NAME:</label>
                <input id="otherdev-new-name" v-model.trim="form.newotherdevname" type="text" class="otherdev-input" autocomplete="off" :maxlength="OTHER_DEV_NAME_MAX_LENGTH" :class="{ 'otherdev-input-error': liveNameValidationMsg }" required>
              </div>


                <div class="otherdev-form-field">
                <label class="otherdev-field-label" for="otherdev-network">NETWORK:</label>

                <div class="otherdev-select-wrapper">
                  <select id="otherdev-network" v-model="form.network" class="otherdev-select" :class="{ 'otherdev-select-placeholder': !form.network }" :disabled="networkLoading">
                    <option value="">--- Select ---</option>
                    <option v-for="network in networkOptions" :key="network" :value="network">{{ network }}</option>
                  </select>

                  <svg class="otherdev-select-icon" width="10" height="6" viewBox="0 0 10 6" fill="none" aria-hidden="true">
                    <path d="M4.58969e-07 0L4.76314 5.25L9.52628 8.32814e-07" stroke="#5376EA" stroke-width="2"/>
                  </svg>
                </div>
              </div>
            </div>

            <div class="otherdev-form-row">
              <div class="otherdev-form-field">
                <label class="otherdev-field-label" for="otherdev-ipaddress">IP ADDRESS:</label>
                <input id="otherdev-ipaddress" v-model.trim="form.ipaddress" type="text" class="otherdev-input" autocomplete="off">
              </div>

              <div class="otherdev-form-field">
                  <label class="otherdev-field-label" for="otherdev-macaddress">MAC ADDRESS:</label>
                  <input id="otherdev-macaddress" v-model.trim="form.macaddress" type="text" class="otherdev-input" autocomplete="off">
                </div>
            </div>

            <div class="otherdev-form-row">
                <div class="otherdev-form-field">
                  <label class="otherdev-field-label" for="otherdev-vendor">VENDOR:</label>
                  <input id="otherdev-vendor" v-model.trim="form.vendor" type="text" class="otherdev-input" autocomplete="off">
                </div>
              </div>

            <button type="button" class="otherdev-advanced-btn" :class="{ 'is-open': advancedOpen }" @click="advancedOpen = !advancedOpen">Advanced
              <svg width="10" height="6" viewBox="0 0 10 6" fill="none" aria-hidden="true">
                <path :d="advancedOpen ? 'M9.52628 5.25L4.76314 0L0 5.25' : 'M4.58969e-07 0L4.76314 5.25L9.52628 8.32814e-07'" stroke="currentColor" stroke-width="2" />
              </svg>
            </button>

            <div v-if="advancedOpen" class="otherdev-advanced-section">




              <div class="otherdev-comment-section">
                <div class="otherdev-comment-header">
                  <label for="otherdev-comment">COMMENT:</label>
                </div>

                <div class="otherdev-comment-body">
                  <textarea id="otherdev-comment" v-model="form.comment" class="otherdev-textarea otherdev-textarea-with-edit-icon" rows="3" />
                  <button type="button" class="otherdev-edit-icon-btn otherdev-comment-edit-btn" aria-label="Open comment editor" title="Open comment editor" @click="showCommentEditor = true">
                    <svg viewBox="0 0 25 25" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                  <g clip-path="url(#otherdev-open-comment-clip)">
                    <path d="M21.5319 25H3.46809C1.55569 25 0 23.4443 0 21.5319V3.46809C0 1.55569 1.55569 0 3.46809 0H21.5319C23.4443 0 25 1.55569 25 3.46809V21.5319C25 23.4443 23.4443 25 21.5319 25ZM3.46809 1.98177C2.64814 1.98177 1.98177 2.64814 1.98177 3.46809V21.5319C1.98177 22.3519 2.64814 23.0182 3.46809 23.0182H21.5319C22.3519 23.0182 23.0182 22.3519 23.0182 21.5319V3.46809C23.0182 2.64814 22.3519 1.98177 21.5319 1.98177H3.46809Z" fill="#5376EA" />
                    <path d="M6.2 7.1C6.2 6.55 6.65 6.1 7.2 6.1H12.65V8.1H8.2V16.8H16.9V12.35H18.9V17.8C18.9 18.35 18.45 18.8 17.9 18.8H7.2C6.65 18.8 6.2 18.35 6.2 17.8V7.1Z" fill="#5376EA" />
                    <path d="M14.05 5.1H19.9V10.95H17.9V8.52L12.25 14.17L10.83 12.75L16.48 7.1H14.05V5.1Z" fill="#5376EA" />
                  </g>
                  <defs>
                    <clipPath id="otherdev-open-comment-clip">
                      <rect width="25" height="25" fill="white"/>
                    </clipPath>
                  </defs>
                </svg>

                  </button>
                </div>
              </div>
            </div>

            <TextEditorModal v-if="showCommentEditor" v-model="form.comment" title="Edit Other Device Comment" @close="showCommentEditor = false" />

            <div class="otherdev-button-container">
              <button type="submit" class="otherdev-submit-btn" :disabled="isSubmitDisabled" :class="{ 'otherdev-submit-btn-disabled': isSubmitDisabled }">{{ loading ? savingText : submitText }}</button>
            </div>

          </div>
        </form>
      </template>
    </div>
  </BaseModal>
</template>
