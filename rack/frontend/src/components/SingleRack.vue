<script setup lang="ts">
import DeviceItem from '@/components/DeviceItem.vue';
import DeviceContextMenu from '@/components/DeviceContextMenu.vue';
import type { Rack, Device } from '@/types/rack';
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import { useToast } from 'vue-toastification';
import { useTheme } from '@/composables/useTheme';
import { useDeviceActions } from '@/composables/useDeviceActions';
import { useDraggedDevice } from '@/composables/useDraggedDevice';
import { useRack } from '@/composables/useRack';
import {
  handleSessionExpired,
  isSessionExpired,
  readJsonApiResponse,
  messageIndicatesSessionLost,
  fetchFailureLikelySessionRelated,
} from '@/utils/connectionStatus';
import { parsePowerStateFromMessage } from '@/utils/powerState';
import { showPowerOperationToast } from '@/utils/powerToast';
import {
  getRackPowerCacheKey,
  mergeRackPowerCacheFromStorage,
  type RackPowerCachePayload,
} from '@/utils/rackPowerCache';
import { isPerformCommandFailureMessage } from '@/utils/performCommandResponse';
import {
  applyRackPowerNodeResultPayload,
  isRackPowerNodeResultPayload,
} from '@/utils/rackPowerStreamApply';

const props = defineProps<{
  rack: Rack;
  metric1: string | null;
  metric2: string | null;
  isBusy?: boolean;
  getMetric: Function;
  isBackViewMode: boolean;
  metric1Color?: string;
  metric2Color?: string;
}>();

const { isDarkMode } = useTheme();
const toast = useToast();
const { executeDeviceAction } = useDeviceActions();
const { getDeviceRows, syncRackPowerFromNodes } = useRack();

const getDeviceRowsForSlot = (slot: { devices: Device[] }, side: 'front' | 'back') => {
  const list = slot.devices.filter((d) => (d.orientation || 'front') === side);
  const heightU = list[0]?.height ?? 1;
  return getDeviceRows(list, heightU);
};
const isActionLoading = ref(false);
const menuVisible = ref(false);
const menuPos = ref({ x: 0, y: 0 });
const selectedDevice = ref<Device | null>(null);

const handleDeviceRightClick = (event: MouseEvent, device: Device) => {
  event.preventDefault();
  selectedDevice.value = device;
  menuPos.value = { x: event.clientX, y: event.clientY };
  menuVisible.value = true;
};

const handleMenuAction = async (payload: { action: string; subAction?: string; device: Device }) => {
  const { action, subAction, device } = payload;
  if (action === 'edit-inventory') {
    emit('edit-inventory', device);
    return;
  }
  isActionLoading.value = true;
  try {
    const result = await executeDeviceAction(action, subAction, device);
    if (result && !result.success) {
      toast.error(result.message || 'Action failed');
      return;
    }
    if (result?.success) {
      if (action === 'power') {
        if (subAction === 'status') {
          device.powerState = parsePowerStateFromMessage(result.message);
          syncRackPowerFromNodes(props.rack);
          props.rack.slots = props.rack.slots.map(slot => ({ ...slot, devices: [...slot.devices] }));
          saveRackPowerCache();
        } else {
          if (subAction === 'on') device.powerState = 'ON';
          else if (subAction === 'off') device.powerState = 'OFF';
          else if (subAction === 'reset') device.powerState = 'RESET';
          syncRackPowerFromNodes(props.rack);
          saveRackPowerCache();
        }
        showPowerOperationToast(toast, device.name, subAction, result.message);
      } else {
        toast.success(result.message);
      }
    }
  } catch {
    toast.error('Action failed');
  } finally {
    isActionLoading.value = false;
  }
};

const LED_COLORS = ['#28c76f', '#00cfe8', '#ff9f43', '#00e676', '#00b0ff'];

type Led = { left: string; top: string; color: string; animationDuration: string; animationDelay: string; blinking: boolean };
type LedDensityKey = 'high' | 'medium' | 'low';

const ledCache = new Map<string, Led[]>();

function applyRackPowerCache() {
  if (typeof window === 'undefined' || !props.rack?.slots) return;
  try {
    mergeRackPowerCacheFromStorage(props.rack);
    syncRackPowerFromNodes(props.rack);
    props.rack.slots = props.rack.slots.map(slot => ({ ...slot, devices: [...slot.devices] }));
  } catch (e) {
    console.error('[Rack Power Cache] Failed to apply cache', e);
  }
}

function saveRackPowerCache() {
  if (typeof window === 'undefined') return;
  try {
    if (!props.rack || !props.rack.slots) return;
    const devices: Record<string, string | undefined> = {};
    props.rack.slots.forEach(slot => {
      slot.devices.forEach(device => {
        if (device.name) {
          devices[device.name] = device.powerState;
        }
      });
    });
    const payload: RackPowerCachePayload = {
      powerOn: props.rack.powerOn,
      backPowerOn: props.rack.backPowerOn,
      devices,
    };
    const key = getRackPowerCacheKey(props.rack.name);
    window.localStorage.setItem(key, JSON.stringify(payload));
  } catch (e) {
    console.error('[Rack Power Cache] Failed to save cache', e);
  }
}

/** ON/RESET only (strict); aligns with syncRackPowerFromNodes / parsePowerStateFromMessage. */
function isDevicePowerOnForLeds(device: Device): boolean {
  const state = (device.powerState || '').trim().toUpperCase();
  return state === 'ON' || state === 'RESET';
}

