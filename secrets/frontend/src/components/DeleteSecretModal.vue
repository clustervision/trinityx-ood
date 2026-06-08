<template>
  <BaseModal @close="$emit('close')">
    <div class="tx-delete-confirm">
      <h3 class="tx-delete-title">Delete secret <strong>{{ item.name }}</strong>?</h3>
      <p class="tx-delete-desc">{{ item.entity }} / {{ item.owner }}</p>
      <div class="tx-delete-actions">
        <button class="tx-btn tx-btn-outline-blue" @click="$emit('close')">Cancel</button>
        <button class="tx-btn tx-btn-danger" @click="$emit('confirm')">Delete</button>
      </div>
    </div>
  </BaseModal>
</template>

<script setup lang="ts">
import BaseModal from './BaseModal.vue'
import type { SecretRecord } from '@/types'

defineProps<{ item: SecretRecord }>()
defineEmits<{ close: []; confirm: [] }>()
</script>
