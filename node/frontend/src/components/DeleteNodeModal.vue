<script setup lang="ts">
import { ref } from 'vue'
import BaseModal from './BaseModal.vue'
import { deleteNode } from '@/api'

const props = defineProps<{
  nodeName: string
}>()

const emit = defineEmits<{
  close: []
  deleted: []
}>()

const deleting = ref(false)
const errorMsg = ref('')

async function onDelete() {
  if (deleting.value) return
  deleting.value = true
  errorMsg.value = ''
  try {
    await deleteNode(props.nodeName)
    emit('deleted')
    emit('close')
  } catch (err: unknown) {
    errorMsg.value = err instanceof Error ? err.message : 'Delete failed.'
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <BaseModal size="small" @close="$emit('close')">
    <div class="tx-delete-confirm">
      <div v-if="errorMsg" class="alert alert-danger" role="alert">{{ errorMsg }}</div>
      <h3 class="tx-delete-title">Delete node <strong>{{ nodeName }}</strong>?</h3>
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
