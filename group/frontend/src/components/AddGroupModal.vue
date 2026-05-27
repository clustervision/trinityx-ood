<script setup lang="ts">

import { ref, onMounted } from 'vue'
import BaseModal from './BaseModal.vue'
import GroupFormFields from './GroupFormFields.vue'
import { fetchResources, submitForm } from '@/services/api'


const props = defineProps({
  groupList: {
    type: Array as () => string[],
    required: true
  }
})


const emit = defineEmits(['close', 'saved'])

const loading = ref(true)
const errorMsg = ref('')
const fatalError = ref(false)
const submitting = ref(false)

const bmcsetupOptions = ref<string[]>([])
const osimageOptions = ref<string[]>([])
const networkOptions = ref<string[]>([])
const bondModeOptions = ref<string[]>([])

const formRef = ref()

onMounted(async () => {
  try {
    const resource_data = await fetchResources()

    bmcsetupOptions.value = resource_data.bmcsetup_list?.options || []
    osimageOptions.value = resource_data.osimage_list?.options || []
    networkOptions.value = resource_data.network_list?.options || []
    bondModeOptions.value = resource_data.bond_modes || []
  } catch (err: any) {
    errorMsg.value = err.message || 'Failed to load form data.'
    fatalError.value = true
  } finally {
    loading.value = false
  }
})
const successMsg = ref('')
async function onSubmit() {
  if (!formRef.value) return
  if (submitting.value) return

  errorMsg.value = ''
  submitting.value = true

  try {
    const payload = formRef.value.buildPayload()
    // console.log('Submitting payload:', payload)
    const result = await submitForm('/api/v1/add', payload)

    if (result.status === true && result.content?.message) {
      emit('saved')
      emit('close')
    } else {
      errorMsg.value = result.content?.message
    }

 } catch (err: unknown) {
    if (err instanceof Error) {
      errorMsg.value = err.message
    } else {
      errorMsg.value = 'Unknown error occurred'
    }
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <BaseModal size="large" @close="$emit('close')">

    <div class="tx-form-page">

      <div v-if="errorMsg" class="alert alert-danger" role="alert">{{ errorMsg }}</div>
      <div v-if="successMsg" class="alert alert-success" role="alert">{{ successMsg }}</div>
      <p v-if="loading" class="tx-loading">Loading...</p>

      <template v-if="!loading && !fatalError">

        <div class="tx-header">
          <h2 class="tx-title">Add Group</h2>
        </div>

        <GroupFormFields
          ref="formRef"
          mode="add"
          :groupList="props.groupList"
          :initial-data="{}"
          :bmcsetup-options="bmcsetupOptions"
          :osimage-options="osimageOptions"
          :network-options="networkOptions"
          :bond-mode-options="bondModeOptions"
          :submitting="submitting"
          submit-label="Add This Group"
          @submit="onSubmit"
        />

      </template>

    </div>
  </BaseModal>
</template>
