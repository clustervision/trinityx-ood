<script setup lang="ts">
import DeviceItem from '@/components/DeviceItem.vue';
import DeviceContextMenu from '@/components/DeviceContextMenu.vue';
import type { Rack, Device } from '@/types/rack';
import axios from 'axios';
import { ref } from 'vue';

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
const isActionLoading = ref(false);
const menuVisible = ref(false);
const menuPos = ref({ x: 0, y: 0 });
const selectedDevice = ref<Device | null>(null);
const handleDeviceRightClick = (event: MouseEvent, device: Device) => {
  event.preventDefault();


  console.log("Opening menu for:", device.name);

  selectedDevice.value = device;
  menuPos.value = { x: event.clientX, y: event.clientY };
  menuVisible.value = true;
};

const handleMenuAction = async (payload: { action: string, subAction?: string, device: Device }) => {
  const { action, subAction, device } = payload;
  //@ts-ignore
  const baseUrl = window.CONTEXT_URL;
  //@ts-ignore
  const Url = window.APP_URL;

  // 1. URL Navigation Actions
  if (['details', 'edit', 'rename', 'clone'].includes(action)) {
    let route = '';
    const typeMap: Record<string, string> = {
      'node': 'trinity_node',
      'switch': 'trinity_switch',
      'controller': 'trinity_cluster',
      'otherdevices': 'trinity_otherdev'
    };

    const section = typeMap[device.type] || 'trinity_node';

    if (device.type === 'controller') {
      // Special case for Controller
      if (action === 'details') route = `${baseUrl}/${section}/`; // Ends with slash, no "show", no name
      if (action === 'edit') route = `${baseUrl}/${section}/edit`; // Ends with edit, no name
    } else {
      // Standard logic for other devices
      if (action === 'details') route = `${baseUrl}/${section}/show/${device.name}`;
      if (action === 'edit') route = `${baseUrl}/${section}/edit/${device.name}`;
      if (action === 'rename') route = `${baseUrl}/${section}/rename/${device.name}`;
      if (action === 'clone') route = `${baseUrl}/${section}/clone/${device.name}`;
    }

    if (route) window.open(route, '_blank')?.focus();
  }

  // 2. API Actions (Power / IPMI)
  if (['power', 'sel', 'chassis'].includes(action)) {
    console.log(`Executing ${action} - ${subAction} on ${device.name}`);
    isActionLoading.value = true;
    try {

      const response = await axios.get(`${Url}perform/${action}/${subAction}/${device.name}`);
       alert(response.data.message || `Command sent: ${subAction}`);
    } catch (e) {
      console.error(e);
      alert('Action failed');
    }
    finally{
      isActionLoading.value = false;
    }
  }
};
const emit = defineEmits(['drop', 'reset', 'power-toggle']);

const toggleBack = () => {
  props.rack.showBackSide = !props.rack.showBackSide;
};

const toggleFront = () => {
  props.rack.showFrontSide = !props.rack.showFrontSide;
};

const hoveredSlot = ref<number | null>(null);
const hoveredSide = ref<'front' | 'back' | null>(null);

const handleDragOver = (uNumber: number, side: 'front' | 'back') => {
  hoveredSlot.value = uNumber;
  hoveredSide.value = side;
};

