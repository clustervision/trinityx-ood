<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import DeviceItem from '@/components/DeviceItem.vue';
import type { Device } from '@/types/rack';

// --- INTERFACES ---
interface RackSlot {
  number: number;
  device: Device | null;
}

interface Rack {
  name: string;
  size: number;
  order: string;
  slots: RackSlot[];
  showBackSide: boolean; 
  powerOn: boolean;
}

// --- STATE ---
const racks = ref<Rack[]>([]);
const metric1 = ref<string | null>(null);
const metric2 = ref<string | null>(null);
const showDropdown1 = ref(false);
const showDropdown2 = ref(false); 
const rawMetricData = ref<any[]>([]); 
const currentMetricType = ref<string | null>(null);
const Url = 'https://yixin3-dev-ctrl001:7755'
const prome_url = 'https://yixin3-dev-ctrl001:9000'

// --- API: LOAD RACKS ---
const loadRacks = async () => {
  try {
    const timestamp = new Date().getTime();
    const response = await axios.get(Url + `/manage_racks?t=${timestamp}`);
    
    const rawMsg = response.data.message;
    
    if (rawMsg) {
      let flatList: any[] = [];

      if (Array.isArray(rawMsg)) {
        rawMsg.forEach((item: any) => {
          if (item.name && item.size) flatList.push(item);
          else flatList.push(...Object.values(item));
        });
      } else if (typeof rawMsg === 'object' && rawMsg !== null) {
        flatList = Object.values(rawMsg);
      }

      const parsedRacks: Rack[] = flatList.map((r: any) => ({
        name: r.name,
        size: parseInt(r.size) || 42,
        order: r.order ? r.order.toLowerCase() : 'ascending',
        slots: [],
        showBackSide: false,
        powerOn: true
      }));

      for (const rack of parsedRacks) {
        rack.slots = generateSlots(rack.size, rack.order);
        if (rack.name) {
           await fetchRackDetails(rack); 
        }
      }
      
      racks.value = parsedRacks;
    }
  } catch (error) {
    console.error("Failed to load racks:", error);
  }
};

const generateSlots = (size: number, order: string) => {
  const slots: RackSlot[] = [];
  for (let i = 1; i <= size; i++) {
    slots.push({ number: i, device: null });
  }
  // If 'ascending', U42 is at top (index 0). U1 is at bottom.
  // If 'descending', U1 is at top (index 0).
  return order === 'ascending' ? slots.reverse() : slots; 
};

// --- API: FETCH DETAILS ---
const fetchRackDetails = async (rack: Rack) => {
  try {
    const timestamp = new Date().getTime();
    const res = await axios.get(Url + `/show_rack/${rack.name}?t=${timestamp}`);
    const rackDict = res.data.message;
    
    if (rackDict && rackDict.devices && Array.isArray(rackDict.devices)) {
      rackDict.devices.forEach((d: any) => {
        const height = parseInt(d.height) || 1;
        const position = Number(d.position);
        
        // LOGIC: Determine which slot index should hold the device component.
        // We need to find the slot that appears "Earliest" in the DOM (top of the visual stack)
        // so the CSS height flows downwards correctly covering the other slots.
        
        let anchorSlotIndex = -1;

        // Calculate all U-numbers this device occupies (e.g. Pos 4, Height 2 -> U4, U5)
        const occupiedUs = [];
        for(let i=0; i<height; i++) {
            occupiedUs.push(position + i);
        }

        // Find which occupied U has the lowest index in our visual 'rack.slots' array
        // (Lowest index = rendered at top of screen)
        let minVisualIndex = Infinity;

        occupiedUs.forEach(u => {
            const idx = rack.slots.findIndex(s => s.number === u);
            if (idx !== -1 && idx < minVisualIndex) {
                minVisualIndex = idx;
            }
        });

        if (minVisualIndex !== Infinity) {
            anchorSlotIndex = minVisualIndex;
        }

        // Assign device to that anchor slot
        if (anchorSlotIndex !== -1) {
          rack.slots[anchorSlotIndex].device = {
            name: d.name,
            position: position,
            height: height,
            type: d.type || 'node',
            orientation: d.orientation || 'front',
            vendor: d.vendor || null,
            status: 'ok'
          };
        }
      });
    }
  } catch (e) {
    console.error(`Failed to load details for ${rack.name}`, e);
  }
};

// --- ACTIONS & METRICS (Standard) ---
const fetchMetricData = async () => {
  try {
    const response = await axios.get(prome_url + '/get_node');
    rawMetricData.value = response.data; 
  } catch (e) { console.error(e); }
};

const getMetricForDevice = (device: Device | null) => {
  if (!device || !rawMetricData.value.length) return undefined;
  const found = rawMetricData.value.find((item: any) => item.hostname === device.name);
  if (!found) return undefined;
  if (currentMetricType.value === 'System Load') return found.load;
  if (currentMetricType.value === 'Temperature') return found.temperature; 
  if (currentMetricType.value === 'Power Consumption') return found.power;
  return undefined;
};

const toggleRackPower = (rack: Rack) => { rack.powerOn = !rack.powerOn; };
const resetRack = (rack: Rack) => { confirm(`Reset ${rack.name}?`); };

