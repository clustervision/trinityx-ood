<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { distributeBlocks, formatCount } from '../utils/progress.js'

const props = defineProps({
  booted: { type: Number, default: 0 },
  booting: { type: Number, default: 0 },
  unknown: { type: Number, default: 0 },
  failed: { type: Number, default: 0 },
  total: { type: Number, default: 0 },
  blocks: { type: Number, default: null },
  labels: { type: Boolean, default: false },
})

// No block count given: fit as many pills as the track is wide, at the same pill
// size as the 10-pill row bars (140px wide, 3px gap), minus a tenth so the main bar
// reads a little calmer than the rows.
const trackEl = ref(null)
const fitted = ref(10)
let resizeObserver
onMounted(() => {
  if (props.blocks || !trackEl.value) return
  const update = () => { fitted.value = Math.max(10, Math.round(((trackEl.value.clientWidth + 3) / 14.3) * 0.9)) }
  resizeObserver = new ResizeObserver(update)
  resizeObserver.observe(trackEl.value)
  update()
})
onUnmounted(() => resizeObserver?.disconnect())

const cells = computed(() => distributeBlocks(props.booted, props.booting, props.failed, props.unknown, props.total, props.blocks || fitted.value))

// label spans follow the real shares, so each sits over its own run of blocks
const segments = computed(() => {
  let start = 0
  const out = []
  for (const [key, label, count] of [['booted', 'booted', props.booted], ['booting', 'booting', props.booting], ['unknown', 'unknown', props.unknown], ['failed', 'failed', props.failed]]) {
    const share = props.total ? (count / props.total) * 100 : 0
    if (count) out.push({ key, label, count, start, share })
    start += share
  }
  return out
})
</script>

<template>
  <div class="boot-split">
    <div v-if="labels" class="split-labels">
      <span
        v-for="s in segments"
        :key="s.key"
        class="split-label"
        :class="[`c-${s.key}`, { hidden: s.share < 7 }]"
        :style="{ left: `${s.start}%`, width: `${s.share}%` }"
      >{{ s.label[0].toUpperCase() + s.label.slice(1) }}: <b class="fmono">{{ formatCount(s.count) }}</b></span>
      <span v-if="!segments.length" class="split-label">no nodes</span>
    </div>
    <div ref="trackEl" class="progress-track blocks block-bar" :title="segments.map((s) => `${s.label}: ${formatCount(s.count)}`).join(', ')">
      <div v-for="(cls, i) in cells" :key="i" class="progress-block" :class="cls" />
    </div>
  </div>
</template>
