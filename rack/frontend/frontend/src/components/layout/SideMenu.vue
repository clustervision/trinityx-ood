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
        <RouterLink to="/" class="menu-link" active-class="active">
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
        <RouterLink to="/manage/rack" class="menu-link" active-class="active">
          <i class="menu-icon tf-icons">
            <img src="@/assets/icons/application-detail.png" alt="icon" width="20"/>
          </i>
          <div data-i18n="Rack">Manage Rack Frames</div>
        </RouterLink>
      </li>

      <li class="menu-item">
        <RouterLink to="/manage/inventory" class="menu-link" active-class="active">
          <i class="menu-icon tf-icons">
             <img src="@/assets/icons/application-monitor.png" alt="icon" width="20"/>
          </i>
          <div data-i18n="Inventory">Manage Inventory</div>
        </RouterLink>
      </li>

       <li class="menu-item">
        <RouterLink to="/manage/unassigned" class="menu-link" active-class="active">
          <i class="menu-icon tf-icons">
             <img src="@/assets/icons/network-status-busy.png" alt="icon" width="20"/>
          </i>
          <div data-i18n="Unassigned">Unassigned Device Pool</div>
        </RouterLink>
      </li>

    </ul>
  </aside>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router';
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
</style>