<template>
  <BaseModal size="wide" @close="$emit('close')">
    <div class="tx-form-page">
      <h2 class="tx-title">
        Tag Detail: <strong>{{ tagName }}</strong>
      </h2>

      <div v-if="errorMsg" class="alert-danger" style="margin-top:1rem;">{{ errorMsg }}</div>
      <div v-if="loading" class="tx-loading">Loading...</div>

      <div v-if="!loading && !errorMsg && Object.keys(detail).length" style="margin-top:1.25rem;">
        <table class="tx-inventory-table" style="width:100%;">
          <tbody>
            <tr v-for="(value, key) in detail" :key="key">
              <td style="font-weight:600;text-align:left;padding:0.5rem 0.75rem;background:#E6EEFF;color:#5376EA;text-transform:uppercase;width:200px;">
                {{ key }}
              </td>
              <td style="text-align:left;padding:0.5rem 0.75rem;">
                <template v-if="value == null || value === ''">
                  <span class="tx-na-box">NONE</span>
                </template>
                <template v-else>{{ value }}</template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="tx-form-footer-right">
        <button type="button" class="tx-btn tx-btn-outline-blue" @click="$emit('close')">Close</button>
      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import BaseModal from './BaseModal.vue'
import { fetchOsimageTagDetail } from '../api'

const props = defineProps({
  tagName: { type: String, required: true },
})
defineEmits(['close'])

const loading = ref(true)
const errorMsg = ref('')
const detail = ref({})

onMounted(async () => {
  try {
    const result = await fetchOsimageTagDetail(props.tagName)
    if (result.error) {
      errorMsg.value = result.error
    } else {
      detail.value = result.tag
    }
  } catch (e) {
    errorMsg.value = String(e?.message || 'Failed to load detail.')
  } finally {
    loading.value = false
  }
})
</script>
