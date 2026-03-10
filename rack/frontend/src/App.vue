<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import SideMenu from '@/components/SideMenu.vue';
import HeaderBar from '@/components/HeaderBar.vue';
import RackView from '@/views/RackView.vue';
import ManageView from '@/views/ManageView.vue';
import AddRack from '@/views/AddRack.vue';
import EditRack from '@/views/EditRack.vue';
import ShowRack from '@/views/ShowRack.vue';
import EditInventory from '@/views/EditInventory.vue';
import FooterBar from '@/components/FooterBar.vue';

const currentView = ref('dashboard');
const footerBaseUrl = typeof window !== 'undefined' ? window.location.origin : '';
const selectedItemName = ref('');
const sideMenuRef = ref<InstanceType<typeof SideMenu> | null>(null);
const rackViewRef = ref<InstanceType<typeof RackView> | null>(null);
const manageRackRef = ref<InstanceType<typeof ManageView> | null>(null);
const manageInventoryRef = ref<InstanceType<typeof ManageView> | null>(null);
const HEADER_HEIGHT = 52;
const scrollWrapperRef = ref<HTMLElement | null>(null);
const layoutPageRef = ref<HTMLElement | null>(null);
const wrapperScrollTop = ref(0);
const footerRevealed = ref(false);
const sidebarPinned = ref(false);

const BOTTOM_THRESHOLD = 2;

function onWrapperScroll() {
  const w = scrollWrapperRef.value;
  if (!w) return;
  wrapperScrollTop.value = w.scrollTop;
  footerRevealed.value = w.scrollTop > HEADER_HEIGHT;
  sidebarPinned.value = w.scrollTop >= HEADER_HEIGHT;
}

function isRightAtBottom(el: HTMLElement): boolean {
  return el.scrollHeight - el.scrollTop - el.clientHeight <= BOTTOM_THRESHOLD;
}

function isRightAtTop(el: HTMLElement): boolean {
  return el.scrollTop <= BOTTOM_THRESHOLD;
}

function onUnifiedWheel(e: WheelEvent) {
  const wrapper = scrollWrapperRef.value;
  const page = layoutPageRef.value;
  if (!wrapper || !page) return;
  const st = wrapper.scrollTop;
  const deltaY = e.deltaY;

  if (st < HEADER_HEIGHT) {
    e.preventDefault();
    wrapper.scrollTop = Math.max(0, Math.min(HEADER_HEIGHT, st + deltaY));
    onWrapperScroll();
    return;
  }

  e.preventDefault();

  if (st > HEADER_HEIGHT) {
    const max = wrapper.scrollHeight - wrapper.clientHeight;
    wrapper.scrollTop = Math.max(HEADER_HEIGHT, Math.min(max, st + deltaY));
    onWrapperScroll();
    return;
  }

  if (deltaY > 0) {
    if (isRightAtBottom(page)) {
      wrapper.scrollTop = st + deltaY;
      onWrapperScroll();
    } else {
      page.scrollTop = Math.min(page.scrollHeight - page.clientHeight, page.scrollTop + deltaY);
    }
  } else {
    if (isRightAtTop(page)) {
      wrapper.scrollTop = Math.max(0, st + deltaY);
      onWrapperScroll();
    } else {
      page.scrollTop = Math.max(0, page.scrollTop + deltaY);
    }
  }
}

let touchStartY = 0;

function onRightTouchStart(e: TouchEvent) {
  touchStartY = e.touches[0]?.clientY ?? 0;
}

function onRightTouchMove(e: TouchEvent) {
  const page = layoutPageRef.value;
  const wrapper = scrollWrapperRef.value;
  const t = e.touches[0];
  if (!page || !wrapper || !t) return;
  const deltaY = touchStartY - t.clientY;
  touchStartY = t.clientY;
  if (deltaY <= 0) return;
  if (!isRightAtBottom(page)) return;
  e.preventDefault();
  wrapper.scrollTop = Math.min(wrapper.scrollHeight - wrapper.clientHeight, wrapper.scrollTop + deltaY);
  onWrapperScroll();
}

const setView = (viewName: string) => {
  currentView.value = viewName;
  selectedItemName.value = '';
};

