<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import DeviceItem from '@/components/rack/DeviceItem.vue';
import type { Device } from '@/types/rack'; // Ensure you have this type or remove import if not used
import { stringifyQuery } from 'vue-router';

// --- INTERFACES ---
interface RackSlot {
  number: number;
  device: Device | null; // Device object or null if empty
}

interface Rack {
  name: string | undefined;
  size: string | undefined;
  order: string | undefined; // 'ascending' or 'descending'
  slots: RackSlot[] | undefined;
}

// --- STATE ---
const currentView = ref<'front' | 'back'>('front');
const racks = ref<Rack[]>([]); // Array of Racks
const metric1 = ref<string | null>(null);
const metric2 = ref<string | null>(null);
const showDropdown1 = ref(false);
const showDropdown2 = ref(false); 

// Store raw metric data
const rawMetricData = ref<any[]>([]); 
const currentMetricType = ref<string | null>(null);

// --- API: LOAD RACKS (HTML PARSING) ---
const loadRacks = async () => {
  try {
    // 1. Fetch the HTML String from the backend
    const response = await fetch('/manage/rack', { headers: { 'Accept': 'text/html' } }); 
    if (!response.ok) throw new Error(`HTTP error! ${response.status}`);
    
    const htmlString = await response.text();
    
    // 2. Parse HTML into Rack Objects
    const parsedRacks = parseHtmlToRackList(htmlString);

    // 3. Populate Slots & Devices for each rack
    for (const rack of parsedRacks) {
      // Generate empty slots (e.g. 1 to 42)
      rack.slots = generateSlots(rack.size, rack.order);
      
      // Fetch devices for this specific rack
      await fetchDevicesForRack(rack);
    }

    racks.value = parsedRacks;
    console.log("Racks loaded:", racks.value);

  } catch (error) {
    console.error("Failed to load racks:", error);
  }
};

// --- HELPER: Parse HTML Table ---
function parseHtmlToRackList(html: string): Rack[] {
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, 'text/html');
  const rows = doc.querySelectorAll('table tbody tr');
  const data: Rack[] = [];

  rows.forEach((row) => {
    const cells = row.querySelectorAll('td');
    if (cells.length > 1) {
      data.push({
        name: cells[1]?.innerText.trim(),
        size: cells[2]?.innerText.trim(),
        order: cells[3]?.innerText.trim().toLowerCase(),
        slots: []
      });
    }
  });
  return data;
}

// --- HELPER: Generate Slots ---
const generateSlots = (size: number, order: string) => {
  const slots: RackSlot[] = [];
  for (let i = 1; i <= size; i++) {
    slots.push({ number: i, device: null });
  }
  return order === 'descending' ? slots.reverse() : slots; 
};

// --- API: FETCH DEVICES FOR A RACK ---
const fetchDevicesForRack = async (rack: Rack) => {
  try {
    const res = await fetch(`/get_nodes/${rack.name}`);
    const deviceNames = await res.json(); // Returns ["node001", "node002"]
    
    // MOCK MAPPING: Since API doesn't give position, fill slots sequentially
    deviceNames.forEach((devName: string, index: number) => {
      // Find the slot based on index (just for visualization purposes)
      if (index < rack.slots.length) {
         rack.slots[index].device = { 
           name: devName, 
           position: rack.slots[index].number,
           orientation: 'front', // Default
           type: 'node', // Default
           status: 'ok'
         };
      }
    });
  } catch (e) {
    console.error(`Failed to load nodes for ${rack.name}`, e);
  }
};

// --- API: FETCH METRICS ---
const fetchMetricData = async () => {
  try {
    // USE RELATIVE PATH (Proxied in vite.config.js)
    const response = await fetch('/get_temperature');
    
    if (!response.ok) throw new Error("Failed to fetch metrics");

    const data = await response.json();
    rawMetricData.value = data; 
    console.log("Metrics loaded:", data);
  } catch (e) {
    console.error("Fetch error:", e);
  }
};

// --- HELPER: MAP METRIC TO DEVICE ---
const getMetricForDevice = (device: Device | null) => {
  if (!device || !rawMetricData.value.length) return undefined; // Return undefined for DeviceItem prop

  const found = rawMetricData.value.find((item: any) => item.hostname === device.name);
  if (!found) return undefined;

  let val = null;
  if (currentMetricType.value === 'System Load') val = found.load;
  else if (currentMetricType.value === 'Temperature') val = found.temperature; 
  else if (currentMetricType.value === 'Power Consumption') val = found.power;
  
  // Ensure we return string, number, or undefined (not null)
  return val !== null ? val : undefined;
};

// --- DROPDOWN LOGIC ---
const selectMetric1 = (name: string) => {
  metric1.value = name;
  currentMetricType.value = name;
  showDropdown1.value = false;
  
  if (name !== 'No Scale') {
    fetchMetricData();
  } else {
    rawMetricData.value = [];
  }
};

const selectMetric2 = (name: string) => {
  metric2.value = name;
  showDropdown2.value = false;
  if (name !== 'No Scale') {
    fetchMetricData();
  }
};

// --- DRAG & DROP ---
const onDrop = (event: DragEvent, targetRackName: string, targetU: number) => {
  console.log("Dropped on", targetRackName, targetU);
};

onMounted(() => {
  loadRacks();
});
</script>

