<template>
  <aside id="layout-menu" class="layout-menu menu-vertical menu bg-menu-theme">
    <div class="menu-inner-shadow"></div>

    <ul class="menu-inner py-1">

      <li class="menu-item">
        <RouterLink to="/" class="menu-link">
          <i class="menu-icon tf-icons">
             <img src="@/assets/icons/computer-network.png" alt="icon" width="20"/>
          </i>
          <div data-i18n="Analytics">Rack Representation</div>
        </RouterLink>
      </li>

      <li class="menu-header small text-uppercase">
        <span class="menu-header-text">Manage</span>
      </li>

      <li class="menu-item">
        <RouterLink to="/manage/rack" class="menu-link">
          <i class="menu-icon tf-icons">
            <img src="@/assets/icons/application-detail.png" alt="icon" width="20"/>
          </i>
          <div data-i18n="Rack">Manage Rack Frames</div>
        </RouterLink>
      </li>

      <li class="menu-item">
        <RouterLink to="/manage/inventory" class="menu-link">
          <i class="menu-icon tf-icons">
              <img src="@/assets/icons/application-monitor.png" alt="icon" width="20"/>
          </i>
          <div data-i18n="Inventory">Manage Inventory</div>
        </RouterLink>
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
import { useRoute } from 'vue-router';
import axios from 'axios';
import DeviceItem from '@/components/DeviceItem.vue';
const url = 'https://yixin3-dev-ctrl001:7755';

// --- STATE ---
const UnassignedNodes = ref<any[]>([]);
const showUnassigned = ref(true); 
const route = useRoute();

// --- API FETCH ---
const fetchUnassignedNodes = async () => {
  try {
    const response = await axios.get(url + '/device_pool');
    
    // Check if valid JSON status
    console.log(response)
    if (response.data.status === undefined && !response.data.message) {
      console.error("Critical: Invalid JSON structure.");
      return;
    }

    const data = response.data;
    // Backend structure: { message: [...] }
    if (data.message && Array.isArray(data.message)) {
      UnassignedNodes.value = data.message;
    } else if (data.inventory) {
      UnassignedNodes.value = data.inventory;
    }
  } catch (error) {
    console.error("Failed to load Unassigned Inventory:", error);
  }
};

onMounted(() => {
  fetchUnassignedNodes();
  watch(
    () => route.path,
    () => fetchUnassignedNodes()
  );
});
</script>

<style scoped>
.menu-item .router-link-active {
    background-color: rgba(67, 89, 113, 0.1);
    color: #696cff;
    font-weight: bold;
}
.menu-item .router-link-active::before {
    content: "";
    position: absolute;
    left: 0;
    width: 3px;
    height: 100%;
    background-color: #696cff;
}

.menu-sub {
  transition: all 0.3s ease;
  background-color: transparent;
}
</style>