<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import RackMetricsHeader from '@/components/RackMetricsHeader.vue';
import SingleRack from '@/components/SingleRack.vue';
import { useRack } from '@/composables/useRack';
import { useRackMetrics } from '../composables/useRackMetrics';
import type { Rack } from '@/types/rack';

const props = defineProps<{ rackName: string; }>();
const emit = defineEmits(['close', 'pool-updated', 'device-taken']);
const { fetchSingleRack , handleRackDrop} = useRack();
const { metric1, metric2, metric1Range, metric2Range, getMetricForDevice } = useRackMetrics();


const rack = ref<any>(null);
const Url = 'https://yixin3-dev-ctrl001:7755';


const loadRackData = async () => {
  if (!props.rackName) return;

  const currentShowBack = rack.value ? rack.value.showBackSide : true;

  // 2. Fetch the fresh data
  const freshRack = await fetchSingleRack(props.rackName);

  freshRack.showBackSide = currentShowBack;

  rack.value = freshRack;
};

const resetRack = (targetRack: any, side: 'front' | 'back') => {
  if (confirm(`Reset ${targetRack.name} ${side} side?`)) {
    console.log("Resetting rack side:", side);
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
        @refresh="loadRackData"
      />

      <div class="card-body">
        <div class="racks-container d-flex justify-content-center">
          <div v-if="rack" class="single-rack-wrapper">
            <div class="racks-container">
              <SingleRack
                :key="rack.name"
                :rack="rack"
                :metric1="metric1"
                :metric2="metric2"
                :range1="metric1Range"
                :range2="metric2Range"
                :get-metric="getMetricForDevice"
                @drop="onDrop"
                @reset="resetRack"
                @dragend="onDragEnd"
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
</style>