/** Pure: build LED array for a device given density. Node+OFF returns []. No logging. */
function buildDeviceLeds(device: Device, densityKey: LedDensityKey): Led[] {
  const type = (device.type || '').toLowerCase();
  const isNode = type === 'node';
  const powerOn = isDevicePowerOnForLeds(device);
  if (isNode && !powerOn) return [];

  let seed = 0;
  for (let i = 0; i < device.name.length; i++) seed += device.name.charCodeAt(i);
  const rand = () => {
    const x = Math.sin(seed++) * 10000;
    return x - Math.floor(x);
  };

  const gridSlots = [8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88];
  const allLeds: Led[] = [];

  // Count per row by density: high 2-4, medium 1-2, low 1 (slightly fewer when merged)
  const countRange: [number, number] = densityKey === 'high' ? [2, 4] : densityKey === 'medium' ? [1, 2] : [1, 1];
  const countSpread = countRange[1] - countRange[0] + 1;

  for (let u = 0; u < device.height; u++) {
    const countPerRow = countRange[0] + Math.floor(rand() * countSpread);
    const rowSlots: number[] = [];
    let attempts = 0;

    while (rowSlots.length < countPerRow && attempts < 50) {
      attempts++;
      const slotIndex = Math.floor(rand() * gridSlots.length);
      const slotPos = gridSlots[slotIndex];
      if (slotPos === undefined) continue;
      if (rowSlots.includes(slotPos)) continue;
      const leftNeighbor = gridSlots[slotIndex - 1];
      const rightNeighbor = gridSlots[slotIndex + 1];
      const hasLeft = leftNeighbor !== undefined && rowSlots.includes(leftNeighbor);
      const hasRight = rightNeighbor !== undefined && rowSlots.includes(rightNeighbor);
      if (hasLeft && hasRight) continue;
      rowSlots.push(slotPos);
    }

    const heightPerU = 100 / device.height;
    const baseTop = (u * heightPerU) + (heightPerU / 2);
    for (const leftPos of rowSlots) {
      allLeds.push({
        left: leftPos + '%',
        top: baseTop + '%',
        color: LED_COLORS[Math.floor(rand() * LED_COLORS.length)] ?? '#28c76f',
        animationDuration: (0.8 + rand() * 1.7) + 's',
        animationDelay: (rand() * 2) + 's',
        blinking: true
      });
    }
  }
  return allLeds;
}

/** Cached LED array. Key excludes powerState so OFF->ON reuses pattern. */
function getCachedDeviceLeds(device: Device, densityKey: LedDensityKey): Led[] {
  const type = (device.type || '').toLowerCase();
  const isNode = type === 'node';
  const powerOn = isDevicePowerOnForLeds(device);
  if (isNode && !powerOn) return [];

  const cacheKey = `${device.name}|${device.height}|${device.type ?? ''}|${densityKey}`;
  let cached = ledCache.get(cacheKey);
  if (cached) return cached;
  cached = buildDeviceLeds(device, densityKey);
  ledCache.set(cacheKey, cached);
  return cached;
}

/** Density key from merged device count at same slot/side. */
function getLedDensityKey(mergedCount: number): LedDensityKey {
  if (mergedCount <= 4) return 'high';
  if (mergedCount <= 10) return 'medium';
  return 'low';
}

const hasController = computed(() => {
  if (!props.rack?.slots) return false;
  return props.rack.slots.some(slot =>
    slot.devices.some(device => device.type === 'controller')
  );
});


const hasSwitch = computed(() => {
  if (!props.rack?.slots) return false;
  return props.rack.slots.some(slot =>
    slot.devices.some(device => device.type === 'switch')
  );
});

const truncatedRackName = computed(() => {
  const name = props.rack?.name || '';
  return name.length > 10 ? name.slice(0, 10) + '...' : name;
});

const powerButtonTooltip = computed(() => {
  const baseState = props.rack.powerOn
    ? 'Click to power OFF all rack nodes (power control is only for nodes).'
    : 'Click to power ON all rack nodes (power control is only for nodes).';

  if (hasController.value && !hasSwitch.value) {
    return `${baseState}\n⚠️ Note: A controller is present.\nControllers cannot be powered off by this button; only nodes are affected.`;
  }
  if (hasSwitch.value && !hasController.value) {
    return `${baseState}\n⚠️ Note: A switch is present.\nSwitches cannot be powered off by this button; only nodes are affected.`;
  }
  if (hasSwitch.value && hasController.value) {
    return `${baseState}\n⚠️ Note: A controller and a switch are present.\nThis power operation only applies to nodes; controllers and switches stay ON.`;
  }
  return baseState;
});

