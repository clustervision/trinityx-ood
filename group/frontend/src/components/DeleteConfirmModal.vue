<script setup lang="ts">
import { ref } from 'vue'
import BaseModal from './BaseModal.vue'
import { deleteGroup } from '@/services/api'

const props = defineProps({
  groupName: { type: String, required: true },
})
const emit = defineEmits(['close', 'deleted'])

const deleting = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

async function onDelete() {
  if (deleting.value) return

  deleting.value = true
  errorMsg.value = ''
  successMsg.value = ''

  try {
    const result = await deleteGroup(props.groupName)
    successMsg.value = result.content.message
    console.log(result);

  setTimeout(() => {
      emit('deleted')
      emit('close')
    }, 3000)

  } catch (err: unknown) {
    if (err instanceof Error) {
      errorMsg.value = err.message
    } else {
      errorMsg.value = 'Delete failed.'
    }
  } finally {
    deleting.value = false

  }
}

</script>


<template>
  <BaseModal size="small" @close="$emit('close')">
    <div class="tx-delete-confirm">
      <div v-if="successMsg" class="alert alert-success" role="alert">{{ successMsg }}</div>
      <div v-if="errorMsg" class="alert alert-danger" role="alert">{{ errorMsg }}</div>
      <h3 class="tx-delete-title">Delete group <strong>{{ groupName }}</strong>?</h3>
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

