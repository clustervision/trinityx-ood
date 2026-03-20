<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import axios from 'axios';
import RackMetricsHeader from '@/components/RackMetricsHeader.vue';
import SingleRack from '@/components/SingleRack.vue';
import { useToast } from "vue-toastification";
import { useRack} from '@/composables/useRack';
import { useRackMetrics } from '../composables/useRackMetrics';
import type { Rack } from '@/types/rack';
import { useTheme } from '@/composables/useTheme';
import switchOnImg from '@/assets/img/Switch-on.png';
import switchOffImg from '@/assets/img/Switch-off.png';
import switchMiddleImg from '@/assets/img/Switch-middle.png';

const { isDarkMode, toggleTheme, setTheme } = useTheme();
const lightSwitchAnimating = ref(false);

const onLightSwitchClick = () => {
  lightSwitchAnimating.value = true;
  toggleTheme();
  setTimeout(() => {
    lightSwitchAnimating.value = false;
  }, 40);
};

const emit = defineEmits(['rack-updated', 'device-taken', 'pool-updated', 'edit-inventory']);

const onEditInventory = (device: { name: string }) => {
  emit('edit-inventory', device.name);
};
const toast = useToast();
const racks = ref<Rack[]>([]);
const { fetchSingleRack, handleRackDrop, syncRackPowerFromNodes } = useRack();
const { metric1, metric2, metric1Range, metric2Range, getMetricForDevice } = useRackMetrics();
const loadingRackName = ref('');

// @ts-expect-error APP_URL is injected globally at runtime
const Url = window.APP_URL;
const isBackViewMode = ref(false);

const RACK_ZOOM_SCALE = 1.6;
const rackZoomActive = ref(false);
const rackZoomPanX = ref(0);
const rackZoomPanY = ref(0);
const rackZoomPanning = ref(false);
let rackZoomPanGrabX = 0;
let rackZoomPanGrabY = 0;
let rackZoomPanStartX = 0;
let rackZoomPanStartY = 0;

const rackZoomInnerStyle = computed(() => {
  if (!rackZoomActive.value) return undefined;
  return {
    transform: `translate(${rackZoomPanX.value}px, ${rackZoomPanY.value}px) scale(${RACK_ZOOM_SCALE})`,
    transformOrigin: '0 0' as const,
  };
});

const isRackZoomPanBlockedTarget = (target: EventTarget | null) => {
  if (!target || !(target instanceof Element)) return false;
  return !!target.closest(
    'button, a, input, select, textarea, [role="button"], .dropdown-menu, .dropdown-toggle, .dropdown-item, .power-btn-circle, .reset-btn'
  );
};

const toggleRackZoom = () => {
  rackZoomActive.value = !rackZoomActive.value;
  if (!rackZoomActive.value) {
    rackZoomPanX.value = 0;
    rackZoomPanY.value = 0;
    rackZoomPanning.value = false;
  }
};

const onRackZoomViewportMouseDown = (e: MouseEvent) => {
  if (!rackZoomActive.value || e.button !== 0) return;
  if (isRackZoomPanBlockedTarget(e.target)) return;
  rackZoomPanning.value = true;
  rackZoomPanGrabX = e.clientX;
  rackZoomPanGrabY = e.clientY;
  rackZoomPanStartX = rackZoomPanX.value;
  rackZoomPanStartY = rackZoomPanY.value;
  e.preventDefault();
};

const onWindowRackZoomMouseMove = (e: MouseEvent) => {
  if (!rackZoomPanning.value) return;
  rackZoomPanX.value = rackZoomPanStartX + (e.clientX - rackZoomPanGrabX);
  rackZoomPanY.value = rackZoomPanStartY + (e.clientY - rackZoomPanGrabY);
};

const onWindowRackZoomMouseUp = () => {
  rackZoomPanning.value = false;
};

const toggleGlobalView = () => {
  isBackViewMode.value = !isBackViewMode.value;
  racks.value.forEach(rack => {
    if (isBackViewMode.value) {
      rack.showFrontSide = false;
      rack.showBackSide = true;
    } else {
      rack.showFrontSide = true;
      rack.showBackSide = false;
    }
  });
};


const loadRacks = async () => {
  try {
    const t = new Date().getTime();
    const response = await axios.get(`${Url}/manage_racks?t=${t}`);
    const rawMsg = response.data.message as unknown;

    if (rawMsg) {
      let flatList: Rack[] = [];
      if (Array.isArray(rawMsg)) {
        rawMsg.forEach((item: unknown) => {
          const rec = item as Rack | Record<string, Rack>;
          if ((rec as Rack).name && (rec as Rack).size) flatList.push(rec as Rack);
          else flatList.push(...Object.values(rec as Record<string, Rack>));
        });
      } else {
        flatList = Object.values(rawMsg as Record<string, Rack>);
      }

      const currentStates = new Map(racks.value.map(r => [r.name, r.showBackSide]));
      const parsedRacks = await Promise.all(flatList.map(async (r) => {
          const fullRack = await fetchSingleRack(r.name);

          fullRack.showBackSide = currentStates.get(r.name) || false;
          return fullRack;
      }));

      racks.value = parsedRacks;
    }
  } catch (error: unknown) {
    console.error("Failed to load racks:", error);
  }
};

