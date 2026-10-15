<script setup>
import { computed } from 'vue'
import { distributeBlocks } from '../utils/progress.js'

const props = defineProps({
  booted: { type: Number, default: 0 },
  booting: { type: Number, default: 0 },
  failed: { type: Number, default: 0 },
  unknown: { type: Number, default: 0 },
  total: { type: Number, default: 0 },
  blocks: { type: Number, default: 20 },
})

const cells = computed(() => distributeBlocks(props.booted, props.booting, props.failed, props.unknown, props.total, props.blocks))
</script>

<template>
  <div class="progress-track blocks block-bar">
    <div v-for="(cls, i) in cells" :key="i" class="progress-block" :class="cls" />
  </div>
</template>
