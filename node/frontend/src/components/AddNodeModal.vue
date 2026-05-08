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
          :cloudname-options="cloudnameOptions"
          :network-options="networkOptions"
          :bond-mode-options="bondModeOptions"
          :hints="hints"
          :get-inventory-ipv4="getInventoryIpv4"
          submit-label="Add Node"
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
import { fetchNodeAddData, submitNodeAdd } from '../api'
import type { InventoryIpv4Record, NodeFormPayload } from '@/types'

withDefaults(defineProps<{
  getInventoryIpv4?: (() => InventoryIpv4Record[]) | null
}>(), {
  getInventoryIpv4: null,
})

const emit = defineEmits<{
  close: []
  saved: []
}>()

const loading = ref(true)
const errorMsg = ref('')
const fatalError = ref(false)
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
    const payload = await fetchNodeAddData()
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
    errorMsg.value = (err as Error).message || 'Failed to load form data.'
    fatalError.value = true
  } finally {
    loading.value = false
  }
})

async function onSubmit() {
  if (!formRef.value) return
  errorMsg.value = ''
  try {
    const record = formRef.value.buildLunaNodeRecord()
    const nodeName = String(record.name ?? '').trim().toLowerCase()
    if (!nodeName) {
      errorMsg.value = 'Please enter a node name.'
      return
    }
    const { ok, data } = await submitNodeAdd(nodeName, record)
    if (ok || data.status === 'success') {
      emit('saved')
      emit('close')
    } else {
      errorMsg.value = data.message || 'Add failed.'
    }
  } catch (err) {
    errorMsg.value = (err as Error).message || 'Network error.'
  }
}
</script>
