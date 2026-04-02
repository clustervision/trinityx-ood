<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import { useToast } from 'vue-toastification';
import { initConnectionStatus, isSessionExpired } from '@/utils/connectionStatus';
import SideMenu from '@/components/SideMenu.vue';
import HeaderBar from '@/components/HeaderBar.vue';
import RackView from '@/views/RackView.vue';
import ManageView from '@/views/ManageView.vue';
import EditRack from '@/views/EditRack.vue';
import ShowRack from '@/views/ShowRack.vue';
import EditInventory from '@/views/EditInventory.vue';
import FooterBar from '@/components/FooterBar.vue';

initConnectionStatus(useToast());

const currentView = ref('dashboard');
const footerBaseUrl = typeof window !== 'undefined' ? window.location.origin : '';
const selectedItemName = ref('');
const rackEditOpen = ref(false);
const inventoryEditOpen = ref(false);
const sideMenuRef = ref<InstanceType<typeof SideMenu> | null>(null);
const rackViewRef = ref<InstanceType<typeof RackView> | null>(null);
const manageRackRef = ref<InstanceType<typeof ManageView> | null>(null);
const manageInventoryRef = ref<InstanceType<typeof ManageView> | null>(null);
const HEADER_HEIGHT = 52;
const scrollWrapperRef = ref<HTMLElement | null>(null);
const layoutPageRef = ref<HTMLElement | null>(null);
const wrapperScrollTop = ref(0);
const footerRevealed = ref(false);
const sidebarPinned = ref(false); // kept for potential future use, but no longer drives layout

const setView = (viewName: string) => {
  currentView.value = viewName;
  selectedItemName.value = '';
};

const headerBreadcrumbs = computed(() => {
  const map: Record<string, { label: string; view?: string }[]> = {
    'dashboard': [{ label: 'Home', view: 'dashboard' }, { label: 'Rack' }],
    'manage-rack': [{ label: 'Home', view: 'dashboard' }, { label: 'Manage Rack Frames' }],
    'manage-inventory': [{ label: 'Home', view: 'dashboard' }, { label: 'Manage Inventory' }],
    'show-rack': [{ label: 'Home', view: 'dashboard' }, { label: 'Manage Rack Frames', view: 'manage-rack' }, { label: 'Show Rack' }],
  };
  return map[currentView.value] ?? [{ label: 'Home', view: 'dashboard' }, { label: 'Page' }];
});

const reloadPage = () => { window.location.reload(); };
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

const handleEditRack = (item: any) => {
  inventoryEditOpen.value = false;
  selectedItemName.value = item.name;
  rackEditOpen.value = true;
};
const handleEditInventory = (item: any) => {
  rackEditOpen.value = false;
  selectedItemName.value = typeof item === 'string' ? item : item?.name ?? '';
  currentView.value = 'manage-inventory';
  inventoryEditOpen.value = true;
};
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

onMounted(() => {
  nextTick(() => {
    const wrapper = scrollWrapperRef.value;
    if (wrapper) {
      wrapper.scrollTop = 0;
    }
  });
});

onUnmounted(() => {
  const wrapper = scrollWrapperRef.value;
  if (wrapper) {
    // no-op for now
  }
});
</script>

