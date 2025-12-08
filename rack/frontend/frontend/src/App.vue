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
          <div class="container-fluid flex-grow-1 container-p-y">
            <RouterView />
          </div>
        </div>
      </div>
      
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