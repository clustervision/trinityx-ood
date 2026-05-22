<template>
  <div class="tx-dns-form-row">
    <div class="tx-field tx-field-match">
      <span class="tx-label">Network:</span>
      <select v-model="form.network" :class="{ 'tx-select-placeholder': !form.network }">
        <option value="">--- Select ---</option>
        <option v-for="n in networkOptions" :key="n" :value="n">{{ n }}</option>
      </select>
    </div>
    <div class="tx-field tx-field-match">
      <span class="tx-label">Host:</span>
      <input
        v-model="form.host"
        type="text"
        :maxlength="DNS_NAME_MAX_LENGTH"
        @keydown.space.prevent
      />
    </div>
    <div class="tx-field tx-field-match tx-ipv4-field">
      <span class="tx-label">IP Address:</span>
      <input
        :value="form.ipaddress"
        type="text"
        inputmode="decimal"
        autocomplete="off"
        placeholder="0.0.0.0"
        @input="onIpInput"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { DnsFormState } from '@/types'
import { DNS_NAME_MAX_LENGTH } from '@/constants/dnsName'
import { formatIpv4Typing } from '@/utils/ipv4Input'

const props = defineProps<{
  form: DnsFormState
  networkOptions: string[]
}>()

function onIpInput(e: Event) {
  props.form.ipaddress = formatIpv4Typing((e.target as HTMLInputElement).value)
}
</script>
