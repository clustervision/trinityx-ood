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
  <div class="tx-interface-block">
    <div class="tx-iface-main-grid">
      <div class="tx-field tx-field-iface-key tx-iface-c1">
        <span class="tx-label">Interface:</span>
        <input type="text" v-model="iface.interface" placeholder="interface" />
      </div>
      <div class="tx-field tx-field-iface-key tx-iface-c2">
        <span class="tx-label">Network:</span>
        <select v-model="iface.network" :class="{ 'tx-select-placeholder': !iface.network }">
          <option value="">--- Select ---</option>
          <option v-for="n in networks" :key="n" :value="n">{{ n }}</option>
        </select>
      </div>
      <div class="tx-field tx-field-iface-key tx-field-ip-next-combo tx-iface-c3-ip">
        <span class="tx-label">IP Address:</span>
        <div class="tx-iface-ip-next-inner">
          <input type="text" v-model="iface.ipaddress" placeholder="IPv4" autocomplete="off" />
          <button type="button" class="tx-btn tx-btn-orange tx-btn-next-ip" @click="onNextIp">
            NEXT IP
          </button>
        </div>
      </div>

      <div class="tx-field tx-field-iface-muted tx-iface-c1">
        <span class="tx-label">Bond Mode:</span>
        <select v-model="iface.bond_mode" :class="{ 'tx-select-placeholder': !iface.bond_mode }">
          <option value="">--- Select ---</option>
          <option v-for="m in bondModes" :key="m" :value="m">{{ m }}</option>
        </select>
      </div>
      <div class="tx-field tx-field-iface-muted tx-iface-c2">
        <span class="tx-label">Bond Member:</span>
        <input type="text" v-model="iface.bond_slaves" placeholder="Bond Member Interfaces" />
      </div>
      <div class="tx-iface-cell-mtu-dhcp">
        <div class="tx-field tx-field-iface-muted tx-iface-c3-mtu">
          <span class="tx-label">MTU:</span>
          <input type="number" v-model.number="iface.mtu" min="68" max="65535" placeholder="68-65535" @blur="clampMtu" />
        </div>
        <label
          class="tx-field tx-field-iface-muted tx-field-dhcp-wrap tx-iface-c3-dhcp"
          :for="dhcpInputId"
        >
          <span class="tx-label">DHCP</span>
          <input
            :id="dhcpInputId"
            class="tx-dhcp-checkbox"
            type="checkbox"
            :checked="dhcpChecked"
            :class="{ 'tx-dhcp-on': dhcpChecked }"
            :aria-checked="dhcpChecked ? 'true' : 'false'"
            @click.prevent="toggleDhcp"
            @keydown.space.prevent="toggleDhcp"
          />
        </label>
      </div>

      <div class="tx-field tx-field-iface-muted tx-iface-c1">
        <span class="tx-label">VLAN ID:</span>
        <input type="number" v-model.number="iface.vlanid" min="0" max="4094" placeholder="VLAN ID" />
      </div>
      <div class="tx-field tx-field-iface-muted tx-iface-c2">
        <span class="tx-label">VLAN Parent:</span>
        <input type="text" v-model="iface.vlan_parent" placeholder="VLAN Parent" />
      </div>
      <div class="tx-field tx-field-iface-muted tx-iface-c3-mac">
        <span class="tx-label">MAC Address:</span>
        <input type="text" v-model="iface.macaddress" placeholder="MAC" autocomplete="off" />
      </div>

      <div class="tx-field tx-field-iface-muted tx-field-options-combo tx-iface-options-span">
        <span class="tx-label">Options:</span>
        <div class="tx-iface-options-input">
          <input type="text" v-model="iface.options" placeholder="options" maxlength="100" />
          <button
            type="button"
            class="tx-expand-text-trigger tx-expand-text-trigger--iface-options"
            aria-label="Edit options in dialog"
            @click="$emit('open-options-editor')"
          ></button>
        </div>
      </div>
      <div class="tx-iface-row-actions">
        <button type="button" class="tx-btn tx-btn-dark" @click="$emit('remove')">Remove Interface</button>
        <button type="button" class="tx-btn tx-btn-orange" @click="$emit('add-after')">+ Add</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { suggestNextFreeIpv424 } from '../utils/nextFreeIpv4'
import type { NodeFormInterface, InventoryIpv4Record } from '@/types'

const props = withDefaults(defineProps<{
  iface: NodeFormInterface
  rowKey?: string | number
  allIfaces?: NodeFormInterface[]
  networks?: string[]
  bondModes?: string[]
  getInventoryIpv4?: (() => InventoryIpv4Record[]) | null
  inventoryExcludeNodeName?: string
}>(), {
  rowKey: 0,
  allIfaces: () => [],
  networks: () => [],
  bondModes: () => [],
  getInventoryIpv4: null,
  inventoryExcludeNodeName: '',
})

const emit = defineEmits<{
  remove: []
  'add-after': []
  'open-options-editor': []
  'update-dhcp': [value: string]
}>()

const dhcpInputId = computed(() => `tx-dhcp-${props.rowKey}`)

const dhcpChecked = computed((): boolean => {
  const v = props.iface.dhcp
  if ((v as unknown) === true || (v as unknown) === 1) return true
  const s = String(v ?? '').trim().toLowerCase()
  return s === 'true' || s === '1' || s === 'yes' || s === 'on'
})

function toggleDhcp() {
  emit('update-dhcp', dhcpChecked.value ? 'false' : 'true')
}

function clampMtu(ev: Event) {
  const v = parseInt((ev.target as HTMLInputElement).value, 10)
  if (!isNaN(v)) {
    if (v < 68) props.iface.mtu = 68
    if (v > 65535) props.iface.mtu = 65535
  }
}

function onNextIp() {
  const records = props.getInventoryIpv4?.() ?? []
  const result = suggestNextFreeIpv424({
    networkName: props.iface.network,
    formInterfaces: props.allIfaces,
    inventoryRecords: records,
    excludeNodeName: props.inventoryExcludeNodeName || '',
  })
  if (!result.ok) {
    if (result.reason === 'network') {
      window.alert('Select a network first.')
    } else if (result.reason === 'subnet') {
      window.alert(
        'No IPv4 subnet found for this network. Pick a network that already has nodes with IPv4 on it, or type an address on the desired subnet first.',
      )
    } else {
      window.alert('No free IPv4 addresses in this /24.')
    }
    return
  }
  props.iface.ipaddress = result.ip
}
</script>
