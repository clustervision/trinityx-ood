<script setup lang="ts">

import { ref, onMounted, onBeforeUnmount } from 'vue'
import type { AxiosInstance } from 'axios'
import BaseModal from './BaseModal.vue'
import { formatBMCNameDisplay, bmcNameTitle } from '@/constants/bmcName'


const props = defineProps<{
  apiClient: AxiosInstance
  bmcName: string,
}>()

const deleting = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

const emit = defineEmits(['close', 'deleted'])

function handleEscKey(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    emit('close')
  }
}

async function onDelete() {
  if (deleting.value) return

  deleting.value = true
  errorMsg.value = ''
  successMsg.value = ''

  try {
    const recordName = encodeURIComponent(props.bmcName)
    const { data } = await props.apiClient.delete(`/api/v1/delete/${recordName}`)

    if (data.status === true) {
      successMsg.value = data.content?.message || 'BMC Setup deleted successfully.'

      setTimeout(() => {
        emit('deleted')
        emit('close')
      }, 3000)

      return
    }

    errorMsg.value = data.content?.message || 'Delete failed.'
    deleting.value = false
  } catch (err: unknown) {
    errorMsg.value = err instanceof Error ? err.message : 'Unknown error occurred.'
    deleting.value = false
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleEscKey)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleEscKey)
})

</script>


<template>
  <BaseModal size="small" @close="$emit('close')">
    <div class="tx-delete-confirm">
      <div v-if="errorMsg" class="alert alert-danger" role="alert">{{ errorMsg }}</div>
      <div v-if="successMsg" class="alert alert-success" role="alert">{{ successMsg }}</div>
      <h3 class="tx-delete-title">Delete BMC Setup <strong class="tx-title-highlight-name" :title="bmcNameTitle(bmcName)">{{ formatBMCNameDisplay(bmcName) }}</strong>?</h3>
      <p class="tx-delete-desc">This action cannot be undone.</p>
      <div class="tx-delete-actions">
        <button type="button" class="tx-btn tx-btn-outline-blue" @click="$emit('close')">Cancel</button>
        <button type="button" class="tx-btn tx-btn-danger" :disabled="deleting" :class="{ 'tx-btn-disabled': deleting }" @click="onDelete">{{ deleting ? 'Deleting...' : 'Delete' }}</button>
      </div>
    </div>
  </BaseModal>
</template>

