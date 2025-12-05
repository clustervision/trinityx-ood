<template>
  <div
    class="device-item draggable"
    :class="[vendorClass, { 'is-dragging': isDragging }]"
    :style="{ height: heightPixels + 'px' }"
    draggable="true"
    @dragstart="onDragStart"
    @dragend="isDragging = false"
  >
    <div class="device-content">
      <span class="device-name">{{ device.name }}</span>
      </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import type { Device } from '@/types/rack';

const props = defineProps<{
  device: Device;
}>();

const isDragging = ref(false);

// 1. Logic ported from rack.html line 215: height * screen_factor - 2
const heightPixels = computed(() => (props.device.height * 30) - 2);

// 2. Logic ported from rack.html line 164: Determining CSS class for background image
const vendorClass = computed(() => {
  const v = props.device.vendor?.toLowerCase() || 'default';
  return `${v}-${props.device.height}`;
});

// 3. Logic ported from rack.js: Setup drag data
const onDragStart = (event: DragEvent) => {
  isDragging.value = true;
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move';
    // Send the device data as a JSON string
    event.dataTransfer.setData('application/json', JSON.stringify(props.device));
  }
};
</script>

<style scoped>
.device-item {
  width: 100%;
  position: absolute; /* Crucial: Devices sit on top of slots */
  z-index: 10;
  cursor: grab;
  border: 1px solid #333;
  /* Background images will be loaded by rack.css via the vendorClass */
}
.device-content {
  padding: 2px;
  color: white;
  text-shadow: 1px 1px 2px black;
  font-size: 10px;
}
</style>