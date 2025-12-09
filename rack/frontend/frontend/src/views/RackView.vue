<script setup lang="ts">
import { ref, onMounted } from 'vue';
import DeviceItem from '@/components/rack/DeviceItem.vue';
import type { RackData, Device } from '@/types/rack';

// --- STATE ---
// const unassignedDevices = ref([]);
const currentView = ref<'front' | 'back'>('front');
const racks = ref<RackData>({});


const loadMockData = async () => {
  try {
    const response = await fetch('/api/racks'); 
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    
    racks.value = data.racks;
    // unassignedDevices.value = data.inventory || [];
    
    console.log("Data loaded from backend:", data);
  } catch (error) {
    console.error("Failed to load racks:", error);
  }
};

onMounted(() => {
  loadMockData();
});

// --- HELPERS ---
const reverseRange = (n: number) => Array.from({length: n}, (_, i) => n - i);

const getDeviceAt = (rackName: string, u: number): Device | undefined => {
  const rack = racks.value[rackName];
  if (!rack) return undefined;
  
  return rack.devices.find(d => 
    d.position === u && d.orientation === currentView.value
  );
};

// --- DRAG & DROP LOGIC ---

const updateDevicePosition = async (deviceName: string, newRackName: string, newPosition: number) => {
  
  console.log(`Attempting to move ${deviceName} to ${newRackName} at U${newPosition}`);
  
  let foundDevice: Device | undefined;
  let sourceRackName: string | null = null;
  
  // Step A: Find the device
  for (const rName in racks.value) {
    const tempRack = racks.value[rName];
    if (!tempRack) continue;
  
    const index = tempRack.devices.findIndex(d => d.name === deviceName);
    if (index !== -1) {
      foundDevice = tempRack.devices[index];
      tempRack.devices.splice(index, 1);
      sourceRackName = rName;
      break;
    }

  const device = racks.value[newRackName]?.devices.find(d => d.name === deviceName);

  if (device) {
    const payload = {
      name: device.name,
      type: device.type,
      rack: newRackName,
      position: newPosition,
      orientation: currentView.value,
      // If your backend needs 'height' or other fields, add them here
    };

    try {
      const response = await fetch('/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload) // Must stringify for Flask to read it
      });

      if (response.ok) {
        console.log("Backend updated successfully");
      } else {
        console.error("Backend failed to update");
        // Optional: Reload data to revert UI if save failed
        loadMockData(); 
      }
    } catch (e) {
      console.error("Network error saving to backend", e);
    }
  }
};
  // Step B: Validate
  if (!foundDevice) {
    console.error(`Error: Could not find device named ${deviceName}`);
    return;
  }

  // Step C: Update properties
  foundDevice.position = newPosition;
  foundDevice.orientation = currentView.value;

  // Step D: Add to new rack
  const targetRack = racks.value[newRackName];
  if (targetRack) {
    targetRack.devices.push(foundDevice);
    console.log("Success: Device moved.");
  } else {
    // Revert if target not found
    if (sourceRackName && racks.value[sourceRackName]) {
      racks.value[sourceRackName]!.devices.push(foundDevice);
    }
  }
};

const onDrop = (event: DragEvent, targetRackName: string, targetU: number) => {
  const data = event.dataTransfer?.getData('application/json');
  if (!data) return;

  const droppedDevice = JSON.parse(data) as Device;
  updateDevicePosition(droppedDevice.name, targetRackName, targetU);
};



const metric1 = ref<string | null>(null);
const metric2 = ref<string | null>(null);
const showDropdown1 = ref(false);
const showDropdown2 = ref(false); 

const selectMetric1 = (name: string) => {
  metric1.value = name;
  showDropdown1.value = false;
};
const selectMetric2 = (name: string) => {
  metric2.value = name;
  showDropdown2.value = false;
};
</script>




<template>
  <div class="card mb-4">
    <div class="card-header">
      <div class="row">
        <div class="col-md-6 d-flex gap-2">
            
            <div class="dropdown">
              <button 
                class="btn btn-primary btn-sm dropdown-toggle" 
                type="button"
                @click="showDropdown1 = !showDropdown1"
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

            <div class="dropdown">
              <button 
                class="btn btn-info btn-sm dropdown-toggle" 
                type="button"
                @click="showDropdown2 = !showDropdown2"
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

        </div>
      </div>
      
      <div class="row mt-3">
         <div class="col-12" v-if="metric1 === 'Temperature'">
            <span>0°C </span>
            <span class="grad" style="display: inline-block; width: 100px; height: 10px; background: linear-gradient(90deg, blue, red); margin: 0 10px;">&nbsp;</span>
            <span> 90°C</span>
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
.controls { margin: 20px; }
.controls button { margin-right: 10px; padding: 5px 10px; }
.controls button.active { background-color: #007bff; color: white; border: none; }
</style>