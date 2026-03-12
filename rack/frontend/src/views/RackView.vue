<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
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
onMounted(loadRacks);
onUnmounted(() => {
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
      <div class="card-body" :class="{ 'rack-view-dark': isDarkMode }" >
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
</template>

<style scoped>
.rack-view-header-wrap {
  overflow: visible;
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
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 58px;
  width: 58px;
  padding: 0;
  margin: 10px 0 0 0;
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
  height: 58px;
  width: auto;
  max-width: 58px;
  object-fit: contain;
  display: block;
  transition: opacity 0.08s ease;
}

.light-switch-btn:active .light-switch-img {
  opacity: 0.9;
}
</style>
