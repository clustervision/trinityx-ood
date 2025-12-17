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

       <li class="menu-item open">
        <a href="javascript:void(0);" class="menu-link menu-toggle" @click="showUnassigned = !showUnassigned">
          <i class="menu-icon tf-icons">
              <img src="@/assets/icons/network-status-busy.png" alt="icon" width="20"/>
          </i>
          <div data-i18n="Unassigned">Unassigned Device Pool</div>
        </a>

        <ul 
          class="menu-sub ps-3 pe-3 pt-2" 
          v-show="showUnassigned" 
          style="display: block; list-style: none; min-height: 100px; border: 2px dashed #ddd;"
          @dragover.prevent
          @drop="onDropBackToPool"
        >
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
                <div class="text-muted small text-center p-2">
                  Drag devices here to unassign
                </div>
             </a>
          </li>
        </ul>
        </li>
    </ul>
  </aside>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import DeviceItem from '@/components/DeviceItem.vue';

const Url = 'https://yixin3-dev-ctrl001:7755';
const UnassignedNodes = ref<any[]>([]);
const showUnassigned = ref(true); 

// Define emits to notify Parent (App.vue) when something changes
const emit = defineEmits(['change-view', 'pool-updated']);

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

// --- NEW: Handle Dropping Back to Pool ---
const onDropBackToPool = async (event: DragEvent) => {
  const data = event.dataTransfer?.getData('application/json');
  if (!data) return;
  const device = JSON.parse(data);

  // If it's already in the pool (no position), ignore
  if (!device.position && device.position !== 0) return;

  try {
    const timestamp = new Date().getTime();
    
    // Use the backend API to "Update Inventory" (which deletes from Rack)
    const payload = {
      name: device.name,
      type: device.type || 'node'
    };
    
    // Double Encode as per your backend requirement
    const doubleEncoded = JSON.stringify(JSON.stringify(payload));

    await axios.post(
      Url + `/update_inventory?t=${timestamp}`, 
      doubleEncoded, 
      { headers: { 'Content-Type': 'application/json' } }
    );

    // Refresh my own list
    await fetchUnassignedNodes();
    
    // Tell App.vue to refresh the Rack View (because a device left the rack)
    emit('pool-updated'); 

  } catch (e) {
    console.error("Failed to unassign device", e);
    alert("Failed to return device to pool.");
  }
};

// Expose the fetch function so App.vue can call it
defineExpose({ fetchUnassignedNodes });

onMounted(() => {
  fetchUnassignedNodes();
});
</script>

<style scoped>
  .layout-menu {
  width: 250px !important;
  min-width: 250px !important;
  max-width: 250px !important;
}


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