<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';
import DeviceItem from '@/components/DeviceItem.vue';
import RackMetricsHeader from '@/components/RackMetricsHeader.vue'; 
import type { Device } from '@/types/rack';

// --- EMITS ---
const emit = defineEmits(['rack-updated', 'device-taken']);

// --- INTERFACES & STATE ---
interface RackSlot { number: number; device: Device | null; }
interface Rack { name: string; size: number; order: string; slots: RackSlot[]; showBackSide: boolean; powerOn: boolean; }

const racks = ref<Rack[]>([]);
const Url = 'https://yixin3-dev-ctrl001:7755';
const prome_url = 'https://yixin3-dev-ctrl001:9090'; 

// ... (Metrics code same as before) ...
// (Metric State, fetchMetricData, watch, getMetricForDevice - KEEP EXISTING CODE)
const metric1 = ref<string | null>('No Scale');
const metric2 = ref<string | null>('No Scale');
const rawMetricData = ref<any[]>([]); 

const fetchMetricData = async () => {
  if (metric1.value === 'No Scale' && metric2.value === 'No Scale') { rawMetricData.value = []; return; }
  try { const response = await axios.get(prome_url + '/get_node'); rawMetricData.value = response.data; } 
  catch (e) { console.error("Fetch metrics error:", e); }
};
watch([metric1, metric2], fetchMetricData);
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

const loadRacks = async () => {
  try {
    const t = new Date().getTime();
    const response = await axios.get(Url + `/manage_racks?t=${t}`);
    const rawMsg = response.data.message;
    if (rawMsg) {
      let flatList: any[] = [];
      if (Array.isArray(rawMsg)) {
        rawMsg.forEach((item: any) => { 
          if (item.name && item.size) flatList.push(item); 
          else flatList.push(...Object.values(item)); 
        });
      } else if (typeof rawMsg === 'object') { 
        flatList = Object.values(rawMsg); 
      }

      // 1. Create a map of the CURRENT toggle states
      const currentStates = new Map(racks.value.map(r => [r.name, r.showBackSide]));

      const parsedRacks: Rack[] = flatList.map((r: any) => ({
        name: r.name, 
        size: parseInt(r.size) || 42, 
        order: r.order ? r.order.toLowerCase() : 'ascending',
        slots: [], 
        // 2. Check if the rack already existed, if so, keep its 'showBackSide' state
        showBackSide: currentStates.has(r.name) ? currentStates.get(r.name)! : false, 
        powerOn: true
      }));

      for (const rack of parsedRacks) {
        rack.slots = generateSlots(rack.size, rack.order);
        if (rack.name) await fetchRackDetails(rack); 
      }
      racks.value = parsedRacks;
    }
  } catch (error) { 
    console.error("Failed to load racks:", error); 
  }
};

const generateSlots = (size: number, order: string) => {
  const slots: RackSlot[] = [];
  for (let i = 1; i <= size; i++) { slots.push({ number: i, device: null }); }
  return order === 'ascending' ? slots : slots.reverse();
};
const fetchRackDetails = async (rack: Rack) => {
  try {
    const t = new Date().getTime();
    const res = await axios.get(Url + `/show_rack/${rack.name}?t=${t}`);
    const rackDict = res.data.message;
    if (rackDict && rackDict.devices && Array.isArray(rackDict.devices)) {
      rackDict.devices.forEach((d: any) => placeDeviceInRack(rack, d));
    }
  } catch (e) { console.error(`Failed to load details for ${rack.name}`, e); }
};
const placeDeviceInRack = (rack: Rack, d: any) => {
    const height = parseInt(d.height) || 1;
    const position = Number(d.position);
    const occupiedUs = [];
    for(let i=0; i<height; i++) occupiedUs.push(position + i);
    let minVisualIndex = Infinity;
    occupiedUs.forEach(u => {
        const idx = rack.slots.findIndex(s => s.number === u);
        if (idx !== -1 && idx < minVisualIndex) minVisualIndex = idx;
    });
    if (minVisualIndex !== Infinity && minVisualIndex !== -1) {
      rack.slots[minVisualIndex].device = {
        name: d.name, position: position, height: height,
        type: d.type || 'node', orientation: d.orientation || 'front',
        vendor: d.vendor || null, status: 'ok'
      };
    }
};
const toggleRackPower = (rack: Rack) => { rack.powerOn = !rack.powerOn; };
const resetRack = (rack: Rack) => { confirm(`Reset ${rack.name}?`); };


// --- INSTANT DROP HANDLER ---
const onDrop = async (event: DragEvent, targetRack: Rack, targetU: number, side: 'front' | 'back') => {
  const data = event.dataTransfer?.getData('application/json');
  if (!data) return;
  const device = JSON.parse(data);

  // 1. CLEAR OLD POSITION (If moved from within rack)
  if (device.dragSource === 'rack') {
     // Find the rack/slot that currently holds this device and remove it
     racks.value.forEach(r => {
        r.slots.forEach(s => {
           if (s.device && s.device.name === device.name) {
              s.device = null; // Instant Removal
           }
        });
     });
  } 
  // 2. OR NOTIFY PARENT (If moved from pool)
  else if (device.dragSource === 'pool') {
      emit('device-taken', device.name); // Tells App.vue -> SideMenu to remove it
  }

  // 3. SET NEW POSITION (Instant Add)
  const tempDevice = {
      name: device.name,
      position: targetU,
      height: device.height || 1,
      type: device.type || 'node',
      orientation: side, 
      vendor: device.vendor || ''
  };
  placeDeviceInRack(targetRack, tempDevice);

  // 4. API CALL
  try {
    const t = new Date().getTime();
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
    const response = await axios.post(Url + `/update_rack?t=${t}`, doubleEncoded, {
       headers: { 'Content-Type': 'application/json' }
    });

    if (response.status === 200) {
       emit('rack-updated'); 
    } else {
       await loadRacks(); // Revert if failed
    }
  } catch (e) {
    console.error("Drop failed", e);
    await loadRacks();
  }
};

