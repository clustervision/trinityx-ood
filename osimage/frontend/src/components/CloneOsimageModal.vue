<template>
  <BaseModal size="large" @close="$emit('close')">
    <div class="tx-form-page">
      <h2 class="tx-title" style="margin-bottom:1.25rem;">
        Clone OS Image <strong>{{ props.sourceName }}</strong>
      </h2>

      <div v-if="loadError" class="alert-danger">{{ loadError }}</div>
      <div v-if="alertMsg" :class="alertOk ? 'alert-success' : 'alert-danger'">{{ alertMsg }}</div>
      <div v-if="loadingData" class="tx-loading">Loading...</div>

      <template v-if="!loadingData && !loadError">
        <!-- Row 1: CLONE NAME, KERNEL VERSION, BARE -->
        <div class="tx-osimage-grid-bare">
          <div class="tx-field" style="flex:1;">
            <span class="tx-label">Clone Name:</span>
            <input v-model="form.newosimage" type="text" />
          </div>
          <div class="tx-field tx-field-emphasis" style="flex:1;">
            <span class="tx-label">Kernel Version:</span>
            <input v-model="form.kernelversion" type="text" />
          </div>
          <div class="tx-field tx-field-bare" style="flex:0 0 auto;">
            <span class="tx-label">Bare:</span>
            <input v-model="form.bare" type="checkbox" />
          </div>
        </div>

        <!-- Row 2: DISTRIBUTION | (OS RELEASE + PATH) -->
        <div class="tx-osimage-grid-bare">
          <div class="tx-field tx-field-emphasis tx-osimage-main-col" style="flex:1;">
            <span class="tx-label">Distribution:</span>
            <input v-model="form.distribution" type="text" />
          </div>
          <div class="tx-osimage-right-pair tx-osimage-span-2">
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
          <button type="button" class="tx-btn tx-btn-blue" :disabled="saving" @click="doClone">
            {{ saving ? 'Cloning...' : 'Clone OS Image' }}
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
            <button type="button" class="tx-btn tx-btn-blue" :disabled="saving" @click="doClone">
              {{ saving ? 'Cloning...' : 'Clone OS Image' }}
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
import { fetchOsimageCloneData, submitOsimageForm } from '../api'

const props = defineProps({
  sourceName: { type: String, required: true },
})
const emit = defineEmits(['close', 'saved'])

const loadingData = ref(true)
const loadError = ref('')
const advancedOpen = ref(false)
const saving = ref(false)
const alertMsg = ref('')
const alertOk = ref(false)

const form = reactive({
  newosimage: '',
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
  bare: false,
})

async function doClone() {
  if (!form.newosimage.trim()) {
    alertMsg.value = 'Clone name is required.'
    alertOk.value = false
    return
  }
  saving.value = true
  alertMsg.value = ''
  try {
    const fd = new FormData()
    fd.append('name', props.sourceName)
    for (const [k, v] of Object.entries(form)) {
      if (k === 'bare') {
        if (v) fd.append(k, 'on')
      } else if (v !== '' && v != null) {
        fd.append(k, v)
      }
    }
    const result = await submitOsimageForm(`/clone/${encodeURIComponent(props.sourceName)}`, fd)
    if (result.ok || result.data?.status === 'success') {
      alertMsg.value = result.data?.message || 'OS Image cloned.'
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

onMounted(async () => {
  try {
    const resp = await fetchOsimageCloneData(props.sourceName)
    if (resp.error) {
      loadError.value = resp.error
      return
    }
    const d = resp.data || {}
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
  } catch (e) {
    loadError.value = e.message || 'Failed to load clone data.'
  } finally {
    loadingData.value = false
  }
})
</script>