const handleRackAction = async (action: 'reset' | 'on' | 'off') => {
  const actionLabel = action === 'reset' ? 'Power Reset' : action === 'on' ? 'Power ON' : 'Power OFF';
  const confirmMsg =
    action === 'reset'
      ? `Power Reset all nodes on ${props.rack.name}? (Switches & Controllers ignored)`
      : `${actionLabel} all nodes on ${props.rack.name}? (Switches & Controllers ignored)`;
  if (!confirm(confirmMsg)) return;

  let nodeCount = 0;
  props.rack.slots.forEach(slot => {
    slot.devices.forEach(device => {
      if (device.type === 'node') nodeCount++;
    });
  });

  // @ts-ignore
  const baseUrl = window.APP_URL || '';
  const url = `${baseUrl}/rack_power/${props.rack.name}/${action}`;

  const handleSuccess = () => {
    const actionName = action.charAt(0).toUpperCase() + action.slice(1);
    if (hasController.value) {
      toast.success(`${actionName} action successful!\n(Controller remained ON)`);
    }
    if (hasSwitch.value) {
      toast.success(`${actionName} action successful!\n(Switch remained ON)`);
    } else if (!hasController.value) {
      toast.success(`${actionName} action successful!`);
    }

    props.rack.slots.forEach(slot => {
      slot.devices.forEach(device => {
        if (device.type !== 'node') return;
        if (action === 'on') device.powerState = 'ON';
        else if (action === 'off') device.powerState = 'OFF';
        else if (action === 'reset') device.powerState = 'RESET';
      });
    });
    syncRackPowerFromNodes(props.rack);
    props.rack.slots = props.rack.slots.map(slot => ({ ...slot, devices: [...slot.devices] }));
    saveRackPowerCache();
    checkPowerStatus();
  };

  isActionLoading.value = true;

  if (nodeCount === 1) {
    console.log(`Single node detected (${nodeCount}), using standard fetch: ${url}`);
    try {
      const response = await fetch(url);
      const parsed = await readJsonApiResponse(response);
      if (parsed.kind === 'session_lost') {
        handleSessionExpired();
        return;
      }
      if (parsed.kind !== 'ok') {
        toast.error('Action failed: Request was not successful.');
        return;
      }
      const data = parsed.data as { message?: string };
      const msg =
        typeof data.message === 'string' ? data.message : String(data.message ?? '');
      if (!isPerformCommandFailureMessage(msg)) {
        handleSuccess();
      } else {
        toast.error(`Action Failed: ${msg || 'Unknown error'}`);
      }
    } catch (e) {
      console.error(e);
      toast.error("Action failed: Connection error.");
    } finally {
      isActionLoading.value = false;
    }
  } else {
    console.log(`Multi-node detected, using SSE: ${url}`);
    let isTaskCompleted = false;
    let taskFailedHandled = false;
    const sseFailedNodes = new Set<string>();
    let sawNodeResultPayload = false;

    const showBulkSuccessToasts = () => {
      const actionName = action.charAt(0).toUpperCase() + action.slice(1);
      if (hasController.value) {
        toast.success(`${actionName} action successful!\n(Controller remained ON)`);
      }
      if (hasSwitch.value) {
        toast.success(`${actionName} action successful!\n(Switch remained ON)`);
      } else if (!hasController.value) {
        toast.success(`${actionName} action successful!`);
      }
    };

    const tryApplySsePayload = (dataStr: string | null | undefined) => {
      if (dataStr == null || dataStr === '') return;
      try {
        const parsed: unknown = JSON.parse(dataStr);
        if (!isRackPowerNodeResultPayload(parsed)) return;
        sawNodeResultPayload = true;
        const { failedNodes, succeededNodes } = applyRackPowerNodeResultPayload(
          props.rack,
          parsed
        );
        failedNodes.forEach((n) => sseFailedNodes.add(n));
        succeededNodes.forEach((n) => sseFailedNodes.delete(n));
        syncRackPowerFromNodes(props.rack);
        props.rack.slots = props.rack.slots.map((slot) => ({
          ...slot,
          devices: [...slot.devices],
        }));
        saveRackPowerCache();
      } catch (err) {
        console.warn('[Rack Power SSE] Ignoring non-JSON or parse error:', err);
      }
    };

    const finishRackPowerSse = () => {
      if (sseFailedNodes.size > 0) {
        toast.warning(
          `Power action incomplete. Failed nodes: ${[...sseFailedNodes].join(', ')}`
        );
      } else if (sawNodeResultPayload) {
        showBulkSuccessToasts();
      }
      checkPowerStatus();
    };

    const source = new EventSource(url);

    const closeConnection = () => {
      source.close();
      isActionLoading.value = false;
    };

    source.addEventListener("started", (e: MessageEvent) => {
      console.log("Task started:", e.data);
      tryApplySsePayload(e.data);
    });

    source.addEventListener("update", (e: MessageEvent) => {
      console.log("Status update:", e.data);
      tryApplySsePayload(e.data);
    });

    // Default SSE event type (no `event:` line) — many backends only emit `message`.
    source.addEventListener("message", (e: MessageEvent) => {
      console.log("[Rack Power SSE] message:", e.data);
      tryApplySsePayload(e.data);
    });

    source.addEventListener("completed", (e: MessageEvent) => {
      console.log("Task completed");
      isTaskCompleted = true;
      tryApplySsePayload(e.data);
      finishRackPowerSse();
      closeConnection();
    });

    source.addEventListener("failed", (e: MessageEvent) => {
      if (isTaskCompleted) return;
      taskFailedHandled = true;
      const msg = (e.data && typeof e.data === 'string') ? e.data : (e.data?.message ?? 'Action failed.');
      console.warn("[Rack Power SSE] Failure from server event 'failed', showing toast:", msg);
      if (messageIndicatesSessionLost(msg)) {
        handleSessionExpired();
      } else {
        toast.error(`Action Failed: ${msg}`);
      }
      closeConnection();
    });
    source.addEventListener("error", (e: MessageEvent) => {
      if (isTaskCompleted) return;
      if (e.data) {
        taskFailedHandled = true;
        const msg = (typeof e.data === 'string') ? e.data : (e.data?.message ?? 'Action failed.');
        console.warn("[Rack Power SSE] Failure from server event 'error', showing toast:", msg);
        if (messageIndicatesSessionLost(msg)) {
          handleSessionExpired();
        } else {
          toast.error(`Action Failed: ${msg}`);
        }
      }
      closeConnection();
    });

    source.onerror = async () => {
      if (isTaskCompleted) {
        console.log("Connection closed after completion (Normal behavior).");
        return;
      }
      source.close();

      // Stream ended without a custom `completed` event but we already parsed node results.
      if (!taskFailedHandled && (sawNodeResultPayload || sseFailedNodes.size > 0)) {
        finishRackPowerSse();
        isTaskCompleted = true;
        isActionLoading.value = false;
        return;
      }

      console.error("[Rack Power SSE] Connection error (no server 'failed' event).");
      if (!taskFailedHandled) {
        try {
          const response = await fetch(url);
          const parsed = await readJsonApiResponse(response);
          if (parsed.kind === 'session_lost') {
            handleSessionExpired();
          } else if (parsed.kind === 'ok') {
            const data = parsed.data as { message?: string };
            const msg =
              typeof data?.message === 'string'
                ? data.message
                : String(data?.message ?? '');
            if (msg && isPerformCommandFailureMessage(msg)) {
              toast.error(`Action Failed: ${msg}`);
            } else {
              toast.error('Action failed or connection lost.');
            }
          } else {
            toast.error('Action failed or connection lost.');
          }
        } catch {
          toast.error("Action failed or connection lost.");
        }
      }
      isActionLoading.value = false;
    };
  }
};

