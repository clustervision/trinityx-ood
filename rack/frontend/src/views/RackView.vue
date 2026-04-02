<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import axios from 'axios';
import RackMetricsHeader from '@/components/RackMetricsHeader.vue';
import SingleRack from '@/components/SingleRack.vue';
import { useToast } from "vue-toastification";
import { useRack} from '@/composables/useRack';
import { useRackMetrics } from '../composables/useRackMetrics';
import type { Rack } from '@/types/rack';
import { useTheme } from '@/composables/useTheme';
import { collectRackDeviceImageUrls, preloadImageUrls } from '@/utils/deviceImageUrls';
import switchOnImg from '@/assets/img/switch-on.png';
import switchOffImg from '@/assets/img/switch-off.png';

const { isDarkMode, toggleTheme, setTheme } = useTheme();

const onLightSwitchClick = () => {
  toggleTheme();
};

function preloadLightSwitchImages() {
  for (const url of [switchOnImg, switchOffImg]) {
    const img = new Image();
    img.src = url;
  }
}

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

const rackFullscreenEl = ref<HTMLElement | null>(null);
const rackIsFullscreen = ref(false);

const RACK_ZOOM_LEVEL = 2;
const rackViewZoom = ref(1);
const rackZoomMagnified = computed(() => rackViewZoom.value >= RACK_ZOOM_LEVEL);

const toggleRackZoom = () => {
  rackViewZoom.value = rackViewZoom.value >= RACK_ZOOM_LEVEL ? 1 : RACK_ZOOM_LEVEL;
};

const syncRackFullscreenState = () => {
  rackIsFullscreen.value = document.fullscreenElement === rackFullscreenEl.value;
};

const toggleRackFullscreen = async () => {
  const el = rackFullscreenEl.value;
  if (!el) return;
  try {
    if (document.fullscreenElement === el) {
      await document.exitFullscreen();
    } else {
      await el.requestFullscreen();
    }
  } catch (e) {
    console.error(e);
    toast.error('Fullscreen is not available in this browser or was blocked.');
  }
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
      preloadImageUrls(collectRackDeviceImageUrls(parsedRacks));
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
  preloadLightSwitchImages();
  loadRacks();
  document.addEventListener('fullscreenchange', syncRackFullscreenState);
});
onUnmounted(async () => {
  document.removeEventListener('fullscreenchange', syncRackFullscreenState);
  if (document.fullscreenElement === rackFullscreenEl.value) {
    try {
      await document.exitFullscreen();
    } catch {
      /* ignore */
    }
  }
  setTheme(false);
});
</script>

<template>
  <!-- pt-2 opts out of container-p-y top (core.css) so metrics sit higher; bottom padding unchanged -->
  <div class="container-fluid flex-grow-1 container-p-y pt-2">
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
              v-show="!isDarkMode"
              :src="switchOnImg"
              alt="Light On"
              class="light-switch-img"
              loading="eager"
            />
            <img
              v-show="isDarkMode"
              :src="switchOffImg"
              alt="Light Off"
              class="light-switch-img"
              loading="eager"
            />
          </span>
        </template>
        <template #fullscreen>
          <button
            type="button"
            class="btn rack-fullscreen-btn"
            :title="rackIsFullscreen ? 'Exit fullscreen (Esc)' : 'Fullscreen rack view'"
            @click="toggleRackFullscreen"
          >
            {{ rackIsFullscreen ? 'Exit Full Screen' : 'Full Screen' }}
          </button>
        </template>
        <template #zoom>
          <button
            type="button"
            class="btn rack-zoom-btn"
            :class="{ 'rack-zoom-btn-on': rackZoomMagnified }"
            :title="rackZoomMagnified ? 'Zoom out (1×)' : 'Zoom in (2×)'"
            :aria-pressed="rackZoomMagnified"
            aria-label="Toggle rack zoom 2×"
            @click="toggleRackZoom"
          >
            <i class="bx bx-search" aria-hidden="true"></i>
          </button>
        </template>
        <template #bottom>
          <button type="button" class="btn flip-view-btn" @click="toggleGlobalView">
            {{ isBackViewMode ? 'Flip to Front view' : 'Flip to Back view' }}
          </button>
        </template>
      </RackMetricsHeader>
      <div
        ref="rackFullscreenEl"
        class="card-body rack-view-racks"
        :class="{ 'rack-view-dark': isDarkMode }"
      >
        <div v-if="rackIsFullscreen" class="rack-fullscreen-exit-bar">
          <button type="button" class="btn btn-sm rack-fullscreen-exit-btn" @click="toggleRackFullscreen">
            Exit fullscreen
          </button>
        </div>
        <div class="rack-zoom-inner" :style="{ zoom: rackViewZoom }">
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
</template>

