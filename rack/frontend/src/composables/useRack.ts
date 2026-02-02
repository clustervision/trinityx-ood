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

  /** Update rack power button state from nodes only. Treat RESET as ON (case-insensitive). */
  const syncRackPowerFromNodes = (rack: Rack) => {
    const hasNodeOn = rack.slots.some((s) =>
      s.devices.some((d) => {
        const state = (d.powerState || '').toUpperCase();
        return d.type === 'node' && (state === 'ON' || state === 'RESET');
      })
    );
    rack.powerOn = hasNodeOn;
    rack.backPowerOn = hasNodeOn;
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

    // Normalize powerState to uppercase (backend may use powerState or power_state)
    const rawState = d.powerState ?? d.power_state ?? '';
    const stateUpper = String(rawState).toUpperCase();
    targetSlot.devices.push({
      name: deviceName,
      position,
      height: d.height,
      type: d.type || 'node',
      orientation: currentSide,
      vendor: d.vendor || null,
      status: 'ok',
      // Preserve RESET state, otherwise treat as ON or OFF
      powerState: stateUpper === 'ON' ? 'ON' : stateUpper === 'RESET' ? 'RESET' : 'OFF'
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
    syncRackPowerFromNodes(rackObj);
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

    let savedPosition: number | null = null;
    let savedOrientation: 'front' | 'back' = side;
    for (const s of targetRack.slots) {
      const found = s.devices.find(d => d.name === draggedDevice.name);
      if (found) {
        savedPosition = found.position;
        savedOrientation = (found.orientation as 'front' | 'back') || side;
        break;
      }
    }

    targetRack.slots.forEach(s => {
      s.devices = s.devices.filter(d => d.name !== draggedDevice.name);
    });

    const restoreDevice = () => {
      if (savedPosition == null || savedPosition < 1) return;
      placeDeviceInRack(targetRack, {
        ...draggedDevice,
        position: savedPosition,
        orientation: savedOrientation
      });
      targetRack.slots = [...targetRack.slots];
      syncRackPowerFromNodes(targetRack);
    };

    const finalPosition = targetU;

    if (finalPosition < 1 || finalPosition + dragHeight - 1 > targetRack.size) {
      toast.error(`Device does not fit rack ${targetRack.name}: exceeds rack height (Max ${targetRack.size}U).`);
      restoreDevice();
      return;
    }

    const ourStart = finalPosition;
    const ourEnd = finalPosition + dragHeight - 1;

    for (const slot of targetRack.slots) {
      for (const existing of slot.devices) {
        if (existing.orientation !== side) continue;
        const exHeight = Number(existing.height) || 1;
        const exStart = existing.position;
        const exEnd = exStart + exHeight - 1;
        const overlaps = ourStart <= exEnd && exStart <= ourEnd;
        if (!overlaps) continue;
        if (exStart === finalPosition) continue;
        toast.error(`Slot overlaps with ${existing.name} (${exStart}U–${exEnd}U).`);
        restoreDevice();
        return;
      }
    }

    const tempDevice = { ...draggedDevice, position: finalPosition, orientation: side };

    placeDeviceInRack(targetRack, tempDevice);
    targetRack.slots = [...targetRack.slots];
    syncRackPowerFromNodes(targetRack);

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

  return { fetchSingleRack, placeDeviceInRack, handleRackDrop, syncRackPowerFromNodes };
}