const checkPowerStatus = async () => {
  if (isSessionExpired.value) return;
  let hasController = false;
  let hasSwitch = false;
  if (props.rack && props.rack.slots) {
    for (const slot of props.rack.slots) {
      for (const device of slot.devices) {
        if (device.type === 'controller') {
          hasController = true;
          break;
        }
        if (device.type === 'switch') {
          hasSwitch = true;
          break;
        }
      }
      if (hasController) break;
      if (hasSwitch) break;

    }
  }

  if (hasController) {
    console.log(`Controller detected in ${props.rack.name}.`);

  }
  if (hasSwitch) {
    console.log(`Switch detected in ${props.rack.name}.`);

  }

  let nodeCount = 0;
  props.rack.slots.forEach(slot => {
    slot.devices.forEach(device => {
      if (device.type === 'node') nodeCount++;
    });
  });

  if (nodeCount === 0) {
      console.log("No nodes in rack (only controller or empty), skipping API check.");
      return;
  }

  // @ts-ignore
  const baseUrl = window.APP_URL || '';
  const url = `${baseUrl}/rack_power/${props.rack.name}/status`;

  console.log(`Checking status (${nodeCount === 1 ? 'Fetch' : 'SSE'}): ${url}`);

  // --- CASE A: Single Node (Use Fetch) ---
  if (nodeCount === 1) {
    try {
      const response = await fetch(url);
      const parsed = await readJsonApiResponse(response);
      if (parsed.kind === 'session_lost') {
        handleSessionExpired();
        return;
      }
      if (parsed.kind !== 'ok') {
        if (!isSessionExpired.value) {
          toast.error('Status check failed.');
        }
        return;
      }
      const data = parsed.data as {
        status?: boolean;
        message?: Array<{ node?: string; name?: string; state?: unknown }>;
      };

      if (data.status && Array.isArray(data.message)) {
        const statusMessages = data.message;
        props.rack.slots.forEach(slot => {
          slot.devices.forEach(device => {
            const item = statusMessages.find(
              (m) => (m.node || m.name) === device.name
            );
            if (item) {
              device.powerState = parsePowerStateFromMessage(item.state ?? item);
            }
          });
        });
        syncRackPowerFromNodes(props.rack);
        // New slot refs so Vue re-renders blinking lights and power button
        props.rack.slots = props.rack.slots.map(slot => ({ ...slot, devices: [...slot.devices] }));
        saveRackPowerCache();
      }
    } catch (e) {
      console.error('[Rack Status] Single-node fetch failed:', e);
      if (isSessionExpired.value) return;
      if (fetchFailureLikelySessionRelated(e)) {
        handleSessionExpired();
      } else {
        toast.error('Status check failed.');
      }
    }
  }
  // --- CASE B: Multi Node (Use SSE) ---
  else {
    const source = new EventSource(url);
    let statusErrorHandled = false;

    const handleStatusData = (raw: any) => {
      // Normalize: backend may send { message: [ { node, state } ], status } or { node001: "ON", ... } or array
      const list: Array<{ name: string; state: string }> = [];
      if (Array.isArray(raw.message)) {
        raw.message.forEach((m: any) => list.push({ name: m.node || m.name, state: m.state ?? m }));
      } else if (Array.isArray(raw)) {
        raw.forEach((m: any) => list.push({ name: m.node || m.name, state: m.state ?? m }));
      } else if (raw && typeof raw === 'object' && !raw.message) {
        Object.entries(raw).forEach(([name, val]) => list.push({ name, state: String(val) }));
      }
      if (list.length === 0) return;
      props.rack.slots.forEach(slot => {
        slot.devices.forEach(device => {
          const item = list.find((d) => d.name === device.name);
          if (item) {
            device.powerState = parsePowerStateFromMessage(item.state);
          }
        });
      });
      syncRackPowerFromNodes(props.rack);
      // New slot refs so Vue re-renders blinking lights and power button
      props.rack.slots = props.rack.slots.map(slot => ({ ...slot, devices: [...slot.devices] }));
      saveRackPowerCache();
      source.close();
    };

    source.addEventListener("started", (e: MessageEvent) => {
      try {
          const data = JSON.parse(e.data);
          handleStatusData(data);
      } catch (err) {
          console.error("Failed to parse status data", err);
          source.close();
      }
    });

    source.addEventListener("update", (e: MessageEvent) => {
       try {
          const data = JSON.parse(e.data);
          handleStatusData(data);
      } catch (err) {
          source.close();
      }
    });

    source.addEventListener("message", (e: MessageEvent) => {
      try {
        const data = JSON.parse(e.data);
        handleStatusData(data);
      } catch {
        source.close();
      }
    });

    source.addEventListener("failed", (e: MessageEvent) => {
      statusErrorHandled = true;
      const msg = (e.data && typeof e.data === 'string') ? e.data : (e.data?.message ?? 'Status check failed.');
      if (messageIndicatesSessionLost(msg)) {
        handleSessionExpired();
      } else if (!isSessionExpired.value) {
        toast.error(`Status check failed: ${msg}`);
      }
      source.close();
    });
    source.addEventListener("error", (e: MessageEvent) => {
      if (e.data) {
        statusErrorHandled = true;
        const msg = (typeof e.data === 'string') ? e.data : (e.data?.message ?? 'Status check failed.');
        if (messageIndicatesSessionLost(msg)) {
          handleSessionExpired();
        } else if (!isSessionExpired.value) {
          toast.error(`Status check failed: ${msg}`);
        }
      }
      source.close();
    });

    source.onerror = async () => {
      if (isSessionExpired.value) {
        source.close();
        return;
      }
      if (!statusErrorHandled) {
        try {
          const response = await fetch(url);
          if (isSessionExpired.value) {
            source.close();
            return;
          }
          const parsed = await readJsonApiResponse(response);
          if (parsed.kind === 'session_lost') {
            handleSessionExpired();
          } else if (parsed.kind === 'error' && !isSessionExpired.value) {
            toast.error('Status check failed or connection lost.');
          }
        } catch (e) {
          // SSE died; fallback fetch often throws when session ends (Firefox: can't establish connection)
          if (fetchFailureLikelySessionRelated(e)) {
            handleSessionExpired();
          } else if (!isSessionExpired.value) {
            toast.error('Status check failed or connection lost.');
          }
        }
      }
      source.close();
    };
  }
};

