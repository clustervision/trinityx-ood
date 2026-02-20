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
const sideMenuRef = ref<InstanceType<typeof SideMenu> | null>(null);
const rackViewRef = ref<InstanceType<typeof RackView> | null>(null);
const manageRackRef = ref<InstanceType<typeof ManageView> | null>(null);
const manageInventoryRef = ref<InstanceType<typeof ManageView> | null>(null);

const setView = (viewName: string) => {
  currentView.value = viewName;
  selectedItemName.value = '';
};

const handleDeviceTakenFromPool = (deviceName: string) => {
  if (sideMenuRef.value) {
    sideMenuRef.value.removeNode(deviceName);
  }
};

// Sync all views when data changes
const syncAllViews = () => {
  if (rackViewRef.value) rackViewRef.value.loadRacks();
  if (sideMenuRef.value) sideMenuRef.value.fetchUnassignedNodes();
  if (manageRackRef.value) manageRackRef.value.refresh();
  if (manageInventoryRef.value) manageInventoryRef.value.refresh();
};

// Called when SideMenu drops something
const handlePoolUpdated = () => syncAllViews();

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
const goBackToManage = (needsRefresh?: { rack?: boolean; inventory?: boolean }) => {
  if (currentView.value.includes('rack')) {
    currentView.value = 'manage-rack';
  } else {
    currentView.value = 'manage-inventory';
  }
  if (needsRefresh?.rack || needsRefresh?.inventory) syncAllViews();
};

// Sync all views on inventory/rack change
const refreshPoolData = () => syncAllViews();
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
         v-show="currentView === 'dashboard'" 
         ref="rackViewRef"
         @device-taken="handleDeviceTakenFromPool"
         @pool-updated="refreshPoolData" 
      />

      <ManageView 
        v-show="currentView === 'manage-rack'" 
        ref="manageRackRef"
        :page-type="'rack'" 
        @add-click="handleAddRack"
        @edit-click="handleEditRack"
        @show-click="handleShowRack"
        @rack-deleted="handlePoolUpdated"
      />
      <ManageView 
        v-show="currentView === 'manage-inventory'" 
        ref="manageInventoryRef"
        :page-type="'inventory'" 
        @edit-click="handleEditInventory"
        @inventory-updated="refreshPoolData"
      />

      <AddRack v-if="currentView === 'add-rack'" @close="(r?: any) => goBackToManage(r)" />
      <EditRack 
        v-if="currentView === 'edit-rack'" 
        :rack-name="selectedItemName"
        @close="(r?: any) => goBackToManage(r)" 
      />
      <ShowRack 
        v-if="currentView === 'show-rack'" 
        :rack-name="selectedItemName"
        @close="() => { goBackToManage(); syncAllViews(); }"
        @device-taken="handleDeviceTakenFromPool"
        @pool-updated="refreshPoolData"
      />
      <EditInventory 
        v-if="currentView === 'edit-inventory'"
        :inventory-name="selectedItemName"
        @inventory-updated="refreshPoolData"
        @close="(r?: any) => goBackToManage(r)"
      />
    </div>
  </div>
</template>

<style>
html, body, #app {
  height: 100%;
  margin: 0;
  overflow: hidden;
}
.layout-wrapper {
  height: 100%;
  display: flex;
  overflow: hidden;
}
.layout-page {
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
}
</style>