const selectMetric1 = (name: string) => {
  metric1.value = name;
  currentMetricType.value = name;
  showDropdown1.value = false;
  if (name !== 'No Scale') fetchMetricData();
  else rawMetricData.value = [];
};
const selectMetric2 = (name: string) => {
  metric2.value = name;
  showDropdown2.value = false;
  if (name !== 'No Scale') fetchMetricData();
};
const getUnit = (n: string | null) => (n === 'Temperature' ? '°C' : n === 'Power Consumption' ? 'Watt' : '');
const getMaxValue = (n: string | null) => 100; // Simplified for brevity

// --- DROP HANDLER ---
const onDrop = async (event: DragEvent, targetRackName: string, targetU: number) => {
  const data = event.dataTransfer?.getData('application/json');
  if (!data) return;
  const device = JSON.parse(data);

  try {
    const timestamp = new Date().getTime();
    const payload = {
      rack: targetRackName,
      name: device.name,
      position: targetU,
      height: device.height || 1,
      type: device.type || 'node',
      orientation: device.orientation || 'front',
      vendor: device.vendor || ''
    };

    // Double Encode
    const doubleEncoded = JSON.stringify(JSON.stringify(payload));

    const response = await axios.post(
      Url + `/update_rack?t=${timestamp}`, 
      doubleEncoded, 
      { headers: { 'Content-Type': 'application/json' } }
    );

    if (response.status === 200) await loadRacks();

  } catch (e: any) {
    if (e.message !== 'Network Error') alert("Failed to update rack.");
    else await loadRacks();
  }
};

onMounted(() => {
  loadRacks();
});
</script>

<template>
  <div class="card mb-4 border-0">
    <div class="card-header p-4 bg-white">
       <button class="btn btn-primary" @click="loadRacks">Refresh</button>
    </div>

    <div class="card-body">
      <div class="racks-container">
        <div v-for="rack in racks" :key="rack.name" class="single-rack-wrapper">
           
           <div class="rack-tabs">
             <div class="rack-tab front-label">FRONT SIDE</div>
             <div class="rack-tab back-toggle" @click="rack.showBackSide = !rack.showBackSide">
               {{ rack.showBackSide ? 'HIDE THE BACK SIDE' : 'SHOW BACK SIDE' }}
             </div>
           </div>

           <div class="d-flex gap-4">
             <div class="rack-column">
                <div class="rack-header-dark">
                   <span class="fw-bold text-white ms-2">{{ rack.name }}</span>
                </div>
                <div class="rack-frame">
                  <div class="rack-row" v-for="slot in rack.slots" :key="slot.number"
                       @drop="onDrop($event, rack.name, slot.number)" @dragover.prevent>
                     <div class="rack-label">{{ slot.number }}</div>
                     
                     <div class="rack-slot" style="overflow: visible;">
                        <DeviceItem 
                          v-if="slot.device"
                          :device="slot.device"
                          :metric-value="getMetricForDevice(slot.device)"
                          :metric-type="metric1 || undefined"
                          :is-rack-view="true" 
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
                       @drop="onDrop($event, rack.name, slot.number)" @dragover.prevent>
                     <div class="rack-label">{{ slot.number }}</div>
                     <div class="rack-slot" style="overflow: visible;">
                        <DeviceItem 
                          v-if="slot.device"
                          :device="slot.device"
                          :metric-value="getMetricForDevice(slot.device)"
                          :metric-type="metric1 || undefined"
                          :is-rack-view="true" 
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
</template>

<style scoped>
/* Keep your styles, but ensure overflow is visible */
.rack-slot { 
    flex-grow: 1; 
    position: relative; 
    display: flex;
    align-items: center;
    justify-content: center;
    /* overflow: hidden;  <-- REMOVED THIS */
}
/* ... rest of styles ... */
.racks-container { display: flex; gap: 40px; padding: 20px; overflow-x: auto; align-items: flex-end; min-height: 600px; }
.single-rack-wrapper { display: flex; flex-direction: column; }
.rack-tabs { display: flex; justify-content: space-between; margin-bottom: 0; }
.rack-tab { padding: 5px 15px; font-size: 0.75rem; font-weight: bold; color: white; text-transform: uppercase; }
.front-label { background-color: #6666ff; border-top-left-radius: 4px; border-top-right-radius: 4px; }
.back-toggle { background-color: #333; cursor: pointer; border-top-left-radius: 4px; border-top-right-radius: 4px; }
.rack-column { min-width: 280px; display: flex; flex-direction: column; }
.rack-header-dark { background-color: #222; display: flex; justify-content: space-between; align-items: center; padding: 5px 0; border-bottom: 1px solid #444; }
.rack-frame { background: #e9ecef; border: 2px solid #222; border-top: none; padding: 0; }
.rack-row { display: flex; height: 30px; border-bottom: 1px solid #adb5bd; background-color: #fff; }
.rack-label { width: 35px; text-align: center; line-height: 30px; font-size: 11px; font-weight: bold; color: #444; background-color: #e9ecef; border-right: 1px solid #dee2e6; }
.rack-label:last-child { border-right: none; border-left: 1px solid #dee2e6; }
</style>