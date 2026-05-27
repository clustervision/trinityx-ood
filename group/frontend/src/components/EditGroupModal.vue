<script setup lang="ts">

import { ref, onMounted, watch, nextTick } from 'vue'
import BaseModal from './BaseModal.vue'
import GroupFormFields from './GroupFormFields.vue'
import { fetchGroupResources, submitForm } from '@/services/api'
import { formatGroupNameDisplay, groupNameTitle } from '@/constants/groupName'

const props = defineProps({
  groupName: { type: String, required: true },
  groupList: {
    type: Array as () => string[],
    required: true
  },
  group: {
    type: Object as () => Record<string, any>,
    required: false,
    default: () => ({})
  }
})
const emit = defineEmits(['close', 'saved'])

const loading = ref(true)
const errorMsg = ref('')
const successMsg = ref('')
const fatalError = ref(false)
const submitting = ref(false)

const formData = ref({})

const bmcsetupOptions = ref<string[]>([])
const osimageOptions = ref<string[]>([])
const networkOptions = ref<string[]>([])
const bondModeOptions = ref<string[]>([])

const hints = ref<Record<string, string>>({})

const formRef = ref()
const initialSnapshot = ref('')
const recordName = ref(props.groupName)
const headerName = ref(props.groupName)

watch(
  [() => formRef.value, () => formRef.value?.form?.name],
  () => {
    const n = formRef.value?.form?.name
    headerName.value =
      n != null && String(n) !== ''
        ? String(n)
        : props.groupName
  },
  { immediate: true }
)

watch(
  () => props.groupName,
  (g) => {
    recordName.value = g
  }
)

async function captureInitialSnapshot() {

  await nextTick()
  await nextTick()

  if (
    !fatalError.value &&
    formRef.value?.comparableSnapshot
  ) {
    initialSnapshot.value =
      formRef.value.comparableSnapshot()
  }
}

onMounted(async () => {

  try {

    const resource_data = await fetchGroupResources(props.groupName)
    // console.log('Fetched group resources:', resource_data)
    bmcsetupOptions.value = resource_data.bmcsetup_list?.options || []
    osimageOptions.value = resource_data.osimage_list?.options || []
    networkOptions.value = resource_data.network_list?.options || []
    bondModeOptions.value = resource_data.bond_modes || []

    formData.value = {
      ...props.group,
      bmcsetupname:  resource_data.bmcsetup_list?.selected || '',

      osimage: resource_data.osimage_list?.selected || '',
    }
    buildHints(props.group)

  } catch (err: any) {
    errorMsg.value = err.message || 'Failed to load edit data.'
    fatalError.value = true
  } finally {
    loading.value = false
  }
  await captureInitialSnapshot()
})

function buildHints(d: any) {

  const h: Record<string, string> = {}
  for (
    const name of [
      'osimagetag',
      'provision_interface',
      'provision_fallback',
      'provision_method',
    ]
  ) {

    const s1 = d[name + '_source'] || ''
    const s2 = d['_' + name + '_source'] || ''
    if (s1 || s2) {  h[name] = '| ' + s1 + s2 }
  }
  hints.value = h
}

async function onSubmit() {

  if (!formRef.value || !initialSnapshot.value) { return }
  if (submitting.value) return
  errorMsg.value = ''
  successMsg.value = ''
  submitting.value = true

  try {
    const currentSnapshot = formRef.value.comparableSnapshot()

    if (currentSnapshot === initialSnapshot.value) {
      errorMsg.value = 'No changes to save.'
      return
    }

    const payload = formRef.value.buildPayload()

    // console.log('Submitting edit payload:', payload)

    const result = await submitForm(`/api/v1/edit`, payload)

    if (result.status === true && result.content?.message) {
      emit('saved')
      emit('close')
      return
    }
    errorMsg.value = result.content?.message || 'Update failed.'
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
          <h2 class="tx-title"> Update group <strong class="tx-title-highlight-name" :title="groupNameTitle(headerName)">{{ formatGroupNameDisplay(headerName) }}</strong></h2>
        </div>
        <GroupFormFields
          ref="formRef"
          mode="edit"
          :groupList="props.groupList"
          :initial-data="formData"
          :bmcsetup-options="bmcsetupOptions"
          :osimage-options="osimageOptions"
          :network-options="networkOptions"
          :bond-mode-options="bondModeOptions"
          :hints="hints"
          :submitting="submitting"
          submit-label="Save Changes"
          @submit="onSubmit"
        />
      </template>
    </div>

  </BaseModal>
</template>
