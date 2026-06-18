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
  <BaseModal size="medium" @close="$emit('close')">
    <div class="tx-form-page">
      <h2 class="tx-title" style="margin-bottom: 1rem">Check IP — {{ networkName }}</h2>
      <div v-if="errorMsg" class="alert-danger">{{ errorMsg }}</div>
      <div class="tx-field tx-field-match tx-ipv4-field" style="max-width: 420px">
        <span class="tx-label">IP Address:</span>
        <input
          :value="ip"
          type="text"
          inputmode="decimal"
          autocomplete="off"
          placeholder="0.0.0.0"
          @input="onIpInput"
          @keyup.enter="runCheck"
        />
      </div>
      <div class="tx-form-footer-right" style="margin-top: 1rem">
        <button type="button" class="tx-btn tx-btn-blue" :disabled="loading" @click="runCheck">
          {{ loading ? 'Checking...' : 'Check IP' }}
        </button>
      </div>
      <pre v-if="result" class="tx-detail-pre" style="margin-top: 1rem">{{ result }}</pre>
    </div>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import BaseModal from './BaseModal.vue'
import { fetchIpInfo } from '@/api'
import { formatIpv4Typing, ipv4ForSubmit } from '@/utils/ipv4Input'

const props = defineProps<{ networkName: string }>()
defineEmits<{ close: [] }>()

const ip = ref('')
const result = ref('')
const errorMsg = ref('')
const loading = ref(false)

function onIpInput(e: Event) {
  ip.value = formatIpv4Typing((e.target as HTMLInputElement).value)
}

async function runCheck() {
  const addr = ipv4ForSubmit(ip.value)
  if (!addr) {
    errorMsg.value = 'Enter an IP address.'
    return
  }
  loading.value = true
  errorMsg.value = ''
  result.value = ''
  try {
    result.value = await fetchIpInfo(props.networkName, addr)
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : 'Check failed.'
  } finally {
    loading.value = false
  }
}
</script>
