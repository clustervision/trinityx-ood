import { ref } from 'vue';
import axios from 'axios';
import type { Rack, RackSlot, Device } from '@/types/rack';

export function useRack() {
  const Url = 'https://yixin3-dev-ctrl001:7755';

  const generateSlots = (size: number, order: string): RackSlot[] => {
    const slots: RackSlot[] = [];
    for (let i = 1; i <= size; i++) {
      slots.push({ number: i, devices: [] });
    }
    return order === 'ascending' ? slots : slots.reverse();
  };

  const placeDeviceInRack = (rack: any, d: any) => {
    const height = parseInt(d.height) || 1;
    const position = Number(d.position);
    const deviceName = d.name;
    const currentSide = d.orientation || 'front'; 


    rack.slots.forEach((s: any) => {
      s.devices = s.devices.filter((dev: any) => dev.name !== deviceName);
    });


    const targetSlot = rack.slots.find((s: any) => s.number === position);
    if (!targetSlot) return;


    const devicesOnSameSide = targetSlot.devices.filter(
      (dev: any) => (dev.orientation || 'front') === currentSide
    );

    if (devicesOnSameSide.length > 0) {
      const existingHeight = devicesOnSameSide[0].height;

      if (height > existingHeight) {
        alert(`Forbidden: New device is taller than existing equipment on the ${currentSide} side.`);
        return;
      }

      if (devicesOnSameSide.length >= 8) {
        console.warn(`Max density reached for ${currentSide} side.`);
        return;
      }

      d.height = existingHeight; 
    }

    targetSlot.devices.push({
      name: deviceName,
      position,
      height: d.height, 
      type: d.type || 'node',
      orientation: currentSide, 
      vendor: d.vendor || null,
      status: 'ok'
    });
  };

  const fetchSingleRack = async (rackName: string): Promise<Rack> => {
    const t = new Date().getTime();
    const res = await axios.get(`${Url}/show_rack/${rackName}?t=${t}`);
    const data = res.data.message;
    
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