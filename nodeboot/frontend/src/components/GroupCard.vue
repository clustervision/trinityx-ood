<script setup>
import { computed } from 'vue'
import WaveChart from './WaveChart.vue'
import { ICON_CONSOLE } from '../utils/icons.js'

const MAX_VISIBLE = 4

const props = defineProps({
  group: { type: Object, required: true },
  curveSeed: { type: Array, default: () => [25, 30, 45] },
})

defineEmits(['open-console', 'see-all'])

const phase1Pct = computed(() => (props.group.booting ? (props.group.phase1 / props.group.booting) * 100 : 0))
const phase2Pct = computed(() => (props.group.booting ? (props.group.phase2 / props.group.booting) * 100 : 0))
const phase3Pct = computed(() => (props.group.booting ? (props.group.phase3 / props.group.booting) * 100 : 0))
const visibleFailed = computed(() => props.group.failedNodes.slice(0, MAX_VISIBLE))
const placeholderCount = computed(() => Math.max(0, MAX_VISIBLE - visibleFailed.value.length))
</script>

<template>
  <div class="group-card">
    <div class="group-header">
      <span class="group-title fmono">{{ group.name }}</span>
      <span class="network-pill fsans">Network: {{ group.network }}</span>
    </div>

    <div class="group-body">
      <div class="chart-panel">
        <div class="chart-top-row">
          <div class="status-label fmono">booting</div>
          <span class="pill-count fmono">{{ group.booting }}</span>
        </div>
        <WaveChart
          :phase1-pct="phase1Pct"
          :phase2-pct="phase2Pct"
          :phase3-pct="phase3Pct"
          :is-empty="group.booting === 0"
          :curve-seed="curveSeed"
        />
      </div>

      <div class="stats-column">
        <div class="status-box green-box">
          <div class="status-box-row">
            <span class="status-box-label fmono">booted</span>
            <span class="status-box-value fmono">{{ group.booted }}</span>
          </div>
        </div>

        <div class="status-box tan-box">
          <div class="status-box-row">
            <span class="status-box-label fmono">not booting</span>
            <span class="status-box-value fmono">{{ group.failed }}</span>
          </div>
          <div class="node-list">
            <div
              v-for="node in visibleFailed"
              :key="node"
              class="node-pill"
              @click="$emit('open-console', node)"
            >
              <span>{{ node }}</span>
              <span class="console-icon" v-html="ICON_CONSOLE" />
            </div>
            <div
              v-for="i in placeholderCount"
              :key="`ph-${i}`"
              class="node-pill placeholder"
              aria-hidden="true"
            >
              <span>&nbsp;</span>
              <span class="console-icon" />
            </div>
          </div>
          <button
            v-if="group.failed > MAX_VISIBLE"
            class="see-all-btn"
            @click="$emit('see-all', group)"
          >
            See all {{ group.failed }} Nodes
          </button>
        </div>
      </div>
    </div>

    <div class="legend">
      <div class="legend-item">
        <span class="legend-swatch" style="background: var(--c-blue-mid)" />
        install.discovered
      </div>
      <div class="legend-item">
        <span class="legend-swatch" style="background: var(--c-blue-soft)" />
        install.downloaded
      </div>
      <div class="legend-item">
        <span class="legend-swatch" style="background: var(--c-blue-lightest)" />
        install.unpack
      </div>
    </div>
  </div>
</template>
