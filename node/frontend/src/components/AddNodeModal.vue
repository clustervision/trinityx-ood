<template>
  <BaseModal size="large" @close="$emit('close')">
    <div class="tx-form-page">
      <div v-if="errorMsg" class="alert alert-danger" role="alert">{{ errorMsg }}</div>
      <p v-if="loading" class="tx-loading">Loading...</p>

      <template v-if="!loading && !fatalError">
        <div class="tx-header">
          <h2 class="tx-title">Add Node</h2>
        </div>

        <NodeFormFields
          ref="formRef"
          :group-options="groupOptions"
          :switch-options="switchOptions"
          :bmcsetup-options="bmcsetupOptions"
          :osimage-options="osimageOptions"
          :network-options="networkOptions"
          :bond-mode-options="bondModeOptions"
          :hints="hints"
          submit-label="Add Node"
          @submit="onSubmit"
        />
      </template>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import BaseModal from './BaseModal.vue'
import NodeFormFields from './NodeFormFields.vue'
import { fetchNodeAddData, submitNodeForm } from '../api.js'

const emit = defineEmits(['close', 'saved'])

const loading = ref(true)
const errorMsg = ref('')
const fatalError = ref(false)
const groupOptions = ref([])
const switchOptions = ref([])
const bmcsetupOptions = ref([])
const osimageOptions = ref([])
const networkOptions = ref([])
const bondModeOptions = ref([])
const hints = ref({})
const formRef = ref(null)

function optionList(payload, ...keys) {
  for (const k of keys) {
    const v = payload[k]
    if (Array.isArray(v)) return v
    if (v && typeof v === 'object' && Array.isArray(v.options)) return v.options
  }
  return []
}

onMounted(async () => {
  try {
    const payload = await fetchNodeAddData()
    groupOptions.value = optionList(payload, 'group_list', 'groups', 'groupname_list')
    switchOptions.value = optionList(payload, 'switch_list', 'switchname_list', 'switches')
    bmcsetupOptions.value = optionList(payload, 'bmcsetup_list', 'bmcsetupname_list')
    osimageOptions.value = optionList(payload, 'osimage_list', 'osimage')
    networkOptions.value = optionList(payload, 'network_list', 'network')
    bondModeOptions.value = payload.bond_modes || payload.bond_mode_list?.options || []
    hints.value = payload.hints || payload.form_hints || {}
  } catch (err) {
    errorMsg.value = err.message || 'Failed to load form data.'
    fatalError.value = true
  } finally {
    loading.value = false
  }
})

async function onSubmit() {
  if (!formRef.value) return
  const fd = formRef.value.buildFormData()
  errorMsg.value = ''
  try {
    const { ok, data } = await submitNodeForm('/add', fd)
    if (ok || data.status === 'success') {
      emit('saved')
      emit('close')
    } else {
      errorMsg.value = data.message || 'Add failed.'
    }
  } catch (err) {
    errorMsg.value = err.message || 'Network error.'
  }
}
</script>
