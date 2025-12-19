<script setup lang="ts">
import { ref } from 'vue';
import SideMenu from '@/components/SideMenu.vue';
import RackView from '@/views/RackView.vue';
import ManageView from '@/views/ManageView.vue';
import AddRack from '@/views/AddRack.vue';
import EditRack from '@/views/EditRack.vue';
import ShowRack from '@/views/ShowRack.vue'; 
import EditInventory from '@/views/EditInventory.vue';

const currentView = ref('dashboard'); 
const selectedItemName = ref('');

// Ref to access SideMenu methods
const sideMenuRef = ref<InstanceType<typeof SideMenu> | null>(null);
const rackViewRef = ref<InstanceType<typeof RackView> | null>(null);

const setView = (viewName: string) => {
  currentView.value = viewName;
  selectedItemName.value = '';
};

// --- INSTANT UPDATE LOGIC ---
// 1. When RackView says "I took a device from pool", remove it from SideMenu
const handleDeviceTakenFromPool = (deviceName: string) => {
  if (sideMenuRef.value) {
    sideMenuRef.value.removeNode(deviceName);
  }
};

// 2. When SideMenu says "I took a device back", refresh RackView
const handlePoolUpdated = () => {
   if (rackViewRef.value) {
      rackViewRef.value.loadRacks();
   }
   // ShowRack handles its own refresh if it's active, 
   // but RackView is the dashboard, so we refresh it via ref.
};

// Standard navigation
const handleAddRack = () => { currentView.value = 'add-rack'; };
const handleEditRack = (item: any) => {
  selectedItemName.value = item.name;
  currentView.value = 'edit-rack';
};
const handleEditInventory = (item: any) => {
  selectedItemName.value = item.name;
  currentView.value = 'edit-inventory';
}
const handleShowRack = (item: any) => {
  selectedItemName.value = item.name;
  currentView.value = 'show-rack';
};
const goBackToManage = () => {
  if (currentView.value.includes('rack')) currentView.value = 'manage-rack';
  else currentView.value = 'manage-inventory';
};
</script>

<template>
  <div class="layout-wrapper">
    <SideMenu 
       ref="sideMenuRef"
       @change-view="setView" 
       @pool-updated="handlePoolUpdated"
    />

    <div class="layout-page">
      <RackView 
         v-if="currentView === 'dashboard'" 
         ref="rackViewRef"
         @device-taken="handleDeviceTakenFromPool"
      />
      
      <ManageView 
         v-if="currentView === 'manage-rack'" 
         :page-type="'rack'" 
         @add-click="handleAddRack"
         @edit-click="handleEditRack"
         @show-click="handleShowRack"
      />
      
      <ManageView 
         v-if="currentView === 'manage-inventory'" 
         :page-type="'inventory'" 
         @edit-click="handleEditInventory"
      />

      <AddRack v-if="currentView === 'add-rack'" @close="goBackToManage" />

      <EditRack 
        v-if="currentView === 'edit-rack'" 
        :rack-name="selectedItemName"
        @close="goBackToManage" 
      />

      <ShowRack 
        v-if="currentView === 'show-rack'" 
        :rack-name="selectedItemName"
        @close="goBackToManage" 
        @device-taken="handleDeviceTakenFromPool"
      />

      <EditInventory 
        v-if="currentView === 'edit-inventory'"
        :inventory-name="selectedItemName"
        @close="goBackToManage"
      />

    </div>
  </div>
</template>

<style>
html, body, #app { height: 100%; margin: 0; }
</style>