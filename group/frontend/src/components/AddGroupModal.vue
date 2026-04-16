<template>
  <BaseModal preset="addGroup" @close="$emit('close')">
    <div class="tx-form-page">
      <div v-if="errorMsg" class="alert alert-danger" role="alert">{{ errorMsg }}</div>
      <p v-if="loading" class="tx-loading">Loading...</p>

      <template v-if="!loading && !fatalError">
        <div class="tx-header">
          <h2 class="tx-title">Add Group</h2>
        </div>

        <GroupFormFields
          ref="formRef"
          mode="add"
          :initial-data="{}"
          :bmcsetup-options="bmcsetupOptions"
          :osimage-options="osimageOptions"
          :network-options="networkOptions"
          :bond-mode-options="bondModeOptions"
          submit-label="Add This Group"
          @submit="onSubmit"
        />
      </template>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import BaseModal from './BaseModal.vue'
import GroupFormFields from './GroupFormFields.vue'
import { fetchAddData, submitForm } from '../api.js'

const emit = defineEmits(['close', 'saved'])

const loading = ref(true)
const errorMsg = ref('')
const fatalError = ref(false)
const bmcsetupOptions = ref([])
const osimageOptions = ref([])
const networkOptions = ref([])
const bondModeOptions = ref([])
const formRef = ref(null)

onMounted(async () => {
  try {
    const payload = await fetchAddData()
    bmcsetupOptions.value = payload.bmcsetup_list?.options || []
    osimageOptions.value = payload.osimage_list?.options || []
    networkOptions.value = payload.network_list?.options || []
    bondModeOptions.value = payload.bond_modes || []
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
    const { ok, data } = await submitForm('/add', fd)
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
