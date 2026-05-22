<template>
  <BaseModal size="wide" @close="$emit('close')">
    <div class="tx-form-page">
      <h2 class="tx-title" style="margin-bottom: 1.25rem">
        IP Address Reserved With <span class="tx-reserved-title-name">{{ networkName }}</span>
      </h2>
      <div v-if="errorMsg" class="alert-danger">{{ errorMsg }}</div>
      <div v-if="loading" class="tx-loading">Loading...</div>
      <div v-else class="tx-inventory-table-wrap tx-reserved-ip-wrap">
        <table class="tx-inventory-table tx-reserved-ip-table">
          <thead>
            <tr>
              <th class="tx-th-regular">S.No</th>
              <th class="tx-th-regular tx-th-sep-blue">IP ADDRESS</th>
              <th class="tx-th-regular tx-th-sep-blue">DEVICE NAME</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, idx) in displayRows" :key="(row.ip || 'empty') + '-' + idx">
              <td>{{ row.ip ? idx + 1 : '' }}</td>
              <td class="tx-td-sep-blue">{{ row.ip }}</td>
              <td class="tx-td-sep-blue">
                <input
                  v-if="row.ip"
                  v-model="row.deviceName"
                  type="text"
                  class="tx-reserved-device-input"
                  :maxlength="DEVICE_NAME_MAX_LENGTH"
                  :title="deviceNameTitle(row.deviceName)"
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </BaseModal>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import BaseModal from './BaseModal.vue'
import { fetchReservedIps } from '@/api'
import type { ReservedIpRow } from '@/types'
import { DEVICE_NAME_MAX_LENGTH, deviceNameTitle } from '@/constants/networkName'

const props = defineProps<{ networkName: string }>()
defineEmits<{ close: [] }>()

const loading = ref(true)
const errorMsg = ref('')
const rows = ref<ReservedIpRow[]>([])

const MIN_ROWS = 12

const displayRows = computed(() => {
  const base = rows.value.length ? [...rows.value] : []
  while (base.length < MIN_ROWS) {
    base.push({ ip: '', deviceName: '' })
  }
  return base
})

onMounted(async () => {
  try {
    rows.value = await fetchReservedIps(props.networkName)
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : 'Failed to load reserved IPs.'
  } finally {
    loading.value = false
  }
})
</script>
