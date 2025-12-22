<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';
import DeviceItem from '@/components/DeviceItem.vue';
import RackMetricsHeader from '@/components/RackMetricsHeader.vue';
import type { Device } from '@/types/rack';
// import onDrop from '@/views/RackView.vue'

const props = defineProps<{ rackName: string; }>();
// Add 'pool-updated' to notify App.vue to refresh the sidebar
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
           
           <div class="rack-tabs">
             <div class="rack-tab front-label">FRONT SIDE</div>
             <div class="rack-tab back-toggle" @click="rack.showBackSide = !rack.showBackSide">
               {{ rack.showBackSide ? 'HIDE BACK SIDE' : 'SHOW BACK SIDE' }}
             </div>
           </div>

           <div class="d-flex gap-4">
             
             <div class="rack-column">
                <div class="rack-header-dark">
                   <span class="fw-bold text-white ms-2">{{ rack.name }} (Front)</span>
                </div>
                <div class="rack-frame">
                  <div class="rack-row" v-for="slot in rack.slots" :key="slot.number"
                       @drop="onDrop($event, rack.name, slot.number, 'front')" @dragover.prevent>
                     
                     <div class="rack-label">{{ slot.number }}</div>
                     
                     <div class="rack-slot" style="position: relative; overflow: visible;">
                        <DeviceItem 
                          v-if="slot.device && (slot.device.orientation === 'front' || !slot.device.orientation)"
                          :device="slot.device"
                          :metric-value="getMetricForDevice(slot.device, metric1)"
                          :metric-type="metric1 || undefined"
                          :is-rack-view="true" 
                          style="position: absolute; top: 0; left: 0; width: 100%; z-index: 10;"
                          :style="{ height: (slot.device.height * 20 - 2) + 'px' }"
                        />
                     </div>
                     
                     <div class="rack-label">{{ slot.number }}</div>
                  </div>
               </div>
             </div>

             <div class="rack-column" v-if="rack.showBackSide">
                <div class="rack-header-dark">
                  <span class="text-white ms-2">{{ rack.name }} (Back)</span>
                </div>
                <div class="rack-frame">
                  <div class="rack-row" v-for="slot in rack.slots" :key="slot.number"
                       @drop="onDrop($event, rack.name, slot.number, 'back')" @dragover.prevent>
                     
                     <div class="rack-label">{{ slot.number }}</div>
                     
                     <div class="rack-slot" style="position: relative; overflow: visible;">
                        <DeviceItem 
                          v-if="slot.device && slot.device.orientation === 'back'"
                          :device="slot.device"
                          :metric-value="getMetricForDevice(slot.device, metric2)"
                          :metric-type="metric2 || undefined"
                          :is-rack-view="true" 
                          style="position: absolute; top: 0; left: 0; width: 100%; z-index: 10;"
                          :style="{ height: (slot.device.height * 20 - 2) + 'px' }"
                        />
                     </div>
                     
                     <div class="rack-label">{{ slot.number }}</div>
                  </div>
               </div>
             </div>

           </div>
        </div>

        <div v-else class="text-center mt-5">
           <div class="spinner-border text-primary" role="status">
             <span class="visually-hidden">Loading Rack...</span>
           </div>
        </div>

      </div>
    </div>
  </div>
  </div>
</template>


<style scoped>
.racks-container { 
  min-height: 600px; 
  align-items: flex-start; 
  padding-top: 20px;
}
.single-rack-wrapper { display: flex; flex-direction: column; }
.rack-tabs { display: flex; justify-content: space-between; margin-bottom: 0; }
.rack-tab { padding: 5px 15px; font-size: 0.75rem; font-weight: bold; color: white; text-transform: uppercase; }
.front-label { background-color: #6666ff; border-top-left-radius: 4px; border-top-right-radius: 4px; }
.back-toggle { background-color: #333; cursor: pointer; border-top-left-radius: 4px; border-top-right-radius: 4px; }

.rack-column { min-width: 280px; display: flex; flex-direction: column; }
.rack-header-dark { background-color: #222; display: flex; justify-content: space-between; align-items: center; padding: 5px 0; border-bottom: 1px solid #444; }
.rack-frame { background: #e9ecef; border: 2px solid #222; border-top: none; padding: 0; }
.rack-row { display: flex; height: 20px; border-bottom: 1px solid #adb5bd; background-color: #fff; }
.rack-label { width: 35px; text-align: center; line-height: 20px; font-size: 11px; font-weight: bold; color: #444; background-color: #e9ecef; border-right: 1px solid #dee2e6; }
.rack-label:last-child { border-right: none; border-left: 1px solid #dee2e6; }
.rack-slot { flex-grow: 1; }
</style>
}