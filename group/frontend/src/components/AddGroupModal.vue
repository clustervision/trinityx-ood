<script setup lang="ts">
import { ref, onMounted } from 'vue'
import BaseModal from './BaseModal.vue'
import GroupFormFields from './GroupFormFields.vue'
import { fetchResources, fetchAddData, submitForm } from '@/services/api'

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
    // const payload = await fetchAddData()
    // if (type === 'add') {
    const resource_data = await fetchResources();
    bmcsetupOptions.value = resource_data.bmcsetup_list?.options
    osimageOptions.value = resource_data.osimage_list?.options
    networkOptions.value = resource_data.network_list?.options
    bondModeOptions.value = resource_data.bond_modes
  // }
    // bmcsetupOptions.value = payload.bmcsetup_list?.options || []
    // osimageOptions.value = payload.osimage_list?.options || []
    // networkOptions.value = payload.network_list?.options || []
    // bondModeOptions.value = payload.bond_modes || []
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


<template>
  <BaseModal size="large" @close="$emit('close')">
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

