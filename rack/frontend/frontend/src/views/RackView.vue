<script setup lang="ts">
import { ref, onMounted } from 'vue';
import DeviceItem from '@/components/rack/DeviceItem.vue';
import type { RackData, Device } from '@/types/rack';

// --- STATE ---
const currentView = ref<'front' | 'back'>('front');
const racks = ref<RackData>({});
const metric1 = ref<string | null>(null);
const metric2 = ref<string | null>(null);
const showDropdown1 = ref(false);
const showDropdown2 = ref(false); 

// Store the raw data from backend
const rawMetricData = ref<any[]>([]); 
// Store the current metric type to decide which field to read (load vs temp)
const currentMetricType = ref<string | null>(null);

// --- API: LOAD RACKS ---
const loadMockData = async () => {
  try {
    const response = await fetch('/api/racks'); 
    if (!response.ok) throw new Error(`HTTP error! ${response.status}`);
    const data = await response.json();
    racks.value = data.racks;
    console.log("Racks loaded:", data);
  } catch (error) {
    console.error("Failed to load racks:", error);
  }
};

onMounted(() => {
  loadMockData();
});

// --- API: FETCH METRICS ---
const fetchMetricData = async () => {
  try {
    const response = await fetch('https://YOUR_VM_IP:7755/get_temperature');
    
    if (!response.ok) throw new Error("Failed to fetch metrics");

    const data = await response.json();
    rawMetricData.value = data; 
    console.log("Metrics loaded:", data);
  } catch (e) {
    console.error("Fetch error:", e);
  }
};

// --- HELPER: MAP METRIC TO DEVICE ---
const getMetricForDevice = (device: Device) => {
  if (!device || !rawMetricData.value.length) return null;

  // Match device name with hostname from API
  const found = rawMetricData.value.find((item: any) => item.hostname === device.name);
  if (!found) return null;

  // Return the specific value based on what is selected in Metric 1
  if (currentMetricType.value === 'System Load') return found.load;
  if (currentMetricType.value === 'Temperature') return found.temperature; 
  if (currentMetricType.value === 'Power Consumption') return found.power;

  return null;
};

// --- DROPDOWN LOGIC ---
const selectMetric1 = (name: string) => {
  metric1.value = name;
  currentMetricType.value = name; // Set the type for coloring
  showDropdown1.value = false;
  
  if (name !== 'No Scale') {
    fetchMetricData();
  } else {
    rawMetricData.value = [];
  }
};

const selectMetric2 = (name: string) => {
  metric2.value = name; // FIX: Now updates metric2, not metric1
  showDropdown2.value = false;
  
  // You can decide if Metric 2 also triggers a fetch or does something else
  if (name !== 'No Scale') {
    fetchMetricData();
  }
};

// --- RACK HELPERS ---
const reverseRange = (n: number) => Array.from({length: n}, (_, i) => n - i);

const getDeviceAt = (rackName: string, u: number): Device | undefined => {
  const rack = racks.value[rackName];
  if (!rack) return undefined;
  return rack.devices.find(d => d.position === u && d.orientation === currentView.value);
};

// --- DRAG & DROP (Simplified for brevity, ensure you include your full logic) ---
const onDrop = (event: DragEvent, targetRackName: string, targetU: number) => {
  // ... Your existing drop logic here ...
  console.log("Dropped on", targetRackName, targetU);
};
</script>

<template>
  <div class="card mb-4">
    <div class="card-header p-4 bg-white">
      
      <div class="d-flex justify-content-between align-items-center mb-3">
        
        <div class="d-flex align-items-center gap-3">
          <div class="dropdown">
            <button 
              class="btn btn-primary dropdown-toggle" 
              type="button" 
              @click="showDropdown1 = !showDropdown1"
              style="min-width: 160px;"
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
          <button 
            class="btn btn-info text-white dropdown-toggle" 
            type="button" 
            @click="showDropdown2 = !showDropdown2"
            style="min-width: 160px;"
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

        <div v-if="metric2 === 'Temperature'" class="d-flex align-items-center gap-2">
            <span class="fw-bold">0°C</span>
            <div style="width: 200px; height: 20px; background: linear-gradient(90deg, blue, lime, red); border: 1px solid #ccc; border-radius: 4px;"></div>
            <span class="fw-bold">90°C</span>
        </div>
      </div>

    </div>

    <div class="card-body">
      <div class="racks-container">
        
        <div v-for="(rack, rackName) in racks" :key="rackName" class="single-rack">
           
           <div class="text-center fw-bold mb-2">{{ rackName }}</div>
           
           <div class="rack-frame">
              <div class="rack-row" v-for="u in reverseRange(42)" :key="u"
                   @drop="onDrop($event, String(rackName), u)" 
                   @dragover.prevent>
                 
                 <div class="rack-label">{{ u }}</div>
                 <div class="rack-slot">
                    <DeviceItem 
                      v-if="getDeviceAt(String(rackName), u)"
                      :device="getDeviceAt(String(rackName), u)!"
                      :metric-value="getMetricForDevice(getDeviceAt(String(rackName), u)!)"
                      :metric-type="metric1" 
                    />
                 </div>
                 <div class="rack-label">{{ u }}</div>
              
              </div>
           </div>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.racks-container { display: flex; gap: 20px; padding: 20px; overflow-x: auto; }
.single-rack { min-width: 300px; }
.rack-frame { background: #eee; border: 2px solid #333; padding: 5px; }
.rack-row { display: flex; height: 30px; border-bottom: 1px solid #ccc; position: relative; }
.rack-slot { flex-grow: 1; border-left: 1px solid #999; border-right: 1px solid #999; position: relative; background: #fff; }
.rack-label { width: 30px; text-align: center; line-height: 30px; font-size: 12px; color: #666; }
</style>