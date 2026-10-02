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
  <div class="tx-network-form tx-add-form-main">
    <div v-if="liveNameValidationMsg" class="alert alert-danger" role="alert">{{ liveNameValidationMsg }}</div>
    <div class="tx-network-row tx-network-row-4">
      <div v-if="showNameField" class="tx-field tx-field-strong tx-field-name-with-rename">
        <span class="tx-label">Name:</span>
        <div class="tx-name-input-wrap">
          <template v-if="renameMode">
            <template v-if="!renaming">
              <input type="text" class="tx-name-input-readonly" :value="nameModel" readonly />
              <button
                type="button"
                class="tx-btn-rename"
                title="Edit name"
                aria-label="Edit name"
                @click="startRename"
              >
                <img :src="renameIconUrl" alt="" width="20" height="20" />
              </button>
            </template>
            <template v-else>
              <input
                v-model="renameDraft"
                type="text"
                class="tx-name-input-editing"
                :class="{ 'input-error': liveNameValidationMsg }"
                :maxlength="NETWORK_NAME_MAX_LENGTH"
                aria-label="Network name"
                @keyup.escape="cancelRename"
              />
              <button
                type="button"
                class="tx-btn-rename tx-btn-rename-cancel-char"
                title="Stop editing name"
                aria-label="Stop editing name"
                @click="cancelRename"
              >
                ×
              </button>
            </template>
          </template>
          <input
            v-else
            v-model="nameModel"
            type="text"
            :class="{ 'input-error': liveNameValidationMsg }"
            :maxlength="NETWORK_NAME_MAX_LENGTH"
          />
        </div>
      </div>
      <div class="tx-field tx-field-strong">
        <span class="tx-label">Network:</span>
        <input v-model="form.network" type="text" />
      </div>
      <div class="tx-field tx-field-match">
        <span class="tx-label">Type:</span>
        <select v-model="form.type" :class="{ 'tx-select-placeholder': !form.type }">
          <option value="">--- Select ---</option>
          <option v-for="t in typeOptions" :key="t" :value="t">{{ t }}</option>
        </select>
      </div>
      <div class="tx-field tx-field-match">
        <span class="tx-label">Zone:</span>
        <select v-model="form.zone" :class="{ 'tx-select-placeholder': !form.zone }">
          <option value="">--- Select ---</option>
          <option v-for="z in zoneOptions" :key="z" :value="z">{{ z }}</option>
        </select>
      </div>
    </div>

    <div class="tx-network-row tx-network-row-3">
      <label class="tx-field tx-field-match tx-field-dhcp-wrap" for="tx-network-dhcp">
        <span class="tx-label">DHCP:</span>
        <input
          id="tx-network-dhcp"
          type="checkbox"
          class="tx-dhcp-checkbox"
          :class="{ 'tx-dhcp-on': form.dhcp }"
          :checked="form.dhcp"
          @click.prevent="form.dhcp = !form.dhcp"
        />
      </label>
      <div class="tx-field tx-field-match">
        <span class="tx-label">DHCP Range Begin:</span>
        <input v-model="form.dhcp_range_begin" type="text" />
      </div>
      <div class="tx-field tx-field-match">
        <span class="tx-label">DHCP Range End:</span>
        <input v-model="form.dhcp_range_end" type="text" />
      </div>
    </div>

    <div class="tx-network-row tx-network-row-2">
      <div class="tx-field tx-field-match">
        <span class="tx-label">Network Gateway:</span>
        <input v-model="form.gateway" type="text" />
      </div>
      <div class="tx-field tx-field-match">
        <span class="tx-label">Nameserver IP:</span>
        <input v-model="form.nameserver_ip" type="text" />
      </div>
    </div>

    <div v-if="!advancedOpen" class="tx-form-footer">
      <button
        type="button"
        class="tx-btn tx-btn-outline-blue tx-btn-advanced-toggle"
        @click="advancedOpen = true"
      >
        Advanced
        <span class="tx-advanced-chevron tx-advanced-chevron-blue"></span>
      </button>
    </div>

    <template v-else>
      <div class="tx-form-footer tx-form-footer-no-submit">
        <button
          type="button"
          class="tx-btn tx-btn-outline-blue tx-btn-advanced-toggle"
          @click="advancedOpen = false"
        >
          Advanced
          <span class="tx-advanced-chevron tx-advanced-chevron-blue is-open"></span>
        </button>
      </div>
      <div class="tx-advanced-body">
        <div class="tx-network-row tx-network-row-2">
          <div class="tx-field tx-field-match">
            <span class="tx-label">NTP Server:</span>
            <input v-model="form.ntp_server" type="text" />
          </div>
          <div class="tx-field tx-field-match">
            <span class="tx-label">Gateway Metric:</span>
            <input v-model="form.gateway_metric" type="text" placeholder="1-1000" />
          </div>
        </div>
        <div class="tx-network-row tx-network-row-4 tx-network-adv-toggles">
          <div class="tx-field tx-field-match">
            <span class="tx-label">Shared:</span>
            <select v-model="form.shared" :class="{ 'tx-select-placeholder': !form.shared }">
              <option value="">--- Select ---</option>
              <option value="true">true</option>
              <option value="false">false</option>
            </select>
          </div>
          <BoolToggle v-model="dhcpNodesOnly" label="DHCP Nodes Only" />
          <BoolToggle v-model="dhcpNodesInPool" label="DHCP Nodes In Pool" />
          <label class="tx-field tx-field-match tx-field-dhcp-wrap tx-network-non-auth" for="tx-network-non-auth">
            <span class="tx-label">Non-Authoritative:</span>
            <input
              id="tx-network-non-auth"
              type="checkbox"
              class="tx-dhcp-checkbox"
              :class="{ 'tx-dhcp-on': form.non_authoritative }"
              :checked="form.non_authoritative"
              @click.prevent="form.non_authoritative = !form.non_authoritative"
            />
          </label>
        </div>
        <NetworkCommentField v-model="form.comment" />
      </div>
      <div class="tx-form-footer-right">
        <slot name="footer-expanded" />
      </div>
    </template>

    <div v-if="!advancedOpen" class="tx-form-footer-right">
      <slot name="footer-actions" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { NetworkFormState } from '@/types'
