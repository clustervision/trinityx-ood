<!--
  This code is part of the TrinityX software suite
  Copyright (C) 2026  ClusterVision Solutions b.v.

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <https://www.gnu.org/licenses/>

  @author      Yixin Zhang
  @copyright   Copyright 2026, Luna2 Project[OOD]
  @license     GPL
  @version     2.0
  @maintainer  Yixin Zhang
  @email       yixin.zhang@clustervision.com
  @status      Development
-->

<template>
  <BaseModal size="large" @close="$emit('close')">
    <div class="tx-form-page">
      <h2 class="tx-title" style="margin-bottom: 1.25rem">Add Network</h2>
      <div v-if="alertMsg" :class="alertOk ? 'alert-success' : 'alert-danger'">{{ alertMsg }}</div>
      <NetworkFormFields
        ref="fieldsRef"
        v-model:name="name"
        :form="form"
        :type-options="typeOptions"
        :zone-options="zoneOptions"
        :rename-mode="false"
      >
        <template #footer-expanded>
          <button type="button" class="tx-btn tx-btn-blue" :disabled="saving || isNameInvalid" @click="doAdd">
            {{ saving ? 'Saving...' : 'Add Network' }}
          </button>
        </template>
        <template #footer-actions>
          <button type="button" class="tx-btn tx-btn-blue" :disabled="saving || isNameInvalid" @click="doAdd">
            {{ saving ? 'Saving...' : 'Add Network' }}
          </button>
        </template>
      </NetworkFormFields>
    </div>
  </BaseModal>
</template>

<script setup lang="ts">
import { reactive, ref, computed } from 'vue'
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
const fieldsRef = ref<InstanceType<typeof NetworkFormFields> | null>(null)
const isNameInvalid = computed(() => Boolean(fieldsRef.value?.liveNameValidationMsg))
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
