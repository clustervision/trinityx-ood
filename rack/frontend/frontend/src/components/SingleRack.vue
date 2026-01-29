<script setup lang="ts">
import DeviceItem from '@/components/DeviceItem.vue';
import DeviceContextMenu from '@/components/DeviceContextMenu.vue';
import type { Rack, Device } from '@/types/rack';
import { ref, onMounted, computed } from 'vue';
import { useToast } from 'vue-toastification';
import { useTheme } from '@/composables/useTheme';
import { useDeviceActions } from '@/composables/useDeviceActions';
import { useDraggedDevice } from '@/composables/useDraggedDevice';

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
  isActionLoading.value = true;
  try {
    const result = await executeDeviceAction(action, subAction, device);
    if (result?.success) {
      alert(result.message);
    }
  } catch {
    alert('Action failed');
  } finally {
    isActionLoading.value = false;
  }
};


const LED_COLORS = ['#28c76f', '#00cfe8', '#ff9f43', '#00e676', '#00b0ff'];

/** Node + powerState ON: blinking LEDs. Node + OFF: no LEDs. Controller/switch/no-type: always blinking LEDs. */
const getDeviceLeds = (device: Device): Array<{ left: string; top: string; color: string; animationDuration: string; animationDelay: string; blinking: boolean }> => {
  const type = (device.type || '').toLowerCase();
  const isNode = type === 'node';
  const powerOn = device.powerState === 'ON';

  if (isNode && !powerOn) return [];

  let seed = 0;
  for (let i = 0; i < device.name.length; i++) seed += device.name.charCodeAt(i);

  const rand = () => {
    const x = Math.sin(seed++) * 10000;
    return x - Math.floor(x);
  };

  const gridSlots = [8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88];
  const allLeds: Array<{ left: string; top: string; color: string; animationDuration: string; animationDelay: string; blinking: boolean }> = [];

  for (let u = 0; u < device.height; u++) {
    const countPerRow = Math.floor(rand() * 4) + 3;

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

    const rowLeds = rowSlots.map(leftPos => {
      const heightPerU = 100 / device.height;

      const baseTop = (u * heightPerU) + (heightPerU / 2);

      return {
        left: leftPos + '%',
        top: baseTop + '%',
        color: LED_COLORS[Math.floor(rand() * LED_COLORS.length)] ?? '#28c76f',
        animationDuration: (0.8 + rand() * 1.7) + 's',
        animationDelay: (rand() * 2) + 's',
        blinking: true
      };
    });

    allLeds.push(...rowLeds);
  }

  return allLeds;
};

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

const powerButtonTooltip = computed(() => {
  const baseState = props.rack.powerOn
    ? 'Power is ON (Click to Turn Off)'
    : 'Power is OFF (Click to Turn On)';

  if (hasController.value && !hasSwitch.value ) {
    return `${baseState}\n⚠️ Note: A Controller is present.\nIt will remain ON and is excluded from this action.`;
  }
  if (hasSwitch.value && !hasController.value) {
    return `${baseState}\n⚠️ Note: A Switch is present.\nIt will remain ON and is excluded from this action.`;
  }
  if (hasSwitch.value && hasController.value) {
    return `${baseState}\n⚠️ Note: Controller and Switch is present.\nThey will remain ON and is excluded from this action.`;
  }
  return baseState;
});

