import { ref } from 'vue';
import axios from 'axios';
// Import the Rack and RackSlot interfaces you already defined
import type { Rack, RackSlot, Device } from '@/types/rack';

export function useRack() {
  const Url = 'https://yixin3-dev-ctrl001:7755';

// useRack.ts
const generateSlots = (size: number, order: string): RackSlot[] => {
  const slots: RackSlot[] = [];
  for (let i = 1; i <= size; i++) {
    slots.push({ number: i, devices: [] }); // Initialize as an empty array
  }
  return order === 'ascending' ? slots : slots.reverse();
};

const placeDeviceInRack = (rack: any, d: any) => {
  const height = parseInt(d.height) || 1;
  const position = Number(d.position);
  const deviceName = d.name;

  // STEP 1: REMOVE FROM OLD POSITION (Fixes the "double device" issue)
  // We search the entire rack and remove any existing instance of this device
  rack.slots.forEach((s: any) => {
    s.devices = s.devices.filter((dev: any) => dev.name !== deviceName);
  });

  // STEP 2: FIND TARGET SLOT
  const targetSlot = rack.slots.find((s: any) => s.number === position);
  if (!targetSlot) return;

  // STEP 3: SPLIT LOGIC & CONSTRAINTS
  if (targetSlot.devices.length > 0) {
    const existingHeight = targetSlot.devices[0].height;

    // Forbidden: New device (A) taller than existing (B)
    if (height > existingHeight) {
      alert("Forbidden: New device cannot be taller than existing devices in this slot.");
      return;
    }

    // Max 8 devices
    if (targetSlot.devices.length >= 8) {
      console.warn("Max 8 devices reached.");
      return;
    }

    // Force A to match B's height
    d.height = existingHeight; 
  }

  // STEP 4: INSERT
  targetSlot.devices.push({
    name: deviceName,
    position,
    height: d.height, 
    type: d.type || 'node',
    orientation: d.orientation || 'front',
    vendor: d.vendor || null,
    status: 'ok'
  });
};

  const fetchSingleRack = async (rackName: string): Promise<Rack> => {
    const t = new Date().getTime();
    const res = await axios.get(`${Url}/show_rack/${rackName}?t=${t}`);
    const data = res.data.message;
    
    // Explicitly type rackObj as Rack
    const rackObj: Rack = {
      name: rackName,
      size: parseInt(data.size) || 42,
      order: (data.order || 'ascending').toLowerCase(),
      slots: [], 
      showBackSide: true,
      powerOn: true,
      backPowerOn: true
    };

    rackObj.slots = generateSlots(rackObj.size, rackObj.order);
    if (data.devices) {
      data.devices.forEach((d: any) => placeDeviceInRack(rackObj, d));
    }
    return rackObj;
  };

  return { fetchSingleRack, placeDeviceInRack };
}