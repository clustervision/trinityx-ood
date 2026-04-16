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
        <div class="tx-field tx-field-iface-muted tx-field-dhcp-wrap tx-iface-c3-dhcp">
          <span class="tx-label">DHCP</span>
          <input
            :id="dhcpInputId"
            v-model="dhcpModel"
            type="checkbox"
          />
        </div>
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

const emit = defineEmits(['remove', 'add-after', 'open-options-editor', 'update-dhcp'])

const dhcpInputId = computed(() => `tx-dhcp-${props.rowKey}`)

function dhcpToBool(d) {
  return d === true || d === 'true' || d === 'True'
}

/* Same pattern as PushOs No Dry: v-model on writable state; parent owns form.interfaces[idx].dhcp */
const dhcpModel = computed({
  get: () => dhcpToBool(props.iface.dhcp),
  set: (on) => {
    emit('update-dhcp', on ? 'true' : 'false')
  },
})

function clampMtu(ev) {
  const v = parseInt(ev.target.value, 10)
  if (!isNaN(v)) {
    if (v < 68) props.iface.mtu = 68
    if (v > 65535) props.iface.mtu = 65535
  }
}
</script>
