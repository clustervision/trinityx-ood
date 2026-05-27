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

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import BaseModal from './BaseModal.vue'
import NodeFormFields from './NodeFormFields.vue'
import { fetchNodeEditData, submitNodeRename, submitNodeUpdate } from '../api'
import type { InventoryIpv4Record, NodeFormPayload } from '@/types'
import { validateNodeNameInput } from '@/constants/displayName'

const props = withDefaults(defineProps<{
  nodeName: string
  getInventoryIpv4?: (() => InventoryIpv4Record[]) | null
  inventoryExcludeNodeName?: string
}>(), {
  getInventoryIpv4: null,
  inventoryExcludeNodeName: '',
})

const emit = defineEmits<{
  close: []
  saved: []
  renamed: [newName: string]
}>()

const loading = ref(true)
const errorMsg = ref('')
const fatalError = ref(false)
const formData = ref<Record<string, unknown>>({})
const groupOptions = ref<string[]>([])
const switchOptions = ref<string[]>([])
const bmcsetupOptions = ref<string[]>([])
const osimageOptions = ref<string[]>([])
const cloudnameOptions = ref<string[]>([])
const networkOptions = ref<string[]>([])
const bondModeOptions = ref<string[]>([])
const hints = ref<Record<string, string>>({})
const formRef = ref<InstanceType<typeof NodeFormFields> | null>(null)

function optionList(payload: NodeFormPayload, ...keys: string[]): string[] {
  for (const k of keys) {
    const v = (payload as Record<string, unknown>)[k]
    if (Array.isArray(v)) return v as string[]
    if (v && typeof v === 'object' && Array.isArray((v as Record<string, unknown>).options))
      return (v as Record<string, unknown>).options as string[]
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
    bondModeOptions.value = (payload.bond_modes || payload.bond_mode_list?.options || []) as string[]
    hints.value = (payload.hints || payload.form_hints || {}) as Record<string, string>
  } catch (err) {
    errorMsg.value = (err as Error).message || 'Failed to load edit data.'
    fatalError.value = true
  } finally {
    loading.value = false
  }
})

async function onSubmit() {
  if (!formRef.value) return
  errorMsg.value = ''
  const pending = formRef.value.getPendingRename?.() ?? null
  if (pending) {
    const nameCheck = validateNodeNameInput(pending.newName)
    if (!nameCheck.ok) {
      errorMsg.value = nameCheck.message
      return
    }
  }
  try {
    const record = formRef.value.buildLunaNodeRecord()
    const urlNode = pending ? pending.oldName : props.nodeName

    const { ok, data } = pending
      ? await submitNodeRename(pending.oldName, record, pending.newName)
      : await submitNodeUpdate(urlNode, record)
    if (ok || data.status === 'success') {
      if (pending) formRef.value.applyRenamedInForm(pending.newName)
      if (pending) emit('renamed', pending.newName)
      emit('saved')
      emit('close')
    } else {
      errorMsg.value = data.message || 'Save failed.'
    }
  } catch (err) {
    errorMsg.value = (err as Error).message || 'Network error.'
  }
}
</script>