const resetRack = async (targetRack: Rack, side: 'front' | 'back') => {
  if (!confirm(`Power Reset all nodes on ${targetRack.name} ${side} side? (Switches & Controllers ignored)`)) return;
  loadingRackName.value = targetRack.name;


  const nodesToReset: Rack['slots'][number]['devices'][number][] = [];
  targetRack.slots.forEach((slot) => {
    slot.devices.forEach((device) => {

      if (device.orientation === side &&
          device.type !== 'switch' &&
          device.type !== 'controller') {
        nodesToReset.push(device);
      }
    });
  });

  if (nodesToReset.length === 0) {
    toast.info(`No eligible nodes found on ${side} side.`);
    return;
  }

  try {
    let successCount = 0;
    let failCount = 0;

    await Promise.all(nodesToReset.map(async (dev) => {
      try {

        await axios.get(`${Url}/perform/power/reset/${dev.name}`);
        successCount++;
      } catch (e) {
        console.error(`Failed to reset ${dev.name}`, e);
        failCount++;
      }
    }));

    if (successCount > 0) toast.success(`Power reset signal sent to ${successCount} nodes.`);
    if (failCount > 0) toast.warning(`Failed to reset ${failCount} nodes.`);

  } catch (e: unknown) {
    console.error("Batch reset failed", e);
    toast.error("An error occurred during batch reset.");
  }
  finally{
      loadingRackName.value = '';
    }
};

// Add this function inside <script setup>

const handlePowerToggle = async (targetRack: Rack, side: 'front' | 'back') => {
  const isCurrentlyOn = side === 'front' ? targetRack.powerOn : targetRack.backPowerOn;
  const action = isCurrentlyOn ? 'off' : 'on';

  if (!confirm(`Power ${action.toUpperCase()} all nodes on ${targetRack.name} ${side} side?`)) return;
  loadingRackName.value = targetRack.name;

  const nodesToToggle: Rack['slots'][number]['devices'][number][] = [];
  targetRack.slots.forEach((slot) => {
    slot.devices.forEach((device) => {
      if (device.orientation === side &&
          device.type !== 'switch' &&
          device.type !== 'controller') {
        nodesToToggle.push(device);
      }
    });
  });

  if (nodesToToggle.length === 0) {
    toast.info(`No eligible nodes found on ${side} side.`);
    loadingRackName.value = '';
    return;
  }

  // 1. Set Loading for THIS rack
  loadingRackName.value = targetRack.name;

  try {
    let successCount = 0;
    await Promise.all(nodesToToggle.map(async (dev) => {
      try {
        await axios.get(`${Url}/perform/power/${action}/${dev.name}`);
        successCount++;
      } catch (e) { console.error(e); }
    }));

    if (successCount > 0) {
      toast.success(`Power ${action} sent to ${successCount} nodes.`);
      // Update local state visually
      if (side === 'front') targetRack.powerOn = !isCurrentlyOn;
      else targetRack.backPowerOn = !isCurrentlyOn;
    }
  } catch (e: unknown) {
    console.error(e);
    toast.error("Batch power failed");
  } finally {
    // 2. Clear Loading
    loadingRackName.value = '';
  }
};


const onDrop = (event: DragEvent, targetRack: Rack, u: number, side: 'front' | 'back') => {
  handleRackDrop(
    event,
    targetRack,
    u,
    side,
    (nameOrNames: string | string[]) => {
      const names = Array.isArray(nameOrNames) ? nameOrNames : [nameOrNames];
      names.forEach((deviceName) => {
        emit('device-taken', deviceName);
        racks.value.forEach((r) => {
          if (r.name !== targetRack.name) {
            r.slots.forEach((slot) => {
              slot.devices = slot.devices.filter((d) => d.name !== deviceName);
            });
            syncRackPowerFromNodes(r);
          }
        });
      });
      // Do not emit('pool-updated') here: it triggers loadRacks() which refetches all racks
      // and overwrites device.powerState (backend show_rack often has no power state), so all LEDs and power buttons go OFF.
    },
    () => {

       loadRacks();
    }
  );
};

defineExpose({ loadRacks });
onMounted(() => {
  loadRacks();
  window.addEventListener('mousemove', onWindowRackZoomMouseMove);
  window.addEventListener('mouseup', onWindowRackZoomMouseUp);
});
onUnmounted(() => {
  window.removeEventListener('mousemove', onWindowRackZoomMouseMove);
  window.removeEventListener('mouseup', onWindowRackZoomMouseUp);
  setTheme(false);
});
</script>