const handleRackAction = async (action: 'reset' | 'on' | 'off') => {
  const actionLabel = action === 'reset' ? 'Power Reset' : action === 'on' ? 'Power ON' : 'Power OFF';
  const confirmMsg =
    action === 'reset'
      ? `Power Reset all nodes on ${props.rack.name}? (Switches & Controllers ignored)`
      : `Power ${actionLabel} all nodes on ${props.rack.name}? (Switches & Controllers ignored)`;
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
    if (hasSwitch.value){
        toast.success(`${actionName} action successful!\n(Switch remained ON)`);
    }
    else {
        toast.success(`${actionName} action successful!`);
    }

    if (action === 'off') {
        props.rack.powerOn = false;
        props.rack.backPowerOn = false;
    } else if (action === 'on') {
        props.rack.powerOn = true;
        props.rack.backPowerOn = true;
    }
  };

  isActionLoading.value = true;

  if (nodeCount === 1) {
    console.log(`Single node detected (${nodeCount}), using standard fetch: ${url}`);
    try {
      const response = await fetch(url);
      const data = await response.json();
      if (data.status) {
        handleSuccess();
      } else {
        toast.error(`Action Failed: ${data.message || 'Unknown error'}`);
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
    const source = new EventSource(url);

    const closeConnection = () => {
      source.close();
      isActionLoading.value = false;
    };

    source.addEventListener("started", (e: MessageEvent) => {
      console.log("Task started:", e.data);
    });

    source.addEventListener("update", (e: MessageEvent) => {
      console.log("Status update:", e.data);
    });

    source.addEventListener("completed", () => {
      console.log("Task completed");
      isTaskCompleted = true;
      handleSuccess();
      closeConnection();
    });

    source.onerror = async (err) => {
      if (isTaskCompleted) {
        console.log("Connection closed after completion (Normal behavior).");
        return;
      }
      console.error("SSE connection error:", err);
      source.close();
      try {
          const response = await fetch(url);
          const data = await response.json();
          if (data && !data.status) {
            toast.error(`Action Failed: ${data.message}`);
          } else {
             toast.error("Action failed or connection lost.");
          }
      } catch (e) {
          toast.error("Action failed or connection lost.");
      }
      isActionLoading.value = false;
    };
  }
};

const checkPowerStatus = async () => {
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
      const data = await response.json();

      if (data.status && Array.isArray(data.message)) {
        const isAnyDeviceOn = data.message.some((item: any) =>
          item.state && item.state.toUpperCase() === 'ON'
        );

        props.rack.powerOn = isAnyDeviceOn;
        props.rack.backPowerOn = isAnyDeviceOn;
      }
    } catch (e) {
      console.error("Single node status check failed:", e);
    }
  }
  // --- CASE B: Multi Node (Use SSE) ---
  else {
    const source = new EventSource(url);

    const handleStatusData = (data: any) => {
      console.log("Initial status received:", data);
          console.log("Status received:", data);
      props.rack.slots.forEach(slot => {
        slot.devices.forEach(device => {


          const deviceStatus = Array.isArray(data)
              ? data.find((d: any) => d.name === device.name)
              : data[device.name];


          if (deviceStatus) {
             const isOn = (deviceStatus.state || deviceStatus).toUpperCase() === 'ON';
             device.powerState = isOn ? 'ON' : 'OFF';
          }
        });
      });
      const values = Object.values(data);
      const isAnyDeviceOn = values.some((val: any) =>
         typeof val === 'string' && val.toUpperCase() === 'ON'
      );

      props.rack.powerOn = isAnyDeviceOn;
      props.rack.backPowerOn = isAnyDeviceOn;
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

    source.onerror = (err) => {
      source.close();
    };
  }
};

onMounted(() => {
  checkPowerStatus();
});

