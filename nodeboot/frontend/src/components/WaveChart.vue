<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  phase1Pct: { type: Number, default: 0 },
  phase2Pct: { type: Number, default: 0 },
  phase3Pct: { type: Number, default: 0 },
  isEmpty: { type: Boolean, default: false },
  curveSeed: { type: Array, default: () => [25, 30, 45] },
})

const WIDTH = 400
const HEIGHT = 200
const HALF_THICKNESS = 36
const WAVE_PERIOD = 4200

const band1El = ref(null)
const band2El = ref(null)
const band3El = ref(null)
const clipEl = ref(null)
const label1El = ref(null)
const label2El = ref(null)
const label3El = ref(null)

const uid = `nb${Math.random().toString(36).slice(2, 9)}`
const shineId = `${uid}Shine`
const clipId = `${uid}Clip`

/** Smooth sine centerline — matches trix1221_lconsole bundle. */
function waveY(x, phase) {
  const mid = HEIGHT * 0.5
  const amp = 28
  return mid + amp * Math.sin((x / WIDTH) * Math.PI * 2 * 1.08 + phase)
}

function wavePhase(curveSeed, time) {
  const seed = Array.isArray(curveSeed) && curveSeed.length
    ? curveSeed.reduce((sum, value) => sum + value, 0) / curveSeed.length
    : 80
  return seed * 0.01 + time / WAVE_PERIOD
}

function ribbonSegmentPath(left, right, phase) {
  if (right - left < 0.8) return ''

  const half = HALF_THICKNESS
  const steps = Math.max(48, Math.round(Math.abs(right - left) / 2))
  const points = []

  for (let i = 0; i <= steps; i++) {
    const x = left + ((right - left) * i) / steps
    const centerY = waveY(x, phase)
    let xTop = x
    let xBottom = x
    if (i === 0) {
      xTop = left
      xBottom = left
    }
    if (i === steps) {
      xTop = right
      xBottom = right
    }
    points.push([xTop, centerY - half, xBottom, centerY + half])
  }

  let d = `M${points[0][0].toFixed(2)},${points[0][1].toFixed(2)}`
  for (let i = 1; i < points.length; i++) {
    d += ` L${points[i][0].toFixed(2)},${points[i][1].toFixed(2)}`
  }
  for (let i = points.length - 1; i >= 0; i--) {
    d += ` L${points[i][2].toFixed(2)},${points[i][3].toFixed(2)}`
  }
  return `${d} Z`
}

function placeLabel(el, x, pct, phase, onLight) {
  if (!el) return
  if (Math.round(pct) <= 0) {
    el.style.display = 'none'
    return
  }
  el.style.display = ''
  const y = waveY(x, phase)
  el.style.left = `${((x / WIDTH) * 100).toFixed(1)}%`
  el.style.top = `${((y / HEIGHT) * 100).toFixed(1)}%`
  el.style.bottom = 'auto'
  el.style.transform = 'translate(-50%, -50%)'
  el.textContent = `${Math.round(pct)}%`
  el.className = onLight ? 'wave-label on-light' : 'wave-label on-dark'
}

function renderBands(p1, p2, p3, phase) {
  const x1 = (WIDTH * p1) / 100
  const x2 = (WIDTH * (p1 + p2)) / 100
  const path1 = ribbonSegmentPath(0, x1, phase)
  const path2 = ribbonSegmentPath(x1, x2, phase)
  const path3 = ribbonSegmentPath(x2, WIDTH, phase)

  band1El.value?.setAttribute('d', path1)
  band2El.value?.setAttribute('d', path2)
  band3El.value?.setAttribute('d', path3)
  clipEl.value?.setAttribute('d', path1 + path2 + path3)

  placeLabel(label1El.value, x1 / 2, p1, phase, false)
  placeLabel(label2El.value, (x1 + x2) / 2, p2, phase, false)
  placeLabel(label3El.value, (x2 + WIDTH) / 2, p3, phase, true)
}

let currentPhases = [25, 30, 45]
let fromPhases = [25, 30, 45]
let toPhases = [25, 30, 45]
let transitionStart = 0
let transitionDuration = 1
let frameId = 0

function startTransition(target, durationMs) {
  fromPhases = [...currentPhases]
  toPhases = target
  transitionDuration = durationMs
  transitionStart = performance.now()
}

function animate(now) {
  const t = Math.min(1, (now - transitionStart) / transitionDuration)
  const eased = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2
  const p1 = fromPhases[0] + (toPhases[0] - fromPhases[0]) * eased
  const p2 = fromPhases[1] + (toPhases[1] - fromPhases[1]) * eased
  const p3 = 100 - p1 - p2
  currentPhases = [p1, p2, p3]
  renderBands(p1, p2, p3, wavePhase(props.curveSeed, now))
  frameId = requestAnimationFrame(animate)
}

onMounted(() => {
  startTransition([props.phase1Pct, props.phase2Pct, props.phase3Pct], 1)
  frameId = requestAnimationFrame(animate)
})

onUnmounted(() => cancelAnimationFrame(frameId))

watch(
  () => [props.phase1Pct, props.phase2Pct, props.phase3Pct],
  ([p1, p2]) => startTransition([p1, p2, 100 - p1 - p2], 700),
)
</script>

<template>
  <div class="visual-area" :class="{ 'is-empty': isEmpty }">
    <svg viewBox="0 0 400 200" preserveAspectRatio="none">
      <defs>
        <linearGradient
          :id="shineId"
          gradientUnits="userSpaceOnUse"
          x1="0"
          y1="0"
          x2="120"
          y2="0"
        >
          <stop offset="0%" stop-color="#fff" stop-opacity="0" />
          <stop offset="50%" stop-color="#fff" stop-opacity="0.35" />
          <stop offset="100%" stop-color="#fff" stop-opacity="0" />
        </linearGradient>
        <clipPath :id="clipId">
          <path ref="clipEl" />
        </clipPath>
      </defs>
      <path ref="band1El" class="wave-band" fill="#1D4ED8" />
      <path ref="band2El" class="wave-band" fill="#54A0FF" />
      <path ref="band3El" class="wave-band" fill="#C0DAFF" />
      <rect
        class="wave-shine"
        x="-120"
        y="0"
        width="120"
        height="200"
        :fill="`url(#${shineId})`"
        :clip-path="`url(#${clipId})`"
        style="pointer-events: none"
      />
    </svg>
    <span ref="label1El" class="wave-label on-dark" />
    <span ref="label2El" class="wave-label on-dark" />
    <span ref="label3El" class="wave-label on-light" />
    <div class="chart-empty-msg">No nodes currently booting</div>
  </div>
</template>