const headerBreadcrumbs = computed(() => {
  const map: Record<string, { label: string; view?: string }[]> = {
    'dashboard': [{ label: 'Home', view: 'dashboard' }, { label: 'Rack' }],
    'manage-rack': [{ label: 'Home', view: 'dashboard' }, { label: 'Manage Rack Frames' }],
    'manage-inventory': [{ label: 'Home', view: 'dashboard' }, { label: 'Manage Inventory' }],
    'add-rack': [{ label: 'Home', view: 'dashboard' }, { label: 'Manage Rack Frames', view: 'manage-rack' }, { label: 'Add Rack' }],
    'edit-rack': [{ label: 'Home', view: 'dashboard' }, { label: 'Manage Rack Frames', view: 'manage-rack' }, { label: 'Edit Rack' }],
    'show-rack': [{ label: 'Home', view: 'dashboard' }, { label: 'Manage Rack Frames', view: 'manage-rack' }, { label: 'Show Rack' }],
    'edit-inventory': [{ label: 'Home', view: 'dashboard' }, { label: 'Manage Inventory', view: 'manage-inventory' }, { label: 'Edit Inventory' }],
  };
  return map[currentView.value] ?? [{ label: 'Home', view: 'dashboard' }, { label: 'Page' }];
});

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
  selectedItemName.value = typeof item === 'string' ? item : item?.name ?? '';
  currentView.value = 'edit-inventory';
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
    const page = layoutPageRef.value;
    const wrapper = scrollWrapperRef.value;
    if (wrapper) {
      wrapper.scrollTop = 0;
      onWrapperScroll();
      wrapper.addEventListener('wheel', onUnifiedWheel, { passive: false, capture: true });
    }
    if (page) {
      page.addEventListener('touchstart', onRightTouchStart, { passive: true });
      page.addEventListener('touchmove', onRightTouchMove, { passive: false });
    }
  });
});

onUnmounted(() => {
  const page = layoutPageRef.value;
  const wrapper = scrollWrapperRef.value;
  if (page) {
    page.removeEventListener('touchstart', onRightTouchStart);
    page.removeEventListener('touchmove', onRightTouchMove);
  }
  if (wrapper) {
    wrapper.removeEventListener('wheel', onUnifiedWheel, true);
  }
});
</script>

<template>
  <div class="layout-outer" :class="{ 'sidebar-pinned': sidebarPinned, 'footer-revealed': footerRevealed }">
    <div
      ref="scrollWrapperRef"
      class="layout-scroll-wrapper"
      :class="{ 'wrapper-pinned': sidebarPinned }"
      @scroll="onWrapperScroll"
    >
      <HeaderBar
        :breadcrumbs="headerBreadcrumbs"
        @navigate="setView"
      />
      <div class="layout-main layout-wrapper">
        <aside class="layout-sidebar">
          <SideMenu
            ref="sideMenuRef"
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
          @edit-inventory="handleEditInventory"
        />
        <EditInventory
          v-if="currentView === 'edit-inventory'"
          :inventory-name="selectedItemName"
          @inventory-updated="refreshPoolData"
          @close="(r?: any) => goBackToManage(r)"
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
  overflow-y: hidden;
  overflow-x: auto;
}

.layout-outer {
  height: 100vh;
  overflow-y: hidden;
  overflow-x: auto;
  --header-height: 52px;
}

.layout-scroll-wrapper {
  height: 100%;
  overflow-y: auto;
  overflow-x: auto;
}
.layout-scroll-wrapper.wrapper-pinned {
  overflow-y: hidden !important;
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
  height: 100vh;
  max-height: 100vh;
  min-height: 100vh;
  display: flex;
  flex-direction: row;
  flex-shrink: 0;
  min-width: 1200px;
}

.layout-sidebar {
  height: 100vh;
  overflow-y: auto;
  overflow-x: hidden;
  flex-shrink: 0;
  width: 250px;
  position: sticky;
  top: 0;
  z-index: 10;
}

.layout-menu {
  position: relative !important;
  top: auto !important;
  bottom: auto !important;
  left: auto !important;
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

/* When viewport is narrow (often due to high zoom), hide sidebar and let content use full width */
@media (max-width: 1400px) {
  .layout-sidebar {
    display: none;
  }

  .layout-right {
    margin-left: 0;
  }
}
</style>