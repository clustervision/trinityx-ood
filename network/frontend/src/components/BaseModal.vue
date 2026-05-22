<template>
  <Teleport to="body">
    <div class="tx-modal-overlay" @mousedown.self="$emit('close')">
      <div class="tx-modal-container" :class="sizeClass">
        <button type="button" class="tx-modal-x" @click="$emit('close')">&times;</button>
        <slot />
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'

const props = withDefaults(
  defineProps<{
    size?: 'small' | 'medium' | 'large' | 'wide'
  }>(),
  { size: 'large' },
)

const emit = defineEmits<{ close: [] }>()

function handleEscKey(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    emit('close')
  }
}

const sizeClass = computed(() => {
  if (props.size === 'small') return 'tx-modal-sm'
  if (props.size === 'medium') return 'tx-modal-md'
  if (props.size === 'wide') return 'tx-modal-wide'
  return 'tx-modal-lg'
})

onMounted(() => {
  document.body.style.overflow = 'hidden'
  window.addEventListener('keydown', handleEscKey)
})
onUnmounted(() => {
  document.body.style.overflow = ''
  window.removeEventListener('keydown', handleEscKey)
})
</script>
