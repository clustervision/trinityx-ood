<template>
  <div class="card-header p-4 bg-white border-bottom metrics-header">
    <div class="metrics-grid">
      <div class="metrics-row metrics-row-1">
        <div class="metrics-main d-flex align-items-center gap-3">
          <div class="dropdown" ref="dropdown1Ref">
            <button
              class="btn dropdown-toggle text-white custom-btn-cyan"
              type="button"
              @click="showDropdown1 = !showDropdown1"
            >
              {{ metric1 ? metric1 : 'No Scale' }}
            </button>
            <ul class="dropdown-menu show dropdown-menu-visible" v-if="showDropdown1">
              <li><a class="dropdown-item" href="#" @click.prevent="selectMetric1(null)">No Scale</a></li>
              <template v-for="opt in metricOptions" :key="opt">
                <li v-if="opt !== metric2">
                  <a class="dropdown-item" href="#" @click.prevent="selectMetric1(opt)" style="min-width: 10em; text-align: left; white-space: nowrap;">{{ opt }}</a>
                </li>
              </template>
            </ul>
          </div>
          <div class="d-flex align-items-center gap-2">
            <span class="text-muted small">0</span>
            <div :class="metric1 ? 'legend-bar' : 'legend-bar-empty'"></div>
            <span class="text-muted small">{{ metric1 ? (range1?.max ?? 100) : 100 }}</span>
          </div>
        </div>
      </div>
      <div class="header-right-controls">
        <slot name="right"></slot>
      </div>
      <div class="metrics-row metrics-row-2 d-flex align-items-center gap-3">
        <div class="dropdown" ref="dropdown2Ref">
          <button
            class="btn dropdown-toggle text-white btn-secondary custom-btn-width"
            type="button"
            @click="showDropdown2 = !showDropdown2"
          >
            {{ metric2 ? metric2 : 'No Scale' }}
          </button>
          <ul class="dropdown-menu show dropdown-menu-visible" v-if="showDropdown2">
            <li><a class="dropdown-item" href="#" @click.prevent="selectMetric2(null)">No Scale</a></li>
            <template v-for="opt in metricOptions" :key="opt">
              <li v-if="opt !== metric1">
                <a class="dropdown-item" href="#" @click.prevent="selectMetric2(opt)" style="min-width: 10em; text-align: left; white-space: nowrap;">{{ opt }}</a>
              </li>
            </template>
          </ul>
        </div>
        <div class="d-flex align-items-center gap-2">
          <span class="text-muted small">0</span>
          <div :class="metric2 ? 'legend-bar' : 'legend-bar-empty'"></div>
          <span class="text-muted small">{{ metric2 ? (range2?.max ?? 100) : 100 }}</span>
        </div>
        <slot name="bottom"></slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

defineProps<{
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
.metrics-header {
  overflow: visible;
}
.metrics-grid {
  display: grid;
  grid-template-columns: 1fr auto;
  grid-template-rows: auto auto;
  align-items: flex-start;
  gap: 0.75rem 0;
  overflow: visible;
}
.metrics-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  overflow: visible;
}
.metrics-row-1 {
  grid-column: 1;
  grid-row: 1;
}
.metrics-row-2 {
  grid-column: 1;
  grid-row: 2;
}
.metrics-row-1 .metrics-main {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 0;
}
/* Light switch: spans both rows, same horizontal padding as left (card p-4), stretch vertically */
.header-right-controls {
  grid-column: 2;
  grid-row: 1 / -1;
  align-self: stretch;
  display: flex;
  align-items: stretch;
  justify-content: flex-end;
  flex-shrink: 0;
}
/* Dropdown not clipped: absolute + high z-index, parent overflow visible */
.dropdown {
  position: relative;
}
.dropdown-menu-visible {
  position: absolute;
  z-index: 1050;
  display: block;
  min-width: 10em;
  max-height: 70vh;
  overflow-y: auto;
}
.custom-btn-cyan {
  background-color: #00C4FF;
  border-color: #00C4FF;
  min-width: 200px;
  border-radius: 5px;
  text-align: left;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: none;
}
.custom-btn-cyan:hover { background-color: #00b0e6; }

.custom-btn-width {
  min-width: 200px;
  text-align: left;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #7d899b;
  border-color: #7d899b;
  box-shadow: none;
}

.legend-bar {
  width: 250px;
  max-width: 100%;
  height: 20px;
  background: linear-gradient(120deg, hsl(246, 100%, 50%),hsl(129, 95%, 43%),hsl(62, 93%, 46%), hsl(0, 100%, 50%));
  border: 1px solid #ddd;
  border-radius: 2px;
}

.legend-bar-empty {
  width: 250px;
  max-width: 100%;
  height: 20px;
  background: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 2px;
}

.text-muted {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #8898aa !important;
  font-weight: bold;
  min-width: 30px;
  text-align: center;
}

.fade-in { animation: fadeIn 0.3s ease-in; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>
