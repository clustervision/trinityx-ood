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
const url = 'https://yixin3-dev-ctrl001:7755'
const prome_url = 'https://yixin3-dev-ctrl001:9000'

// --- API: LOAD RACKS ---
const loadRacks = async () => {
  try {
    // New Backend returns JSON directly
    const response = await axios.get(url + '/manage_racks');
    
    // structure: { status: true, message: [ {name: 'Rack1', size: 42, ...} ] }
    if (response.data.status) {
      // Handle nested array if backend appends list to list, otherwise standard array
      const rawList = Array.isArray(response.data.message) 
        ? response.data.message.flat() 
        : [];

      const parsedRacks: Rack[] = rawList.map((r: any) => ({
        name: r.name,
        size: parseInt(r.size),
        order: r.order ? r.order.toLowerCase() : 'ascending',
        slots: [],
        showBackSide: false,
        powerOn: true
      }));

      // Generate slots and fetch nodes for each rack
      for (const rack of parsedRacks) {
        rack.slots = generateSlots(rack.size, rack.order);
        await fetchDevicesForRack(rack);
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
  return order === 'descending' ? slots.reverse() : slots; 
};

const fetchDevicesForRack = async (rack: Rack) => {
  try {
    // Backend: /get_nodes/<rack_name> -> { status: true, message: ["node1", "node2"] }
    const res = await axios.get(url + `/get_nodes/${rack.name}`);
    
    if (res.data.status && Array.isArray(res.data.message)) {
      const deviceNames = res.data.message;
      
      deviceNames.forEach((devName: string, index: number) => {
        if (index < rack.slots.length) {
           rack.slots[index].device = { 
             name: devName, 
             position: rack.slots[index].number,
             orientation: 'front', 
             type: 'node', 
             status: 'ok'
           };
        }
      });
    }
  } catch (e) {
    console.error(`Failed to load nodes for ${rack.name}`, e);
  }
};

// --- API: METRICS ---
const fetchMetricData = async () => {
  try {
    // Assuming endpoint exists for metrics
    const response = await axios.get(prome_url + '/get_node');
    rawMetricData.value = response.data; 
  } catch (e) {
    console.error("Fetch error:", e);
  }
};

const getMetricForDevice = (device: Device | null) => {
  if (!device || !rawMetricData.value.length) return undefined;
  const found = rawMetricData.value.find((item: any) => item.hostname === device.name);
  if (!found) return undefined;

  let val = null;
  if (currentMetricType.value === 'System Load') val = found.load;
  else if (currentMetricType.value === 'Temperature') val = found.temperature; 
  else if (currentMetricType.value === 'Power Consumption') val = found.power;
  return val !== null ? val : undefined;
};

// --- ACTIONS ---
const toggleRackPower = (rack: Rack) => {
  rack.powerOn = !rack.powerOn;
  // Add API call here if needed
};

const resetRack = (rack: Rack) => {
  if(confirm(`Are you sure you want to RESET ${rack.name}?`)) {
      console.log('Resetting', rack.name);
  }
};

const selectMetric1 = (name: string) => {
  metric1.value = name;
  currentMetricType.value = name;
  showDropdown1.value = false;
  if (name !== 'No Scale') fetchMetricData();
  else rawMetricData.value = [];
};

// --- LEGEND / GRAPH HELPERS ---
const getUnit = (metricName: string | null) => {
  if (metricName === 'Power Consumption') return 'Watt';
  if (metricName === 'Temperature' || metricName === 'GPU Temperature') return '°C';
  return '';
};

const getMaxValue = (metricName: string | null) => {
  if (!rawMetricData.value || rawMetricData.value.length === 0) return 100;

  let key = '';
  if (metricName === 'System Load') key = 'load';
  else if (metricName === 'Temperature') key = 'temperature';
  else if (metricName === 'Power Consumption') key = 'power';
  else if (metricName === 'GPU Temperature') key = 'gpu_temp';

  if (!key) return 100;
  const max = Math.max(...rawMetricData.value.map((d: any) => parseFloat(d[key]) || 0));
  return max > 0 ? max.toFixed(1) : 0;
};

const selectMetric2 = (name: string) => {
  metric2.value = name;
  showDropdown2.value = false;
  if (name !== 'No Scale') fetchMetricData();
};

const onDrop = (event: DragEvent, targetRackName: string, targetU: number) => {
  console.log("Dropped on", targetRackName, targetU);
};

onMounted(() => {
  loadRacks();
});
</script>

<template>
  <div class="card mb-4 border-0">
    <div class="card-header p-4 bg-white">
      <div class="d-flex align-items-center gap-3 mb-3">
        <div class="dropdown">
          <button 
            class="btn dropdown-toggle" 
            :class="metric1 === 'Power Consumption' ? 'btn-primary' : 'btn-info text-white'"
            type="button" 
            @click="showDropdown1 = !showDropdown1" 
            style="min-width: 180px;"
          >
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

        <div v-if="metric1 && metric1 !== 'No Scale'" class="d-flex align-items-center gap-2">
          <span class="text-muted">{{ 0 }} {{ getUnit(metric1) }}</span>
          <div class="legend-bar"></div>
          <span class="text-muted">{{ getMaxValue(metric1) }} {{ getUnit(metric1) }}</span>
        </div>
      </div>

      <div class="d-flex align-items-center gap-3">
        <div class="dropdown">
          <button 
            class="btn btn-secondary dropdown-toggle" 
            type="button" 
            @click="showDropdown2 = !showDropdown2" 
            style="min-width: 180px;"
          >
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

        <div v-if="metric2 && metric2 !== 'No Scale'" class="d-flex align-items-center gap-2">
          <span class="text-muted">{{ 0 }} {{ getUnit(metric2) }}</span>
          <div class="legend-bar"></div>
          <span class="text-muted">{{ getMaxValue(metric2) }} {{ getUnit(metric2) }}</span>
        </div>
      </div>
    </div>

    <div class="card-body">
      <div class="racks-container">
        
        <div v-for="rack in racks" :key="rack.name" class="single-rack-wrapper">
           
           <div class="rack-tabs">
             <div class="rack-tab front-label">
               FRONT SIDE
             </div>
             
             <div 
               class="rack-tab back-toggle"
               @click="rack.showBackSide = !rack.showBackSide"
             >
               {{ rack.showBackSide ? 'HIDE THE BACK SIDE' : 'SHOW BACK SIDE' }}
             </div>
           </div>

           <div class="d-flex gap-4">
             
             <div class="rack-column">
                <div class="rack-header-dark">
                   <div class="d-flex align-items-center gap-3">
                     <span class="fw-bold text-white ms-2">U</span>
                     <span class="fw-bold text-white rack-title">{{ rack.name }}</span>
                   </div>
                   <div class="d-flex align-items-center gap-2 me-2">
                     <button class="btn btn-light btn-xs fw-bold reset-btn" @click="resetRack(rack)">RESET</button>
                     <i class='bx bx-power-off fs-5 cursor-pointer' :class="rack.powerOn ? 'text-success' : 'text-danger'" @click="toggleRackPower(rack)"></i>
                     <span class="fw-bold text-white">U</span>
                   </div>
                </div>
                <div class="rack-frame">
                  <div class="rack-row" v-for="slot in rack.slots" :key="slot.number"
                       @drop="onDrop($event, rack.name, slot.number)" @dragover.prevent>
                     <div class="rack-label">{{ slot.number < 10 ? '0' + slot.number : slot.number }}</div>
                     <div class="rack-slot" :class="{'bg-light': !slot.device}">
                        <DeviceItem 
                          v-if="slot.device"
                          :device="slot.device"
                          :metric-value="getMetricForDevice(slot.device)"
                          :metric-type="metric1 || undefined"
                          :is-back-view="false" 
                        />
                     </div>
                     <div class="rack-label">{{ slot.number < 10 ? '0' + slot.number : slot.number }}</div>
                  </div>
               </div>
             </div>

             <div class="rack-column" v-if="rack.showBackSide">
                <div class="rack-header-dark">
                   <div class="d-flex align-items-center gap-3">
                     <span class="fw-bold text-white ms-2">U</span>
                     <span class="fw-bold text-white rack-title">{{ rack.name }}</span>
                   </div>
                   <div class="d-flex align-items-center gap-2 me-2">
                     <button class="btn btn-light btn-xs fw-bold reset-btn" @click="resetRack(rack)">RESET</button>
                     <i class='bx bx-power-off fs-5 cursor-pointer' :class="rack.powerOn ? 'text-success' : 'text-danger'" @click="toggleRackPower(rack)"></i>
                     <span class="fw-bold text-white">U</span>
                   </div>
                </div>
                <div class="rack-frame">
                  <div class="rack-row" v-for="slot in rack.slots" :key="slot.number"
                       @drop="onDrop($event, rack.name, slot.number)" @dragover.prevent>
                     <div class="rack-label">{{ slot.number < 10 ? '0' + slot.number : slot.number }}</div>
                     <div class="rack-slot" :class="{'bg-light': !slot.device}">
                        <DeviceItem 
                          v-if="slot.device"
                          :device="slot.device"
                          :metric-value="getMetricForDevice(slot.device)"
                          :metric-type="metric1 || undefined"
                          :is-back-view="true" 
                        />
                     </div>
                     <div class="rack-label">{{ slot.number < 10 ? '0' + slot.number : slot.number }}</div>
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
.racks-container { 
    display: flex; 
    gap: 40px; 
    padding: 20px; 
    overflow-x: auto; 
    align-items: flex-end;
    min-height: 600px;
}

.single-rack-wrapper { 
    display: flex;
    flex-direction: column;
}

.rack-tabs {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0;
}

.rack-tab {
  padding: 5px 15px;
  font-size: 0.75rem;
  font-weight: bold;
  color: white;
  text-transform: uppercase;
}

.front-label {
  background-color: #6666ff;
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
}

.back-toggle {
  background-color: #333;
  cursor: pointer;
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
}

.rack-column {
  min-width: 280px;
  display: flex;
  flex-direction: column;
}

.rack-header-dark {
    background-color: #222; 
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 5px 0;
    border-bottom: 1px solid #444;
}

.reset-btn {
  font-size: 0.65rem;
  padding: 1px 5px;
  height: 20px;
  line-height: 1;
}

.rack-frame { 
    background: #e9ecef; 
    border: 2px solid #222; 
    border-top: none;
    padding: 0; 
}

.rack-row { 
    display: flex; 
    height: 30px; 
    border-bottom: 1px solid #adb5bd; 
    background-color: #fff;
}

.rack-label { 
    width: 35px; 
    text-align: center; 
    line-height: 30px; 
    font-size: 11px; 
    font-weight: bold;
    color: #444;
    background-color: #e9ecef; 
    border-right: 1px solid #dee2e6;
}
.rack-label:last-child {
  border-right: none;
  border-left: 1px solid #dee2e6;
}

.rack-slot { 
    flex-grow: 1; 
    position: relative; 
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}

.legend-bar {
  width: 200px; 
  height: 20px; 
  background: linear-gradient(90deg, blue, green, yellow, red); 
  border: 1px solid #ccc; 
  border-radius: 4px;
}

.btn-primary { background-color: #6666ff; border-color: #6666ff; }
.btn-info { background-color: #0dcaf0; border-color: #0dcaf0; }
.cursor-pointer { cursor: pointer; }

</style>