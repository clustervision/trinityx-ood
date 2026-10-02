import { ref } from 'vue';
import axios from 'axios';
import { useToast } from "vue-toastification";
import type { Rack, RackSlot, Device } from '@/types/rack';
import { isOtherDevices0U } from '@/utils/deviceKind';
import { parsePowerStateFromMessage } from '@/utils/powerState';
import { mergeRackPowerCacheFromStorage } from '@/utils/rackPowerCache';

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

  /** Max devices that can merge at one position by height (U). 1U->4, 2U->8, 3U->15, ..., 8U->40. */
  const getMaxDevicesForHeight = (heightU: number): number => {
    const h = Math.min(8, Math.max(1, Math.floor(heightU)));
    return h <= 2 ? 4 * h : 5 * h;
  };

  /**
   * Chunk devices into rows for display:
   * 1U: one row, cols = count (1–4).
   * 2U and all U when count <= 4*h: rows of 4 (last row 1–4). E.g. 5 devices → 4+1, 8 → 4+4.
   * 3U+ when count > 4*h: all in rows of 5 (e.g. 15 devices → 5+5+5, not 4+4+4+3).
   */
  const getDeviceRows = (devices: any[], heightU: number): any[][] => {
    const h = Math.min(8, Math.max(1, Math.floor(heightU)));
    const n = devices.length;
    const rows: any[][] = [];
    if (h === 1) {
      if (n > 0) rows.push(devices);
      return rows;
    }
    const firstCount = 4 * h;
    let i = 0;
    if (n <= firstCount) {
      while (i < n) {
        rows.push(devices.slice(i, i + 4));
        i += 4;
      }
    } else {
      while (i < n) {
        rows.push(devices.slice(i, i + 5));
        i += 5;
      }
    }
    return rows;
  };

  /**
   * Rack power button: power-btn-on iff rack.powerOn.
   * With a controller: always green (on).
   * Without a controller: green if any node has ON or RESET; otherwise off (power-btn-off).
   */
  const syncRackPowerFromNodes = (rack: Rack) => {
    const hasController = rack.slots.some((s) =>
      s.devices.some((d) => d.type === 'controller')
    );
    if (hasController) {
      rack.powerOn = true;
      rack.backPowerOn = true;
      return;
    }
    const anyNodeOnOrReset = rack.slots.some((s) =>
      s.devices.some((d) => {
        if (d.type !== 'node') return false;
        const state = (d.powerState || '').trim().toUpperCase();
        return state === 'ON' || state === 'RESET';
      })
    );
    rack.powerOn = anyNodeOnOrReset;
    rack.backPowerOn = anyNodeOnOrReset;
  };

  const placeDeviceInRack = (rack: any, d: any, options?: { enforceMergeLimit?: boolean }): boolean => {
    const enforceMergeLimit = options?.enforceMergeLimit !== false;
    const height = parseInt(d.height) || 1;
    const position = Number(d.position);
    const deviceName = d.name;
    const currentSide = d.orientation || 'front';

    rack.slots.forEach((s: any) => {
      s.devices = s.devices.filter((dev: any) => dev.name !== deviceName);
    });


    const targetSlot = rack.slots.find((s: any) => s.number === position);
    if (!targetSlot) return false;

    const devicesOnSameSide = targetSlot.devices.filter(
      (dev: any) => (dev.orientation || 'front') === currentSide
    );

    if (devicesOnSameSide.length > 0) {
      const existingHeight = devicesOnSameSide[0].height;
      if (height > existingHeight) {
        if (enforceMergeLimit) toast.error(`Forbidden: New device is taller than existing equipment on the ${currentSide} side.`);
        return false;
      }
      d.height = existingHeight;
      if (enforceMergeLimit) {
        const maxAllowed = getMaxDevicesForHeight(existingHeight);
        if (devicesOnSameSide.length >= maxAllowed) {
          toast.error(`Max ${maxAllowed} devices allowed at this ${existingHeight}U position.`);
          return false;
        }
      }
    } else {
      if (enforceMergeLimit && height > 8) {
        toast.error('Device height cannot exceed 8U.');
        return false;
      }
    }

    const rawState = d.powerState ?? d.power_state ?? '';
    const powerState = parsePowerStateFromMessage(rawState);
    targetSlot.devices.push({
      name: deviceName,
      position,
      height: d.height,
      type: d.type || 'node',
      orientation: currentSide,
      vendor: d.vendor || null,
      status: 'ok',
      powerState
    });
    return true;
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
      data.devices.forEach((d: any) => placeDeviceInRack(rackObj, d, { enforceMergeLimit: false }));
    }
    mergeRackPowerCacheFromStorage(rackObj);
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

    const parsed = JSON.parse(data);

    if (parsed.multi === true && Array.isArray(parsed.devices) && parsed.devices.length > 0) {
      const devices: any[] = parsed.devices;
      if (devices.some((d) => isOtherDevices0U(d))) {
        toast.error('0U devices cannot be placed on rack. It stays in Unassigned Pool only.');
        return;
      }
      let currentU = targetU;
      const placedNames: string[] = [];
      for (const draggedDevice of devices) {
        const dragHeight = parseInt(draggedDevice.height) || 1;
        if (dragHeight > 8) {
          toast.error(`Device ${draggedDevice.name}: height cannot exceed 8U.`);
          break;
        }
        if (currentU < 1 || currentU + dragHeight - 1 > targetRack.size) {
          toast.error(
            `Device ${draggedDevice.name} does not fit rack ${targetRack.name}: exceeds rack height (Max ${targetRack.size}U).`
          );
          break;
        }
        const ourStart = currentU;
        const ourEnd = currentU + dragHeight - 1;
        let overlaps = false;
        for (const slot of targetRack.slots) {
          for (const existing of slot.devices) {
            if (existing.orientation !== side) continue;
            const exHeight = Number(existing.height) || 1;
            const exStart = existing.position;
            const exEnd = exStart + exHeight - 1;
            if (ourStart <= exEnd && exStart <= ourEnd) {
              overlaps = true;
              break;
            }
          }
          if (overlaps) break;
        }
        if (overlaps) {
          toast.error(`Device ${draggedDevice.name} would overlap existing equipment.`);
          break;
        }
        const tempDevice = { ...draggedDevice, position: currentU, orientation: side };
        if (!placeDeviceInRack(targetRack, tempDevice)) {
          break;
        }
        targetRack.slots = [...targetRack.slots];
        syncRackPowerFromNodes(targetRack);
        try {
          const payload = { ...tempDevice, rack: targetRack.name };
          const doubleEncoded = JSON.stringify(JSON.stringify(payload));
          await axios.post(`${Url}/update_rack`, doubleEncoded, {
            headers: { 'Content-Type': 'application/json' }
          });
          placedNames.push(draggedDevice.name);
        } catch (e) {
          console.error('Drop failed for', draggedDevice.name, e);
          toast.error(`Failed to add ${draggedDevice.name} to rack.`);
          if (onError) onError();
          break;
        }
        currentU += dragHeight;
      }
      if (placedNames.length > 0 && onSuccess) {
        onSuccess(placedNames.length === 1 ? placedNames[0] : placedNames);
      }
      if (placedNames.length > 0) {
        toast.success(
          placedNames.length === devices.length
            ? `${placedNames.length} device(s) added to rack ${targetRack.name}`
            : `${placedNames.length} of ${devices.length} device(s) added to rack ${targetRack.name}`
        );
      }
      return;
    }

    const draggedDevice = parsed;
    if (isOtherDevices0U(draggedDevice)) {
      toast.error('0U device cannot be placed on rack. It stays in Unassigned Pool only.');
      return;
    }
    const dragHeight = parseInt(draggedDevice.height) || 1;

    let savedPosition: number | null = null;
    let savedOrientation: 'front' | 'back' = side;
    let savedPowerState: string | undefined;
    for (const s of targetRack.slots) {
      const found = s.devices.find(d => d.name === draggedDevice.name);
      if (found) {
        savedPosition = found.position;
        savedOrientation = (found.orientation as 'front' | 'back') || side;
        savedPowerState = found.powerState;
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

    let finalPosition = targetU;

    if (dragHeight > 8) {
      toast.error('Device height cannot exceed 8U.');
      restoreDevice();
      return;
    }
    if (finalPosition < 1 || finalPosition + dragHeight - 1 > targetRack.size) {
      toast.error(`Device does not fit rack ${targetRack.name}: exceeds rack height (Max ${targetRack.size}U).`);
      restoreDevice();
      return;
    }

    let ourStart = finalPosition;
    let ourEnd = finalPosition + dragHeight - 1;
    let mergeHeight: number | null = null;

    for (const slot of targetRack.slots) {
      for (const existing of slot.devices) {
        if (existing.orientation !== side) continue;
        const exHeight = Number(existing.height) || 1;
        const exStart = existing.position;
        const exEnd = exStart + exHeight - 1;
        const overlaps = ourStart <= exEnd && exStart <= ourEnd;
        if (!overlaps) continue;
        if (exStart === finalPosition && dragHeight <= exHeight) continue;
        if (dragHeight <= exHeight) {
          finalPosition = exStart;
          ourStart = exStart;
          ourEnd = exStart + exHeight - 1;
          mergeHeight = exHeight;
          break;
        }
        toast.error(`Slot overlaps with ${existing.name} (${exStart}U–${exEnd}U).`);
        restoreDevice();
        return;
      }
      if (mergeHeight != null) break;
    }

    const tempDevice = {
      ...draggedDevice,
      position: finalPosition,
      orientation: side,
      ...(mergeHeight != null ? { height: mergeHeight } : {}),
      powerState: draggedDevice.powerState ?? draggedDevice.power_state ?? savedPowerState ?? 'OFF'
    };

    if (!placeDeviceInRack(targetRack, tempDevice)) {
      restoreDevice();
      return;
    }
    // New slot refs so Vue detects change and re-renders LEDs (device refs preserved)
    targetRack.slots = targetRack.slots.map(slot => ({ ...slot, devices: [...slot.devices] }));
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

  return { fetchSingleRack, placeDeviceInRack, handleRackDrop, syncRackPowerFromNodes, getMaxDevicesForHeight, getDeviceRows };
}
