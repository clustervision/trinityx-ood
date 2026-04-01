<template>
  <div class="metrics-header-card">
    <div class="metrics-shell">
      <div class="metrics-left">
        <div class="metrics-left-top">
          <slot name="fullscreen"></slot>
          <slot name="zoom"></slot>
        </div>
        <div class="metrics-left-bottom">
          <slot name="bottom"></slot>
        </div>
      </div>

      <div class="metrics-scales">
        <div class="scale-bundle">
          <div class="dropdown" ref="dropdown1Ref">
            <button
              class="btn scale-dropdown-btn dropdown-toggle"
              type="button"
              @click="showDropdown1 = !showDropdown1"
            >
              <span class="scale-dropdown-label">{{ metric1 ? metric1 : 'Choose Scale' }}</span>
            </button>
            <ul class="dropdown-menu show dropdown-menu-visible" v-if="showDropdown1">
              <li>
                <a class="dropdown-item scale-dropdown-item" href="#" @click.prevent="selectMetric1(null)">No Scale</a>
              </li>
              <template v-for="opt in metricOptions" :key="opt">
                <li v-if="opt !== metric2">
                  <a class="dropdown-item scale-dropdown-item" href="#" @click.prevent="selectMetric1(opt)">{{ opt }}</a>
                </li>
              </template>
            </ul>
          </div>
          <div class="scale-display-wrap" aria-hidden="true">
            <span class="scale-edge">0</span>
            <div class="scale-track">
              <div
                class="scale-track-fill"
                :style="barFillStyle1"
              ></div>
            </div>
            <span class="scale-edge scale-edge-max" :title="maxLabel1">{{ maxLabel1 }}</span>
          </div>
        </div>
        <div class="scale-bundle">
          <div class="dropdown" ref="dropdown2Ref">
            <button
              class="btn scale-dropdown-btn dropdown-toggle"
              type="button"
              @click="showDropdown2 = !showDropdown2"
            >
              {{ metric2 ? metric2 : 'Choose Scale' }}
            </button>
            <ul class="dropdown-menu show dropdown-menu-visible" v-if="showDropdown2">
              <li><a class="dropdown-item" href="#" @click.prevent="selectMetric2(null)">No Scale</a></li>
              <template v-for="opt in metricOptions" :key="opt">
                <li v-if="opt !== metric1">
                  <a
                    class="dropdown-item"
                    href="#"
                    @click.prevent="selectMetric2(opt)"
                    style="min-width: 10em; text-align: left; white-space: nowrap;"
                  >{{ opt }}</a>
                </li>
              </template>
            </ul>
          </div>
          <div class="scale-display-wrap" aria-hidden="true">
            <span class="scale-edge">0</span>
            <div class="scale-track">
              <div
                class="scale-track-fill"
                :style="barFillStyle2"
              ></div>
            </div>
            <span class="scale-edge scale-edge-max" :title="maxLabel2">{{ maxLabel2 }}</span>
          </div>
        </div>
      </div>

      <div class="metrics-far-right">
        <slot name="right"></slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';

type HeaderMetricRange = {
  min: number;
  max: number;
  hasData?: boolean;
  peak?: number;
  avg?: number;
};

const props = defineProps<{
  metric1: string | null;
  metric2: string | null;
  range1?: HeaderMetricRange;
  range2?: HeaderMetricRange;
}>();

const metricOptions = [
  'Temperature',
  'System Load',
  'Power Consumption',
  'GPU Temperature'
];

/** 红→黄→绿→青→蓝→紫 彩虹条（所有指标共用） */
const RAINBOW_BAR =
  'linear-gradient(90deg, #ff0000 0%, #ffaa00 14%, #ffee00 28%, #22c55e 42%, #06b6d4 56%, #2563eb 70%, #7c3aed 84%, #db2777 100%)';

function formatPeak(n: number): string {
  if (!Number.isFinite(n)) return '—';
  const a = Math.abs(n);
  if (a >= 100) return n.toFixed(0);
  if (a >= 10) return n.toFixed(1);
  return n.toFixed(2);
}

const barFillStyle1 = computed(() => ({
  width: props.metric1 ? '100%' : '0%',
  background: props.metric1 ? RAINBOW_BAR : '#b8c0d0',
}));

const barFillStyle2 = computed(() => ({
  width: props.metric2 ? '100%' : '0%',
  background: props.metric2 ? RAINBOW_BAR : '#b8c0d0',
}));

const maxLabel1 = computed(() => {
  if (!props.metric1) return '';
  if (props.range1?.hasData) return formatPeak(props.range1.peak ?? 0);
  return '—';
});

const maxLabel2 = computed(() => {
  if (!props.metric2) return '';
  if (props.range2?.hasData) return formatPeak(props.range2.peak ?? 0);
  return '—';
});

const emit = defineEmits(['update:metric1', 'update:metric2', 'refresh']);

