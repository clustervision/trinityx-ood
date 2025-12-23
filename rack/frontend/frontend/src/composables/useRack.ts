import { ref } from 'vue';
import axios from 'axios';
// Import the Rack and RackSlot interfaces you already defined
import type { Rack, RackSlot, Device } from '@/types/rack';

export function useRack() {
  const Url = 'https://yixin3-dev-ctrl001:7755';

  const generateSlots = (size: number, order: string): RackSlot[] => {
    const slots: RackSlot[] = [];
    for (let i = 1; i <= size; i++) {
      slots.push({ number: i, device: null });
    }
    return order === 'ascending' ? slots : slots.reverse();
  };

  const placeDeviceInRack = (rack: any, d: any) => {
    const height = parseInt(d.height) || 1;
    const position = Number(d.position);
    const occupiedUs = Array.from({ length: height }, (_, i) => position + i);

    let minVisualIndex = Infinity;
    occupiedUs.forEach(u => {
      const idx = rack.slots.findIndex((s: any) => s.number === u);
      if (idx !== -1 && idx < minVisualIndex) minVisualIndex = idx;
    });

    if (minVisualIndex !== Infinity && minVisualIndex !== -1) {
      rack.slots[minVisualIndex].device = {
        name: d.name, position, height,
        type: d.type || 'node', orientation: d.orientation || 'front',
        vendor: d.vendor || null, status: 'ok'
      };
    }
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