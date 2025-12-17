<template>
  <div class="container-fluid flex-grow-1 container-p-y">
    <div class="card mb-4 border-0">
      <div class="card-header bg-white d-flex justify-content-between align-items-center p-4">
        
        <div class="d-flex gap-3">
           <div class="dropdown">
              <button class="btn btn-info text-white dropdown-toggle" type="button">
                Select 1st Metric
              </button>
           </div>
           <div class="dropdown">
              <button class="btn btn-secondary dropdown-toggle" type="button">
                Select 2nd Metric
              </button>
           </div>
        </div>

        <div class="d-flex align-items-center gap-2">
           <!-- <span class="badge bg-warning text-dark me-2">Power <i class='bx bx-chevron-down'></i></span> -->
           <button class="btn btn-secondary" @click="$emit('close')">Back</button>
        </div>
      </div>

      <div class="card-body d-flex justify-content-center align-items-start pt-5" style="min-height: 500px; background-color: #fcfcfc;">
        
        <div v-if="loading" class="text-center">Loading Rack...</div>
        
        <div v-else-if="rack" class="d-flex gap-5">
           
           <div class="rack-column">
              <div class="rack-header-dark">
                 <span class="fw-bold text-white ms-2">U</span>
                 <span class="fw-bold text-white rack-title">{{ rack.name }} Front</span>
                 <span class="fw-bold text-white me-2">U</span>
              </div>
              <div class="rack-frame">
                 <div class="rack-row" v-for="slot in rack.slots" :key="slot.number">
                    <div class="rack-label">{{ slot.number < 10 ? '0' + slot.number : slot.number }}</div>
                    <div class="rack-slot" :class="{'bg-light': !slot.device}">
                       <DeviceItem v-if="slot.device" :device="slot.device" :is-rack-view="true" />
                    </div>
                    <div class="rack-label">{{ slot.number < 10 ? '0' + slot.number : slot.number }}</div>
                 </div>
              </div>
           </div>

           <div class="rack-column">
              <div class="rack-header-dark">
                 <span class="fw-bold text-white ms-2">U</span>
                 <span class="fw-bold text-white rack-title">{{ rack.name }} Back</span>
                 <span class="fw-bold text-white me-2">U</span>
              </div>
              <div class="rack-frame">
                 <div class="rack-row" v-for="slot in rack.slots" :key="slot.number">
                    <div class="rack-label">{{ slot.number < 10 ? '0' + slot.number : slot.number }}</div>
                    <div class="rack-slot bg-light">
                       </div>
                    <div class="rack-label">{{ slot.number < 10 ? '0' + slot.number : slot.number }}</div>
                 </div>
              </div>
           </div>

        </div>
        <div v-else class="alert alert-danger">Rack Not Found</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';
import DeviceItem from '@/components/DeviceItem.vue';

const Url = 'https://yixin3-dev-ctrl001:7755';
const props = defineProps<{ rackName: string }>();
const emit = defineEmits(['close']);

// Interfaces
interface Device {
  name: string;
  position: number;
  height: number;
  type: string;
  orientation?: string;
  vendor?: string;
}

interface RackSlot {
  number: number;
  device: Device | null;
}

interface Rack {
  name: string;
  size: number;
  order: string;
  slots: RackSlot[];
}

const rack = ref<Rack | null>(null);
const loading = ref(true);

const generateSlots = (size: number, order: string) => {
  const slots: RackSlot[] = [];
  for (let i = 1; i <= size; i++) {
    slots.push({ number: i, device: null });
  }
  return order === 'descending' ? slots.reverse() : slots.reverse(); // Default visual is typically Top=Max
};

const loadRackData = async () => {
  if (!props.rackName) return;
  loading.value = true;
  
  try {
    const t = new Date().getTime();
    // Using the endpoint you confirmed returns the device list
    const response = await axios.get(Url + `/show_rack/${props.rackName}?t=${t}`);
    
    // Handle the JSON structure: { message: { name: "...", devices: [...] } }
    const data = response.data.message;
    
    if (data) {
      const size = parseInt(data.size) || 42;
      const order = (data.order || 'ascending').toLowerCase();
      
      const newRack: Rack = {
        name: data.name,
        size: size,
        order: order,
        slots: generateSlots(size, order)
      };

      // Populate Devices
      if (data.devices && Array.isArray(data.devices)) {
        data.devices.forEach((d: any) => {
          // Find the slot matching the device position
          // Note: Logic depends on visual order, but position is absolute U number
          const slotIndex = newRack.slots.findIndex(s => s.number === d.position);
          
          if (slotIndex !== -1) {
             // Create Device Object
             const deviceObj: Device = {
               name: d.name,
               position: d.position,
               height: d.height,
               type: d.type,
               orientation: d.orientation,
               vendor: d.vendor
             };
             // Assign to slot
             newRack.slots[slotIndex].device = deviceObj;
          }
        });
      }
      rack.value = newRack;
    }
  } catch (e) {
    console.error("Failed to load visual rack", e);
  } finally {
    loading.value = false;
  }
};

onMounted(loadRackData);
watch(() => props.rackName, loadRackData);
</script>

<style scoped>
/* Copied and adapted from RackView styles */
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
</style>