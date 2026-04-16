<template>
  <div class="tx-interface-block">
    <!-- Row 1: Interface, Network, MTU, DHCP -->
    <div class="tx-iface-grid tx-iface-grid--row1">
      <div class="tx-field tx-field-iface-key">
        <span class="tx-label">Interface:</span>
        <input type="text" v-model="iface.interface" required placeholder="interface" />
      </div>
      <div class="tx-field tx-field-iface-key">
        <span class="tx-label">Network:</span>
        <select v-model="iface.network" :class="{ 'tx-select-placeholder': !iface.network }">
          <option value="">--- Select ---</option>
          <option v-for="n in networks" :key="n" :value="n">{{ n }}</option>
        </select>
      </div>
      <div class="tx-field tx-field-iface-muted">
        <span class="tx-label">MTU:</span>
        <input type="number" v-model.number="iface.mtu" min="68" max="65535" placeholder="68-65535" @blur="clampMtu" />
      </div>
      <div class="tx-field tx-field-iface-muted tx-field-dhcp-wrap">
        <span class="tx-label">DHCP</span>
        <input type="checkbox" v-model="dhcpChecked" />
      </div>
    </div>

    <!-- Row 2: Bond Mode, Bond Member, VLAN ID -->
    <div class="tx-iface-grid tx-iface-grid--row2">
      <div class="tx-field tx-field-iface-muted">
        <span class="tx-label">Bond Mode:</span>
        <select v-model="iface.bond_mode" :class="{ 'tx-select-placeholder': !iface.bond_mode }">
          <option value="">--- Select ---</option>
          <option v-for="m in bondModes" :key="m" :value="m">{{ m }}</option>
        </select>
      </div>
      <div class="tx-field tx-field-iface-muted">
        <span class="tx-label">Bond Member:</span>
        <input type="text" v-model="iface.bond_slaves" placeholder="Bond Member Interfaces" />
      </div>
      <div class="tx-field tx-field-iface-muted">
        <span class="tx-label">VLAN ID:</span>
        <input type="number" v-model.number="iface.vlanid" min="0" max="4094" placeholder="VLAN ID" />
      </div>
    </div>

    <!-- Row 3: Options, VLAN Parent -->
    <div class="tx-iface-grid tx-iface-grid--row3">
      <div class="tx-field tx-field-iface-muted tx-field-options-combo">
        <span class="tx-label">Options:</span>
        <div class="tx-iface-options-input">
          <button
            type="button"
            class="tx-expand-text-trigger tx-expand-text-trigger--leading"
            aria-label="Edit options in dialog"
            @click="$emit('open-options-editor')"
          ></button>
          <input type="text" v-model="iface.options" placeholder="options" maxlength="100" />
        </div>
      </div>
      <div class="tx-field tx-field-iface-muted">
        <span class="tx-label">VLAN Parent:</span>
        <input type="text" v-model="iface.vlan_parent" placeholder="VLAN Parent" />
      </div>
    </div>

    <!-- Actions row -->
    <div class="tx-interface-actions">
      <button type="button" class="tx-btn tx-btn-dark" @click="$emit('remove')">Remove Interface</button>
      <button type="button" class="tx-btn tx-btn-orange" @click="$emit('add-after')">+ Add</button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  iface: { type: Object, required: true },
  networks: { type: Array, default: () => [] },
  bondModes: { type: Array, default: () => [] },
})
defineEmits(['remove', 'add-after', 'open-options-editor'])

const dhcpChecked = computed({
  get: () => props.iface.dhcp === true || props.iface.dhcp === 'true' || props.iface.dhcp === 'True',
  set: (v) => { props.iface.dhcp = v ? 'true' : 'false' },
})

function clampMtu(e) {
  const v = parseInt(e.target.value, 10)
  if (!isNaN(v)) {
    if (v < 68) props.iface.mtu = 68
    if (v > 65535) props.iface.mtu = 65535
  }
}
</script>
