<template>
  <div
    class="device-item draggable"
    :class="[
       vendorClass, 
       { 'is-dragging': isDragging },
       isRackView ? 'is-absolute' : 'is-relative'  ]"
    
    :style="{ 
       height: heightPixels + 'px',
       backgroundColor: metricColor,  
       backgroundImage: metricColor ? 'none' : '' 
    }"
    
    draggable="true"
    @dragstart="onDragStart"
    @dragend="isDragging = false"
  >
    <div class="device-content">
      <span class="device-name">
         {{ device.name }} 
         <span v-if="metricValue">({{ metricValue }})</span>
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import type { Device } from '@/types/rack';
import { useRackSizing } from '@/composables/useRackSizing'; 

const props = defineProps<{
  device: Device;
  // 3. NEW PROPS
  metricValue?: number | string; // The actual number (e.g., 0.38 or 60)
  metricType?: string;           // 'Temperature' or 'System Load'
  isRackView?: boolean;
}>();

const isDragging = ref(false);
const { unitPixelHeight } = useRackSizing(); 

const heightPixels = computed(() => {
  return (props.device.height * unitPixelHeight.value) - 2;
});

// 4. CALCULATE HEATMAP COLOR
const metricColor = computed(() => {
  if (!props.metricValue || !props.metricType) return undefined; // No color if no data

  const value = parseFloat(props.metricValue.toString());
  
  // LOGIC A: Temperature (0°C to 100°C) -> Blue to Red
  if (props.metricType === 'Temperature') {
    // Clamp value between 0 and 100
    const ratio = Math.min(Math.max(value, 0), 100) / 100; 
    // Mix Blue (0,0,255) and Red (255,0,0)
    const r = Math.round(255 * ratio);
    const b = Math.round(255 * (1 - ratio));
    return `rgb(${r}, 0, ${b})`;
  }

  // LOGIC B: System Load (0.0 to 1.0+) -> Green to Red
  if (props.metricType === 'System Load') {
    // Assume 1.0 (100%) is max load for coloring
    let ratio = Math.min(Math.max(value, 0), 1);
    // Green (0,255,0) to Red (255,0,0)
    const r = Math.round(255 * ratio);
    const g = Math.round(255 * (1 - ratio));
    return `rgb(${r}, ${g}, 0)`;
  }

  return undefined; // Default to standard vendor CSS
});

// 4. Vendor Class Calculation
const vendorClass = computed(() => {
  const type = props.device.type;
  const vendor = props.device.vendor ? props.device.vendor.toLowerCase() : '';
  const height = props.device.height;

  // 1. Switch Logic
  if (type === 'switch') {
    return 'switch'; // This maps to .switch class in CSS
  }

  // 2. Default/Empty Logic
  if (!vendor || vendor === 'none') {
    return 'default';
  }

  // 3. Allowed Vendors Logic
  const allowedVendors = ["dell", "hp", "lenovo", "gigabyte", "supermicro", "asus"];
  if (!allowedVendors.includes(vendor)) {
    return 'noname';
  }

  // 4. Standard Case
  return `${vendor}-${height}`; // e.g., 'dell-2'
});

// 5. Drag Start Event
const onDragStart = (event: DragEvent) => {
  isDragging.value = true;
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move';
    event.dataTransfer.setData('application/json', JSON.stringify(props.device));
  }
};
</script>

<style scoped>
.device-item {
  width: 100%;
  z-index: 10;
  cursor: grab;
  border: 1px solid #333;
  transition: background-color 0.3s ease; /* Smooth color transition */
}
/* ... */
</style>

<style scoped>
.device-item {
  width: 100%;
  position: absolute; 
  z-index: 10;
  cursor: grab;
  border: 1px solid #333;
  /* Background images are loaded by rack.css using vendorClass */
}

.device-item.is-absolute {
  position: absolute;
}
.device-item.is-relative {
  position: relative; /* This makes them list normally in the sidebar */
  margin-bottom: 5px;
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