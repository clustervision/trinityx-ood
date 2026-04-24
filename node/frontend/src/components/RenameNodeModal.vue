<template>
  <BaseModal size="small" @close="$emit('close')">
    <div class="tx-form-page tx-rename-page">
      <div class="tx-header">
        <h2 class="tx-title">Rename Node</h2>
      </div>
      <div v-if="errorMsg" class="alert alert-danger" role="alert">{{ errorMsg }}</div>
      <p v-if="loading" class="tx-loading">Loading...</p>
      <form v-else class="tx-rename-form" @submit.prevent="onSubmit">
        <div class="tx-field" style="width:100%;max-width:100%">
          <span class="tx-label">Current name:</span>
          <input type="text" :value="currentName" readonly style="flex:1" />
        </div>
        <div class="tx-field" style="width:100%;max-width:100%">
          <span class="tx-label">New name:</span>
          <input
            v-model="newName"
            type="text"
            required
            maxlength="100"
            style="flex:1"
            autocomplete="off"
            @keypress="noSpaces"
          />
        </div>
        <div class="tx-form-footer tx-rename-form-footer" style="margin-top:1rem">
          <span></span>
          <div class="tx-rename-footer-actions">
            <button type="button" class="tx-btn tx-btn-outline-blue" :disabled="submitting" @click="$emit('close')">
              Cancel
            </button>
            <button type="submit" class="tx-btn tx-btn-blue" :disabled="submitting || !canSubmit">
              Rename
            </button>
          </div>
        </div>
      </form>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import BaseModal from './BaseModal.vue'
import { fetchNodeRenameData, submitNodeForm } from '../api.js'

const props = defineProps({
  currentName: { type: String, required: true },
})

const emit = defineEmits(['close', 'success'])

const loading = ref(true)
const errorMsg = ref('')
const newName = ref('')
const submitting = ref(false)

const canSubmit = computed(() => {
  const t = (newName.value || '').trim()
  return t.length > 0 && t !== props.currentName
})

async function load() {
  loading.value = true
  errorMsg.value = ''
  newName.value = ''
  try {
    const payload = await fetchNodeRenameData(props.currentName)
    const d = payload.data || {}
    newName.value = d.newname != null ? String(d.newname) : ''
  } catch (e) {
    errorMsg.value = e.message || 'Could not load rename data.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  load()
})

watch(
  () => props.currentName,
  () => {
    load()
  },
)

function noSpaces(e) {
  if (e.charCode === 32) e.preventDefault()
}

async function onSubmit() {
  const next = (newName.value || '').trim()
  if (!next || next === props.currentName) return
  errorMsg.value = ''
  submitting.value = true
  const fd = new FormData()
  fd.append('name', props.currentName)
  fd.append('newname', next)
  try {
    const { ok, status, data } = await submitNodeForm(
      `/rename/${encodeURIComponent(props.currentName)}`,
      fd,
    )
    if (ok && (status === 204 || data?.status === 'success')) {
      emit('success', next)
      emit('close')
    } else {
      errorMsg.value = data?.message || `Rename failed (${status})`
    }
  } catch (e) {
    errorMsg.value = e.message || 'Network error.'
  } finally {
    submitting.value = false
  }
}
</script>