const emit = defineEmits(['drop', 'reset', 'power-toggle']);

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
          <div v-if="isDarkMode" class="device-dark-overlay" style="z-index: 5;"></div>

          <div class="d-flex align-items-center position-relative" style="z-index: 4;">
            <span class="u-header-label">U</span>
            <span class="rack-title text-white">{{ rack.name }}</span>
          </div>
          <div class="d-flex align-items-center gap-1 position-relative" style="z-index: 4;">
              <button class="btn btn-light btn-xs fw-bold reset-btn" @click="handleRackAction('reset')">RESET</button>
              <i class='bx bx-power-off cursor-pointer'
                :class="rack.powerOn ? 'text-danger' : 'text-success'"
                :title="powerButtonTooltip"
                @click="handleRackAction(rack.powerOn ? 'off' : 'on')">
              </i>
              <span class="u-header-label ms-1">U</span>
            </div>
        </div>

        <div ref="frontFrameRef" class="rack-frame"
             @dragenter="onFrameDragEnter"
             @dragleave="onFrameDragLeave"
             @dragover.prevent="handleDragOver($event, 'front')"
             @drop.prevent="handleDrop($event, 'front')">
          <div v-if="isDarkMode" class="device-dark-overlay" style="z-index: 5; pointer-events: none;"></div>

          <div class="rack-row" v-for="slot in rack.slots" :key="slot.number">

              <div class="rack-label">{{ slot.number }}</div>

              <div class="rack-slot d-flex align-items-start" style="position: relative; height: 100%;">
                <div v-if="hoveredSlot === slot.number && hoveredSide === 'front'" class="placement-preview"></div>
                <div v-if="conflictSlots.has(slot.number) && hoveredSide === 'front'" class="placement-preview placement-preview-conflict"></div>

               <div v-for="device in slot.devices.filter(d => d.orientation === 'front')" :key="device.name"
                class="flex-fill h-100 position-relative"
                :style="{ pointerEvents: isDragOverRack ? 'none' : 'auto' }">

                <div class="position-absolute w-100"
                    :style="{
                        height: (device.height * 20 - 2) + 'px',
                        [rack.order === 'descending' ? 'bottom' : 'top']: '0',
                        zIndex: 10
                    }"
                    :title="isDarkMode ? device.name : undefined">
                    <template v-if="isDarkMode">
                        <div v-for="(led, index) in getDeviceLeds(device)" :key="index"
                            :class="['device-led', { 'device-led-static': !led.blinking }]"
                            :style="{
                              top: led.top, left: led.left, backgroundColor: led.color, boxShadow: '0 0 3px ' + led.color,
                              ...(led.blinking ? { animationDuration: led.animationDuration, animationDelay: led.animationDelay } : {}),
                              zIndex: 40, pointerEvents: 'none'
                            }">
                        </div>
                    </template>
                    <div v-if="isDarkMode" class="device-dark-overlay"style="pointer-events: none;"></div>
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
             <div class="rack-label">{{ slot.number }}</div>
          </div>
        </div>
      </div>

      <div class="rack-column" v-if="rack.showBackSide">

        <div class="rack-header-dark position-relative">

          <div v-if="isDarkMode" class="device-dark-overlay" style="z-index: 5;"></div>

          <div class="d-flex align-items-center position-relative" style="z-index: 4;">
            <span class="u-header-label">U</span>
            <span class="rack-title text-white">{{ rack.name }}</span>
          </div>
          <div class="d-flex align-items-center gap-1 position-relative" style="z-index: 4;">
              <template v-if="rack.showFrontSide === false">
                <button class="btn btn-light btn-xs fw-bold reset-btn" @click="handleRackAction('reset')">RESET</button>
                <i class='bx bx-power-off cursor-pointer'
                  :class="rack.backPowerOn ? 'text-danger' : 'text-success'"
                  :title="powerButtonTooltip"
                  @click="handleRackAction(rack.powerOn ? 'off' : 'on')">
                </i>
              </template>
              <span class="u-header-label">U</span>
            </div>
        </div>

        <div ref="backFrameRef" class="rack-frame"
             @dragenter="onFrameDragEnter"
             @dragleave="onFrameDragLeave"
             @dragover.prevent="handleDragOver($event, 'back')"
             @drop.prevent="handleDrop($event, 'back')">
          <div v-if="isDarkMode" class="device-dark-overlay" style="z-index: 5; pointer-events: none;"></div>

          <div class="rack-row" v-for="slot in rack.slots" :key="slot.number">

              <div class="rack-label">{{ slot.number }}</div> <div class="rack-slot d-flex align-items-start" style="position: relative; height: 100%; flex-grow: 1;">
                <div v-if="hoveredSlot === slot.number && hoveredSide === 'back'" class="placement-preview"></div>
                <div v-if="conflictSlots.has(slot.number) && hoveredSide === 'back'" class="placement-preview placement-preview-conflict"></div>

                <div v-for="device in slot.devices.filter(d => d.orientation === 'back')"
                    :key="device.name"
                    class="flex-fill h-100 position-relative"
                    :style="{ pointerEvents: isDragOverRack ? 'none' : 'auto' }">

                    <div class="position-absolute w-100"
                        :style="{
                            height: (device.height * 20 - 2) + 'px',
                            [rack.order === 'descending' ? 'bottom' : 'top']: '0',
                            zIndex: 10
                        }"
                        :title="isDarkMode ? device.name : undefined">

                        <template v-if="isDarkMode">
                            <div v-for="(led, index) in getDeviceLeds(device)" :key="index"
                                :class="['device-led', { 'device-led-static': !led.blinking }]"
                                :style="{
                                  top: led.top, left: led.left, backgroundColor: led.color, boxShadow: '0 0 3px ' + led.color,
                                  ...(led.blinking ? { animationDuration: led.animationDuration, animationDelay: led.animationDelay } : {}),
                                  zIndex: 40, pointerEvents: 'none'
                                }">
                            </div>
                        </template>
                        <div v-if="isDarkMode" class="device-dark-overlay" style="pointer-events: none;"></div>
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
</style>
