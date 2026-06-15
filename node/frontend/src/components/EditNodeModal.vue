<template>
  <BaseModal size="large" @close="$emit('close')">
    <div class="tx-form-page">
      <div v-if="errorMsg" class="alert alert-danger" role="alert">{{ errorMsg }}</div>
      <p v-if="loading" class="tx-loading">Loading...</p>

      <template v-if="!loading && !fatalError">
        <div class="tx-header">
          <h2 class="tx-title">
            Update node
            <strong
              class="tx-title-highlight-name"
              :title="displayNameTitle(headerName)"
            >{{ formatDisplayName(headerName) }}</strong>
          </h2>
        </div>

        <NodeFormFields
          ref="formRef"
          mode="edit"
          :record-name="props.nodeName"
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
import { ref, onMounted, watch, nextTick } from 'vue'
import BaseModal from './BaseModal.vue'
import NodeFormFields from './NodeFormFields.vue'
import { fetchNodeEditData, removeInterface, submitNodeRename, submitNodeUpdate } from '../api'
import type { InventoryIpv4Record, NodeFormPayload } from '@/types'
import { displayNameTitle, formatDisplayName, validateNodeNameInput } from '@/constants/displayName'
import { removedInterfaceNames } from '@/utils/nodeInterfaces'

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
const submitting = ref(false)
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
const initialSnapshot = ref('')
const headerName = ref(props.nodeName)

watch(
  [() => formRef.value, () => formRef.value?.form?.name],
  () => {
    const n = formRef.value?.form?.name
    headerName.value =
      n != null && String(n) !== ''
        ? String(n)
        : props.nodeName
  },
  { immediate: true },
)

function optionList(payload: NodeFormPayload, ...keys: string[]): string[] {
  for (const k of keys) {
    const v = (payload as Record<string, unknown>)[k]
    if (Array.isArray(v)) return v as string[]
    if (v && typeof v === 'object' && Array.isArray((v as Record<string, unknown>).options))
      return (v as Record<string, unknown>).options as string[]
  }
  return []
}

async function captureInitialSnapshot() {
  await nextTick()
  await nextTick()
  await nextTick()
  if (!fatalError.value && formRef.value?.comparableSnapshot) {
    initialSnapshot.value = formRef.value.comparableSnapshot()
  }
}

watch(
  () => formRef.value,
  async (ref) => {
    if (!ref || loading.value || fatalError.value) return
    await nextTick()
    if (ref.comparableSnapshot) {
      initialSnapshot.value = ref.comparableSnapshot()
    }
  },
  { flush: 'post' },
)

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
  await captureInitialSnapshot()
})

async function onSubmit() {
  if (!formRef.value) return
  if (!initialSnapshot.value && formRef.value.comparableSnapshot) {
    initialSnapshot.value = formRef.value.comparableSnapshot()
  }
  if (!initialSnapshot.value) {
    errorMsg.value = 'Form is still loading. Please wait and try again.'
    return
  }
  if (submitting.value) return
  errorMsg.value = ''
  submitting.value = true

  const pending = formRef.value.getPendingRename?.() ?? null
  if (pending) {
    const nameCheck = validateNodeNameInput(pending.newName)
    if (!nameCheck.ok) {
      errorMsg.value = nameCheck.message
      submitting.value = false
      return
    }
  }

  try {
    const currentSnapshot = formRef.value.comparableSnapshot()
    if (currentSnapshot === initialSnapshot.value) {
      errorMsg.value = 'No changes to save.'
      return
    }

    const recordKey = pending ? pending.oldName : props.nodeName
    const removedFromInitial = formRef.value.getRemovedInterfaceNames?.() ?? []
    const removedFromSnapshot = removedInterfaceNames(
      initialSnapshot.value,
      formRef.value.form.interfaces,
    )
    const removed = [...new Set([...removedFromInitial, ...removedFromSnapshot])]
    for (const ifaceName of removed) {
      await removeInterface(recordKey, ifaceName)
    }

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
  } finally {
    submitting.value = false
  }
}
</script>