const powerStatusIntervalId = ref<ReturnType<typeof setInterval> | null>(null);
const POWER_STATUS_INTERVAL_MS = 60 * 1000;

onMounted(() => {
  // Try to restore last known power/LED state from local cache
  applyRackPowerCache();
  checkPowerStatus();
});

watch(
  () => isDarkMode.value,
  (dark) => {
    if (powerStatusIntervalId.value) {
      clearInterval(powerStatusIntervalId.value);
      powerStatusIntervalId.value = null;
    }
    if (dark && !isSessionExpired.value) {
      powerStatusIntervalId.value = setInterval(() => checkPowerStatus(), POWER_STATUS_INTERVAL_MS);
    }
  },
  { immediate: true }
);

watch(isSessionExpired, (expired) => {
  if (expired && powerStatusIntervalId.value) {
    clearInterval(powerStatusIntervalId.value);
    powerStatusIntervalId.value = null;
  }
});

onUnmounted(() => {
  if (powerStatusIntervalId.value) {
    clearInterval(powerStatusIntervalId.value);
    powerStatusIntervalId.value = null;
  }
});

const emit = defineEmits(['drop', 'reset', 'power-toggle', 'edit-inventory']);

const toggleBack = () => {
  props.rack.showBackSide = !props.rack.showBackSide;
};

const toggleFront = () => {
  props.rack.showFrontSide = !props.rack.showFrontSide;
};

const { draggedDevice } = useDraggedDevice();
const hoveredSlot = ref<number | null>(null);
const hoveredSide = ref<'front' | 'back' | null>(null);
const conflictSlots = ref<Set<number>>(new Set());
const isDragOverRack = ref(false);

const ROW_HEIGHT_PX = 20;
const frontFrameRef = ref<HTMLElement | null>(null);
const backFrameRef = ref<HTMLElement | null>(null);

function getSlotFromEvent(event: DragEvent, side: 'front' | 'back'): number | null {
  const frameEl = side === 'front' ? frontFrameRef.value : backFrameRef.value;
  if (!frameEl || !props.rack.slots.length) return null;
  const rect = frameEl.getBoundingClientRect();
  const relativeY = event.clientY - rect.top;
  const rowIndex = Math.floor(relativeY / ROW_HEIGHT_PX);
  const clamped = Math.max(0, Math.min(rowIndex, props.rack.slots.length - 1));
  const slot = props.rack.slots[clamped];
  return slot ? slot.number : null;
}

const handleDragOver = (event: DragEvent, side: 'front' | 'back') => {
  const slotNumber = getSlotFromEvent(event, side);
  if (slotNumber == null) return;
  hoveredSlot.value = slotNumber;
  hoveredSide.value = side;

  const conflicts = new Set<number>();
  const device = draggedDevice.value;
  const height = device ? (Number(device.height) || 1) : 1;
  const ourStart = slotNumber;
  const ourEnd = slotNumber + height - 1;

  if (device && ourEnd <= props.rack.size) {
    for (const slot of props.rack.slots) {
      for (const existing of slot.devices) {
        if (existing.orientation !== side || existing.name === device.name) continue;
        const exHeight = Number(existing.height) || 1;
        const exStart = existing.position;
        const exEnd = exStart + exHeight - 1;
        const overlaps = ourStart <= exEnd && exStart <= ourEnd;
        if (!overlaps) continue;
        if (exStart === ourStart) continue;
        for (let s = Math.max(ourStart, exStart); s <= Math.min(ourEnd, exEnd); s++) {
          conflicts.add(s);
        }
      }
    }
  }
  conflictSlots.value = conflicts;
};

const handleDrop = (event: DragEvent, side: 'front' | 'back') => {
  const slotNumber = getSlotFromEvent(event, side);
  if (slotNumber != null) {
    emit('drop', event, props.rack, slotNumber, side);
  }
  clearPreview();
};

const onFrameDragEnter = () => {
  isDragOverRack.value = true;
};