import { NETWORK_NAME_MAX_LENGTH, validateNetworkNameInput } from '@/constants/networkName'
import { punAppAssetUrl } from '@/utils'
import BoolToggle from './BoolToggle.vue'
import NetworkCommentField from './NetworkCommentField.vue'

const props = withDefaults(
  defineProps<{
    form: NetworkFormState
    name?: string
    showNameField?: boolean
    renameMode?: boolean
    typeOptions?: string[]
    zoneOptions?: string[]
  }>(),
  {
    name: '',
    showNameField: true,
    renameMode: false,
    typeOptions: () => [],
    zoneOptions: () => [],
  },
)

const emit = defineEmits<{
  'update:name': [value: string]
}>()

const advancedOpen = ref(false)
const renaming = ref(false)
const renameDraft = ref('')
const renameIconUrl = punAppAssetUrl('icons/icon-rename.png')

const nameModel = computed({
  get: () => props.name,
  set: (v: string) => emit('update:name', v),
})

const liveNameValidationMsg = computed(() => {
  if (!props.showNameField) return ''
  const raw = props.renameMode && renaming.value ? renameDraft.value : nameModel.value
  const n = String(raw || '').trim()
  if (!n) return ''
  const check = validateNetworkNameInput(n)
  return check.ok ? '' : check.message
})

/** Opposite toggles: one TRUE → other FALSE; one FALSE → other TRUE. */
const dhcpNodesOnly = computed({
  get: () => props.form.dhcp_nodes_only,
  set: (value: boolean) => {
    props.form.dhcp_nodes_only = value
    props.form.dhcp_nodes_in_pool = !value
  },
})

const dhcpNodesInPool = computed({
  get: () => props.form.dhcp_nodes_in_pool,
  set: (value: boolean) => {
    props.form.dhcp_nodes_in_pool = value
    props.form.dhcp_nodes_only = !value
  },
})

function startRename() {
  renameDraft.value = props.name
  renaming.value = true
}

function cancelRename() {
  renaming.value = false
  renameDraft.value = ''
}

function getPendingRename(): { pending: boolean; newName: string } {
  if (!props.renameMode || !renaming.value) {
    return { pending: false, newName: props.name }
  }
  const trimmed = renameDraft.value.trim()
  if (!trimmed || trimmed === props.name) {
    cancelRename()
    return { pending: false, newName: props.name }
  }
  return { pending: true, newName: trimmed }
}

defineExpose({ getPendingRename, cancelRename, advancedOpen, liveNameValidationMsg })
</script>
