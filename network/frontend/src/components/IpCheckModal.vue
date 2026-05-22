<template>
  <BaseModal size="medium" @close="$emit('close')">
    <div class="tx-form-page">
      <h2 class="tx-title" style="margin-bottom: 1rem">Check IP — {{ networkName }}</h2>
      <div v-if="errorMsg" class="alert-danger">{{ errorMsg }}</div>
      <div class="tx-field tx-field-emphasis" style="max-width: 420px">
        <span class="tx-label">IP Address:</span>
        <input v-model="ip" type="text" placeholder="__.___.___.___" @keyup.enter="runCheck" />
      </div>
      <div class="tx-form-footer-right" style="margin-top: 1rem">
        <button type="button" class="tx-btn tx-btn-outline-blue" @click="$emit('close')">Close</button>
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

const props = defineProps<{ networkName: string }>()
defineEmits<{ close: [] }>()

const ip = ref('')
const result = ref('')
const errorMsg = ref('')
const loading = ref(false)

async function runCheck() {
  const addr = ip.value.trim()
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