const onFrameDragLeave = (event: DragEvent) => {
  const related = event.relatedTarget as Node | null;
  if (related && (frontFrameRef.value?.contains(related) || backFrameRef.value?.contains(related))) return;
  isDragOverRack.value = false;
};

const clearPreview = () => {
  hoveredSlot.value = null;
  hoveredSide.value = null;
  conflictSlots.value = new Set();
  isDragOverRack.value = false;
};
</script>

<template>
  <div class="single-rack-wrapper" @dragleave="clearPreview">
    <Teleport to="body">
      <div v-if="isActionLoading || props.isBusy" class="loader-overlay">
      <div class="spinner"></div>
      <span>Processing...</span>
    </div>
    </Teleport>
    <div class="rack-tabs">
    <div
        class="rack-tab front-label"
        :class="{ 'cursor-pointer': props.isBackViewMode }"
        @click="props.isBackViewMode ? toggleFront() : null"
      >
        {{ props.isBackViewMode ? (rack.showFrontSide ? 'HIDE FRONT' : 'SHOW FRONT') : 'FRONT' }}
      </div>

      <div
        class="rack-tab back-toggle"
        :class="{ 'cursor-pointer': !props.isBackViewMode }"
        @click="!props.isBackViewMode ? toggleBack() : null"
      >
        {{ !props.isBackViewMode ? (rack.showBackSide ? 'HIDE BACK' : 'SHOW BACK') : 'BACK' }}
      </div>
    </div>
    <div class="d-flex gap-1">

      <div class="rack-column" v-if="rack.showFrontSide !== false">

        <div class="rack-header-light position-relative">
          <div
            class="device-dark-overlay"
            :class="{ 'device-dark-overlay--inactive': !isDarkMode }"
            style="z-index: 5;"
          ></div>

          <div class="d-flex align-items-center position-relative" style="z-index: 4;">
            <span class="u-header-label">U</span>
            <span class="rack-title text-white" :title="rack.name">{{ truncatedRackName }}</span>
          </div>
          <div class="d-flex align-items-center gap-1 position-relative" style="z-index: 4;">
              <button class="btn btn-light btn-xs fw-bold reset-btn" @click="handleRackAction('reset')">RESET</button>
              <span
                class="power-btn-circle cursor-pointer"
                :class="rack.powerOn ? 'power-btn-on' : 'power-btn-off'"
                :title="powerButtonTooltip"
                @click="handleRackAction(rack.powerOn ? 'off' : 'on')"
              >
                <i class="bx bx-power-off"></i>
              </span>
              <span class="u-header-label ms-1">U</span>
            </div>
        </div>

        <div ref="frontFrameRef" class="rack-frame"
             @dragenter="onFrameDragEnter"
             @dragleave="onFrameDragLeave"
             @dragover.prevent="handleDragOver($event, 'front')"
             @drop.prevent="handleDrop($event, 'front')">
          <div
            class="device-dark-overlay"
            :class="{ 'device-dark-overlay--inactive': !isDarkMode }"
            style="z-index: 5;"
          ></div>

          <div class="rack-row" v-for="slot in rack.slots" :key="slot.number">

              <div class="rack-label">{{ slot.number }}</div>

              <div class="rack-slot d-flex align-items-start" style="position: relative; height: 100%;">
                <div v-if="hoveredSlot === slot.number && hoveredSide === 'front'" class="placement-preview"></div>
                <div v-if="conflictSlots.has(slot.number) && hoveredSide === 'front'" class="placement-preview placement-preview-conflict"></div>

               <template v-if="slot.devices.filter(d => d.orientation === 'front').length > 0">
                <div
                  class="merged-devices-wrapper flex-fill position-relative d-flex flex-column"
                  :style="{
                    pointerEvents: isDragOverRack ? 'none' : 'auto',
                    height: ((slot.devices.find(d => d.orientation === 'front')?.height ?? 1) * 20 - 2) + 'px',
                    [rack.order === 'descending' ? 'bottom' : 'top']: '0'
                  }"
                  :title="slot.devices.filter(d => d.orientation === 'front').map(d => d.name).join('\n')">
                  <div
                    v-for="(row, rowIdx) in getDeviceRowsForSlot(slot, 'front')"
                    :key="'front-' + slot.number + '-' + rowIdx"
                    class="merged-devices-row d-flex"
                    :style="{ flex: '1 1 0', minHeight: 0 }">
                    <div
                      v-for="device in row"
                      :key="'front-' + device.name + '-' + slot.number + '-' + slot.devices.filter(d => d.orientation === 'front').map(d => d.name).sort().join(',')"
                      class="merged-devices-cell position-relative"
                      :style="{ flex: `0 0 ${100 / row.length}%`, maxWidth: `${100 / row.length}%` }">
                      <div
                        class="position-absolute w-100 h-100"
                        :style="{
                          [rack.order === 'descending' ? 'bottom' : 'top']: '0',
                          zIndex: 10
                        }">
                        <template v-if="isDarkMode && !isDragOverRack">
                          <div v-for="(led, index) in getCachedDeviceLeds(device, getLedDensityKey(slot.devices.filter(d => d.orientation === 'front').length))" :key="index"
                              :class="['device-led', { 'device-led-static': !led.blinking }]"
                              :style="{
                                top: led.top, left: led.left, backgroundColor: led.color, boxShadow: '0 0 3px ' + led.color,
                                ...(led.blinking ? { animationDuration: led.animationDuration, animationDelay: led.animationDelay } : {}),
                                zIndex: 40, pointerEvents: 'none'
                              }">
                          </div>
                        </template>
                        <div
                          class="device-dark-overlay"
                          :class="{ 'device-dark-overlay--inactive': !isDarkMode }"
                        ></div>
                        <DeviceItem
                          :device="device"
                          :metric1-value="getMetric(device, metric1,true)?.value"
                          :metric1-color="getMetric(device, metric1, true)?.color"
                          :metric1-type="metric1"
                          :metric2-value="getMetric(device, metric2,true)?.value"
                          :metric2-color="getMetric(device, metric2, true)?.color"
                          :metric2-type="metric2"
                          :is-rack-view="true"
                          style="width: 100%; height: 100%; display: block;"
                          @device-right-click="handleDeviceRightClick"
                        />
                      </div>
                    </div>
                  </div>
                </div>
               </template>
            </div>
             <div class="rack-label">{{ slot.number }}</div>
          </div>
        </div>
      </div>

      <div class="rack-column" v-if="rack.showBackSide">

        <div class="rack-header-dark position-relative">

          <div
            class="device-dark-overlay"
            :class="{ 'device-dark-overlay--inactive': !isDarkMode }"
            style="z-index: 5;"
          ></div>

          <div class="d-flex align-items-center position-relative" style="z-index: 4;">
            <span class="u-header-label">U</span>
            <span class="rack-title text-white" :title="rack.name">{{ truncatedRackName }}</span>
          </div>
          <div class="d-flex align-items-center gap-1 position-relative" style="z-index: 4;">
              <template v-if="rack.showFrontSide === false">
                <button class="btn btn-light btn-xs fw-bold reset-btn" @click="handleRackAction('reset')">RESET</button>
                <span
                  class="power-btn-circle cursor-pointer"
                  :class="rack.backPowerOn ? 'power-btn-on' : 'power-btn-off'"
                  :title="powerButtonTooltip"
                  @click="handleRackAction(rack.backPowerOn ? 'off' : 'on')"
                >
                  <i class="bx bx-power-off"></i>
                </span>
              </template>
              <span class="u-header-label">U</span>
            </div>
        </div>

        <div ref="backFrameRef" class="rack-frame"
             @dragenter="onFrameDragEnter"
             @dragleave="onFrameDragLeave"
             @dragover.prevent="handleDragOver($event, 'back')"
             @drop.prevent="handleDrop($event, 'back')">
          <div
            class="device-dark-overlay"
            :class="{ 'device-dark-overlay--inactive': !isDarkMode }"
            style="z-index: 5;"
          ></div>

          <div class="rack-row" v-for="slot in rack.slots" :key="slot.number">

              <div class="rack-label">{{ slot.number }}</div> <div class="rack-slot d-flex align-items-start" style="position: relative; height: 100%; flex-grow: 1;">
                <div v-if="hoveredSlot === slot.number && hoveredSide === 'back'" class="placement-preview"></div>
                <div v-if="conflictSlots.has(slot.number) && hoveredSide === 'back'" class="placement-preview placement-preview-conflict"></div>

                <template v-if="slot.devices.filter(d => d.orientation === 'back').length > 0">
                <div
                  class="merged-devices-wrapper flex-fill position-relative d-flex flex-column"
                  :style="{
                    pointerEvents: isDragOverRack ? 'none' : 'auto',
                    height: ((slot.devices.find(d => d.orientation === 'back')?.height ?? 1) * 20 - 2) + 'px',
                    [rack.order === 'descending' ? 'bottom' : 'top']: '0'
                  }"
                  :title="slot.devices.filter(d => d.orientation === 'back').map(d => d.name).join('\n')">
                  <div
                    v-for="(row, rowIdx) in getDeviceRowsForSlot(slot, 'back')"
                    :key="'back-' + slot.number + '-' + rowIdx"
                    class="merged-devices-row d-flex"
                    :style="{ flex: '1 1 0', minHeight: 0 }">
                    <div
                      v-for="device in row"
                      :key="'back-' + device.name + '-' + slot.number + '-' + slot.devices.filter(d => d.orientation === 'back').map(d => d.name).sort().join(',')"
                      class="merged-devices-cell position-relative"
                      :style="{ flex: `0 0 ${100 / row.length}%`, maxWidth: `${100 / row.length}%` }">
                      <div
                        class="position-absolute w-100 h-100"
                        :style="{
                          [rack.order === 'descending' ? 'bottom' : 'top']: '0',
                          zIndex: 10
                        }">
                        <template v-if="isDarkMode && !isDragOverRack">
                          <div v-for="(led, index) in getCachedDeviceLeds(device, getLedDensityKey(slot.devices.filter(d => d.orientation === 'back').length))" :key="index"
                              :class="['device-led', { 'device-led-static': !led.blinking }]"
                              :style="{
                                top: led.top, left: led.left, backgroundColor: led.color, boxShadow: '0 0 3px ' + led.color,
                                ...(led.blinking ? { animationDuration: led.animationDuration, animationDelay: led.animationDelay } : {}),
                                zIndex: 40, pointerEvents: 'none'
                              }">
                          </div>
                        </template>
                        <div
                          class="device-dark-overlay"
                          :class="{ 'device-dark-overlay--inactive': !isDarkMode }"
                        ></div>
                        <DeviceItem
                          :device="device"
                          :metric1-value="getMetric(device, metric1,true)?.value"
                          :metric1-color="getMetric(device, metric1, true)?.color"
                          :metric1-type="metric1"
                          :metric2-value="getMetric(device, metric2,true)?.value"
                          :metric2-color="getMetric(device, metric2, true)?.color"
                          :metric2-type="metric2"
                          :is-rack-view="true"
                          style="width: 100%; height: 100%; display: block;"
                          @device-right-click="handleDeviceRightClick"
                        />
                      </div>
                    </div>
                  </div>
                </div>
               </template>
                </div>
              <div class="rack-label">{{ slot.number }}</div>
          </div>
        </div>
      </div>

      <Teleport to="body">
            <DeviceContextMenu
              :visible="menuVisible"
              :position="menuPos"
              :device="selectedDevice"
              @close="menuVisible = false"
              @action="handleMenuAction"
            />
          </Teleport>
    </div>
  </div>
