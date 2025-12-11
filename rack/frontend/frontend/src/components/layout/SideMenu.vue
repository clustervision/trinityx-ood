<template>
  <aside id="layout-menu" class="layout-menu menu-vertical menu bg-menu-theme">
    <div class="app-brand demo">
      <a href="/" class="app-brand-link">
        <span class="app-brand-logo demo">
            <img src="@/assets/img/logo.png" alt="Logo" style="width: 40px;">
        </span>
        <span class="app-brand-text demo menu-text fw-bolder ms-2">alertX</span>
      </a>

      <a href="javascript:void(0);" class="layout-menu-toggle menu-link text-large ms-auto d-block d-xl-none">
        <i class="bx bx-chevron-left bx-sm align-middle"></i>
      </a>
    </div>

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
          <div v-if="inventory.length > 0">
             <div v-for="device in inventory" :key="device.name" class="mb-2">
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
import { ref, onMounted } from 'vue';
import { RouterLink } from 'vue-router';
// Import the component you created
import DeviceItem from '@/components/rack/DeviceItem.vue'; 

// --- STATE ---
const inventory = ref<any[]>([]);
const showUnassigned = ref(true); // Default to open

// --- API FETCH ---
const fetchInventory = async () => {
  try {
    // Fetching directly from the URL you provided
    const response = await fetch('/manage/rack'); 
    const data = await response.json();
    
    // Assigning the 'inventory' array from your JSON example
    if (data.inventory) {
      inventory.value = data.inventory;
    }
  } catch (error) {
    console.error("Failed to load Unassigned Inventory:", error);
  }
};

onMounted(() => {
  fetchInventory();
});
</script>

<style scoped>
/* Basic active state styling to match your theme */
.menu-item .router-link-active {
    background-color: rgba(67, 89, 113, 0.1);
    color: #696cff; /* Example theme color */
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

/* Added style for the submenu to ensure items don't touch edges */
.menu-sub {
  transition: all 0.3s ease;
  background-color: transparent; /* Or match your theme */
}
</style>