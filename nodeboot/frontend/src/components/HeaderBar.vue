<script setup>
import { ref, computed, watch } from 'vue'
import { formatCount } from '../utils/progress.js'
import { overviewOf } from '../utils/stages.js'
import SplitBar from './SplitBar.vue'
import { ICON_CHECK, ICON_BOOTING, ICON_WARNING, ICON_LAYERS, ICON_GRID, ICON_UNKNOWN } from '../utils/icons.js'

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

// failed/unknown split by reason, as Boot Overview does: the backend's group.failed
// counts both.
const totals = computed(() => {
  const sum = { total: 0, booted: 0, booting: 0, failed: 0, unknown: 0 }
  for (const image of props.images) {
    for (const group of image.groups) {
      const counts = overviewOf(group)
      for (const key in sum) sum[key] += counts[key] || 0
      sum.booted += group.booted
    }
  }
  return sum
})

const pct = computed(() => (totals.value.total ? Math.round((totals.value.booted / totals.value.total) * 100) : 0))
</script>

<template>
  <div class="panel main-card">
    <div class="main-card-header">
      <div class="title-row">
        <div class="main-title fmono">Node Boot Overview</div>
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
      <SplitBar v-bind="totals" labels />
      <div class="main-progress-side">
        <span class="main-progress-pct fmono">{{ pct }}%</span>
      </div>
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
      <div class="stat-pill-row pill-neutral">
        <span class="stat-pill-label">
          <span class="stat-pill-icon" v-html="ICON_UNKNOWN" />
          <span class="stat-pill-text">Unknown:</span>
        </span>
        <span class="stat-pill-value">{{ formatCount(totals.unknown) }}</span>
      </div>
      <div class="main-progress-sub">
        <span class="fmono">{{ formatCount(totals.booted) }} / {{ formatCount(totals.total) }} ({{ pct }}%)</span> nodes booted
      </div>
    </div>
  </div>
</template>