const showDropdown1 = ref(false);
const showDropdown2 = ref(false);
const dropdown1Ref = ref<HTMLElement | null>(null);
const dropdown2Ref = ref<HTMLElement | null>(null);

const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as Node;
  if (dropdown1Ref.value && !dropdown1Ref.value.contains(target)) {
    showDropdown1.value = false;
  }
  if (dropdown2Ref.value && !dropdown2Ref.value.contains(target)) {
    showDropdown2.value = false;
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});

const selectMetric1 = (val: string | null) => {
  emit('update:metric1', val);
  showDropdown1.value = false;
};

const selectMetric2 = (val: string | null) => {
  emit('update:metric2', val);
  showDropdown2.value = false;
};
</script>

<style scoped>
.metrics-header-card {
  overflow: visible;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
  padding: 1rem 1.25rem;
  margin-top: -6px;
  margin-bottom: 0.5rem;
  font-family: var(--font-geist, 'Geist', system-ui, sans-serif);
  font-weight: 500;
}

.metrics-shell {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 1.25rem 1.5rem;
  overflow: visible;
}

.metrics-left {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  flex-shrink: 0;
}

.metrics-left-top {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 0.65rem;
  flex-wrap: wrap;
}

.metrics-left-top :deep(.rack-fullscreen-btn) {
  flex-shrink: 0;
  min-width: unset;
}

.metrics-left-top :deep(.rack-zoom-btn) {
  flex-shrink: 0;
}

.metrics-left-bottom :deep(.flip-view-btn) {
  flex-shrink: 0;
}

.metrics-scales {
  flex: 1 1 320px;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-width: 280px;
  max-width: 640px;
}

.scale-bundle {
  --rack-toolbar-height: 30px;
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  gap: 0.5rem;
  padding: 4px 6px;
  min-height: var(--rack-toolbar-height);
  background: #eef3ff;
  border: none;
  border-radius: 8px;
  overflow: visible;
  box-sizing: border-box;
}

.dropdown {
  position: relative;
  flex: 0 0 152px;
  width: 152px;
  min-width: 152px;
  max-width: 152px;
}

.dropdown-menu-visible {
  position: absolute;
  z-index: 1050;
  display: block;
  /* Narrower than theme .dropdown-menu (12rem); width still grows with longest label */
  min-width: 6.75rem;
  width: max-content;
  max-width: min(100vw - 1.5rem, 18rem);
  max-height: 70vh;
  overflow-y: auto;
  left: 0;
  top: 100%;
  margin-top: 4px;
  box-sizing: border-box;
}

.dropdown-menu-visible .scale-dropdown-item {
  font-family: var(--font-geist, 'Geist', system-ui, sans-serif);
  font-size: 13px;
  font-weight: 550;
  line-height: 1.3;
  text-align: left;
  white-space: nowrap;
}

.scale-dropdown-btn {
  width: 100%;
  height: var(--rack-toolbar-height, 38px);
  text-align: left;
  display: inline-flex;
  justify-content: space-between;
  align-items: center;
  overflow: hidden;
  font-family: var(--font-geist, 'Geist', system-ui, sans-serif);
  font-weight: 550;
  font-size: 13px;
  line-height: 1;
  background: #eef3ff !important;
  border: none !important;
  outline: none !important;
  color: #5376ea !important;
  border-radius: 8px;
  padding: 0 8px;
  box-shadow: none !important;
  box-sizing: border-box;
}

.scale-dropdown-label {
  flex: 1 1 auto;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  text-align: left;
}

.scale-dropdown-btn:hover,
.scale-dropdown-btn:focus,
.scale-dropdown-btn:focus-visible {
  background: #e2e9fc !important;
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
  color: #5376ea !important;
}

/* 0–track–100: white background, prefer wider flex growth */
.scale-display-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1 1 220px;
  min-width: 180px;
  min-height: var(--rack-toolbar-height, 38px);
  padding: 0 12px;
  background: #fff;
  border-radius: 4px;
  box-sizing: border-box;
}

.scale-edge {
  font-size: 13px;
  font-weight: 550;
  color: #5376ea;
  min-width: 1.25rem;
  text-align: center;
  font-family: var(--font-geist, 'Geist', system-ui, sans-serif);
}

.scale-edge-max {
  min-width: 2.5rem;
  max-width: 4.5rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.scale-track {
  flex: 1 1 auto;
  height: 6px;
  border-radius: 999px;
  background: #dfe3ea;
  border: none;
  overflow: hidden;
  pointer-events: none;
}

.scale-track-fill {
  height: 100%;
  border-radius: 999px;
  background: #b8c0d0;
  max-width: 100%;
  transition: width 0.2s ease;
}

.metrics-far-right {
  margin-left: auto;
  display: flex;
  align-items: stretch;
  align-self: stretch;
  flex-shrink: 0;
}

@media (max-width: 991.98px) {
  .metrics-far-right {
    margin-left: 0;
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
