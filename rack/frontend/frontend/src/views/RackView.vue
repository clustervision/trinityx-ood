<script setup lang="ts">
import { ref, onMounted } from 'vue';
import DeviceItem from '@/components/rack/DeviceItem.vue';
import type { RackData, Device } from '@/types/rack';

// --- STATE ---
const currentView = ref<'front' | 'back'>('front');
const racks = ref<RackData>({});

// --- MOCK DATA ---
const loadMockData = () => {
  racks.value = {
    "Rack-01": {
      name: "Rack-01",
      size: 42,
      devices: [
        { name: "Node-01", type: "node", height: 2, vendor: "dell", position: 40, orientation: "front" },
        { name: "Switch-A", type: "switch", height: 1, vendor: "cisco", position: 35, orientation: "front" }
      ]
    },
    "Rack-02": {
      name: "Rack-02",
      size: 42,
      devices: []
    }
  };
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
const updateDevicePosition = (deviceName: string, newRackName: string, newPosition: number) => {
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
  }

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
</script>

<template>
  <div class="rack-page">
    <h2>Rack Management</h2>
    
    <div class="controls">
      <button @click="currentView = 'front'" :class="{ active: currentView === 'front' }">Front View</button>
      <button @click="currentView = 'back'" :class="{ active: currentView === 'back' }">Back View</button>
    </div>

    <div class="racks-container">
      <div v-for="(rack, rackName) in racks" :key="rackName" class="single-rack">
        <h3>{{ rackName }} ({{ currentView }})</h3>

        <div class="rack-frame">
          <div 
            v-for="u in reverseRange(rack.size)" 
            :key="u" 
            class="rack-row"
          >
            <div class="rack-pillar-left"></div>
            <div class="rack-label">{{ u }}</div>

            <div 
              class="rack-slot"
              @dragover.prevent
              @drop="onDrop($event, rackName as string, u)"
            >
              <DeviceItem 
                v-if="getDeviceAt(rackName as string, u)" 
                :device="getDeviceAt(rackName as string, u)!" 
              />
            </div>

            <div class="rack-label">{{ u }}</div>
            <div class="rack-pillar-right"></div>
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
.controls { margin: 20px; }
.controls button { margin-right: 10px; padding: 5px 10px; }
.controls button.active { background-color: #007bff; color: white; border: none; }
</style>