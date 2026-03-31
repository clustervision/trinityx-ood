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
        <div class="scale-row">
          <div class="dropdown" ref="dropdown1Ref">
            <button
              class="btn scale-dropdown-btn dropdown-toggle"
              type="button"
              @click="showDropdown1 = !showDropdown1"
            >
              {{ metric1 ? metric1 : 'Choose Scale' }}
            </button>
            <ul class="dropdown-menu show dropdown-menu-visible" v-if="showDropdown1">
              <li><a class="dropdown-item" href="#" @click.prevent="selectMetric1(null)">No Scale</a></li>
              <template v-for="opt in metricOptions" :key="opt">
                <li v-if="opt !== metric2">
                  <a
                    class="dropdown-item"
                    href="#"
                    @click.prevent="selectMetric1(opt)"
                    style="min-width: 10em; text-align: left; white-space: nowrap;"
                  >{{ opt }}</a>
                </li>
              </template>
            </ul>
          </div>
          <div class="scale-slider-wrap">
            <span class="scale-edge">0</span>
            <input
              type="range"
              class="metric-scale-slider"
              min="0"
              max="100"
              :value="slider1Value"
              disabled
              tabindex="-1"
              aria-hidden="true"
            />
            <span class="scale-edge">100</span>
          </div>
        </div>
        <div class="scale-row">
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
          <div class="scale-slider-wrap">
            <span class="scale-edge">0</span>
            <input
              type="range"
              class="metric-scale-slider"
              min="0"
              max="100"
              :value="slider2Value"
              disabled
              tabindex="-1"
              aria-hidden="true"
            />
            <span class="scale-edge">100</span>
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

const props = defineProps<{
  metric1: string | null;
  metric2: string | null;
  range1?: { min: number; max: number };
  range2?: { min: number; max: number };
}>();

const metricOptions = [
  'Temperature',
  'System Load',
  'Power Consumption',
  'GPU Temperature'
];

const slider1Value = computed(() => {
  if (!props.metric1) return 50;
  const max = props.range1?.max ?? 100;
  return Math.min(100, Math.max(0, Math.round(max)));
});

const slider2Value = computed(() => {
  if (!props.metric2) return 50;
  const max = props.range2?.max ?? 100;
  return Math.min(100, Math.max(0, Math.round(max)));
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
  flex: 1 1 280px;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-width: 240px;
  max-width: 520px;
}

.scale-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem 1rem;
  overflow: visible;
}

.dropdown {
  position: relative;
  flex: 0 0 auto;
}

.dropdown-menu-visible {
  position: absolute;
  z-index: 1050;
  display: block;
  min-width: 10em;
  max-height: 70vh;
  overflow-y: auto;
  left: 0;
  top: 100%;
  margin-top: 4px;
}

.scale-dropdown-btn {
  min-width: 160px;
  text-align: left;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-family: var(--font-geist, 'Geist', system-ui, sans-serif);
  font-weight: 500;
  font-size: 0.875rem;
  background: #eef3ff !important;
  border: 1px solid #5376ea !important;
  color: #5376ea !important;
  border-radius: 8px;
  padding: 0.45rem 0.85rem;
  box-shadow: none;
}

.scale-dropdown-btn:hover,
.scale-dropdown-btn:focus {
  background: #eef3ff !important;
  border-color: #5376ea !important;
  color: #5376ea !important;
}

.scale-slider-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1 1 200px;
  min-width: 160px;
}

.scale-edge {
  font-size: 0.75rem;
  font-weight: 500;
  color: #5376ea;
  min-width: 1.25rem;
  text-align: center;
  font-family: var(--font-geist, 'Geist', system-ui, sans-serif);
}

.metric-scale-slider {
  flex: 1 1 auto;
  height: 6px;
  border-radius: 3px;
  accent-color: #5376ea;
  cursor: default;
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