defineExpose({ loadRacks });
onMounted(() => { loadRacks(); });
</script>

<template>
  <div class="container-fluid flex-grow-1 container-p-y">
  <div class="card mb-4 border-0">
    <RackMetricsHeader v-model:metric1="metric1" v-model:metric2="metric2" @refresh="loadRacks" />
    <div class="card-body">
      <div class="racks-container">
        <div v-for="rack in racks" :key="rack.name" class="single-rack-wrapper">
           <div class="rack-tabs">
             <div class="rack-tab front-label">FRONT SIDE</div>
             <div class="rack-tab back-toggle" @click="rack.showBackSide = !rack.showBackSide">
               {{ rack.showBackSide ? 'HIDE BACK' : 'SHOW BACK' }}
             </div>
           </div>

           <div class="d-flex gap-4">
             <div class="rack-column">
                <div class="rack-header-dark">
                   <span class="fw-bold text-white ms-2">{{ rack.name }}</span>
                   <div class="d-flex align-items-center gap-2 me-2">
                     <button class="btn btn-light btn-xs fw-bold reset-btn" @click="resetRack(rack)">RESET</button>
                     <i class='bx bx-power-off fs-5 cursor-pointer' :class="rack.powerOn ? 'text-success' : 'text-danger'" @click="toggleRackPower(rack)"></i>
                   </div>
                </div>
                <div class="rack-frame">
                  <div class="rack-row" v-for="slot in rack.slots" :key="slot.number"
                       @drop="onDrop($event, rack, slot.number, 'front')" @dragover.prevent>
                     <div class="rack-label">{{ slot.number }}</div>
                     <div class="rack-slot" style="position: relative; overflow: visible;">
                        <DeviceItem 
                          v-if="slot.device && (slot.device.orientation === 'front' || !slot.device.orientation)"
                          :device="slot.device"
                          :metric-value="getMetricForDevice(slot.device, metric1)"
                          :metric-type="metric1 || undefined"
                          :is-rack-view="true" 
                          style="position: absolute; top: 0; left: 0; width: 100%; z-index: 10;"
                          :style="{ height: (slot.device.height * 30 - 2) + 'px' }"
                        />
                     </div>
                     <div class="rack-label">{{ slot.number }}</div>
                  </div>
               </div>
             </div>

             <div class="rack-column" v-if="rack.showBackSide">
                <div class="rack-header-dark"><span class="text-white">{{ rack.name }} Back</span></div>
                <div class="rack-frame">
                  <div class="rack-row" v-for="slot in rack.slots" :key="slot.number"
                       @drop="onDrop($event, rack, slot.number, 'back')" @dragover.prevent>
                     <div class="rack-label">{{ slot.number }}</div>
                     <div class="rack-slot" style="position: relative; overflow: visible;">
                        <DeviceItem 
                          v-if="slot.device && slot.device.orientation === 'back'"
                          :device="slot.device"
                          :metric-value="getMetricForDevice(slot.device, metric2)"
                          :metric-type="metric2 || undefined"
                          :is-rack-view="true" 
                          style="position: absolute; top: 0; left: 0; width: 100%; z-index: 10;"
                          :style="{ height: (slot.device.height * 30 - 2) + 'px' }"
                        />
                     </div>
                     <div class="rack-label">{{ slot.number }}</div>
                  </div>
               </div>
             </div>
           </div>
        </div>
      </div>
    </div>
  </div>
  </div>
</template>

<style scoped>
.racks-container { display: flex; gap: 40px; padding: 20px; overflow-x: auto; align-items: flex-end; min-height: 600px; width:100% }
.single-rack-wrapper { display: flex; flex-direction: column; flex-shrink: 0;}
.rack-tabs { display: flex; justify-content: space-between; margin-bottom: 0; }
.rack-tab { padding: 5px 15px; font-size: 0.75rem; font-weight: bold; color: white; text-transform: uppercase; }
.front-label { background-color: #6666ff; border-top-left-radius: 4px; border-top-right-radius: 4px; }
.back-toggle { background-color: #333; cursor: pointer; border-top-left-radius: 4px; border-top-right-radius: 4px; }
.rack-column { min-width: 300px; display: flex; flex-direction: column; flex:1;}
.rack-header-dark { background-color: #222; display: flex; justify-content: space-between; align-items: center; padding: 5px 0; border-bottom: 1px solid #444; }
.reset-btn { font-size: 0.65rem; padding: 1px 5px; height: 20px; line-height: 1; }
.rack-frame { background: #e9ecef; border: 2px solid #222; border-top: none; padding: 0; }
.rack-row { display: flex; height: 30px; border-bottom: 1px solid #adb5bd; background-color: #fff; }
.rack-label { width: 35px; text-align: center; line-height: 30px; font-size: 11px; font-weight: bold; color: #444; background-color: #e9ecef; border-right: 1px solid #dee2e6; }
.rack-label:last-child { border-right: none; border-left: 1px solid #dee2e6; }
.rack-slot { flex-grow: 1; }
.cursor-pointer { cursor: pointer; }
</style>