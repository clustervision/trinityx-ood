<script setup>
import { ref, computed, watch } from 'vue'
import { distributeBlocks, formatCount } from '../utils/progress.js'
import { useProgressTrack } from '../composables/useProgressTrack.js'
import { ICON_CHECK, ICON_BOOTING, ICON_WARNING, ICON_LAYERS, ICON_GRID } from '../utils/icons.js'

const props = defineProps({
  images: { type: Array, default: () => [] },
})

const stored = localStorage.getItem('nodeboot-theme')
const theme = ref(stored === 'dark' ? 'dark' : 'light')

const isDark = computed(() => theme.value === 'dark')

watch(isDark, (dark) => {
  document.documentElement.classList.toggle('dark', dark)
}, { immediate: true })

watch(theme, (value) => {
  localStorage.setItem('nodeboot-theme', value)
})

const themeOptions = [
  { value: 'light', label: 'Light theme' },
  { value: 'dark', label: 'Dark theme' },
]

const { trackEl, blockCount } = useProgressTrack(1, 60, 6, 5, 3)

const totals = computed(() => {
  let total = 0
  let booted = 0
  let booting = 0
  let failed = 0
  for (const image of props.images) {
    for (const group of image.groups) {
      total += group.total
      booted += group.booted
      booting += group.booting
      failed += group.failed
    }
  }
  return { total, booted, booting, failed }
})

const pct = computed(() => (totals.value.total ? Math.round((totals.value.booted / totals.value.total) * 100) : 0))
const blocks = computed(() => distributeBlocks(totals.value.booted, totals.value.booting, totals.value.failed, totals.value.total, blockCount.value))

function blockClass(index) {
  return blocks.value[index - 1]
}
</script>

<template>
  <div class="panel main-card">
    <div class="main-card-header">
      <div class="title-row">
        <div class="main-title fmono">Node Boot</div>
        <div class="theme-toggle-group" role="radiogroup" aria-label="Theme">
          <button
            v-for="option in themeOptions"
            :key="option.value"
            class="theme-toggle-segment"
            :class="{ active: theme === option.value }"
            :aria-label="option.label"
            :title="option.label"
            role="radio"
            :aria-checked="theme === option.value"
            @click="theme = option.value"
          >
            <svg v-if="option.value === 'light'" viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="8" cy="8" r="3.2" />
              <path d="M8 1.2v1.6M8 13.2v1.6M1.2 8h1.6M13.2 8h1.6M3.4 3.4l1.1 1.1M11.5 11.5l1.1 1.1M3.4 12.6l1.1-1.1M11.5 4.5l1.1-1.1" />
            </svg>
            <svg v-else viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">
              <path d="M13.8 9.8A6 6 0 0 1 6.2 2.2a6 6 0 1 0 7.6 7.6Z" />
            </svg>
          </button>
        </div>
      </div>
      <div class="header-right">
        <div class="live-badge">
          <span class="live-dot" />
          Live
        </div>
      </div>
    </div>

    <div class="main-progress-row">
      <div ref="trackEl" class="main-progress-track">
        <div
          v-for="i in blockCount"
          :key="i"
          class="progress-block"
          :class="blockClass(i)"
        />
      </div>
      <span class="main-progress-pct fmono">{{ pct }}%</span>
    </div>

    <div class="main-progress-sub fmono">
      {{ formatCount(totals.booted) }} / {{ formatCount(totals.total) }} nodes booted
    </div>

    <div class="main-stats-row">
      <div class="stat-pill-row pill-purple">
        <span class="stat-pill-label">
          <span class="stat-pill-icon" v-html="ICON_LAYERS" />
          <span class="stat-pill-text">Images:</span>
        </span>
        <span class="stat-pill-value">{{ images.length }}</span>
      </div>
      <div class="stat-pill-row pill-neutral">
        <span class="stat-pill-label">
          <span class="stat-pill-icon" v-html="ICON_GRID" />
          <span class="stat-pill-text">Nodes:</span>
        </span>
        <span class="stat-pill-value">{{ formatCount(totals.total) }}</span>
      </div>
      <div class="stat-pill-row pill-green">
        <span class="stat-pill-label">
          <span class="stat-pill-icon" v-html="ICON_CHECK" />
          <span class="stat-pill-text">Booted:</span>
        </span>
        <span class="stat-pill-value">{{ formatCount(totals.booted) }}</span>
      </div>
      <div class="stat-pill-row pill-blue">
        <span class="stat-pill-label">
          <span class="stat-pill-icon" v-html="ICON_BOOTING" />
          <span class="stat-pill-text">Booting:</span>
        </span>
        <span class="stat-pill-value">{{ formatCount(totals.booting) }}</span>
      </div>
      <div class="stat-pill-row pill-tan">
        <span class="stat-pill-label">
          <span class="stat-pill-icon" v-html="ICON_WARNING" />
          <span class="stat-pill-text">Failed:</span>
        </span>
        <span class="stat-pill-value">{{ formatCount(totals.failed) }}</span>
      </div>
    </div>
  </div>
</template>
