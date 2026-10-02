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

<script setup lang="ts">
import { computed } from 'vue'
import type { NetworkInterface } from '@/types/network'

// const props = defineProps({
//   iface: { type: Object, required: true },
//   rowKey: { type: [String, Number], default: 0 },
//   networks: { type: Array, default: () => [] },
//   bondModes: { type: Array, default: () => [] },
// })

const props = defineProps<{
  iface: NetworkInterface
  rowKey: string | number
  networks: string[]
  bondModes: string[]
}>()

// const emit = defineEmits(['remove', 'add-after', 'open-options-editor'])
const emit = defineEmits<{
  (e: 'update:iface', payload: NetworkInterface): void
  (e: 'remove'): void
  (e: 'add-after'): void
  (e: 'open-options-editor'): void
  (e: 'update-dhcp', v: string): void
}>()

const dhcpInputId = computed(() => `tx-dhcp-${props.rowKey}`)

const dhcpChecked = computed(() => {
  const v = props.iface.dhcp

  if (v === true || v === 'true' || v === 1 || v === '1') {
    return true
  }

  const s = String(v ?? '').toLowerCase()
  return ['yes', 'on'].includes(s)
})

/** Fully controlled: block native toggle (Vue 3 props / label can desync), parent owns state */
function toggleDhcp() {
  emit('update-dhcp', dhcpChecked.value ? 'false' : 'true')
}

function clampMtu(ev: Event) {
  const target = ev.target as HTMLInputElement
  const v = parseInt(target.value, 10)

  if (isNaN(v)) return

  const clamped = v < 68 ? 68 : v > 65535 ? 65535 : v

  emit('update:iface', {
    ...props.iface,
    mtu: String(clamped),
  })
}

function emitUpdate<K extends keyof NetworkInterface>(key: K, value: NetworkInterface[K]) {
  emit('update:iface', {
    ...props.iface,
    [key]: value,
  })
}


</script>


<template>
  <div class="tx-interface-block">
    <!-- 3 columns: align with Add Group grid (Name | OS Image | Setup BMC) -->
    <div class="tx-iface-main-grid">
      <!-- Row 1 -->
      <div class="tx-field tx-field-iface-key tx-iface-c1">
        <span class="tx-label">Interface:</span>
        <input type="text" v-model="iface.interface" @input="emitUpdate('interface', ($event.target as HTMLSelectElement).value)" required placeholder="interface" />
      </div>
      <div class="tx-field tx-field-iface-key tx-iface-c2">
        <span class="tx-label">Network:</span>
        <select v-model="iface.network" :class="{ 'tx-select-placeholder': !iface.network }">
          <option value="">--- Select ---</option>
          <option v-for="n in networks" :key="n" :value="n">{{ n }}</option>
        </select>
      </div>
      <div class="tx-iface-cell-mtu-dhcp">
        <div class="tx-field tx-field-iface-muted tx-iface-c3-mtu">
          <span class="tx-label">MTU:</span>
          <input type="number" v-model="iface.mtu" min="68" max="65535" placeholder="68-65535" @input="emitUpdate('mtu', String(($event.target as HTMLInputElement).value))" @blur="clampMtu" />
        </div>
        <label
          class="tx-field tx-field-iface-muted tx-field-dhcp-wrap tx-iface-c3-dhcp"
          :for="dhcpInputId"
        >
          <span class="tx-label">DHCP</span>
          <input :id="dhcpInputId" class="tx-dhcp-checkbox" type="checkbox" :checked="dhcpChecked" :class="{ 'tx-dhcp-on': dhcpChecked }" :aria-checked="dhcpChecked ? 'true' : 'false'" @click.prevent="toggleDhcp" @keydown.space.prevent="toggleDhcp" />
        </label>
      </div>

      <!-- Row 2 -->
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
      <div class="tx-field tx-field-iface-muted tx-iface-c3-vlan">
        <span class="tx-label">VLAN ID:</span>
        <input type="number" v-model="iface.vlanid" min="0" max="4094" placeholder="VLAN ID" />
      </div>

      <!-- Row 3: Options spans col 1–2; VLAN Parent in col 3 (below MTU / VLAN ID) -->
      <div class="tx-field tx-field-iface-muted tx-field-options-combo tx-iface-c1 tx-iface-row3-options-span">
        <span class="tx-label">Options:</span>
        <div class="tx-iface-options-input">
          <input type="text" v-model="iface.options" placeholder="options" maxlength="100" />
          <button type="button" class="tx-expand-text-trigger tx-expand-text-trigger--iface-options" aria-label="Edit options in dialog" @click="$emit('open-options-editor')"></button>
        </div>
      </div>
      <div class="tx-field tx-field-iface-muted tx-iface-c3-vlanparent">
        <span class="tx-label">VLAN Parent:</span>
        <input type="text" v-model="iface.vlan_parent" placeholder="VLAN Parent" />
      </div>
    </div>

    <div class="tx-interface-actions">
      <button type="button" class="tx-btn tx-btn-dark" @click="$emit('remove')">Remove Interface</button>
      <button type="button" class="tx-btn tx-btn-orange" @click="$emit('add-after')">+ Add</button>
    </div>
  </div>
</template>


