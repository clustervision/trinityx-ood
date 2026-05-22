<template>
  <BaseModal size="small" @close="$emit('close')">
    <div class="tx-delete-confirm">
      <div v-if="errorMsg" class="alert-danger" role="alert">{{ errorMsg }}</div>
      <h3 class="tx-delete-title">
        Delete <strong>{{ host }}</strong> from network <strong>{{ network }}</strong
        >?
      </h3>
      <p class="tx-delete-desc">This action cannot be undone.</p>
      <div class="tx-delete-actions">
        <button type="button" class="tx-btn tx-btn-outline-blue" @click="$emit('close')">Cancel</button>
        <button type="button" class="tx-btn tx-btn-danger" :disabled="deleting" @click="onDelete">
          {{ deleting ? 'Deleting...' : 'Delete' }}
        </button>
      </div>
    </div>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import BaseModal from './BaseModal.vue'
import { deleteDnsEntry } from '@/api'

const props = defineProps<{ network: string; host: string }>()
const emit = defineEmits<{ close: []; deleted: [] }>()

const deleting = ref(false)
const errorMsg = ref('')

async function onDelete() {
  deleting.value = true
  errorMsg.value = ''
  try {
    await deleteDnsEntry(props.network, props.host)
    emit('deleted')
    emit('close')
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : 'Delete failed.'
  } finally {
    deleting.value = false
  }
}
</script>
