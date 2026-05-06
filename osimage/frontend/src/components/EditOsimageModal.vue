<template>
  <BaseModal size="large" @close="$emit('close')">
    <div class="tx-form-page">
      <h2 class="tx-title" style="margin-bottom:1.25rem;">
        Update OS Image <strong>{{ props.imageName }}</strong>
      </h2>

      <div v-if="loadError" class="alert-danger">{{ loadError }}</div>
      <div v-if="alertMsg" :class="alertOk ? 'alert-success' : 'alert-danger'">{{ alertMsg }}</div>
      <div v-if="loadingData" class="tx-loading">Loading...</div>

      <template v-if="!loadingData && !loadError">
        <!-- Rows 1–2: one grid so column 2 (Kernel / OS Release) shares tracks -->
        <div class="tx-osimage-grid-bare">
          <div class="tx-field tx-field-name-with-rename" style="flex:1;">
            <span class="tx-label">Name:</span>
            <div class="tx-name-input-wrap">
              <template v-if="!renaming">
                <input
                  type="text"
                  class="tx-name-input-readonly"
                  :value="currentName"
                  readonly
                />
                <button
                  type="button"
                  class="tx-btn-rename"
                  title="Edit name"
                  aria-label="Edit name"
                  @click="startRename"
                >
                  <img :src="renameIconUrl" alt="" width="20" height="20" />
                </button>
              </template>
              <template v-else>
                <input
                  v-model="newName"
                  type="text"
                  class="tx-name-input-editing"
                  aria-label="OS image name"
                  @keyup.escape="cancelRename"
                />
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
          <div class="tx-field tx-field-emphasis" style="flex:1;">
            <span class="tx-label">Kernel Version:</span>
            <input v-model="form.kernelversion" type="text" />
          </div>
          <div class="tx-field tx-field-bare" style="flex:0 0 auto;">
            <span class="tx-label">Bare:</span>
            <input v-model="form.bare" type="checkbox" />
          </div>
          <div class="tx-field tx-field-emphasis tx-osimage-main-col tx-osimage-bare-r2" style="flex:1;">
            <span class="tx-label">Distribution:</span>
            <input v-model="form.distribution" type="text" />
          </div>
          <div class="tx-osimage-right-pair tx-osimage-span-2 tx-osimage-bare-r2">
            <div class="tx-field tx-field-emphasis">
              <span class="tx-label">OS Release:</span>
              <input v-model="form.osrelease" type="text" />
            </div>
            <div class="tx-field">
              <span class="tx-label">Path:</span>
              <input v-model="form.path" type="text" />
            </div>
          </div>
        </div>

        <!-- Full-width: GRAB FILE SYSTEMS -->
        <div class="tx-osimage-grid-full">
          <div class="tx-field" style="width:100%;">
            <span class="tx-label">Grab File Systems:</span>
            <input v-model="form.grab_filesystems" type="text" style="flex:1;" />
          </div>
        </div>

        <!-- Full-width: GRAB EXCLUDE -->
        <div class="tx-osimage-grid-full">
          <div class="tx-field" style="width:100%;">
            <span class="tx-label">Grab Exclude:</span>
            <input v-model="form.grab_exclude" type="text" style="flex:1;" />
          </div>
        </div>

        <!-- Collapsed: footer with Advanced + Submit in one row -->
        <div v-if="!advancedOpen" class="tx-form-footer">
          <button
            type="button"
            class="tx-btn tx-btn-outline-blue tx-btn-advanced-toggle"
            @click="advancedOpen = true"
          >
            Advanced
            <span class="tx-advanced-chevron tx-advanced-chevron-blue"></span>
          </button>
          <button type="button" class="tx-btn tx-btn-blue" :disabled="saving" @click="doSave">
            {{ saving ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>

        <!-- Expanded: Advanced toggle, fields, then submit -->
        <template v-else>
          <div class="tx-form-footer tx-form-footer-no-submit">
            <button
              type="button"
              class="tx-btn tx-btn-outline-blue tx-btn-advanced-toggle"
              @click="advancedOpen = false"
            >
              Advanced
              <span class="tx-advanced-chevron tx-advanced-chevron-blue is-open"></span>
            </button>
          </div>

          <div class="tx-advanced-body">
            <div class="tx-adv-grid">
              <div class="tx-adv-full">
                <div class="tx-field" style="width:100%;">
                  <span class="tx-label">Kernel Options:</span>
                  <input v-model="form.kerneloptions" type="text" style="flex:1;" />
                </div>
              </div>
              <div class="tx-adv-full">
                <div class="tx-field" style="width:100%;">
                  <span class="tx-label">Kernel Modules:</span>
                  <input v-model="form.kernelmodules" type="text" style="flex:1;" />
                </div>
              </div>
              <div class="tx-adv-full">
                <div class="tx-field" style="width:100%;">
                  <span class="tx-label">Kernel File:</span>
                  <input v-model="form.kernelfile" type="text" style="flex:1;" />
                </div>
              </div>
              <div class="tx-adv-full">
                <div class="tx-field" style="width:100%;">
                  <span class="tx-label">Intrd File:</span>
                  <input v-model="form.initrdfile" type="text" style="flex:1;" />
                </div>
              </div>
              <div class="tx-adv-full">
                <div class="tx-field" style="width:100%;">
                  <span class="tx-label">Image File:</span>
                  <input v-model="form.imagefile" type="text" style="flex:1;" />
                </div>
              </div>
              <div class="tx-adv-full">
                <div class="tx-field" style="width:100%;">
                  <span class="tx-label">Tag:</span>
                  <input v-model="form.tag" type="text" style="flex:1;" />
                </div>
              </div>
              <div class="tx-adv-full">
                <div class="tx-field-block" style="width:100%;">
                  <div class="tx-label-row">
                    <span class="tx-label">Comment:</span>
                  </div>
                  <textarea v-model="form.comment" rows="4"></textarea>
                </div>
              </div>
            </div>
          </div>

          <div class="tx-form-footer-right">
            <button type="button" class="tx-btn tx-btn-blue" :disabled="saving" @click="doSave">
              {{ saving ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </template>
      </template>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import BaseModal from './BaseModal.vue'
import { fetchOsimageEditData, submitOsimageForm } from '../api'
import { messageForDisplay } from '../utils/sanitizeUserMessage'

const props = defineProps({
  imageName: { type: String, required: true },
})
const emit = defineEmits(['close', 'saved', 'renamed'])

const loadingData = ref(true)
const loadError = ref('')
const advancedOpen = ref(false)
const saving = ref(false)
const alertMsg = ref('')
const alertOk = ref(false)
const currentName = ref('')
const renaming = ref(false)
const newName = ref('')
const renameIconUrl = `${import.meta.env.BASE_URL}icons/icon-rename.png`

const form = reactive({
  kernelversion: '',
  distribution: '',
  osrelease: '',
  path: '',
  grab_filesystems: '',
  grab_exclude: '',
  kerneloptions: '',
  kernelmodules: '',
  kernelfile: '',
  initrdfile: '',
  imagefile: '',
  comment: '',
  tag: '',
  bare: false,
})

function startRename() {
  newName.value = currentName.value
  renaming.value = true
}

function cancelRename() {
  renaming.value = false
  newName.value = ''
}

/** Inline rename is committed together with Save (same pattern as ../node Edit Node). */
async function commitPendingRename() {
  if (!renaming.value) return true
  const trimmed = newName.value.trim()
  if (!trimmed || trimmed === currentName.value) {
    cancelRename()
    return true
  }
  const fd = new FormData()
  fd.append('name', currentName.value)
  fd.append('newname', trimmed)
  const result = await submitOsimageForm(`/rename/${encodeURIComponent(currentName.value)}`, fd)
  if (result.ok || result.status === 204 || result.data?.status === 'success') {
    currentName.value = trimmed
    renaming.value = false
    newName.value = ''
    emit('renamed', trimmed)
    return true
  }
  alertMsg.value = result.data?.message || `Rename failed (${result.status})`
  alertOk.value = false
  return false
}

async function doSave() {
  saving.value = true
  alertMsg.value = ''
  try {
    const renameOk = await commitPendingRename()
    if (!renameOk) return

    const fd = new FormData()
    fd.append('name', currentName.value)
    for (const [k, v] of Object.entries(form)) {
      if (k === 'bare') {
        if (v) fd.append(k, 'on')
      } else if (v !== '' && v != null) {
        fd.append(k, v)
      }
    }
    const result = await submitOsimageForm(`/edit/${encodeURIComponent(currentName.value)}`, fd)
    if (result.ok || result.status === 204 || result.data?.status === 'success') {
      alertMsg.value = result.data?.message || 'OS Image updated.'
      alertOk.value = true
      setTimeout(() => emit('saved'), 600)
    } else {
      alertMsg.value = result.data?.message || `Error (${result.status})`
      alertOk.value = false
    }
  } catch (e) {
    alertMsg.value = messageForDisplay(e.message || 'Network error.')
    alertOk.value = false
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const resp = await fetchOsimageEditData(props.imageName)
    if (resp.error) {
      loadError.value = messageForDisplay(resp.error)
      return
    }
    const d = resp.data || {}
    currentName.value = d.name || props.imageName
    form.kernelversion = d.kernelversion || ''
    form.distribution = d.distribution || ''
    form.osrelease = d.osrelease || ''
    form.path = d.path || ''
    form.grab_filesystems = d.grab_filesystems || ''
    form.grab_exclude = d.grab_exclude || ''
    form.kerneloptions = d.kerneloptions || ''
    form.kernelmodules = d.kernelmodules || ''
    form.kernelfile = d.kernelfile || ''
    form.initrdfile = d.initrdfile || ''
    form.imagefile = d.imagefile || ''
    form.comment = d.comment || ''
    form.tag = d.tag || ''
  } catch (e) {
    loadError.value = messageForDisplay(e.message || 'Failed to load OS image data.')
  } finally {
    loadingData.value = false
  }
})
</script>
