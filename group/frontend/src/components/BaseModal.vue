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

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  size: { type: String, default: 'large' },
})
defineEmits(['close'])

const sizeClass = computed(() => {
  if (props.size === 'small') return 'tx-modal-sm'
  if (props.size === 'medium') return 'tx-modal-md'
  return 'tx-modal-lg'
})

onMounted(() => { document.body.style.overflow = 'hidden' })
onUnmounted(() => { document.body.style.overflow = '' })
</script>
