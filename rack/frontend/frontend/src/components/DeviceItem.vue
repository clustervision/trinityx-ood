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
const Url = 'https://yixin3-dev-ctrl001:7755';

const props = defineProps<{
  device: Device;
  metricValue?: number | string; 
  metricType?: string;          
  isRackView?: boolean;
}>();

const isDragging = ref(false);
const { unitPixelHeight } = useRackSizing(); 

const heightPixels = computed(() => {
  return (props.device.height * unitPixelHeight.value) - 2;
});

const metricColor = computed(() => {
  if (!props.metricValue || !props.metricType) return undefined; 
  const value = parseFloat(props.metricValue.toString());
  
  if (props.metricType === 'Temperature') {
    const ratio = Math.min(Math.max(value, 0), 100) / 100; 
    const r = Math.round(255 * ratio);
    const b = Math.round(255 * (1 - ratio));
    return `rgb(${r}, 0, ${b})`;
  }

  if (props.metricType === 'System Load') {
    let ratio = Math.min(Math.max(value, 0), 1);
    const r = Math.round(255 * ratio);
    const g = Math.round(255 * (1 - ratio));
    return `rgb(${r}, ${g}, 0)`;
  }

  return undefined; 
});

const vendorClass = computed(() => {
  const type = props.device.type;
  const vendor = props.device.vendor ? props.device.vendor.toLowerCase() : '';
  const height = props.device.height;

  if (type === 'switch') return 'switch';
  if (!vendor || vendor === 'none') return 'default';

  const allowedVendors = ["dell", "hp", "lenovo", "gigabyte", "supermicro", "asus"];
  if (!allowedVendors.includes(vendor)) return 'noname';

  return `${vendor}-${height}`; 
});

// --- UPDATED DRAG START ---
const onDragStart = (event: DragEvent) => {
  isDragging.value = true;
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move';
    
    // Add 'dragSource' to the payload
    const payload = {
      ...props.device,
      dragSource: props.isRackView ? 'rack' : 'pool' 
    };
    
    event.dataTransfer.setData('application/json', JSON.stringify(payload));
  }
};
</script>

<style scoped>
/* Same styles as before */
.device-item {
  width: 65%;
  z-index: 10;
  cursor: grab;
  border: 1px solid #333;
  transition: background-color 0.3s ease;
}
.device-item.is-absolute { position: absolute; }
.device-item.is-relative { position: relative; margin-bottom: 5px; }
.device-content { padding: 2px; color: white; text-shadow: 1px 1px 2px black; font-size: 10px; overflow: hidden; white-space: nowrap; }
</style>