const clearPreview = () => {
  hoveredSlot.value = null;
  hoveredSide.value = null;
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
        <div class="rack-header-light">
          <div class="d-flex align-items-center">
            <span class="u-header-label">U</span>
            <span class="rack-title text-white">{{ rack.name }}</span>
          </div>
          <div class="d-flex align-items-center gap-1 ">
            <button class="btn btn-light btn-xs fw-bold reset-btn" @click="$emit('reset', rack, 'front')">RESET</button>
           <i class='bx bx-power-off cursor-pointer'
              :class="rack.powerOn ? 'text-success' : 'text-danger'"
              @click="$emit('power-toggle', rack, 'front')">
            </i>
            <span class="u-header-label ms-1">U</span>
          </div>
        </div>

        <div class="rack-frame">
          <div class="rack-row" v-for="slot in rack.slots" :key="slot.number"
               @drop="$emit('drop', $event, rack, slot.number, 'front'); clearPreview()"
               @dragover.prevent="handleDragOver(slot.number, 'front')">
              <div class="rack-label">{{ slot.number }}</div>

              <div class="rack-slot d-flex align-items-start" style="position: relative; height: 100%;">
                <div v-if="hoveredSlot === slot.number && hoveredSide === 'front'" class="placement-preview"></div>

                <div v-for="device in slot.devices.filter(d => d.orientation === 'front')" :key="device.name" class="flex-fill h-100 position-relative">
                  <DeviceItem
                    :device="device"
                    :metric1-value="getMetric(device, metric1,true)?.value"
                    :metric1-color="getMetric(device, metric1, true)?.color"
                    :metric1-type="metric1"
                    :metric2-value="getMetric(device, metric2,true)?.value"
                    :metric2-color="getMetric(device, metric2, true)?.color"
                    :metric2-type="metric2"
                    :is-rack-view="true"
                    style="position: absolute; width: 100%;"
                    :style="{ height: (device.height * 20 - 2) + 'px', [rack.order === 'descending' ? 'bottom' : 'top']: '0' }"
                    @device-right-click="handleDeviceRightClick"
                  />
                </div>
              </div>
              <div class="rack-label">{{ slot.number }}</div>
          </div>
        </div>
      </div>

      <div class="rack-column" v-if="rack.showBackSide">
        <div class="rack-header-dark">
          <div class="d-flex align-items-center">
            <span class="u-header-label">U</span>
            <span class="rack-title text-white">{{ rack.name }}</span>
          </div>
          <div class="d-flex align-items-center gap-1">
            <button class="btn btn-light btn-xs fw-bold reset-btn" @click="$emit('reset', rack, 'back')">RESET</button>
            <i class='bx bx-power-off cursor-pointer'
              :class="rack.backPowerOn ? 'text-success' : 'text-danger'"
              @click="$emit('power-toggle', rack, 'back')">
            </i>
            <span class="u-header-label">U</span>
          </div>
        </div>

        <div class="rack-frame">
          <div class="rack-row" v-for="slot in rack.slots" :key="slot.number"
               @drop="$emit('drop', $event, rack, slot.number, 'back'); clearPreview()"
               @dragover.prevent="handleDragOver(slot.number, 'back')">
              <div class="rack-label">{{ slot.number }}</div>

              <div class="rack-slot d-flex align-items-start" style="position: relative; height: 100%; flex-grow: 1;">
                <div v-if="hoveredSlot === slot.number && hoveredSide === 'back'" class="placement-preview"></div>

                <div v-for="device in slot.devices.filter(d => d.orientation === 'back')" :key="device.name" class="flex-fill h-100 position-relative">
                  <DeviceItem
                    :device="device"
                    :metric1-value="getMetric(device, metric1,true)?.value"
                    :metric1-color="getMetric(device, metric1, true)?.color"
                    :metric1-type="metric1"
                    :metric2-value="getMetric(device, metric2,true)?.value"
                    :metric2-color="getMetric(device, metric2, true)?.color"
                    :metric2-type="metric2"
                    :is-rack-view="true"
                    style="position: absolute; width: 100%;"
                    :style="{ height: (device.height * 20 - 2) + 'px', [rack.order === 'descending' ? 'bottom' : 'top']: '0' }"
                    @device-right-click="handleDeviceRightClick"
                  />
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
    </div> </div>
</template>

<style scoped>

.cursor-pointer { cursor: pointer; }


.placement-preview {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  background-color: rgba(0, 242, 255, 0.3); border: 1px solid #00f2ff;
  box-shadow: inset 0 0 10px rgba(0, 242, 255, 0.5), 0 0 15px rgba(0, 242, 255, 0.4);
  z-index: 5; pointer-events: none; animation: pulse-glow 1.2s infinite ease-in-out;
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

  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
  font-weight: bold;
  backdrop-filter: blur(2px);
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
}

.rack-frame {
  background: var(--rack-frame-bg);
  border: 2px solid var(--border-color);
  border-top: none;
  padding: 0;
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
}

.rack-label:last-child {
  border-right: none;
  border-left: 1px solid var(--border-color);
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
.u-header-label { width: 20px; text-align: center; font-size: 10px; font-weight: bold; color: #444; background-color: #e9ecef; display: inline-block; line-height: 16px; }
.rack-header-dark { background-color: #222; display: flex; justify-content: space-between; align-items: center; padding: 0; height: 20px; overflow: hidden; border: 2px solid #222; border-bottom: none; }
.rack-header-light { background-color: #aaaaaa; display: flex; justify-content: space-between; align-items: center; padding: 0; height: 20px; overflow: hidden; border: 2px solid #222; border-bottom: none; }
.rack-title { margin-left: 10px; font-size: 0.8rem; font-weight: bold; }
.reset-btn { font-size: 0.55rem; padding: 1px 2px; height: 12px; line-height: 0.5; }
.rack-frame { background: #e9ecef; border: 2px solid #222; border-top: none; padding: 0; }
.rack-row { display: flex; height: 20px; border-bottom: 1px solid #adb5bd; background-color: #fff; }
.rack-label { width: 20px; text-align: center; line-height: 20px; font-size: 11px; font-weight: bold; color: #444; background-color: #e9ecef; border-right: 1px solid #dee2e6; }
.rack-label:last-child { border-right: none; border-left: 1px solid #dee2e6; }
.rack-slot { flex-grow: 1; }
</style>
