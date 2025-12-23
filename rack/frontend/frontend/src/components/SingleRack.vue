<script setup lang="ts">
import DeviceItem from '@/components/DeviceItem.vue';
import type {Rack} from '@/types/rack';

const props = defineProps<{
  rack: Rack;            
  metric1: string | null; 
  metric2: string | null; 
  getMetric: Function;  
}>();

const emit = defineEmits(['drop', 'reset', 'power-toggle']);
const toggleBack = () => { 
  props.rack.showBackSide = !props.rack.showBackSide; 
};
</script>


<template>
  <div class="single-rack-wrapper">
    <div class="rack-tabs">
      <div class="rack-tab front-label">FRONT SIDE</div>
      <div class="rack-tab back-toggle" @click="toggleBack">
        {{ rack.showBackSide ? 'HIDE BACK' : 'SHOW BACK' }}
      </div>
    </div>

    <div class="d-flex gap-0">
      <div class="rack-column">
        <div class="rack-header-light">
          <div class="d-flex align-items-center">
            <span class="u-header-label">U</span> 
            <span class="rack-title text-white">{{ rack.name }}</span>
          </div>
          <div class="d-flex align-items-center gap-1 ">
            <button class="btn btn-light btn-xs fw-bold reset-btn" @click="$emit('reset', rack, 'front')">RESET</button> 
            <i class='bx bx-power-off':class="rack.powerOn ?'text-success' : 'text-danger'" @click="rack.powerOn = !rack.powerOn"></i>
            <span class="u-header-label ms-1">U</span> 
          </div>
        </div>
        <div class="rack-frame">
          <div class="rack-row" v-for="slot in rack.slots" :key="slot.number"
               @drop="$emit('drop', $event, rack, slot.number, 'front')" @dragover.prevent>
            <div class="rack-label">{{ slot.number }}</div>
            <div class="rack-slot" style="position: relative;">
              <DeviceItem 
                v-if="slot.device && (slot.device.orientation === 'front' || !slot.device.orientation)"
                :device="slot.device"
                :metric-value="getMetric(slot.device, metric1)"
                :metric-type="metric1 || undefined"
                :is-rack-view="true"
                style="position: absolute; width: 100%;"
                :style="{ height: (slot.device.height * 20 - 2) + 'px' }"
              />
            </div>
            <div class="rack-label">{{ slot.number }}</div>
          </div>
        </div>
      </div>

      <div class="rack-column" v-if="rack.showBackSide">
        <div class="rack-header-dark">
          <div class="d-flex align-items-center">
            <span class="u-header-label">U</span>
            <span class="rack-title text-white">{{ rack.name }}</span>
          </div>
          <div class="d-flex align-items-center gap-1">
            <button class="btn btn-light btn-xs fw-bold reset-btn" @click="$emit('reset', rack, 'back')">RESET</button>
            <i class='bx bx-power-off' :class="rack.backPowerOn ? 'text-success' : 'text-danger'" @click="rack.backPowerOn = !rack.backPowerOn"></i>
            <span class="u-header-label">U</span>
          </div>
        </div>
        <div class="rack-frame">
          <div class="rack-row" v-for="slot in rack.slots" :key="slot.number"
               @drop="$emit('drop', $event, rack, slot.number, 'back')" @dragover.prevent>
            <div class="rack-label">{{ slot.number }}</div>
            <div class="rack-slot" style="position: relative;">
              <DeviceItem 
                v-if="slot.device && slot.device.orientation === 'back'"
                :device="slot.device"
                :metric-value="getMetric(slot.device, metric2)"
                :metric-type="metric2 || undefined"
                :is-rack-view="true"
                style="position: absolute; width: 100%;"
                :style="{ height: (slot.device.height * 20 - 2) + 'px' }"
              />
            </div>
            <div class="rack-label">{{ slot.number }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<style scoped>
.racks-container { display: flex;flex-wrap: wrap; gap: 10px; padding: 10px; overflow-x: auto; align-items: flex-end; width:100% }
.single-rack-wrapper { display: flex; flex-direction: column; flex-shrink: 0;}
.rack-tabs { display: flex; justify-content: space-between; margin-bottom: 0; }
.rack-tab { padding: 4px 12px; font-size: 0.5rem; font-weight: bold; color: white; text-transform: uppercase; }
.front-label { background-color: #6666ff; border-top-left-radius: 5px; border-top-right-radius: 5px; }
.back-toggle { background-color: #333; cursor: pointer; border-top-left-radius: 5px; border-top-right-radius: 5px; }
.rack-column { min-width: 180px; display: flex; flex-direction: column; flex:1;}
.u-header-label { width: 20px; text-align: center;font-size: 10px;font-weight: bold;color: #444;background-color: #e9ecef;display: inline-block;line-height: 16px; 
}
.rack-header-dark {
  background-color: #222;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0;
  height: 20px;
  overflow: hidden;
  border: 2px solid #222; 
  border-bottom: none;
}
.rack-header-light {
  background-color: #aaaaaa;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0;
  height: 20px;
  overflow: hidden;
  border: 2px solid #222; 
  border-bottom: none;
}
.rack-title {margin-left: 10px;font-size: 0.8rem;font-weight: bold;}
.reset-btn { font-size: 0.55rem; padding: 1px 2px; height: 12px; line-height: 0.5; }
.rack-frame { background: #e9ecef; border: 2px solid #222; border-top: none; padding: 0; }
.rack-row { display: flex; height: 20px; border-bottom: 1px solid #adb5bd; background-color: #fff; }
.rack-label { width: 20px;text-align: center; line-height: 20px; font-size: 11px; font-weight: bold; color: #444; background-color: #e9ecef; border-right: 1px solid #dee2e6; 
}
.rack-label:last-child { border-right: none; border-left: 1px solid #dee2e6; }
.rack-slot { flex-grow: 1; }
.cursor-pointer { cursor: pointer; }
</style>