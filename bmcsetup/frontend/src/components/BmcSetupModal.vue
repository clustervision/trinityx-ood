<script setup lang="ts">

import { ref, onMounted, onBeforeUnmount, watch, reactive, computed } from 'vue'
import type { AxiosInstance } from 'axios'
import BaseModal from './BaseModal.vue'
import TextEditorModal from './TextEditorModal.vue'

interface BMCSetup {
  name: string
  userid: number | null
  username: string | null
  password: string | null
  netchannel: number | null
  mgmtchannel: number | null
  unmanaged_bmc_users: string | null
  comment: string | null
}

type BmcData = Partial<BMCSetup> & Record<string, unknown>

type BmcFormMode = 'add' | 'update' | 'clone'

const props = withDefaults(defineProps<{
  mode: BmcFormMode
  apiClient: AxiosInstance
  bmcName?: string
  bmcList?: string[]
  bmcData?: BmcData
}>(), {
  bmcName: '',
  bmcList: () => [],
  bmcData: () => ({})
})

const emit = defineEmits<{
  (event: 'close'): void
  (event: 'saved'): void
}>()

const loading = ref(false)
const errorMsg = ref('')
const successMsg = ref('')
const fatalError = ref(false)
const showPassword = ref(false)
const nameEditable = ref(false)
const showCommentEditor = ref(false)

const isAdd = computed(() => props.mode === 'add')
const isUpdate = computed(() => props.mode === 'update')
const isClone = computed(() => props.mode === 'clone')

const modalTitle = computed(() => {
  if (isAdd.value) return 'Add BMC Setup'
  if (isUpdate.value) return `Update BMC Setup: ${props.bmcName}`
  return `Clone BMC Setup: ${props.bmcName}`
})

