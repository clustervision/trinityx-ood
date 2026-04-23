<template>
  <BaseModal size="large" @close="$emit('close')">
    <div class="tx-form-page">
      <div v-if="errorMsg" class="alert alert-danger" role="alert">{{ errorMsg }}</div>
      <p v-if="loading" class="tx-loading">Loading...</p>

      <template v-if="!loading && !fatalError">
        <div class="tx-header">
          <h2 class="tx-title">Update group <strong class="tx-title-highlight-name">{{ headerName }}</strong></h2>
        </div>

        <GroupFormFields
          ref="formRef"
          mode="edit"
          :initial-data="formData"
          :bmcsetup-options="bmcsetupOptions"
          :osimage-options="osimageOptions"
          :network-options="networkOptions"
          :bond-mode-options="bondModeOptions"
          :hints="hints"
          submit-label="Save Changes"
          @submit="onSubmit"
        />
      </template>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import BaseModal from './BaseModal.vue'
import GroupFormFields from './GroupFormFields.vue'
import { fetchEditData, submitForm, submitRename } from '../api.js'

const props = defineProps({
  groupName: { type: String, required: true },
})
const emit = defineEmits(['close', 'saved'])

const loading = ref(true)
const errorMsg = ref('')
const fatalError = ref(false)
const formData = ref({})
const bmcsetupOptions = ref([])
const osimageOptions = ref([])
const networkOptions = ref([])
const bondModeOptions = ref([])
const hints = ref({})
const formRef = ref(null)
const initialSnapshot = ref(null)
/** Server record key for /rename and /edit; updated after a successful rename in this session. */
const recordName = ref(props.groupName)
const headerName = ref(props.groupName)

watch(
  [() => formRef.value, () => formRef.value?.form?.name],
  () => {
    const n = formRef.value?.form?.name
    headerName.value = n != null && String(n) !== '' ? String(n) : props.groupName
  },
  { immediate: true },
)

watch(
  () => props.groupName,
  (g) => {
    recordName.value = g
  },
)

async function captureInitialSnapshot() {
  await nextTick()
  await nextTick()
  if (!fatalError.value && formRef.value?.comparableSnapshot) {
    initialSnapshot.value = formRef.value.comparableSnapshot()
    recordName.value = props.groupName
  }
}

onMounted(async () => {
  try {
    const payload = await fetchEditData(props.groupName)
    if (!payload.data || !payload.data.name) {
      errorMsg.value = 'This group is not available at this moment.'
      fatalError.value = true
      return
    }
    formData.value = payload.data
    bmcsetupOptions.value = payload.bmcsetup_list?.options || []
    osimageOptions.value = payload.osimage_list?.options || []
    networkOptions.value = payload.network_list?.options || []
    bondModeOptions.value = payload.bond_modes || []
    buildHints(payload.data)
  } catch (err) {
    errorMsg.value = err.message || 'Failed to load edit data.'
    fatalError.value = true
  } finally {
    loading.value = false
  }
  await captureInitialSnapshot()
})

function buildHints(d) {
  const h = {}
  for (const name of ['osimagetag', 'provision_interface', 'provision_fallback', 'provision_method']) {
    const s1 = d[name + '_source'] || ''
    const s2 = d['_' + name + '_source'] || ''
    if (s1 || s2) h[name] = '| ' + s1 + s2
  }
  hints.value = h
}

function stripName(obj) {
  const { name: _n, ...rest } = obj
  return rest
}

function restChanged(snap, initial) {
  return JSON.stringify(stripName(snap)) !== JSON.stringify(stripName(initial))
}

function isSuccess(res) {
  return res.ok || res.data?.status === 'success'
}

async function onSubmit() {
  if (!formRef.value || !initialSnapshot.value) return
  const snap = formRef.value.comparableSnapshot()
  const initial = initialSnapshot.value

  if (JSON.stringify(snap) === JSON.stringify(initial)) {
    errorMsg.value = 'No changes to save.'
    return
  }

  const nameChanged = snap.name !== initial.name
  const restDirty = restChanged(snap, initial)

  if (nameChanged && !snap.name) {
    errorMsg.value = 'Group name cannot be empty.'
    return
  }

  errorMsg.value = ''

  try {
    if (nameChanged && !restDirty) {
      const res = await submitRename(recordName.value, snap.name)
      if (!isSuccess(res)) {
        errorMsg.value = res.data?.message || 'Rename failed.'
        return
      }
      emit('saved')
      emit('close')
      return
    }

    if (!nameChanged && restDirty) {
      const fd = formRef.value.buildFormData({ nameForPayload: recordName.value })
      const res = await submitForm(`/edit/${encodeURIComponent(recordName.value)}`, fd)
      if (!isSuccess(res)) {
        errorMsg.value = res.data?.message || 'Update failed.'
        return
      }
      emit('saved')
      emit('close')
      return
    }

    if (nameChanged && restDirty) {
      const resRename = await submitRename(recordName.value, snap.name)
      if (!isSuccess(resRename)) {
        errorMsg.value = resRename.data?.message || 'Rename failed.'
        return
      }
      recordName.value = snap.name
      const fd = formRef.value.buildFormData({ nameForPayload: recordName.value })
      const resEdit = await submitForm(`/edit/${encodeURIComponent(recordName.value)}`, fd)
      if (!isSuccess(resEdit)) {
        errorMsg.value = resEdit.data?.message || 'Update failed after rename.'
        return
      }
      emit('saved')
      emit('close')
    }
  } catch (err) {
    errorMsg.value = err.message || 'Network error.'
  }
}
</script>
