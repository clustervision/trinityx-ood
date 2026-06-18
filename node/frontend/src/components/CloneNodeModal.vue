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
      <div v-if="errorMsg" class="alert alert-danger" role="alert">{{ errorMsg }}</div>
      <p v-if="loading" class="tx-loading">Loading...</p>

      <template v-if="!loading && !fatalError">
        <div class="tx-header">
          <h2 class="tx-title">
            Clone node
            <strong
              class="tx-title-highlight-name"
              :title="displayNameTitle(cloneSourceDisplayName)"
            >{{ formatDisplayName(cloneSourceDisplayName) }}</strong>
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

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import BaseModal from './BaseModal.vue'
import NodeFormFields from './NodeFormFields.vue'
import { fetchNodeCloneData, submitNodeClone } from '../api'
import type { InventoryIpv4Record, NodeFormPayload } from '@/types'
import { displayNameTitle, formatDisplayName, validateNodeNameInput } from '@/constants/displayName'

const props = withDefaults(defineProps<{
  sourceNodeName: string
  getInventoryIpv4?: (() => InventoryIpv4Record[]) | null
  inventoryExcludeNodeName?: string
}>(), {
  getInventoryIpv4: null,
  inventoryExcludeNodeName: '',
})

const emit = defineEmits<{
  close: []
  saved: []
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

const cloneSourceDisplayName = computed((): string => {
  const n = formData.value?.name
  if (n != null && String(n).trim() !== '') return String(n)
  return props.sourceNodeName || ''
})

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
    bondModeOptions.value = (payload.bond_modes || payload.bond_mode_list?.options || []) as string[]
    hints.value = (payload.hints || payload.form_hints || {}) as Record<string, string>
  } catch (err) {
    errorMsg.value = (err as Error).message || 'Failed to load clone data.'
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
    const newName = String(record.newnodename ?? '').trim()
    if (!newName) {
      errorMsg.value = 'Please enter a clone name.'
      return
    }
    const nameCheck = validateNodeNameInput(newName)
    if (!nameCheck.ok) {
      errorMsg.value = nameCheck.message
      return
    }
    const { ok, data, status } = await submitNodeClone(newName, record)
    if (ok || data.status === 'success') {
      emit('saved')
      emit('close')
    } else {
      errorMsg.value =
        data.message || data.error || (status ? `Clone failed (HTTP ${status}).` : 'Clone failed.')
    }
  } catch (err) {
    errorMsg.value = (err as Error).message || 'Network error.'
  }
}
</script>
