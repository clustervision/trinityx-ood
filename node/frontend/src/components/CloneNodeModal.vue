<template>
  <BaseModal size="large" @close="$emit('close')">
    <div class="tx-form-page">
      <div v-if="errorMsg" class="alert alert-danger" role="alert">{{ errorMsg }}</div>
      <p v-if="loading" class="tx-loading">Loading...</p>

      <template v-if="!loading && !fatalError">
        <div class="tx-header">
          <h2 class="tx-title tx-clone-page-title">
            <span class="tx-clone-title-label">Clone Node</span>
            <span class="tx-clone-source-node-name">{{ cloneSourceDisplayName }}</span>
          </h2>
        </div>

        <NodeFormFields
          ref="formRef"
          mode="clone"
          :initial-data="formData"
          :group-options="groupOptions"
          :switch-options="switchOptions"
          :bmcsetup-options="bmcsetupOptions"
          :osimage-options="osimageOptions"
          :cloudname-options="cloudnameOptions"
          :network-options="networkOptions"
          :bond-mode-options="bondModeOptions"
          :hints="hints"
          :get-inventory-ipv4="getInventoryIpv4"
          :inventory-exclude-node-name="inventoryExcludeNodeName"
          submit-label="Clone Node"
          @submit="onSubmit"
        />
      </template>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import BaseModal from './BaseModal.vue'
import NodeFormFields from './NodeFormFields.vue'
import { fetchNodeCloneData, submitNodeForm } from '../api.js'

const props = defineProps({
  sourceNodeName: { type: String, required: true },
  getInventoryIpv4: { type: Function, default: null },
  inventoryExcludeNodeName: { type: String, default: '' },
})
const emit = defineEmits(['close', 'saved'])

const loading = ref(true)
const errorMsg = ref('')
const fatalError = ref(false)
const formData = ref({})
const groupOptions = ref([])
const switchOptions = ref([])
const bmcsetupOptions = ref([])
const osimageOptions = ref([])
const cloudnameOptions = ref([])
const networkOptions = ref([])
const bondModeOptions = ref([])
const hints = ref({})
const formRef = ref(null)

const cloneSourceDisplayName = computed(() => {
  const n = formData.value?.name
  if (n != null && String(n).trim() !== '') return String(n)
  return props.sourceNodeName || ''
})

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
    const payload = await fetchNodeCloneData(props.sourceNodeName)
    if (!payload.data || payload.data.name == null || payload.data.name === '') {
      errorMsg.value = 'This node is not available at this moment.'
      fatalError.value = true
      return
    }
    formData.value = payload.data
    groupOptions.value = optionList(payload, 'group_list', 'groups', 'groupname_list')
    switchOptions.value = optionList(payload, 'switch_list', 'switchname_list', 'switches')
    bmcsetupOptions.value = optionList(payload, 'bmcsetup_list', 'bmcsetupname_list')
    osimageOptions.value = optionList(payload, 'osimage_list', 'osimage')
    cloudnameOptions.value = optionList(
      payload,
      'cloudname_list',
      'cloud_name_list',
      'cloud_list',
    )
    networkOptions.value = optionList(payload, 'network_list', 'network')
    bondModeOptions.value = payload.bond_modes || payload.bond_mode_list?.options || []
    hints.value = payload.hints || payload.form_hints || {}
  } catch (err) {
    errorMsg.value = err.message || 'Failed to load clone data.'
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
    const { ok, data, status } = await submitNodeForm(`/clone/${encodeURIComponent(props.sourceNodeName)}`, fd)
    if (ok || data.status === 'success') {
      emit('saved')
      emit('close')
    } else {
      errorMsg.value =
        data.message || data.error || (status ? `Clone failed (HTTP ${status}).` : 'Clone failed.')
    }
  } catch (err) {
    errorMsg.value = err.message || 'Network error.'
  }
}
</script>
