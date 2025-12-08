<script setup lang="ts">
import { RouterView } from 'vue-router'
import SideMenu from '@/components/layout/SideMenu.vue'
</script>

<template>
  <div class="layout-wrapper layout-content-navbar">
    <div class="layout-container">
      
      <SideMenu />

      <div class="layout-page">
        <div class="content-wrapper">
          <RouterView />
        </div>
      </div>
      
    </div>
  </div>
</template>

<style>
/* Ensure the layout takes full height */
.layout-container {
    display: flex;
    height: 100vh;
}
.layout-page {
    flex-grow: 1;
    overflow-y: auto;
}
</style>