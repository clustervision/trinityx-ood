<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import RackMetricsHeader from '@/components/RackMetricsHeader.vue';
import SingleRack from '@/components/SingleRack.vue';
import { useRack } from '@/composables/useRack';
import { useRackMetrics } from '../composables/useRackMetrics';
import type { Rack } from '@/types/rack';
import { useToast } from 'vue-toastification';

const props = defineProps<{ rackName: string; }>();
const emit = defineEmits(['close', 'pool-updated', 'device-taken', 'edit-inventory']);

const onEditInventory = (device: { name: string }) => {
  emit('edit-inventory', device.name);
};
const { fetchSingleRack , handleRackDrop} = useRack();
const { metric1, metric2, metric1Range, metric2Range, getMetricForDevice, fetchMetricData } = useRackMetrics();
const toast = useToast()
const loadingRackName = ref('');
const rack = ref<any>(null);
//@ts-ignore
const Url = window.APP_URL;

const RACK_ZOOM_LEVEL = 2;
const rackViewZoom = ref(1);
const rackZoomMagnified = computed(() => rackViewZoom.value >= RACK_ZOOM_LEVEL);

const toggleRackZoom = () => {
  rackViewZoom.value = rackViewZoom.value >= RACK_ZOOM_LEVEL ? 1 : RACK_ZOOM_LEVEL;
};

const loadRackData = async () => {
  if (!props.rackName) return;

  const currentShowBack = rack.value ? rack.value.showBackSide : true;
  const freshRack = await fetchSingleRack(props.rackName);
  freshRack.showBackSide = currentShowBack;
  rack.value = freshRack;
  await fetchMetricData();
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
    finally{
    loadingRackName.value = '';

    }
  }));
  if (successCount > 0) toast.success(`Power reset signal sent to ${successCount} nodes.`);
  if (failCount > 0) toast.warning(`Failed to reset ${failCount} nodes.`);
};


// Add this function inside <script setup>

const handlePowerToggle = async (targetRack: any, side: 'front' | 'back') => {
  // 1. Determine current state and target action
  const isCurrentlyOn = side === 'front' ? targetRack.powerOn : targetRack.backPowerOn;
  const action = isCurrentlyOn ? 'off' : 'on'; // If on, turn off. If off, turn on.
  const confirmMsg = `Power ${action.toUpperCase()} all nodes on ${targetRack.name} ${side} side? (Switches/Controllers ignored)`;

  if (!confirm(confirmMsg)) return;
  loadingRackName.value = targetRack.name;
  // 2. Identify target devices
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

    return;
  }

  // 3. Start Loading (Using the state from previous step)
    loadingRackName.value = targetRack.name;


  try {
    let successCount = 0;

    await Promise.all(nodesToToggle.map(async (dev) => {
      try {
        // API Call: /perform/power/on/{name} or /perform/power/off/{name}
        await axios.get(`${Url}/perform/power/${action}/${dev.name}`);
        successCount++;
      } catch (e) {
        console.error(`Failed to power ${action} ${dev.name}`, e);
      }
    }));

    // 4. Update UI State only on success
    if (successCount > 0) {
      toast.success(`${successCount} nodes powered ${action}.`);
      if (side === 'front') targetRack.powerOn = !isCurrentlyOn;
      else targetRack.backPowerOn = !isCurrentlyOn;
    }

  } catch (e) {
    console.error("Batch power toggle failed", e);
    toast.error("An error occurred during power toggle.");
  } finally {
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
      names.forEach((n) => emit('device-taken', n));
      emit('pool-updated');
    },
    () => {
      loadRackData();
    }
  );
};

const onDragEnd = () => {
  setTimeout(() => {
    loadRackData();
  }, 400);
};


onMounted(() => {
  loadRackData();
});
</script>

<template>
  <div class="container-fluid flex-grow-1 container-p-y">
    <div class="card mb-4 border-0 h-100">
      <div class="card-header d-flex align-items-center justify-content-between">
        <h5 class="mb-0">Rack Details: {{ props.rackName }}</h5>
          <button class="btn btn-warning" @click="$emit('close')">Back</button>
      </div>
      <RackMetricsHeader
        v-model:metric1="metric1"
        v-model:metric2="metric2"
        :range1="metric1Range"
        :range2="metric2Range"
        @refresh="loadRackData"
      >
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
      </RackMetricsHeader>

      <div class="card-body">
        <div class="racks-container d-flex justify-content-center">
          <div v-if="rack" class="single-rack-wrapper rack-zoom-inner" :style="{ zoom: rackViewZoom }">
            <div class="racks-container">
              <SingleRack
                :key="rack.name"
                :rack="rack"
                :metric1="metric1"
                :metric2="metric2"
                :range1="metric1Range"
                :range2="metric2Range"
                :get-metric="getMetricForDevice"
                :is-back-view-mode="false"
                @drop="onDrop"
                @reset="resetRack"
                @dragend="onDragEnd"
                @power-toggle="handlePowerToggle"
                @edit-inventory="onEditInventory"
                :is-busy="loadingRackName === rack.name"
              />
            </div>
          </div>
          <div v-else class="text-center p-5">
            <div class="spinner-border text-primary" role="status"></div>
            <p>Loading Rack Data...</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.racks-container { display: flex; flex-wrap: wrap; gap: 10px; padding: 10px; overflow-x: auto; align-items: flex-end; width:100%; }

.rack-zoom-inner {
  width: 100%;
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
</style>
