menuVisible<template>
  <div class="card-header p-4 bg-white border-bottom">

    <div class="d-flex flex-column gap-3">

      <div class="d-flex align-items-center gap-3">
        <div class="dropdown">
          <button
            class="btn dropdown-toggle text-white custom-btn-cyan"
            type="button"
            @click="showDropdown1 = !showDropdown1"
          >
            {{ metric1 ? metric1 : 'No Scale' }}
          </button>

          <ul class="dropdown-menu show" v-if="showDropdown1" style="display: block; position: absolute; z-index: 1000;">

              <li><a class="dropdown-item" href="#" @click.prevent="selectMetric1(null)">No Scale</a></li>

              <template v-for="opt in metricOptions" :key="opt">
                <li v-if="opt !== metric2">
                  <a class="dropdown-item" href="#" @click.prevent="selectMetric1(opt)" style="min-width: 10em; text-align: left; white-space: nowrap;">{{ opt   }}</a>
                </li>
              </template>
          </ul>
        </div>

        <div class="d-flex align-items-center gap-2">
          <span class="text-muted small">{{ range1?.min ?? 0 }}</span>
          <div :class="metric1 ? 'legend-bar' : 'legend-bar-empty'"></div>
          <span class="text-muted small">{{ range1?.max ?? 90 }}</span>
        </div>
      </div>

      <div class="d-flex align-items-center gap-3">
        <div class="dropdown">
          <button
            class="btn dropdown-toggle text-white btn-secondary custom-btn-width"
            type="button"
            @click="showDropdown2 = !showDropdown2"
          >
            {{ metric2 ? metric2 : 'No Scale' }}
          </button>

          <ul class="dropdown-menu show" v-if="showDropdown2" style="display: block; position: absolute; z-index: 1000;">

              <li><a class="dropdown-item" href="#" @click.prevent="selectMetric2(null)">No Scale</a></li>

              <template v-for="opt in metricOptions" :key="opt">
                <li v-if="opt !== metric1">
                  <a class="dropdown-item" href="#" @click.prevent="selectMetric2(opt)"style="min-width: 10em; text-align: left; white-space: nowrap;">{{ opt   }}</a>
                </li>
              </template>
          </ul>
        </div>

        <div class="d-flex align-items-center gap-2">
          <span class="text-muted small">{{ range2?.min ?? 0 }}</span>
          <div :class="metric2 ? 'legend-bar' : 'legend-bar-empty'"></div>
          <span class="text-muted small">{{ range2?.max ?? 90 }}</span>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

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

const emit = defineEmits(['update:metric1', 'update:metric2', 'refresh']);

const showDropdown1 = ref(false);
const showDropdown2 = ref(false);

// Update type to allow null (for Reset functionality)
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
/* Your existing styles... */
.custom-btn-cyan {
  background-color: #00C4FF;
  border-color: #00C4FF;
  min-width: 200px;
  border-radius: 5px;
  text-align: left;
  display: flex;
  justify-content: space-between;
  align-items: center;
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
}

.legend-bar {
  width: 250px;
  height: 20px;
  background: linear-gradient(120deg, hsl(246, 100%, 50%),hsl(129, 95%, 43%),hsl(62, 93%, 46%), hsl(0, 100%, 50%));
  border: 1px solid #ddd;
  border-radius: 2px;
}

.legend-bar-empty {
  width: 250px;
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