const submitText = computed(() => {
  if (isAdd.value) return 'Add BMC Setup'
  if (isUpdate.value) return 'Update BMC Setup'
  return 'Clone BMC Setup'
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

  return props.bmcList.some((existingName) => existingName.trim() === trimmedName)
}

function getSourceBmcData(): BmcData {
  const data = props.bmcData || {}
  const sourceName = props.bmcName.trim()

  if (!isRecord(data)) return {}

  const directByName = data[sourceName]
  if (isRecord(directByName)) return directByName as BmcData

  const bmcsetup = data.bmcsetup
  if (isRecord(bmcsetup) && isRecord(bmcsetup[sourceName])) {
    return bmcsetup[sourceName] as BmcData
  }

  const config = data.config
  if (isRecord(config)) {
    const configBmcSetup = config.bmcsetup
    if (isRecord(configBmcSetup) && isRecord(configBmcSetup[sourceName])) {
      return configBmcSetup[sourceName] as BmcData
    }
  }

  return data as BmcData
}

const liveNameValidationMsg = computed(() => {
  const sourceName = props.bmcName.trim()

  if (isAdd.value) {
    const name = form.name.trim()
    if (!name) return ''
    if (nameExists(name)) return `BMC Setup "${name}" already exists.`
    return ''
  }

  if (isUpdate.value) {
    const updateName = form.name.trim()
    if (!updateName) return ''
    if (updateName !== sourceName && nameExists(updateName)) {
      return `BMC Setup "${updateName}" already exists.`
    }
    return ''
  }

  if (isClone.value) {
    const cloneName = form.newbmcname.trim()
    if (!cloneName) return ''
    if (cloneName === sourceName) {
      return 'BMC New Name must be different from the source name.'
    }
    if (nameExists(cloneName)) {
      return `BMC Setup "${cloneName}" already exists.`
    }
    return ''
  }

  return ''
})

const submitValidationMsg = computed(() => {
  if ((isAdd.value || isUpdate.value) && !form.name.trim()) {
    return 'Name is required.'
  }

  if (isClone.value && !form.newbmcname.trim()) {
    return 'BMC New Name is required for clone.'
  }

  return liveNameValidationMsg.value
})

const isSubmitDisabled = computed(() => {
  return loading.value || Boolean(submitValidationMsg.value)
})


const form = reactive<{
  name: string
  newbmcname: string
  userid: number | null
  username: string
  password: string
  netchannel: number | null
  mgmtchannel: number | null
  unmanaged_bmc_users: string
  comment: string
}>({
  name: '',
  newbmcname: '',
  userid: null,
  username: '',
  password: '',
  netchannel: null,
  mgmtchannel: null,
  unmanaged_bmc_users: '',
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

function asNumberOrNull(value: unknown): number | null {
  if (value === null || value === undefined || value === '') return null
  const numberValue = Number(value)
  return Number.isFinite(numberValue) ? numberValue : null
}

function emptyToNull(value: string): string | null {
  const trimmed = value.trim()
  return trimmed === '' ? null : trimmed
}

watch(
  () => [props.mode, props.bmcData, props.bmcName] as const,
  () => {
    nameEditable.value = props.mode === 'add'
    errorMsg.value = ''
    successMsg.value = ''

    if (props.mode === 'add') {
      form.name = ''
      form.newbmcname = ''
      form.userid = null
      form.username = ''
      form.password = ''
      form.netchannel = null
      form.mgmtchannel = null
      form.unmanaged_bmc_users = ''
      form.comment = ''
      return
    }

    const bmcData = getSourceBmcData()

    form.name = asString(bmcData.name ?? props.bmcName)
    form.newbmcname = ''
    form.userid = asNumberOrNull(bmcData.userid)
    form.username = asString(bmcData.username)
    form.password = asString(bmcData.password)
    form.netchannel = asNumberOrNull(bmcData.netchannel)
    form.mgmtchannel = asNumberOrNull(bmcData.mgmtchannel)
    form.unmanaged_bmc_users = asString(bmcData.unmanaged_bmc_users)
    form.comment = decodeCommentValue(bmcData.comment)
  },
  { immediate: true, deep: true }
)

onMounted(() => {
  window.addEventListener('keydown', handleEscKey)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleEscKey)
})

function buildPayload(targetName?: string) {
  const sourceName = props.mode === 'add'
    ? form.name.trim()
    : (targetName || props.bmcName.trim())

  const bmcPayload: Record<string, unknown> = {
    name: sourceName,
    userid: form.userid,
    username: emptyToNull(form.username),
    password: emptyToNull(form.password),
    netchannel: form.netchannel,
    mgmtchannel: form.mgmtchannel,
    unmanaged_bmc_users: emptyToNull(form.unmanaged_bmc_users),
    comment: encodeCommentValue(form.comment)
  }

  if (props.mode === 'clone') {
    bmcPayload.newbmcname = form.newbmcname.trim()
  }

  return {
    config: {
      bmcsetup: {
        [sourceName]: bmcPayload
      }
    }
  }
}

function buildRenamePayload(oldName: string, newbmcname: string) {
  return {
    config: {
      bmcsetup: {
        [oldName]: {
          name: oldName,
          newbmcname: newbmcname
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
    : props.bmcName.trim()

  const updateName = form.name.trim()
  const newbmcname = form.newbmcname.trim()

  if (!sourceName) {
    errorMsg.value = 'Name is required.'
    return
  }


  if (props.mode === 'update') {
    if (!updateName) {
      errorMsg.value = 'Name is required.'
      return
    }


  }

  if (props.mode === 'clone') {
    if (!newbmcname) {
      errorMsg.value = 'BMC New Name is required for clone.'
      return
    }

    if (newbmcname === sourceName) {
      errorMsg.value = 'BMC New Name must be different from the source name.'
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
          errorMsg.value = renameResponse.data.content?.message || 'BMC setup rename failed.'
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
          ? 'BMC setup added successfully.'
          : props.mode === 'update'
            ? 'BMC setup updated successfully.'
            : 'BMC setup cloned successfully.')

      setTimeout(() => {
        emit('saved')
        emit('close')
      }, 3000)

      return
    }

    errorMsg.value = data.content?.message || 'BMC setup save failed.'
  } catch (err: unknown) {
    errorMsg.value = err instanceof Error ? err.message : 'Unknown error occurred.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <BaseModal size="large" @close="emit('close')">
    <div class="tx-form-page bmc-modal-page">
       <div v-if="liveNameValidationMsg || errorMsg" class="alert-danger" role="alert">
          {{ liveNameValidationMsg || errorMsg }}
        </div>
      <div v-if="successMsg" class="alert-success" role="alert">{{ successMsg }}</div>

      <template v-if="!fatalError">
        <div class="bmc-header bmc-modal-header">
          <h2 class="bmc-title">{{ modalTitle }}</h2>
        </div>

        <p v-if="loading" class="tx-loading">Saving...</p>

        <form id="bmcForm" class="bmc-form" @submit.prevent="onSubmit">
          <div class="bmc-form-container">

            <div class="bmc-form-row">
              <div v-if="!isClone" class="bmc-form-field mandatory">
                <label class="bmc-field-label" for="bmc-name">NAME:</label>

                <div class="bmc-name-wrapper">
                  <input id="bmc-name" v-model.trim="form.name" type="text" autocomplete="off" :disabled="isUpdate && !nameEditable" required class="bmc-input" :class="{'bmc-input-disabled': isUpdate && !nameEditable,'bmc-input-with-edit-icon': isUpdate,'bmc-input-error': liveNameValidationMsg && !isClone}">

                  <button v-if="isUpdate" type="button" class="bmc-edit-icon-btn" :class="{ 'is-active': nameEditable }" aria-label="Enable BMC name editing" title="Rename BMC setup" @click="nameEditable = true">
                    <svg viewBox="0 0 25 25" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                      <g clip-path="url(#bmc-edit-name-clip)">
                        <path d="M6.22774 17.4148C5.80661 17.4148 5.39292 17.2488 5.0907 16.9466C4.72903 16.5849 4.5581 16.0697 4.63489 15.5643L5.10556 12.4777L12.1235 5.45978L16.5627 9.89894L9.54472 16.9169L6.47546 17.3999C6.39371 17.4123 6.30949 17.4197 6.22774 17.4197V17.4148ZM6.96595 13.4166L6.67116 15.3587L8.60091 15.0565L13.7609 9.89646L12.1235 8.25902L6.96595 13.4166Z" fill="#5376EA"/>
                        <path d="M15.1284 11.3308L10.6892 6.8916L12.3192 5.2616C13.216 4.36485 14.675 4.36485 15.5718 5.2616L16.7609 6.45066C17.6576 7.34741 17.6576 8.80648 16.7609 9.70323L15.1308 11.3332L15.1284 11.3308ZM13.4909 6.8916L15.1284 8.52904L15.3587 8.29866C15.4826 8.1748 15.4826 7.97414 15.3587 7.85028L14.1697 6.66122C14.0458 6.53736 13.8452 6.53736 13.7213 6.66122L13.4909 6.8916Z" fill="#5376EA"/>
                        <path d="M19.8053 18.4329H5.1947V20.4147H19.8053V18.4329Z" fill="#5376EA"/>
                        <path d="M21.5319 25H3.46809C1.55569 25 0 23.4443 0 21.5319V3.46809C0 1.55569 1.55569 0 3.46809 0H21.5319C23.4443 0 25 1.55569 25 3.46809V21.5319C25 23.4443 23.4443 25 21.5319 25ZM3.46809 1.98177C2.64814 1.98177 1.98177 2.64814 1.98177 3.46809V21.5319C1.98177 22.3519 2.64814 23.0182 3.46809 23.0182H21.5319C22.3519 23.0182 23.0182 22.3519 23.0182 21.5319V3.46809C23.0182 2.64814 22.3519 1.98177 21.5319 1.98177H3.46809Z" fill="#5376EA"/>
                      </g>
                      <defs>
                        <clipPath id="bmc-edit-name-clip">
                          <rect width="25" height="25" fill="white"/>
                        </clipPath>
                      </defs>
                    </svg>
                  </button>
                </div>
              </div>

              <div v-if="isClone" class="bmc-form-field mandatory">
                <label class="bmc-field-label" for="bmc-new-name">CLONE NAME:</label>
                <input id="bmc-new-name" v-model.trim="form.newbmcname" type="text" class="bmc-input" autocomplete="off" :class="{ 'bmc-input-error': liveNameValidationMsg }" required>
              </div>

              <div class="bmc-form-field mandatory">
                <label class="bmc-field-label" for="bmc-userid">USER ID:</label>
                <input id="bmc-userid" v-model.number="form.userid" type="number" class="bmc-input" min="0">
              </div>
            </div>


            <div class="bmc-form-row">
              <div class="bmc-form-field mandatory">
                <label class="bmc-field-label" for="bmc-username">USER NAME:</label>
                <input id="bmc-username" v-model.trim="form.username" type="text" class="bmc-input" autocomplete="username">
              </div>

              <div class="bmc-form-field mandatory">
                <label class="bmc-field-label" for="bmc-password">PASSWORD:</label>
                <div class="bmc-password-wrapper">
                  <input id="bmc-password" v-model="form.password" :type="showPassword ? 'text' : 'password'" class="bmc-input bmc-password-input" autocomplete="new-password">

                  <button type="button" class="bmc-toggle-password" :aria-label="showPassword ? 'Hide password' : 'Show password'" @click="showPassword = !showPassword">
                    <svg width="16" height="16" viewBox="0 0 14 5" fill="none" aria-hidden="true">
                      <path d="M0.5 0C3 2.5 10 3.5 13 0" stroke="#5376EA" stroke-width="2"/>
                      <path d="M1.5 1L0 3" stroke="#5376EA" stroke-width="2"/>
                      <path d="M5 2.5L4.33008 5" stroke="#5376EA" stroke-width="2"/>
                      <path d="M12 1L13.5 3" stroke="#5376EA" stroke-width="2"/>
                      <path d="M8.5 2.5L9.16992 5" stroke="#5376EA" stroke-width="2"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <div class="bmc-form-row">
              <div class="bmc-form-field">
                <label class="bmc-field-label" for="bmc-netchannel">NETWORK CHANNEL:</label>
                <input id="bmc-netchannel" v-model.number="form.netchannel" type="number" class="bmc-input" placeholder="">
              </div>

              <div class="bmc-form-field">
                <label class="bmc-field-label" for="bmc-mgmtchannel">MANAGEMENT CHANNEL:</label>
                <input id="bmc-mgmtchannel" v-model.number="form.mgmtchannel" type="number" class="bmc-input" placeholder="">
              </div>
            </div>

            <div class="bmc-form-row full-width">
              <div class="bmc-form-field">
                <label class="bmc-field-label" for="bmc-unmanaged-users">UNMANAGED BMC USERS:</label>
                <input id="bmc-unmanaged-users" v-model.trim="form.unmanaged_bmc_users" type="text" class="bmc-input"  autocomplete="off">
              </div>
            </div>

            <div class="bmc-comment-section">
              <div class="bmc-comment-header">
                <label for="bmc-comment">COMMENT:</label>
              </div>

              <div class="bmc-comment-body">
                <textarea id="bmc-comment" v-model="form.comment" class="bmc-textarea bmc-textarea-with-edit-icon" rows="3" />
                <button type="button" class="bmc-edit-icon-btn bmc-comment-edit-btn" aria-label="Open comment editor" title="Open comment editor" @click="showCommentEditor = true">
                <svg viewBox="0 0 25 25" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                  <g clip-path="url(#bmc-open-comment-clip)">
                    <path d="M21.5319 25H3.46809C1.55569 25 0 23.4443 0 21.5319V3.46809C0 1.55569 1.55569 0 3.46809 0H21.5319C23.4443 0 25 1.55569 25 3.46809V21.5319C25 23.4443 23.4443 25 21.5319 25ZM3.46809 1.98177C2.64814 1.98177 1.98177 2.64814 1.98177 3.46809V21.5319C1.98177 22.3519 2.64814 23.0182 3.46809 23.0182H21.5319C22.3519 23.0182 23.0182 22.3519 23.0182 21.5319V3.46809C23.0182 2.64814 22.3519 1.98177 21.5319 1.98177H3.46809Z" fill="#5376EA" />
                    <path d="M6.2 7.1C6.2 6.55 6.65 6.1 7.2 6.1H12.65V8.1H8.2V16.8H16.9V12.35H18.9V17.8C18.9 18.35 18.45 18.8 17.9 18.8H7.2C6.65 18.8 6.2 18.35 6.2 17.8V7.1Z" fill="#5376EA" />
                    <path d="M14.05 5.1H19.9V10.95H17.9V8.52L12.25 14.17L10.83 12.75L16.48 7.1H14.05V5.1Z" fill="#5376EA" />
                  </g>
                  <defs>
                    <clipPath id="bmc-open-comment-clip">
                      <rect width="25" height="25" fill="white"/>
                    </clipPath>
                  </defs>
                </svg>
                </button>
              </div>
            </div>

            <TextEditorModal v-if="showCommentEditor" v-model="form.comment" title="Edit BMC Comment" @close="showCommentEditor = false" />

            <div class="bmc-button-container">
              <button type="submit" class="bmc-submit-btn" :disabled="isSubmitDisabled" :class="{ 'bmc-submit-btn-disabled': isSubmitDisabled }">{{ loading ? savingText : submitText }}</button>
            </div>
          </div>
        </form>
      </template>
    </div>
  </BaseModal>
</template>
