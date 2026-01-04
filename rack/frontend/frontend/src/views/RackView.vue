<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import RackMetricsHeader from '@/components/RackMetricsHeader.vue'; 
import SingleRack from '@/components/SingleRack.vue';
import { useToast } from "vue-toastification";
import { useRack } from '@/composables/useRack';
import { useRackMetrics } from '../composables/useRackMetrics';
import type { Rack } from '@/types/rack';

const emit = defineEmits(['rack-updated', 'device-taken']);
const toast = useToast();
const racks = ref<Rack[]>([]);
const { fetchSingleRack, placeDeviceInRack } = useRack();
const { metric1, metric2, metric1Range, metric2Range, getMetricForDevice } = useRackMetrics();

const Url = 'https://yixin3-dev-ctrl001:7755';

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

const onDrop = async (event: DragEvent, targetRack: Rack, targetU: number, side: 'front' | 'back') => {
  const data = event.dataTransfer?.getData('application/json');
  if (!data) return;
  const draggedDevice = JSON.parse(data);
  const dragHeight = parseInt(draggedDevice.height) || 1;

  if (targetU + dragHeight - 1 > targetRack.size) {
      toast.error(`Installation failed: Device exceeds rack height (Max ${targetRack.size}U).`);
      return;
    }
  for (let i = 0; i < dragHeight; i++) {
    const checkU = targetU + i;
    const slotToCheck = targetRack.slots.find(s => s.number === checkU);
    
    if (slotToCheck) {
      const existingDevice = slotToCheck.devices.find(d => d.orientation === side && d.name !== draggedDevice.name);
      
      if (existingDevice) {
        if (existingDevice.position !== targetU) {
          toast.error(`Slot ${checkU} is occupied by ${existingDevice.name}`);
          return; 
        }
        
        if (existingDevice.position === targetU && existingDevice.height < dragHeight) {
          toast.error(`Space is too small: existing device only has height ${existingDevice.height}`);
          return; 
        }
      }
    }
  }
  targetRack.slots.forEach(s => {
    s.devices = s.devices.filter(d => d.name !== draggedDevice.name);
  });

  let finalPosition = targetU; 

  const tempDevice = { ...draggedDevice, position: finalPosition, orientation: side };
  placeDeviceInRack(targetRack, tempDevice);

  targetRack.slots = [...targetRack.slots];

  try {
    const payload = { ...tempDevice, rack: targetRack.name };
    const doubleEncoded = JSON.stringify(JSON.stringify(payload));
    await axios.post(`${Url}/update_rack`, doubleEncoded, {
       headers: { 'Content-Type': 'application/json' }
    });
    if (draggedDevice.dragSource === 'pool') {
      emit('device-taken', draggedDevice.name); 
    }
    toast.success(`${draggedDevice.name}  added to rack ${targetRack.name}`);
  } catch (e) {
    await loadRacks();
  }
};

defineExpose({ loadRacks });
onMounted(loadRacks);
</script>

<template>
  <div class="container-fluid flex-grow-1 container-p-y">
    <div class="card mb-4 border-0">
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
</style>