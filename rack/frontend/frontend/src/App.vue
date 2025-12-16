<script setup lang="ts">
import { RouterView } from 'vue-router'
import SideMenu from '@/components/SideMenu.vue'
import { ref } from 'vue';
import RackView from '@/views/RackView.vue';
import ManageView from '@/views/ManageView.vue';

// 'dashboard', 'manage-rack', or 'manage-inventory'
const currentView = ref('dashboard'); 

// Function to handle switching
const setView = (viewName: string) => {
  currentView.value = viewName;
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
      />
      
      <ManageView 
         v-if="currentView === 'manage-inventory'" 
         :page-type="'inventory'" 
      />
    </div>
  </div>
</template>

<style>

/* Ensure body takes full space */
html, body, #app {
  height: 100%;
  margin: 0;
}
</style>