<template>
  <div class="container-fluid flex-grow-1 container-p-y">
    <div class="card-body position-relative rack-view-header-wrap">
      <RackMetricsHeader
        v-model:metric1="metric1"
        v-model:metric2="metric2"
        :range1="metric1Range"
        :range2="metric2Range"
        @refresh="loadRacks"
      >
        <template #right>
          <span
            class="light-switch-btn"
            :title="isDarkMode ? 'Light Off (click to turn on blinking)' : 'Light On (click to turn off blinking)'"
            @click="onLightSwitchClick"
          >
            <img
              :src="lightSwitchAnimating ? switchMiddleImg : (isDarkMode ? switchOffImg : switchOnImg)"
              :alt="isDarkMode ? 'Light Off' : 'Light On'"
              class="light-switch-img"
            />
          </span>
        </template>
        <template #zoom>
          <button
            type="button"
            class="btn rack-zoom-toggle-btn"
            :title="rackZoomActive ? 'Zoom out (drag rack area to pan when zoomed)' : 'Zoom in (drag rack area to pan)'"
            @click="toggleRackZoom"
          >
            {{ rackZoomActive ? 'Zoom out' : 'Zoom in' }}
          </button>
        </template>
        <template #bottom>
          <button
            class="btn flip-view-btn"
            :class="isBackViewMode ? 'btn-custom-grey' : 'btn-dark'"
            @click="toggleGlobalView"
          >
            {{ isBackViewMode ? 'Flip to Front View' : 'Flip to Back View' }}
          </button>
        </template>
      </RackMetricsHeader>
      <div class="card-body rack-view-racks" :class="{ 'rack-view-dark': isDarkMode }" >
        <div
          class="rack-zoom-viewport"
          :class="{ 'rack-zoom-viewport--active': rackZoomActive }"
          @mousedown="onRackZoomViewportMouseDown"
        >
          <div
            class="rack-zoom-inner"
            :class="{ 'rack-zoom-inner--scaled': rackZoomActive }"
            :style="rackZoomInnerStyle"
          >
            <div class="racks-container">
              <SingleRack
                v-for="rack in racks"
                :key="rack.name"
                :rack="rack"
                :metric1="metric1"
                :metric2="metric2"
                :get-metric="getMetricForDevice"
                :is-back-view-mode="isBackViewMode"
                @drop="onDrop"
                @reset="resetRack"
                @power-toggle="handlePowerToggle"
                @edit-inventory="onEditInventory"
                :is-busy="loadingRackName === rack.name"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.rack-view-header-wrap {
  overflow: visible;
}

.rack-view-racks {
  margin-top: 10px;
}

.rack-zoom-viewport {
  width: 100%;
}

.rack-zoom-viewport--active {
  overflow: hidden;
  min-height: min(70vh, 900px);
  cursor: grab;
  border-radius: 6px;
  user-select: none;
}

.rack-zoom-viewport--active:active {
  cursor: grabbing;
}

.rack-zoom-inner--scaled {
  will-change: transform;
}

.racks-container { display: flex;flex-wrap: wrap; gap: 10px; padding: 10px; overflow-x: auto; align-items: flex-end; width:100% }
.btn-custom-grey {
  background-color: #d3d3d3;
  border-color: #c0c0c0;
  color: #000;
}

.btn-custom-grey:hover {
  background-color: #bebebe;
}

.rack-zoom-toggle-btn {
  background-color: #8692a4;
  border-color: #8692a4;
  color: #fff;
  height: 38px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 14px;
  font-weight: normal;
  padding: 0.375rem 0.75rem;
  border-radius: 5px;
  box-shadow: none;
}

.rack-zoom-toggle-btn:hover {
  background-color: #778496;
  border-color: #778496;
  color: #fff;
}

.rack-zoom-toggle-btn:focus {
  color: #fff;
  box-shadow: 0 0 0 0.2rem rgba(134, 146, 164, 0.35);
}

.flip-view-btn {
  min-width: 200px;
  max-width: 100%;
  height: 38px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 14px;
  font-weight: normal;
  padding: 0.375rem 0.75rem;
  white-space: normal;
  border-radius: 5px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: none;
}

.light-switch-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  width: 86px;
  padding: 0;
  margin: 0;
  margin-right: -16px;
  border: none;
  background: transparent;
  cursor: pointer;
  transition: transform 0.1s ease;
  flex-shrink: 0;
}

.light-switch-btn:hover {
  transform: scale(1.05);
}

.light-switch-img {
  height: 100%;
  width: auto;
  max-height: 86px;
  max-width: 86px;
  object-fit: contain;
  display: block;
  transition: opacity 0.08s ease;
}

.light-switch-btn:active .light-switch-img {
  opacity: 0.9;
}
</style>
