<template>
  <BaseModal size="large" @close="$emit('close')">
    <div class="tx-form-page">
      <div v-if="errorMsg" class="alert alert-danger" role="alert">{{ errorMsg }}</div>
      <p v-if="loading" class="tx-loading">Loading...</p>

      <template v-if="!loading && !fatalError">
        <div class="tx-header">
          <h2 class="tx-title">Edit Node</h2>
        </div>

        <NodeFormFields
          ref="formRef"
          mode="edit"
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
          submit-label="Save Changes"
          @submit="onSubmit"
        />
      </template>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import BaseModal from './BaseModal.vue'
import NodeFormFields from './NodeFormFields.vue'
import { fetchNodeEditData, submitNodeForm } from '../api.js'

const props = defineProps({
  nodeName: { type: String, required: true },
  getInventoryIpv4: { type: Function, default: null },
  inventoryExcludeNodeName: { type: String, default: '' },
})
const emit = defineEmits(['close', 'saved', 'renamed'])

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
/** After a successful /rename, subsequent /edit/ must use the new name (URL + payload) even if parent prop is stale. */
const editTargetName = ref('')

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
    const payload = await fetchNodeEditData(props.nodeName)
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
    errorMsg.value = err.message || 'Failed to load edit data.'
    fatalError.value = true
  } finally {
    loading.value = false
  }
})

watch(
  () => props.nodeName,
  (n) => {
    if (n) editTargetName.value = n
  },
  { immediate: true },
)

async function onSubmit() {
  if (!formRef.value) return
  errorMsg.value = ''
  const didRename = formRef.value.getPendingRename?.() ?? null
  let recordName = editTargetName.value
  try {
    if (didRename) {
      const rfd = new FormData()
      rfd.append('name', didRename.oldName)
      rfd.append('newname', didRename.newName)
      const re = await submitNodeForm(
        `/rename/${encodeURIComponent(didRename.oldName)}`,
        rfd,
      )
      if (!re.ok) {
        errorMsg.value = re.data?.message || `Rename failed (${re.status})`
        return
      }
      formRef.value.applyRenamedInForm(didRename.newName)
      editTargetName.value = didRename.newName
      recordName = didRename.newName
    }
    const fd = formRef.value.buildFormData()
    const { ok, data } = await submitNodeForm(`/edit/${encodeURIComponent(recordName)}`, fd)
    if (ok || data.status === 'success') {
      if (didRename) emit('renamed', recordName)
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
