<template>
  <aside id="layout-menu" class="layout-menu menu-vertical menu bg-menu-theme">
    <div class="menu-inner-shadow"></div>

    <ul class="menu-inner py-1">

      <li class="menu-item">
        <a href="javascript:void(0);" class="menu-link" @click="$emit('change-view', 'dashboard')">
          <i class="menu-icon tf-icons">
             <img src="@/assets/icons/computer-network.png" alt="icon" width="20"/>
          </i>
          <div data-i18n="Analytics">Rack Representation</div>
        </a>
      </li>

      <li class="menu-header small text-uppercase">
        <span class="menu-header-text">Manage</span>
      </li>

      <li class="menu-item">
        <a href="javascript:void(0);" class="menu-link" @click="$emit('change-view', 'manage-rack')">
          <i class="menu-icon tf-icons">
            <img src="@/assets/icons/application-detail.png" alt="icon" width="20"/>
          </i>
          <div data-i18n="Rack">Manage Rack Frames</div>
        </a>
      </li>

      <li class="menu-item">
        <a href="javascript:void(0);" class="menu-link" @click="$emit('change-view', 'manage-inventory')">
          <i class="menu-icon tf-icons">
              <img src="@/assets/icons/application-monitor.png" alt="icon" width="20"/>
          </i>
          <div data-i18n="Inventory">Manage Inventory</div>
        </a>
      </li>

       <li class="menu-item" :class="{ 'open': showUnassigned }">
        <a href="javascript:void(0);" class="menu-link menu-toggle" @click="showUnassigned = !showUnassigned">
          <i class="menu-icon tf-icons">
              <img src="@/assets/icons/network-status-busy.png" alt="icon" width="20"/>
          </i>
          <div data-i18n="Unassigned">Unassigned Device Pool</div>
          </a>

        <ul class="menu-sub ps-3 pe-3 pt-2" v-show="showUnassigned" style="display: block; list-style: none;">
          <div v-if="UnassignedNodes.length > 0">
             <div v-for="device in UnassignedNodes" :key="device.name" class="mb-2">
                <DeviceItem
                  :device="device"
                  :is-rack-view="false"
                />
             </div>
          </div>
          <li v-else class="menu-item">
             <a href="javascript:void(0)" class="menu-link">
                <div class="text-danger small">Device Pool <strong>EMPTY</strong></div>
             </a>
          </li>
        </ul>
      </li>
      </ul>
  </aside>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router'; // Only used for watching path changes if needed
import axios from 'axios';
import DeviceItem from '@/components/DeviceItem.vue';
const Url = 'https://yixin3-dev-ctrl001:7755';

// Define the emits so Vue knows this component sends events
const emit = defineEmits(['change-view']);

const UnassignedNodes = ref<any[]>([]);
const showUnassigned = ref(true); 
const route = useRoute();

const fetchUnassignedNodes = async () => {
  try {
    const response = await axios.get(Url + '/device_pool');
    const data = response.data; 
    
    if (data.message && Array.isArray(data.message)) {
       UnassignedNodes.value = data.message;
    } else {
       UnassignedNodes.value = [];
    }
  } catch (error) {
    console.error("Failed to load Unassigned Inventory:", error);
    UnassignedNodes.value = [];
  }
};

onMounted(() => {
  fetchUnassignedNodes();
});
</script>

<style scoped>
/* Keep your existing styles */
.menu-item .router-link-active {
    background-color: rgba(67, 89, 113, 0.1);
    color: #696cff;
    font-weight: bold;
}

.menu-sub {
  transition: all 0.3s ease;
  background-color: transparent;
}
</style>