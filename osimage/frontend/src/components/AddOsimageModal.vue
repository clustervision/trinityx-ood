<template>
  <BaseModal size="large" @close="$emit('close')">
    <div class="tx-form-page">
      <h2 class="tx-title" style="margin-bottom:1.25rem;">Add OS Image</h2>

      <div v-if="alertMsg" :class="alertOk ? 'alert-success' : 'alert-danger'">{{ alertMsg }}</div>

      <div class="tx-osimage-main-row">
        <div class="tx-field tx-field-emphasis tx-osimage-main-col">
          <span class="tx-label">Name:</span>
          <input v-model="form.name" type="text" />
        </div>
        <div class="tx-field tx-field-emphasis tx-osimage-main-col">
          <span class="tx-label">Kernel Version:</span>
          <input v-model="form.kernelversion" type="text" />
        </div>
      </div>

      <div class="tx-osimage-main-row">
        <div class="tx-field tx-field-emphasis tx-osimage-main-col">
          <span class="tx-label">Distribution:</span>
          <input v-model="form.distribution" type="text" />
        </div>
        <div class="tx-osimage-right-pair tx-osimage-main-col">
          <div class="tx-field tx-field-emphasis">
            <span class="tx-label">OS Release:</span>
            <input v-model="form.osrelease" type="text" />
          </div>
          <div class="tx-field tx-osimage-path-field">
            <span class="tx-label">Path:</span>
            <input v-model="form.path" type="text" />
          </div>
        </div>
      </div>

      <div class="tx-osimage-grid-full">
        <div class="tx-field" style="width:100%;">
          <span class="tx-label">Grab File Systems:</span>
          <input v-model="form.grab_filesystems" type="text" style="flex:1;" />
        </div>
      </div>

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
        <button type="button" class="tx-btn tx-btn-blue" :disabled="saving" @click="doAdd">
          {{ saving ? 'Saving...' : 'Add OS Image' }}
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
              <OsimageCommentField v-model="form.comment" />
            </div>
          </div>
        </div>

        <div class="tx-form-footer-right">
          <button type="button" class="tx-btn tx-btn-blue" :disabled="saving" @click="doAdd">
            {{ saving ? 'Saving...' : 'Add OS Image' }}
          </button>
        </div>
      </template>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, reactive } from 'vue'
import BaseModal from './BaseModal.vue'
import OsimageCommentField from './OsimageCommentField.vue'
import { fetchOsimages, submitOsimageForm } from '../api'
import { validateOsimageNameInput } from '../constants/osimageName'

const emit = defineEmits(['close', 'saved'])

const advancedOpen = ref(false)
const saving = ref(false)
const alertMsg = ref('')
const alertOk = ref(false)

const form = reactive({
  name: '',
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
})

async function doAdd() {
  const enteredName = String(form.name || '').trim()
  if (!enteredName) {
    alertMsg.value = 'Name is required.'
    alertOk.value = false
    return
  }
  const nameCheck = validateOsimageNameInput(enteredName)
  if (!nameCheck.ok) {
    alertMsg.value = nameCheck.message
    alertOk.value = false
    return
  }
  saving.value = true
  alertMsg.value = ''
  try {
    // Frontend guard: prevent creating duplicates based on current list data.
    const list = await fetchOsimages()
    const wanted = enteredName.toLowerCase()
    const exists = (list.images || []).some((row) => {
      const raw = String(row?.name || '')
      const normalized = raw.replace(/\s*\*\s*$/, '').trim().toLowerCase()
      return normalized === wanted
    })
    if (exists) {
      alertMsg.value = `OS Image "${enteredName}" already exists.`
      alertOk.value = false
      return
    }

    const fd = new FormData()
    for (const [k, v] of Object.entries(form)) {
      if (v == null) continue
      if (typeof v === 'string' && v.trim() === '') continue
      fd.append(k, v)
    }
    const result = await submitOsimageForm('/add', fd)
    if (result.ok || result.data?.status === 'success') {
      alertMsg.value = result.data?.message || 'OS Image created.'
      alertOk.value = true
      setTimeout(() => emit('saved'), 600)
    } else {
      alertMsg.value = result.data?.message || `Error (${result.status})`
      alertOk.value = false
    }
  } catch (e) {
    const raw = String(e?.message || '').trim()
    alertMsg.value = raw || 'Network error.'
    alertOk.value = false
  } finally {
    saving.value = false
  }
}
</script>