</template>

<style scoped>

.cursor-pointer { cursor: pointer; }
.power-btn-circle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: none;
  box-shadow: none;
}
.power-btn-circle i {
  color: #fff;
  font-size: 10px;
}
.power-btn-off {
  background-color: #dc3545;
}
.power-btn-off:hover {
  background-color: #c82333;
}
.power-btn-on {
  background-color: #28a745;
}
.power-btn-on:hover {
  background-color: #218838;
}
.placement-preview {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  background-color: rgba(0, 242, 255, 0.3); border: 1px solid #00f2ff;
  box-shadow: inset 0 0 10px rgba(0, 242, 255, 0.5), 0 0 15px rgba(0, 242, 255, 0.4);
  z-index: 15;  animation: pulse-glow 1.2s infinite ease-in-out; pointer-events: none;
}
.placement-preview-conflict {
  background-color: rgba(244, 67, 54, 0.4); border: 1px solid #f44336;
  box-shadow: inset 0 0 10px rgba(244, 67, 54, 0.5), 0 0 15px rgba(244, 67, 54, 0.4);
}
.device-led-static {
  animation: none !important;
  opacity: 1;
}
@keyframes pulse-glow { 0% { opacity: 0.5; } 50% { opacity: 0.8; } 100% { opacity: 0.5; } }
.racks-container { display: flex; flex-wrap: wrap; gap: 10px; padding: 10px; overflow-x: auto; align-items: flex-end; width:100% }
.single-rack-wrapper { display: flex; flex-direction: column; flex-shrink: 0;position: relative; }
.loader-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 9999;
  background-color: rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
  font-weight: bold;
  /* backdrop-filter: blur(1px); */
}
.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f3f3;
  border-top: 5px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}
