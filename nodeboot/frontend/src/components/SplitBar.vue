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
const trackWidth = ref(0)
let resizeObserver
onMounted(() => {
  if (!trackEl.value) return
  const update = () => {
    trackWidth.value = trackEl.value.clientWidth
    if (!props.blocks) fitted.value = Math.max(10, Math.round(((trackWidth.value + 3) / 14.3) * 0.9))
  }
  resizeObserver = new ResizeObserver(update)
  resizeObserver.observe(trackEl.value)
  update()
})
onUnmounted(() => resizeObserver?.disconnect())

const cells = computed(() => distributeBlocks(props.booted, props.booting, props.failed, props.unknown, props.total, props.blocks || fitted.value))

// each label starts on the first pill of its colour, measured in pixels from the
// pill layout (3px gap), so the word and the colour line up exactly
const GAP = 3
const segments = computed(() => {
  const n = cells.value.length
  const pill = (trackWidth.value - (n - 1) * GAP) / n
  const out = []
  for (const [key, count] of [['booted', props.booted], ['booting', props.booting], ['unknown', props.unknown], ['failed', props.failed]]) {
    if (!count) continue
    const first = cells.value.indexOf(`b-${key}`)
    const run = cells.value.filter((c) => c === `b-${key}`).length
    out.push({ key, label: key, count, left: first < 0 ? 0 : first * (pill + GAP), width: run * (pill + GAP) - GAP })
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
        :class="[`c-${s.key}`, { hidden: s.width < 60 }]"
        :style="{ left: `${s.left}px`, width: `${s.width}px` }"
      >{{ s.label[0].toUpperCase() + s.label.slice(1) }}: <b class="fmono">{{ formatCount(s.count) }}</b></span>
      <span v-if="!segments.length" class="split-label">no nodes</span>
    </div>
    <div ref="trackEl" class="progress-track blocks block-bar" :title="segments.map((s) => `${s.label}: ${formatCount(s.count)}`).join(', ')">
      <div v-for="(cls, i) in cells" :key="i" class="progress-block" :class="cls" />
    </div>
  </div>
</template>
