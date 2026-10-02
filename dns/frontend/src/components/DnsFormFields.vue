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
  <div>
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
          :maxlength="DNS_HOST_MAX_LENGTH"
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
    <div v-if="showUnspecifiedIpv4Warning" class="alert-warning" role="status">
      0.0.0.0 is the unspecified address. Confirm this is intentional before submitting.
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { DnsFormState } from '@/types'
import { DNS_HOST_MAX_LENGTH } from '@/constants/dnsName'
import { formatIpv4Typing, isUnspecifiedIpv4 } from '@/utils/ipv4Input'

const props = defineProps<{
  form: DnsFormState
  networkOptions: string[]
}>()

const showUnspecifiedIpv4Warning = computed(() => isUnspecifiedIpv4(props.form.ipaddress))

function onIpInput(e: Event) {
  props.form.ipaddress = formatIpv4Typing((e.target as HTMLInputElement).value)
}
</script>