<template>
  <div class="layout-outer" :class="{ 'sidebar-pinned': sidebarPinned, 'footer-revealed': footerRevealed }">
    <div v-if="isSessionExpired" class="session-expired-banner">
      Session expired. Please log in to OOD again —
      <a href="#" class="session-expired-link" @click.prevent="reloadPage">refresh this page</a>
      after logging in.
    </div>
    <div
      ref="scrollWrapperRef"
      class="layout-scroll-wrapper"
    >
      <HeaderBar
        :breadcrumbs="headerBreadcrumbs"
        @navigate="setView"
      />
      <div class="layout-main layout-wrapper">
        <aside class="layout-sidebar">
          <SideMenu
            ref="sideMenuRef"
            :current-view="currentView"
            @change-view="setView"
            @pool-updated="handlePoolUpdated"
            @edit-inventory="handleEditInventory"
          />
        </aside>
        <div class="layout-right">
          <div ref="layoutPageRef" class="layout-page">
        <RackView
          v-show="currentView === 'dashboard'"
          ref="rackViewRef"
          @device-taken="handleDeviceTakenFromPool"
          @pool-updated="refreshPoolData"
          @edit-inventory="handleEditInventory"
        />

        <ManageView
          v-show="currentView === 'manage-rack'"
          ref="manageRackRef"
          :page-type="'rack'"
          :modal-host-active="currentView === 'manage-rack'"
          @edit-click="handleEditRack"
          @show-click="handleShowRack"
          @rack-deleted="handlePoolUpdated"
          @rack-added="syncAllViews"
        />
        <ManageView
          v-show="currentView === 'manage-inventory'"
          ref="manageInventoryRef"
          :page-type="'inventory'"
          :modal-host-active="currentView === 'manage-inventory'"
          @edit-click="handleEditInventory"
          @inventory-updated="refreshPoolData"
        />

        <EditRack
          v-model:open="rackEditOpen"
          :rack-name="selectedItemName"
          :modal-host-active="currentView === 'manage-rack'"
          @close="(p?: { rack?: boolean }) => { if (p?.rack) syncAllViews(); }"
        />
        <ShowRack
          v-if="currentView === 'show-rack'"
          :rack-name="selectedItemName"
          @close="() => { goBackToManage(); syncAllViews(); }"
          @device-taken="handleDeviceTakenFromPool"
          @pool-updated="refreshPoolData"
          @edit-inventory="handleEditInventory"
        />
        <EditInventory
          v-model:open="inventoryEditOpen"
          :inventory-name="selectedItemName"
          :modal-host-active="currentView === 'manage-inventory'"
          @inventory-updated="refreshPoolData"
          @close="(p?: { inventory?: boolean }) => { if (p?.inventory) syncAllViews(); }"
        />
          </div>
        </div>
      </div>
      <footer v-if="footerBaseUrl" class="layout-footer">
        <FooterBar :url="footerBaseUrl" />
      </footer>
    </div>
  </div>
</template>

<style>
html, body, #app {
  height: 100%;
  margin: 0;
  overflow-x: auto;
  overflow-y: auto;
}

.session-expired-banner {
  position: sticky;
  top: 0;
  z-index: 100;
  background: #dc3545;
  color: white;
  text-align: center;
  padding: 10px 16px;
  font-weight: 500;
}
.session-expired-banner .session-expired-link {
  color: #fff;
  text-decoration: underline;
  font-weight: 600;
}
.session-expired-banner .session-expired-link:hover {
  color: #ffe0e0;
}

.layout-outer {
  min-height: 100vh;
  overflow: visible;
  --header-height: 52px;
}

.layout-scroll-wrapper {
  height: auto;
  overflow: visible;
}

.layout-scroll-wrapper > header {
  position: relative;
  z-index: 20;
}

.layout-scroll-wrapper > .layout-main.layout-wrapper {
  position: relative;
  z-index: 0;
}

.layout-main.layout-wrapper {
  display: flex;
  flex-direction: row;
  flex-shrink: 0;
  min-width: 1200px;
  min-height: calc(100vh - 52px);
}

.layout-sidebar {
  height: auto;
  overflow-y: auto;
  overflow-x: hidden;
  flex-shrink: 0;
  width: 232px;
  position: relative;
}

.layout-right {
  flex: 1 1 auto;
  min-width: 0;
  display: flex;
  flex-direction: column;
  margin-left: 0;
}

.layout-page {
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
  overflow-x: visible;
}

.layout-footer {
  flex-shrink: 0;
  width: 100%;
  position: relative;
  z-index: 1;
}

/* On very narrow viewports / high zoom, hide footer to avoid layout crowding */
@media (max-width: 1199.98px) {
  .layout-footer {
    display: none;
  }
}
</style>