.device-dark-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.35);
  z-index: 8;
  pointer-events: none !important;
  /* backdrop-filter: blur(1px); */
}

.device-dark-overlay--inactive {
  opacity: 0;
}

.flex-fill .device-dark-overlay {
    z-index: 20;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.rack-header-light {
  background-color: var(--rack-header-bg);
  border: 2px solid var(--border-color);
  border-bottom: none;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0;
  height: 20px;
  overflow: hidden;
  color: #fff;
}
.rack-header-dark {
  background-color: #222;
  border: 2px solid #222;
  border-bottom: none;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0;
  height: 20px;
  overflow: hidden;
  color: #fff;
  z-index: 5;
}
.rack-frame {
  background: var(--rack-frame-bg);
  border: 2px solid var(--border-color);
  border-top: none;
  padding: 0;
  position: relative;

}
.rack-row {
  display: flex;
  height: 20px;
  border-bottom: 1px solid var(--border-color);
  background-color: var(--rack-slot-bg);
}
.rack-label {
  width: 20px;
  text-align: center;
  line-height: 20px;
  font-size: 11px;
  font-weight: bold;
  color: var(--rack-text);
  background-color: var(--rack-frame-bg);
  border-right: 1px solid var(--border-color);
  z-index: 3;
}
.rack-label:last-child {
  border-right: none;
  border-left: 1px solid var(--border-color);
  z-index: 5;
}
.rack-title {
  margin-left: 10px;
  font-size: 0.8rem;
  font-weight: bold;
  color: #fff !important;
}
.rack-tabs { display: flex; justify-content: space-between; margin-bottom: 0; }
.rack-tab { padding: 4px 12px; font-size: 0.5rem; font-weight: bold; color: white; text-transform: uppercase; }
.front-label { background-color: #6666ff; border-top-left-radius: 5px; border-top-right-radius: 5px; }
.back-toggle { background-color: #333; cursor: pointer; border-top-left-radius: 5px; border-top-right-radius: 5px; }
.rack-column { min-width: 180px; display: flex; flex-direction: column; flex:1; }
.u-header-label { width: 20px; text-align: center; font-size: 10px; font-weight: bold; color: #444; background-color: #e9ecef; display: inline-block; line-height: 16px; z-index: 3;}
.rack-header-dark { background-color: #222; display: flex; justify-content: space-between; align-items: center; padding: 0; height: 20px; overflow: hidden; border: 2px solid #222; border-bottom: none; }
.rack-header-light { background-color: #aaaaaa; display: flex; justify-content: space-between; align-items: center; padding: 0; height: 20px; overflow: hidden; border: 2px solid #222; border-bottom: none; }
.rack-title { margin-left: 10px; font-size: 0.8rem; font-weight: bold; }
.reset-btn { font-size: 0.55rem; padding: 1px 2px; height: 12px; line-height: 0.5; z-index: 3}
.rack-frame { background: #e9ecef; border: 2px solid #222; border-top: none; padding: 0; z-index: 5;}
.rack-row { display: flex; height: 20px; border-bottom: 1px solid #adb5bd; background-color: #fff; }
.rack-label { width: 20px; text-align: center; line-height: 20px; font-size: 11px; font-weight: bold; color: #444; background-color: #e9ecef; border-right: 1px solid #dee2e6;z-index: 3; }
.rack-label:last-child { border-right: none; border-left: 1px solid #dee2e6; z-index: 4;}
.rack-slot { flex-grow: 1; }
.merged-devices-wrapper { overflow: hidden; }
.merged-devices-cell { min-width: 0; }
</style>
