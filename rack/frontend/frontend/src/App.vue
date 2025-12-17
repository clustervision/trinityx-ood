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

const setView = (viewName: string) => {
  currentView.value = viewName;
  selectedItemName.value = '';
};

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
    <SideMenu @change-view="setView" />

    <div class="layout-page">
      <RackView v-if="currentView === 'dashboard'" />
      
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