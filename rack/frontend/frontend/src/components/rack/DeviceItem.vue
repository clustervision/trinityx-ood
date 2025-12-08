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
import { useRackSizing } from '@/composables/useRackSizing'; 

// 1. Define Props (ONLY ONCE)
const props = defineProps<{
  device: Device;
}>();

// 2. Setup State
const isDragging = ref(false);
const { unitPixelHeight } = useRackSizing(); 

// 3. Dynamic Height Calculation (Using the composable)
const heightPixels = computed(() => {
  return (props.device.height * unitPixelHeight.value) - 2;
});

// 4. Vendor Class Calculation
const vendorClass = computed(() => {
  const v = props.device.vendor?.toLowerCase() || 'default';
  return `${v}-${props.device.height}`;
});

// 5. Drag Start Event
const onDragStart = (event: DragEvent) => {
  isDragging.value = true;
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move';
    event.dataTransfer.setData('application/json', JSON.stringify(props.device));
    event.dataTransfer.setData('source', 'rack'); // Optional: Helps identify source
  }
};
</script>

<style scoped>
.device-item {
  width: 100%;
  position: absolute; 
  z-index: 10;
  cursor: grab;
  border: 1px solid #333;
  /* Background images are loaded by rack.css using vendorClass */
}

.device-content {
  padding: 2px;
  color: white;
  text-shadow: 1px 1px 2px black;
  font-size: 10px;
  overflow: hidden;
  white-space: nowrap;
}
</style>