<template>
  <div class="card mb-4">
    <div class="card-header p-4 bg-white">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <div class="d-flex align-items-center gap-3">
          <div class="dropdown">
            <button class="btn btn-primary dropdown-toggle" type="button" @click="showDropdown1 = !showDropdown1" style="min-width: 160px;">
              {{ metric1 ? metric1 : 'Select 1st Metric' }}
            </button>
            <ul class="dropdown-menu show" v-if="showDropdown1" style="display: block;">
              <li><a class="dropdown-item" href="#" @click.prevent="selectMetric1('No Scale')">No Scale</a></li>
              <li><a class="dropdown-item" href="#" @click.prevent="selectMetric1('Temperature')">Temperature</a></li>
              <li><a class="dropdown-item" href="#" @click.prevent="selectMetric1('System Load')">System Load</a></li>
              <li><a class="dropdown-item" href="#" @click.prevent="selectMetric1('Power Consumption')">Power Consumption</a></li>
                <li><a class="dropdown-item" href="#" @click.prevent="selectMetric1('GPU Temperature')">GPU Temperature</a></li>
            </ul>
          </div>
          <div v-if="metric1 === 'Temperature'" class="d-flex align-items-center gap-2">
            <span class="fw-bold">0°C</span>
            <div style="width: 200px; height: 20px; background: linear-gradient(90deg, blue, lime, red); border: 1px solid #ccc; border-radius: 4px;"></div>
            <span class="fw-bold">90°C</span>
          </div>
        </div>

        <button class="btn btn-dark" @click="currentView = currentView === 'front' ? 'back' : 'front'">
          Flip to {{ currentView === 'front' ? 'Back' : 'Front' }} View
        </button>
      </div>

      <div class="d-flex align-items-center gap-3">
        <div class="dropdown">
          <button class="btn btn-info text-white dropdown-toggle" type="button" @click="showDropdown2 = !showDropdown2" style="min-width: 160px;">
            {{ metric2 ? metric2 : 'Select 2nd Metric' }}
          </button>
          <ul class="dropdown-menu show" v-if="showDropdown2" style="display: block;">
            <li><a class="dropdown-item" href="#" @click.prevent="selectMetric2('No Scale')">No Scale</a></li>
            <li><a class="dropdown-item" href="#" @click.prevent="selectMetric2('Temperature')">Temperature</a></li>
            <li><a class="dropdown-item" href="#" @click.prevent="selectMetric2('System Load')">System Load</a></li>
             <li><a class="dropdown-item" href="#" @click.prevent="selectMetric2('Power Consumption')">Power Consumption</a></li>
                <li><a class="dropdown-item" href="#" @click.prevent="selectMetric2('GPU Temperature')">GPU Temperature</a></li>
          </ul>
        </div>
        <div v-if="metric2 === 'Temperature'" class="d-flex align-items-center gap-2">
            <span class="fw-bold">0°C</span>
            <div style="width: 200px; height: 20px; background: linear-gradient(90deg, blue, lime, red); border: 1px solid #ccc; border-radius: 4px;"></div>
            <span class="fw-bold">90°C</span>
        </div>
      </div>
    </div>

    <div class="card-body">
      <div class="racks-container">
        <div v-if="racks.length === 0" class="text-muted w-100 text-center">
            No racks available. Please add a rack in "Manage Rack Frames".
        </div>

        <div v-for="rack in racks" :key="rack.name" class="single-rack">
           
           <div class="rack-header d-flex justify-content-between px-2 mb-1">
               <span class="fw-bold">U</span>
               <span class="fw-bold">{{ rack.name }}</span>
               <span class="fw-bold">U</span>
           </div>
           
           <div class="rack-frame">
              <div class="rack-row" v-for="slot in rack.slots" :key="slot.number"
                   @drop="onDrop($event, rack.name, slot.number)" 
                   @dragover.prevent>
                 
                 <div class="rack-label">{{ slot.number }}</div>
                 
                 <div class="rack-slot" :class="{'bg-light': !slot.device}">
                    <DeviceItem 
                      v-if="slot.device"
                      :device="slot.device"
                      :metric-value="getMetricForDevice(slot.device)"
                      :metric-type="metric1 || undefined"
                    />
                 </div>

                 <div class="rack-label">{{ slot.number }}</div>
              
              </div>
           </div>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.racks-container { 
    display: flex; 
    gap: 20px; 
    padding: 20px; 
    overflow-x: auto; 
    align-items: flex-start;
}

.single-rack { 
    min-width: 280px; 
    /* Prevent shrinking */
    flex-shrink: 0; 
}

.rack-header {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-bottom: none;
    padding-top: 5px;
    padding-bottom: 5px;
}

.rack-frame { 
    background: #e9ecef; 
    border: 2px solid #495057; 
    padding: 0; /* Tight fit */
}

.rack-row { 
    display: flex; 
    height: 30px; 
    border-bottom: 1px solid #adb5bd; 
    position: relative; 
    background-color: #fff;
}

/* Side labels (U Numbers) */
.rack-label { 
    width: 35px; 
    text-align: center; 
    line-height: 30px; 
    font-size: 11px; 
    font-weight: bold;
    color: #fff;
    background-color: #6c757d; /* Dark grey sidebar like screenshot */
    border-bottom: 1px solid #495057;
}

.rack-slot { 
    flex-grow: 1; 
    position: relative; 
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}
</style>