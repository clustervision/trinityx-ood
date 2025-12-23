<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';
import DeviceItem from '@/components/DeviceItem.vue';
import RackMetricsHeader from '@/components/RackMetricsHeader.vue';
import type { Device } from '@/types/rack';
import SingleRack from '@/components/SingleRack.vue';

const props = defineProps<{ rackName: string; }>();
const emit = defineEmits(['close', 'pool-updated', 'device-taken']);
const Url = 'https://yixin3-dev-ctrl001:7755';
const prome_url = 'https://yixin3-dev-ctrl001:9090';

interface RackSlot { number: number; device: Device | null; }
interface Rack { name: string; size: number; order: string; slots: RackSlot[]; showBackSide: boolean; }

const rack = ref<Rack | null>(null);
const metric1 = ref<string | null>('No Scale');
const metric2 = ref<string | null>('No Scale');
const rawMetricData = ref<any[]>([]); 

// --- 1. LOAD DATA ---
const loadRackData = async () => {
  if (!props.rackName) return;
  try {
    const timestamp = new Date().getTime();
    const res = await axios.get(Url + `/show_rack/${props.rackName}?t=${timestamp}`);
    const rackDict = res.data.message;
    
    if (rackDict) {
      const size = parseInt(rackDict.size) || 42;
      const order = rackDict.order ? rackDict.order.toLowerCase() : 'ascending';
      
      // If rack already exists, just update slots to avoid full re-render flicker
      if (!rack.value) {
         rack.value = {
            name: props.rackName,
            size: size,
            order: order,
            slots: generateSlots(size, order),
            showBackSide: false 
         };
      } else {
         // clear slots to refill
         rack.value.slots.forEach(s => s.device = null);
      }

      if (rackDict.devices && Array.isArray(rackDict.devices)) {
        rackDict.devices.forEach((d: any) => placeDeviceInRack(rack.value!, d));
      }
    }
  } catch (e) {
    console.error(`Failed to load details`, e);
  }
};

const generateSlots = (size: number, order: string) => {
  const slots: RackSlot[] = [];
  for (let i = 1; i <= size; i++) slots.push({ number: i, device: null });
  return order === 'ascending' ? slots : slots.reverse();
};

const placeDeviceInRack = (currentRack: Rack, d: any) => {
    const height = parseInt(d.height) || 1;
    const position = Number(d.position);
    const occupiedUs = [];
    for(let i=0; i<height; i++) occupiedUs.push(position + i);

    let minVisualIndex = Infinity;
    occupiedUs.forEach(u => {
        const idx = currentRack.slots.findIndex(s => s.number === u);
        if (idx !== -1 && idx < minVisualIndex) minVisualIndex = idx;
    });

    if (minVisualIndex !== Infinity && minVisualIndex !== -1) {
      currentRack.slots[minVisualIndex].device = {
        name: d.name,
        position: position,
        height: height,
        type: d.type || 'node',
        orientation: d.orientation || 'front',
        vendor: d.vendor || null,
        status: 'ok'
      };
    }
};

const onDrop = async (event: DragEvent, targetRackName: string, targetU: number, side: 'front' | 'back') => {
  const data = event.dataTransfer?.getData('application/json');
  if (!data) return;
  const device = JSON.parse(data);


  if (device.dragSource === 'rack' && rack.value) {
     rack.value.slots.forEach(s => {
        // Find the slot holding this device and clear it
        if (s.device && s.device.name === device.name) {
           s.device = null; 
        }
     });
  } 

  else if (device.dragSource === 'pool') {
      emit('device-taken', device.name); 
  }
  
  if (rack.value) {
      const tempDevice = {
          name: device.name,
          position: targetU,
          height: device.height || 1,
          type: device.type || 'node',
          orientation: side, 
          vendor: device.vendor || ''
      };
      placeDeviceInRack(rack.value, tempDevice);
  }


  try {
    const timestamp = new Date().getTime();    
    const payload = {
      rack: targetRackName,
      name: device.name,
      position: targetU,
      height: device.height || 1,
      type: device.type || 'node',
      orientation: side, // Send correct orientation to backend
      vendor: device.vendor || ''
    };

    const doubleEncoded = JSON.stringify(JSON.stringify(payload));
        // B. Send to Backend
    await axios.post(
      Url + `/update_rack?t=${timestamp}`, 
      doubleEncoded, 
      { headers: { 'Content-Type': 'application/json' } }
    );
    
    // C. Refresh everything to be sure
    emit('pool-updated','close','device-taken'); // Tell App to refresh sidebar
    await loadRackData(); // Refresh current view

  } catch (e: any) {
    console.error("Failed to update rack", e);
    // If failed, reload to revert optimistic change
    await loadRackData();
  }
};

// --- 3. METRICS ---
const fetchMetricData = async () => {
  if (metric1.value === 'No Scale' && metric2.value === 'No Scale') {
    rawMetricData.value = [];
    return;
  }
  try {
    const response = await axios.get(prome_url + '/get_node');
    rawMetricData.value = response.data; 
  } catch (e) { console.error(e); }
};

const getMetricForDevice = (device: Device | null, type: string | null) => {
  if (!device || !type || type === 'No Scale' || !rawMetricData.value.length) return undefined;
  const found = rawMetricData.value.find((item: any) => item.hostname === device.name);
  if (!found) return undefined;
  if (type === 'System Load') return found.load;
  if (type === 'Temperature') return found.temperature; 
  if (type === 'Power Consumption') return found.power;
  if (type === 'GPU Temperature') return found.gpu_temp;
  return undefined;
};

watch([metric1, metric2], fetchMetricData);

defineExpose({ loadRackData });
onMounted(() => { loadRackData(); });
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
        </div>
        </div>
        </div>
        </div>

</template>

<style scoped>
.racks-container { display: flex;flex-wrap: wrap; gap: 10px; padding: 10px; overflow-x: auto; align-items: flex-end; width:100% }
</style>
