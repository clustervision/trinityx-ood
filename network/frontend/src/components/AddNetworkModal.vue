<template>
  <BaseModal size="large" @close="$emit('close')">
    <div class="tx-form-page">
      <h2 class="tx-title" style="margin-bottom: 1.25rem">Add Network</h2>
      <div v-if="alertMsg" :class="alertOk ? 'alert-success' : 'alert-danger'">{{ alertMsg }}</div>
      <NetworkFormFields
        v-model:name="name"
        :form="form"
        :type-options="typeOptions"
        :zone-options="zoneOptions"
        :rename-mode="false"
      >
        <template #footer-collapsed>
          <button type="button" class="tx-btn tx-btn-blue" :disabled="saving" @click="doAdd">
            {{ saving ? 'Saving...' : 'Add Network' }}
          </button>
        </template>
        <template #footer-expanded>
          <button type="button" class="tx-btn tx-btn-blue" :disabled="saving" @click="doAdd">
            {{ saving ? 'Saving...' : 'Add Network' }}
          </button>
        </template>
        <template #footer-actions>
          <button type="button" class="tx-btn tx-btn-blue" :disabled="saving" @click="doAdd">
            {{ saving ? 'Saving...' : 'Add Network' }}
          </button>
        </template>
      </NetworkFormFields>
    </div>
  </BaseModal>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import BaseModal from './BaseModal.vue'
import NetworkFormFields from './NetworkFormFields.vue'
import { createNetwork, DEFAULT_NETWORK_TYPES, DEFAULT_NETWORK_ZONES } from '@/api'
import { validateNetworkNameInput } from '@/constants/networkName'
import { emptyNetworkForm } from '@/formDefaults'

const emit = defineEmits<{ close: []; saved: [] }>()

const name = ref('')
const form = reactive(emptyNetworkForm())
const typeOptions = [...DEFAULT_NETWORK_TYPES]
const zoneOptions = [...DEFAULT_NETWORK_ZONES]
const saving = ref(false)
const alertMsg = ref('')
const alertOk = ref(false)

async function doAdd() {
  saving.value = true
  alertMsg.value = ''
  try {
    const v = validateNetworkNameInput(name.value)
    if (!v.ok) {
      alertMsg.value = v.message
      alertOk.value = false
      return
    }
    await createNetwork(v.name, form)
    alertMsg.value = 'Network added successfully.'
    alertOk.value = true
    setTimeout(() => emit('saved'), 600)
  } catch (e) {
    alertMsg.value = e instanceof Error ? e.message : 'Add failed.'
    alertOk.value = false
  } finally {
    saving.value = false
  }
}
</script>
