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
import { fetchNodeAddData, fetchNodes, submitNodeAdd } from '../api'
import type { InventoryIpv4Record, NodeFormPayload } from '@/types'
import { validateNodeNameInput } from '@/constants/displayName'

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

function normalizeNodeName(name: unknown): string {
  return String(name ?? '')
    .replace(/\s+\*$/, '')
    .trim()
    .toLowerCase()
}

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
    const nodeNameRaw = String(record.name ?? '').trim()
    const nodeName = normalizeNodeName(nodeNameRaw)
    if (!nodeNameRaw) {
      errorMsg.value = 'Please enter a node name.'
      return
    }
    const nameCheck = validateNodeNameInput(nodeNameRaw)
    if (!nameCheck.ok) {
      errorMsg.value = nameCheck.message
      return
    }
    const existing = await fetchNodes()
    const existingNames = new Set(
      (existing.nodes || []).map((row) => normalizeNodeName(row.name)),
    )
    if (existingNames.has(nodeName)) {
      errorMsg.value = `Node '${nodeNameRaw}' already exists. Please choose a different name.`
      return
    }

    const { ok, data } = await submitNodeAdd(nodeNameRaw, record)
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
