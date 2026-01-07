<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import RackMetricsHeader from '@/components/RackMetricsHeader.vue'; 
import SingleRack from '@/components/SingleRack.vue';
import { useToast } from "vue-toastification";
import { useRack} from '@/composables/useRack';
import { useRackMetrics } from '../composables/useRackMetrics';
import type { Rack } from '@/types/rack';

const emit = defineEmits(['rack-updated', 'device-taken']);
const toast = useToast();
const racks = ref<Rack[]>([]);
const { fetchSingleRack, handleRackDrop} = useRack();
const { metric1, metric2, metric1Range, metric2Range, getMetricForDevice } = useRackMetrics();

const Url = 'https://yixin3-dev-ctrl001:7755';
const isBackViewMode = ref(false);
const toggleGlobalView = () => {
  isBackViewMode.value = !isBackViewMode.value;
  racks.value.forEach(rack => {
    if (isBackViewMode.value) {
      rack.showFrontSide = false;
      rack.showBackSide = true;
    } else {
      rack.showFrontSide = true;
      rack.showBackSide = false;
    }
  });
};
const loadRacks = async () => {
  try {
    const t = new Date().getTime();
    const response = await axios.get(`${Url}/manage_racks?t=${t}`);
    const rawMsg = response.data.message;
    
    if (rawMsg) {
      let flatList: any[] = [];
      if (Array.isArray(rawMsg)) {
        rawMsg.forEach((item: any) => { 
          if (item.name && item.size) flatList.push(item); 
          else flatList.push(...Object.values(item)); 
        });
      } else { 
        flatList = Object.values(rawMsg); 
      }

      const currentStates = new Map(racks.value.map(r => [r.name, r.showBackSide]));
      const parsedRacks = await Promise.all(flatList.map(async (r: any) => {
          const fullRack = await fetchSingleRack(r.name);

          fullRack.showBackSide = currentStates.get(r.name) || false;
          return fullRack;
      }));

      racks.value = parsedRacks;
    }
  } catch (error) { 
    console.error("Failed to load racks:", error); 
  }
};

const resetRack = (rack: Rack, side: 'front' | 'back' = 'front') => { 
  confirm(`Reset ${rack.name} ${side} side?`); 
};

const onDrop = (event: DragEvent, targetRack: Rack, u: number, side: 'front' | 'back') => {
  handleRackDrop(
    event, 
    targetRack, 
    u, 
    side, 
    (deviceName: string) => {
       emit('device-taken', deviceName);

       racks.value.forEach(r => {
         if (r.name !== targetRack.name) {
           r.slots.forEach(slot => {
             slot.devices = slot.devices.filter(d => d.name !== deviceName);
           });
         }
       });
    },
    () => {

       loadRacks();
    }
  );
};

defineExpose({ loadRacks });
onMounted(loadRacks);
</script>

<template>
  <div class="container-fluid flex-grow-1 container-p-y">
    <div class="card-body position-relative"> <div style="position: absolute; right: 20px; top: 15px; z-index: 10;">
    <button 
      class="btn fw-bold"
      :class="isBackViewMode ? 'btn-dark' : 'btn-custom-grey'"
      @click="toggleGlobalView"
      style="font-size: 12px; padding: 4px 15px;"
    >
      {{ isBackViewMode ? 'Flip to Front' : 'Flip to Back' }}
    </button>
  </div>
      <RackMetricsHeader v-model:metric1="metric1"
       v-model:metric2="metric2"
       :range1="metric1Range"
        :range2="metric2Range" 
        @refresh="loadRacks" />
      <div class="card-body">
        <div class="racks-container">
          <SingleRack 
            v-for="rack in racks" 
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
    </div>
  </div>
</template>

<style scoped>
  .racks-container { display: flex;flex-wrap: wrap; gap: 10px; padding: 10px; overflow-x: auto; align-items: flex-end; width:100% }
.btn-custom-grey {
  background-color: #d3d3d3;
  border-color: #c0c0c0;
  color: #000;
}

.btn-custom-grey:hover {
  background-color: #bebebe;
}
</style>