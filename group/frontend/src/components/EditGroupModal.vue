<template>
  <BaseModal size="large" @close="$emit('close')">
    <div class="tx-form-page">
      <div v-if="errorMsg" class="alert alert-danger" role="alert">{{ errorMsg }}</div>
      <p v-if="loading" class="tx-loading">Loading...</p>

      <template v-if="!loading && !fatalError">
        <div class="tx-header">
          <h2 class="tx-title">Update group <strong class="tx-title-highlight-name">{{ groupName }}</strong></h2>
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
import { ref, onMounted } from 'vue'
import BaseModal from './BaseModal.vue'
import GroupFormFields from './GroupFormFields.vue'
import { fetchEditData, submitForm } from '../api.js'

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

async function onSubmit() {
  if (!formRef.value) return
  const fd = formRef.value.buildFormData()
  errorMsg.value = ''
  try {
    const { ok, data } = await submitForm(`/edit/${encodeURIComponent(props.groupName)}`, fd)
    if (ok || data.status === 'success') {
      emit('saved')
      emit('close')
    } else {
      errorMsg.value = data.message || 'Update failed.'
    }
  } catch (err) {
    errorMsg.value = err.message || 'Network error.'
  }
}
</script>