<style scoped>
.rack-view-header-wrap {
  overflow: visible;
}

.rack-view-racks {
  margin-top: 10px;
  position: relative;
}

.rack-fullscreen-exit-bar {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  justify-content: flex-end;
  padding: 8px 10px 0;
  margin: -4px 0 4px;
  pointer-events: none;
}

.rack-fullscreen-exit-btn {
  pointer-events: auto;
  background-color: #fff;
  border: 2px solid #5376ea;
  color: #5376ea;
  font-family: var(--font-geist, 'Geist', system-ui, sans-serif);
  font-weight: 500;
}

.rack-fullscreen-exit-btn:hover {
  background-color: #5376ea;
  border-color: #5376ea;
  color: #fff;
}

.rack-view-racks:fullscreen {
  margin-top: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  box-sizing: border-box;
  background-color: #f5f5f9;
}

.rack-view-racks.rack-view-dark:fullscreen {
  background-color: #191919;
}

.racks-container { display: flex;flex-wrap: wrap; gap: 10px; padding: 10px; overflow-x: auto; align-items: flex-end; width:100% }

.rack-zoom-inner {
  width: 100%;
}

.rack-fullscreen-btn {
  background-color: #fff;
  border: 2px solid #5376ea;
  color: #5376ea;
  height: 38px;
  font-family: var(--font-geist, 'Geist', system-ui, sans-serif);
  font-size: 14px;
  font-weight: 500;
  padding: 0.375rem 1rem;
  border-radius: 8px;
  box-shadow: none;
}

.rack-fullscreen-btn:hover {
  background-color: #5376ea;
  border-color: #5376ea;
  color: #fff;
}

.rack-fullscreen-btn:focus {
  color: #fff;
  background-color: #5376ea;
  border-color: #5376ea;
  box-shadow: 0 0 0 0.2rem rgba(83, 118, 234, 0.35);
}

.rack-zoom-btn {
  width: 40px;
  height: 38px;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background-color: #5376ea !important;
  border: 1px solid #5376ea !important;
  color: #fff !important;
  border-radius: 8px;
  box-shadow: none;
  font-size: 1.25rem;
  line-height: 1;
  transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;
}

.rack-zoom-btn:hover,
.rack-zoom-btn.rack-zoom-btn-on,
.rack-zoom-btn.rack-zoom-btn-on:hover {
  background-color: #ffba30 !important;
  border-color: #ffba30 !important;
  color: #1a1a1a !important;
}

.rack-zoom-btn:focus {
  box-shadow: 0 0 0 0.2rem rgba(255, 186, 48, 0.45);
}

.flip-view-btn {
  min-width: 160px;
  height: 38px;
  font-family: var(--font-geist, 'Geist', system-ui, sans-serif);
  font-size: 13px;
  font-weight: 500;
  padding: 0.35rem 0.85rem;
  white-space: nowrap;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: none;
  background: #111 !important;
  border: 1px solid #111 !important;
  color: #fff !important;
}

.flip-view-btn:hover {
  background: #2a2a2a !important;
  border-color: #2a2a2a !important;
  color: #fff !important;
}

.flip-view-btn:focus {
  box-shadow: 0 0 0 0.2rem rgba(17, 17, 17, 0.35);
  color: #fff !important;
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
  flex-shrink: 0;
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
