<template>
  <Teleport to="body">
    <div class="tx-modal-overlay" @mousedown.self="$emit('close')">
      <div class="tx-modal-container tx-modal-md">
        <button type="button" class="tx-modal-x" @click="$emit('close')">&times;</button>
        <slot />
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'

const emit = defineEmits<{ close: [] }>()

function handleEscKey(event: KeyboardEvent) {
  if (event.key === 'Escape') emit('close')
}

onMounted(() => {
  document.body.style.overflow = 'hidden'
  window.addEventListener('keydown', handleEscKey)
})
onUnmounted(() => {
  document.body.style.overflow = ''
  window.removeEventListener('keydown', handleEscKey)
})
</script>
