<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  size: { type: String, default: 'large' },
  closeDisabled: { type: Boolean, default: false },
})
const emit = defineEmits(['close'])

const sizeClass = computed(() => {
  if (props.size === 'small') return 'tx-modal-sm'
  if (props.size === 'medium') return 'tx-modal-md'
  if (props.size === 'wide') return 'tx-modal-wide'
  return 'tx-modal-lg'
})

onMounted(() => { document.body.style.overflow = 'hidden' })
onUnmounted(() => { document.body.style.overflow = '' })

function tryClose() {
  if (props.closeDisabled) return
  emit('close')
}
</script>

<template>
  <Teleport to="body">
    <div class="tx-modal-overlay" @mousedown.self="tryClose">
      <div class="tx-modal-container" :class="sizeClass">
        <button type="button" class="tx-modal-x" :disabled="closeDisabled" @click="tryClose">&times;</button>
        <slot />
      </div>
    </div>
  </Teleport>
</template>

