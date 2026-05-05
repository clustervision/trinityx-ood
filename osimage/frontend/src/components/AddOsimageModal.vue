<template>
  <BaseModal size="large" @close="$emit('close')">
    <div class="tx-form-page">
      <h2 class="tx-title" style="margin-bottom:1.25rem;">Add OS Image</h2>

      <div v-if="alertMsg" :class="alertOk ? 'alert-success' : 'alert-danger'">{{ alertMsg }}</div>

      <!-- Row 1: NAME, KERNEL VERSION -->
      <div class="tx-osimage-grid-top">
        <div class="tx-field" style="flex:1;">
          <span class="tx-label">Name:</span>
          <input v-model="form.name" type="text" />
        </div>
        <div class="tx-field" style="flex:1;">
          <span class="tx-label">Kernel Version:</span>
          <input v-model="form.kernelversion" type="text" />
        </div>
      </div>

      <!-- Row 2: DISTRIBUTION, OS RELEASE, PATH -->
      <div class="tx-osimage-grid-row3">
        <div class="tx-field" style="flex:1;">
          <span class="tx-label">Distribution:</span>
          <input v-model="form.distribution" type="text" />
        </div>
        <div class="tx-field" style="flex:0 0 auto;">
          <span class="tx-label">OS Release:</span>
          <input v-model="form.osrelease" type="text" style="max-width:100px;" />
        </div>
        <div class="tx-field" style="flex:1;">
          <span class="tx-label">Path:</span>
          <input v-model="form.path" type="text" />
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
          <span class="tx-advanced-chevron"></span>
        </button>
        <button type="button" class="tx-btn tx-btn-blue" :disabled="saving" @click="doAdd">
          {{ saving ? 'Saving...' : 'Add OS Image' }}
        </button>
      </div>

      <!-- Expanded: Advanced toggle, fields, then submit -->
      <template v-else>
        <div style="margin-top:1rem;">
          <button
            type="button"
            class="tx-btn tx-btn-blue tx-btn-advanced-toggle"
            @click="advancedOpen = false"
          >
            Advanced
            <span class="tx-advanced-chevron is-open"></span>
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
import { submitOsimageForm } from '../api'

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
  if (!form.name.trim()) {
    alertMsg.value = 'Name is required.'
    alertOk.value = false
    return
  }
  saving.value = true
  alertMsg.value = ''
  try {
    const fd = new FormData()
    for (const [k, v] of Object.entries(form)) {
      if (v !== '' && v != null) fd.append(k, v)
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
    alertMsg.value = e.message || 'Network error.'
    alertOk.value = false
  } finally {
    saving.value = false
  }
}
</script>
