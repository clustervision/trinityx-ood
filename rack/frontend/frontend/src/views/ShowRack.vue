<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import RackMetricsHeader from '@/components/RackMetricsHeader.vue';
import SingleRack from '@/components/SingleRack.vue';
import { useRack } from '@/composables/useRack';
import { useRackMetrics } from '../composables/useRackMetrics';

const props = defineProps<{ rackName: string; }>();
const emit = defineEmits(['close', 'pool-updated', 'device-taken']);

// 2. INITIALIZE COMPOSABLE LOGIC
const { fetchSingleRack } = useRack();
const { metric1, metric2, getMetricForDevice } = useRackMetrics();

// 3. DEFINE LOCAL STATE
const rack = ref<any>(null);
const Url = 'https://yixin3-dev-ctrl001:7755';

// 4. DEFINE HANDLERS
const loadRackData = async () => {
  if (!props.rackName) return;

  // 1. Save the current state if the rack already exists
  const currentShowBack = rack.value ? rack.value.showBackSide : true; // Default to true

  // 2. Fetch the fresh data
  const freshRack = await fetchSingleRack(props.rackName);

  // 3. Re-apply the saved toggle state to the fresh object
  freshRack.showBackSide = currentShowBack;
  
  rack.value = freshRack;
};

const resetRack = (targetRack: any, side: 'front' | 'back') => {
  if (confirm(`Reset ${targetRack.name} ${side} side?`)) {
    // Add your reset API logic here
    console.log("Resetting rack side:", side);
  }
};

const onDrop = async (event: DragEvent, targetRack: any, targetU: number, side: 'front' | 'back') => {
  const data = event.dataTransfer?.getData('application/json');
  if (!data) return;
  const device = JSON.parse(data);

  // Optimistic UI update: Remove from old position if it was in the rack
  if (device.dragSource === 'rack' && rack.value) {
     rack.value.slots.forEach((s: any) => {
        if (s.device && s.device.name === device.name) s.device = null;
     });
  } else if (device.dragSource === 'pool') {
      emit('device-taken', device.name);
  }

  try {
    const payload = {
      rack: targetRack.name,
      name: device.name,
      position: targetU,
      height: device.height || 1,
      type: device.type || 'node',
      orientation: side,
      vendor: device.vendor || ''
    };

    const doubleEncoded = JSON.stringify(JSON.stringify(payload));
    await axios.post(`${Url}/update_rack?t=${Date.now()}`, doubleEncoded, {
       headers: { 'Content-Type': 'application/json' }
    });
    
    await loadRackData(); // Refresh to ensure sync with backend
    emit('pool-updated');
  } catch (e) {
    console.error("Drop failed", e);
    await loadRackData(); // Revert on failure
  }
};

// 5. LIFECYCLE
onMounted(() => {
  loadRackData();
});
</script>

<template>
  <div class="container-fluid flex-grow-1 container-p-y">
    <div class="card mb-4 border-0 h-100">
      
      <RackMetricsHeader
        v-model:metric1="metric1"
        v-model:metric2="metric2"
        @refresh="loadRackData"
      />

      <div class="card-body">
        <div class="racks-container d-flex justify-content-center">
          <div v-if="rack" class="single-rack-wrapper">
            <div class="racks-container">
              <SingleRack 
                :key="rack.name"
                :rack="rack"
                :metric1="metric1"
                :metric2="metric2"
                :get-metric="getMetricForDevice"
                @drop="onDrop" 
                @reset="resetRack"
              />
            </div>
          </div>
          <div v-else class="text-center p-5">
            <div class="spinner-border text-primary" role="status"></div>
            <p>Loading Rack Data...</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.racks-container { display: flex; flex-wrap: wrap; gap: 10px; padding: 10px; overflow-x: auto; align-items: flex-end; width:100%; }
</style>