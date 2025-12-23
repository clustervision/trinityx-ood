<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';
import DeviceItem from '@/components/DeviceItem.vue';
import RackMetricsHeader from '@/components/RackMetricsHeader.vue'; 
import type { Device } from '@/types/rack';
import SingleRack from '@/components/SingleRack.vue';
import {useToast} from "vue-toastification"

// --- EMITS ---
const emit = defineEmits(['rack-updated', 'device-taken']);

// --- INTERFACES & STATE ---
interface RackSlot { number: number; device: Device | null; }

interface Rack { 
  name: string; 
  size: number; 
  order: string; 
  slots: RackSlot[]; 
  showBackSide: boolean; 
  powerOn: boolean;
  backPowerOn: boolean;
}

const racks = ref<Rack[]>([]);
const Url = 'https://yixin3-dev-ctrl001:7755';
const prome_url = 'https://yixin3-dev-ctrl001:9090'; 
const metric1 = ref<string | null>('No Scale');
const metric2 = ref<string | null>('No Scale');
const rawMetricData = ref<any[]>([]); 
const toast = useToast();

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
        powerOn: true,
        backPowerOn: true
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

const toggleBackPower = (rack: Rack) => { 
  rack.backPowerOn = !rack.backPowerOn; 
};

// Update existing resetRack to handle sides
const resetRack = (rack: Rack, side: 'front' | 'back' = 'front') => { 
  confirm(`Reset ${rack.name} ${side} side?`); 
  // Add your API call logic here for the specific side
};

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
      toast.success(`Rack Update\n${device.name} Added to Rack ${targetRack.name}.`);
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
          <SingleRack 
            v-for="rack in racks" 
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
</template>

<style scoped>
  .racks-container { display: flex;flex-wrap: wrap; gap: 10px; padding: 10px; overflow-x: auto; align-items: flex-end; width:100% }
</style>
