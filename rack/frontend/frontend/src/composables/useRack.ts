import { ref } from 'vue';
import axios from 'axios';
import { useToast } from "vue-toastification";
import type { Rack, RackSlot, Device } from '@/types/rack';

export function useRack() {
  //@ts-ignore
  const Url = window.APP_URL;
  const toast = useToast();

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
      size: parseInt(data.size),
      order: (data.order || 'ascending').toLowerCase(),
      slots: [],
      showBackSide: true,
      showFrontSide: true,
      powerOn: true,
      backPowerOn: true
    };

    rackObj.slots = generateSlots(rackObj.size, rackObj.order);
    if (data.devices) {
      data.devices.forEach((d: any) => placeDeviceInRack(rackObj, d));
    }
    return rackObj;
  };

  const handleRackDrop = async (
    event: DragEvent,
    targetRack: Rack,
    targetU: number,
    side: 'front' | 'back',
    onSuccess?: Function,
    onError?: Function
  ) => {
    const data = event.dataTransfer?.getData('application/json');
    if (!data) return;

    const draggedDevice = JSON.parse(data);
    const dragHeight = parseInt(draggedDevice.height) || 1;
    if (targetU + dragHeight - 1 > targetRack.size) {
      toast.error(`Installation failed: Device fits out of rack bounds (Max ${targetRack.size}U).`);
      return;
    }
    for (let i = 0; i < dragHeight; i++) {
      const checkU = targetU + i;
      const slotToCheck = targetRack.slots.find(s => s.number === checkU);

      if (slotToCheck) {
        const existingDevice = slotToCheck.devices.find(d => d.orientation === side && d.name !== draggedDevice.name);

        if (existingDevice) {
          if (existingDevice.position !== targetU) {
            toast.error(`Slot ${checkU} is occupied by ${existingDevice.name}`);
            return;
          }
          if (existingDevice.position === targetU && existingDevice.height < dragHeight) {
            toast.error(`Space is too small: existing device only has height ${existingDevice.height}`);
            return;
          }
        }
      }
    }

    targetRack.slots.forEach(s => {
      s.devices = s.devices.filter(d => d.name !== draggedDevice.name);
    });

    let finalPosition = targetU;


    const tempDevice = { ...draggedDevice, position: finalPosition, orientation: side };

    placeDeviceInRack(targetRack, tempDevice);

    targetRack.slots = [...targetRack.slots];
    try {
      const payload = { ...tempDevice, rack: targetRack.name };
      const doubleEncoded = JSON.stringify(JSON.stringify(payload));

      await axios.post(`${Url}/update_rack`, doubleEncoded, {
         headers: { 'Content-Type': 'application/json' }
      });

      toast.success(`${draggedDevice.name} added to rack ${targetRack.name}`);

      if (onSuccess) onSuccess(draggedDevice.name);

    } catch (e) {
      console.error("Drop failed", e);
      if (onError) onError();
    }
  };

  return { fetchSingleRack, placeDeviceInRack, handleRackDrop };
}
