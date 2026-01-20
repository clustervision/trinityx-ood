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

const { isDarkMode, toggleTheme, setTheme } = useTheme();

const emit = defineEmits(['rack-updated', 'device-taken','pool-updated']);
const toast = useToast();
const racks = ref<Rack[]>([]);
const { fetchSingleRack, handleRackDrop} = useRack();
const { metric1, metric2, metric1Range, metric2Range, getMetricForDevice } = useRackMetrics();
const loadingRackName = ref('');

//@ts-ignore
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
    const rawMsg = response.data.message;

    if (rawMsg) {
      let flatList: any[] = [];
      if (Array.isArray(rawMsg)) {
        rawMsg.forEach((item: any) => {
          if (item.name && item.size) flatList.push(item);
          else flatList.push(...Object.values(item));
        });
      } else {
        flatList = Object.values(rawMsg);
      }

      const currentStates = new Map(racks.value.map(r => [r.name, r.showBackSide]));
      const parsedRacks = await Promise.all(flatList.map(async (r: any) => {
          const fullRack = await fetchSingleRack(r.name);

          fullRack.showBackSide = currentStates.get(r.name) || false;
          return fullRack;
      }));

      racks.value = parsedRacks;
    }
  } catch (error) {
    console.error("Failed to load racks:", error);
  }
};

const resetRack = async (targetRack: any, side: 'front' | 'back') => {
  if (!confirm(`Power Reset all nodes on ${targetRack.name} ${side} side? (Switches & Controllers ignored)`)) return;
  loadingRackName.value = targetRack.name;


  const nodesToReset: any[] = [];
  targetRack.slots.forEach((slot: any) => {
    slot.devices.forEach((device: any) => {

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

  } catch (e: any) {
    console.error("Batch reset failed", e);
    toast.error("An error occurred during batch reset.");
  }
  finally{
      loadingRackName.value = '';
    }
};

// Add this function inside <script setup>

const handlePowerToggle = async (targetRack: any, side: 'front' | 'back') => {
  const isCurrentlyOn = side === 'front' ? targetRack.powerOn : targetRack.backPowerOn;
  const action = isCurrentlyOn ? 'off' : 'on';

  if (!confirm(`Power ${action.toUpperCase()} all nodes on ${targetRack.name} ${side} side?`)) return;
  loadingRackName.value = targetRack.name;

  const nodesToToggle: any[] = [];
  targetRack.slots.forEach((slot: any) => {
    slot.devices.forEach((device: any) => {
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
  } catch (e) {
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
    (deviceName: string) => {
       emit('device-taken', deviceName);

       racks.value.forEach(r => {
         if (r.name !== targetRack.name) {
           r.slots.forEach(slot => {
             slot.devices = slot.devices.filter(d => d.name !== deviceName);
           });
         }
       });
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
    <div class="card-body position-relative"> <div style="position: absolute; right: 80px; top: 55px; z-index: 10;">
    <button
      class="btn fw-bold"
      :class="isBackViewMode ? 'btn-custom-grey': 'btn-dark'"
      @click="toggleGlobalView"
      style="font-size: 12px; padding: 4px 15px;"
    >
      {{ isBackViewMode ? 'Flip to Front View' : 'Flip to Back View' }}
    </button>
    <button
          class="btn fw-bold"
          :class="isDarkMode ? 'btn-light' : 'btn-secondary'"
          @click="toggleTheme"
          style="font-size: 12px; padding: 4px 15px;"
        >
          <i class='bx' :class="isDarkMode ? 'bx-sun' : 'bx-moon'"></i>
          {{ isDarkMode ? 'Light' : 'Night' }}
        </button>
  </div>
      <RackMetricsHeader v-model:metric1="metric1"
       v-model:metric2="metric2"
       :range1="metric1Range"
        :range2="metric2Range"
        @refresh="loadRacks" />
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
            :is-busy="loadingRackName === rack.name"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.racks-container { display: flex;flex-wrap: wrap; gap: 10px; padding: 10px; overflow-x: auto; align-items: flex-end; width:100% }
.btn-custom-grey {
  background-color: #d3d3d3;
  border-color: #c0c0c0;
  color: #000;
}

.btn-custom-grey:hover {
  background-color: #bebebe;
}
</style>
