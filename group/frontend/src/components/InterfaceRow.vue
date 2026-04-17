<template>
  <div class="tx-interface-block">
    <!-- 3 columns: align with Add Group grid (Name | OS Image | Setup BMC) -->
    <div class="tx-iface-main-grid">
      <!-- Row 1 -->
      <div class="tx-field tx-field-iface-key tx-iface-c1">
        <span class="tx-label">Interface:</span>
        <input type="text" v-model="iface.interface" required placeholder="interface" />
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
        <input type="number" v-model.number="iface.vlanid" min="0" max="4094" placeholder="VLAN ID" />
      </div>

      <!-- Row 3 -->
      <div class="tx-field tx-field-iface-muted tx-field-options-combo tx-iface-c1">
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
      <div class="tx-field tx-field-iface-muted tx-iface-c2">
        <span class="tx-label">VLAN Parent:</span>
        <input type="text" v-model="iface.vlan_parent" placeholder="VLAN Parent" />
      </div>
      <div class="tx-iface-cell-spacer" aria-hidden="true"></div>
    </div>

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
  rowKey: { type: [String, Number], default: 0 },
  networks: { type: Array, default: () => [] },
  bondModes: { type: Array, default: () => [] },
})

const emit = defineEmits(['remove', 'add-after', 'open-options-editor'])

const dhcpInputId = computed(() => `tx-dhcp-${props.rowKey}`)

const dhcpChecked = computed(() => {
  const v = props.iface.dhcp
  if (v === true || v === 1) return true
  const s = String(v ?? '').trim().toLowerCase()
  return s === 'true' || s === '1' || s === 'yes' || s === 'on'
})

/** Fully controlled: block native toggle (Vue 3 props / label can desync), parent owns state */
function toggleDhcp() {
  emit('update-dhcp', dhcpChecked.value ? 'false' : 'true')
}

function clampMtu(ev) {
  const v = parseInt(ev.target.value, 10)
  if (!isNaN(v)) {
    if (v < 68) props.iface.mtu = 68
    if (v > 65535) props.iface.mtu = 65535
  }
}
</script>
