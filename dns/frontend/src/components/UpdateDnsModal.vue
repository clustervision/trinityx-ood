<template>
  <BaseModal size="wide" @close="$emit('close')">
    <div class="tx-form-page">
      <h2 class="tx-title" style="margin-bottom: 1rem">Update DNS Entry</h2>
      <div v-if="alertMsg" :class="alertOk ? 'alert-success' : 'alert-danger'" role="alert">
        {{ alertMsg }}
      </div>
      <DnsFormFields :form="form" :network-options="networkOptions" />
      <div class="tx-form-footer-right" style="margin-top: 1.25rem">
        <button type="button" class="tx-btn tx-btn-blue" :disabled="saving" @click="submit">
          {{ saving ? 'Updating...' : 'Update DNS Entry' }}
        </button>
      </div>
    </div>
  </BaseModal>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import BaseModal from './BaseModal.vue'
import DnsFormFields from './DnsFormFields.vue'
import { fetchDnsEntries, fetchNetworks, saveDnsEntry } from '@/api'
import { validateDnsLabel } from '@/constants/dnsName'
import { validateIpv4ForSubmit } from '@/utils/ipv4Input'
import type { DnsFormState } from '@/types'

const props = defineProps<{ network: string; host: string }>()
const emit = defineEmits<{ close: []; saved: [] }>()

const original = { network: props.network, host: props.host }

const form = reactive<DnsFormState>({
  network: props.network,
  host: props.host,
  ipaddress: '',
})

const networkOptions = ref<string[]>([])
const saving = ref(false)
const alertMsg = ref('')
const alertOk = ref(false)

onMounted(async () => {
  try {
    networkOptions.value = await fetchNetworks()
    const entries = await fetchDnsEntries()
    const row = entries.find(
      (e) => e.network === props.network && e.host === props.host,
    )
    if (row) {
      form.network = row.network
      form.host = row.host
      form.ipaddress = row.ipaddress || ''
    }
  } catch (e) {
    alertMsg.value = e instanceof Error ? e.message : 'Failed to load entry.'
    alertOk.value = false
  }
})

async function submit() {
  saving.value = true
  alertMsg.value = ''

  const net = validateDnsLabel(form.network, 'Network')
  if (!net.ok) {
    alertMsg.value = net.message
    saving.value = false
    return
  }
  const host = validateDnsLabel(form.host, 'Host')
  if (!host.ok) {
    alertMsg.value = host.message
    saving.value = false
    return
  }
  const ip = validateIpv4ForSubmit(form.ipaddress)
  if (!ip.ok) {
    alertMsg.value = ip.message
    saving.value = false
    return
  }

  try {
    await saveDnsEntry(
      { network: net.value, host: host.value, ipaddress: ip.value },
      original,
    )
    alertMsg.value = 'DNS entry updated successfully.'
    alertOk.value = true
    setTimeout(() => emit('saved'), 500)
  } catch (e) {
    alertMsg.value = e instanceof Error ? e.message : 'Update failed.'
    alertOk.value = false
  } finally {
    saving.value = false
  }
}
</script>
