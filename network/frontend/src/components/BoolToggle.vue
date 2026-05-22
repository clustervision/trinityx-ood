<template>
  <div class="tx-field tx-tri-field tx-field-match tx-network-bool-toggle">
    <span class="tx-label">{{ label }}:</span>
    <div class="tx-tri-inner">
      <div class="tx-segmented" role="group" :aria-label="label">
        <button
          type="button"
          class="tx-seg"
          :class="{ 'is-active': modelValue === true }"
          data-v="true"
          @click="$emit('update:modelValue', true)"
        >
          TRUE
        </button>
        <button
          type="button"
          class="tx-seg"
          :class="{ 'is-active': modelValue === false }"
          data-v="false"
          @click="$emit('update:modelValue', false)"
        >
          FALSE
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  modelValue: boolean
}>()

defineEmits<{ 'update:modelValue': [value: boolean] }>()
</script>
