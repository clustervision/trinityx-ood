<template>
  <div
    class="device-item draggable"
    :class="[
       vendorClass,
       { 'is-dragging': isDragging },
       isRackView ? 'is-absolute' : 'is-relative'
    ]"
    :style="{ height: heightPixels + 'px' }"
    draggable="true"
    @dragstart="onDragStart"
    @dragend="isDragging = false"
    @contextmenu.prevent="onRightClick"
  >
    <div class="device-content">
      <span class="device-name">{{ device.name }}</span>
    </div>

    <div class="indicators-overlay">

      <div
        v-if="metric1Type && metric1Type !== 'No Scale'"
        class="indicator-box"
        :style="{ backgroundColor: getColor(metric1Value, metric1Type) }"
        :title="`${metric1Type}: ${metric1Value ?? 'No Data'}`"
      ></div>

      <div
        v-if="metric2Type && metric2Type !== 'No Scale'"
        class="indicator-box"
        :style="{ backgroundColor: getColor(metric2Value, metric2Type) }"
        :title="`${metric2Type}: ${metric2Value ?? 'No Data'}`"
      ></div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import type { Device } from '@/types/rack';
import { useRackSizing } from '@/composables/useRackSizing';

const props = defineProps<{
  device: Device;
  metric1Value?: number;
  metric1Type?: string | null;
  metric2Value?: number;
  metric2Type?: string | null;
  isRackView?: boolean;
}>();
const emit = defineEmits(['device-right-click']);
const isDragging = ref(false);
const { unitPixelHeight } = useRackSizing();

const heightPixels = computed(() => {
  return (props.device.height * unitPixelHeight.value) - 2;
});

const onRightClick = (event: MouseEvent) => {

  emit('device-right-click', event, props.device);
};

const getColor = (val: number | undefined | null, type: string | null) => {
  if (!type || type === 'No Scale') return 'transparent';

  if (val === undefined || val === null) {
    return '#666666';
  }

  const value = parseFloat(val.toString());

  if (type === 'Temperature') {
    const ratio = Math.min(Math.max(value, 0), 100) / 100;
    const hue = (1 - ratio) * 120;
    return `hsl(${hue}, 100%, 45%)`;
  }

  if (type === 'System Load') {
    const ratio = Math.min(Math.max(value, 0), 1);
    const hue = (1 - ratio) * 120;
    return `hsl(${hue}, 100%, 45%)`;
  }
  if (type === 'Power Consumption') {
    const ratio = Math.min(Math.max(value, 0), 500) / 500;
    const hue = (1 - ratio) * 120;
    return `hsl(${hue}, 100%, 45%)`;
  }
  return '#cccccc';
};

const vendorClass = computed(() => {
  const type = props.device.type;
  const vendor = props.device.vendor ? props.device.vendor.toLowerCase() : '';
  const height = props.device.height;
  if (type === 'switch') return 'switch';
  if (!vendor || vendor === 'none') return 'default';
  return `${vendor}-${height}`;
});

const onDragStart = (event: DragEvent) => {
  isDragging.value = true;
  if (event.dataTransfer) {
    const offsetY = event.offsetY;
    const uOffset = Math.floor(offsetY / unitPixelHeight.value);

    event.dataTransfer.effectAllowed = 'move';
    const payload = {
      ...props.device,
      dragSource: props.isRackView ? 'rack' : 'pool',
      uOffset: uOffset
    };
    event.dataTransfer.setData('application/json', JSON.stringify(payload));
  }
};
</script>

<style scoped>
.device-item {
  width: 100%;
  z-index: 10;
  cursor: grab;
  border: 1px solid #333;
  background-color: #3a3a3a;
  color: white;
  position: relative;
  display: flex;
  align-items: center;
  padding-left: 5px;
  overflow: hidden;
}

.device-item.is-absolute { position: absolute; }
.device-item.is-relative { position: relative; margin-bottom: 5px; }

.device-content {
  overflow: hidden;
  white-space: nowrap;
  font-size: 10px;
  text-shadow: 1px 1px 2px black;
  width: 80%;
}


.indicators-overlay {
  position: absolute;
  top: 2px;
  right: 2px;
  display: flex;
  gap: 2px;
  z-index: 20;
}


.indicator-box {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  border: 1px solid rgba(255,255,255,0.3);
  box-shadow: 0 1px 2px rgba(0,0,0,0.5);
}
</style>
