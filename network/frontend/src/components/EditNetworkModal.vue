<template>
  <BaseModal size="large" @close="$emit('close')">
    <div class="tx-form-page">
      <h2 class="tx-title" style="margin-bottom: 1.25rem">Update Network</h2>
      <div v-if="loadError" class="alert-danger">{{ loadError }}</div>
      <div v-if="alertMsg" :class="alertOk ? 'alert-success' : 'alert-danger'">{{ alertMsg }}</div>
      <div v-if="loadingData" class="tx-loading">Loading...</div>
      <template v-if="!loadingData && !loadError">
        <NetworkFormFields
          ref="fieldsRef"
          v-model:name="currentName"
          :form="form"
          :type-options="typeOptions"
          :zone-options="zoneOptions"
          rename-mode
        >
          <template #footer-expanded>
            <button type="button" class="tx-btn tx-btn-blue" :disabled="saving || isNameInvalid" @click="doSave">
              {{ saving ? 'Saving...' : 'Save Changes' }}
            </button>
          </template>
          <template #footer-actions>
            <button type="button" class="tx-btn tx-btn-blue" :disabled="saving || isNameInvalid" @click="doSave">
              {{ saving ? 'Saving...' : 'Save Changes' }}
            </button>
          </template>
        </NetworkFormFields>
      </template>
    </div>
  </BaseModal>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, computed } from 'vue'
import BaseModal from './BaseModal.vue'
import NetworkFormFields from './NetworkFormFields.vue'
import {
  fetchNetworkRecord,
  recordToFormState,
  renameNetwork,
  updateNetwork,
  DEFAULT_NETWORK_TYPES,
  DEFAULT_NETWORK_ZONES,
} from '@/api'
import { validateNetworkNameInput } from '@/constants/networkName'
import { emptyNetworkForm } from '@/formDefaults'

const props = defineProps<{ networkName: string }>()
const emit = defineEmits<{ close: []; saved: []; renamed: [name: string] }>()

const fieldsRef = ref<InstanceType<typeof NetworkFormFields> | null>(null)
const isNameInvalid = computed(() => Boolean(fieldsRef.value?.liveNameValidationMsg))
const loadingData = ref(true)
const loadError = ref('')
const saving = ref(false)
const alertMsg = ref('')
const alertOk = ref(false)
const currentName = ref('')
const form = reactive(emptyNetworkForm())
const typeOptions = ref([...DEFAULT_NETWORK_TYPES])
const zoneOptions = ref([...DEFAULT_NETWORK_ZONES])

async function commitPendingRename(): Promise<boolean> {
  const pending = fieldsRef.value?.getPendingRename?.()
  if (!pending?.pending) return true
  const v = validateNetworkNameInput(pending.newName)
  if (!v.ok) {
    alertMsg.value = v.message
    alertOk.value = false
    return false
  }
  await renameNetwork(currentName.value, v.name)
  currentName.value = v.name
  fieldsRef.value?.cancelRename?.()
  emit('renamed', v.name)
  return true
}

async function doSave() {
  saving.value = true
  alertMsg.value = ''
  try {
    const renameOk = await commitPendingRename()
    if (!renameOk) return
    await updateNetwork(currentName.value, form)
    alertMsg.value = 'Network updated successfully.'
    alertOk.value = true
    setTimeout(() => emit('saved'), 600)
  } catch (e) {
    alertMsg.value = e instanceof Error ? e.message : 'Save failed.'
    alertOk.value = false
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const { record, error } = await fetchNetworkRecord(props.networkName)
    if (error) {
      loadError.value = error
      return
    }
    currentName.value = String(record.name || props.networkName)
    Object.assign(form, recordToFormState(record))
    const t = form.type.trim()
    const z = form.zone.trim()
    if (t && !typeOptions.value.includes(t)) typeOptions.value.push(t)
    if (z && !zoneOptions.value.includes(z)) zoneOptions.value.push(z)
  } catch (e) {
    loadError.value = e instanceof Error ? e.message : 'Failed to load network.'
  } finally {
    loadingData.value = false
  }
})
</script>
