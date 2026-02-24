<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import SideMenu from '@/components/SideMenu.vue';
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
const scrollWrapperRef = ref<HTMLElement | null>(null);
const layoutPageRef = ref<HTMLElement | null>(null);
const footerRevealed = ref(false);

const BOTTOM_THRESHOLD = 2;

function onWrapperScroll() {
  const w = scrollWrapperRef.value;
  footerRevealed.value = w ? w.scrollTop > 0 : false;
}
let touchStartY = 0;

function isRightAtBottom(el: HTMLElement): boolean {
  return el.scrollHeight - el.scrollTop - el.clientHeight <= BOTTOM_THRESHOLD;
}

function onRightWheel(e: WheelEvent) {
  const page = layoutPageRef.value;
  const wrapper = scrollWrapperRef.value;
  if (!page || !wrapper || e.deltaY <= 0) return;
  if (!isRightAtBottom(page)) return;
  e.preventDefault();
  wrapper.scrollTop = Math.min(wrapper.scrollHeight - wrapper.clientHeight, wrapper.scrollTop + e.deltaY);
  onWrapperScroll();
}

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

function onWrapperWheel(e: WheelEvent) {
  const wrapper = scrollWrapperRef.value;
  if (!wrapper || e.deltaY >= 0) return;
  if (wrapper.scrollTop <= 0) return;
  e.preventDefault();
  wrapper.scrollTop = Math.max(0, wrapper.scrollTop + e.deltaY);
  onWrapperScroll();
}

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
    if (page) {
      page.addEventListener('wheel', onRightWheel, { passive: false });
      page.addEventListener('touchstart', onRightTouchStart, { passive: true });
      page.addEventListener('touchmove', onRightTouchMove, { passive: false });
    }
    if (wrapper) {
      wrapper.addEventListener('wheel', onWrapperWheel, { passive: false, capture: true });
    }
  });
});

onUnmounted(() => {
  const page = layoutPageRef.value;
  const wrapper = scrollWrapperRef.value;
  if (page) {
    page.removeEventListener('wheel', onRightWheel);
    page.removeEventListener('touchstart', onRightTouchStart);
    page.removeEventListener('touchmove', onRightTouchMove);
  }
  if (wrapper) {
    wrapper.removeEventListener('wheel', onWrapperWheel, true);
  }
});
</script>

<template>
  <div class="layout-outer" :class="{ 'footer-revealed': footerRevealed }">
    <div ref="scrollWrapperRef" class="layout-scroll-wrapper" @scroll="onWrapperScroll">
      <div class="layout-main layout-wrapper">
        <aside class="layout-sidebar">
          <SideMenu
            ref="sideMenuRef"
            @change-view="setView"
            @pool-updated="handlePoolUpdated"
            @edit-inventory="handleEditInventory"
          />
        </aside>
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
  overflow: hidden;
}

/* 外层固定，不滚动 */
.layout-outer {
  height: 100vh;
  overflow: hidden;
}

/* 此层仅用于「右边滑到底后再滑」时露出 footer；不显示自身滚动条，由 JS 滚动；禁止 transform 以免 fixed 失效 */
.layout-scroll-wrapper {
  height: 100%;
  overflow-y: hidden;
  overflow-x: hidden;
}

/* 一整块固定一屏高，避免 main 被内容撑高导致整页滚动；只有右侧 layout-page 内部滚动 */
.layout-main.layout-wrapper {
  height: 100vh;
  max-height: 100vh;
  min-height: 100vh;
  display: flex;
  flex-direction: row;
  flex-shrink: 0;
}

/* 左侧 sidemenu：对右边固定，高度 100vh，有自己滚动条；footer 露出时改为流式，永远在 footer 上面 */
.layout-sidebar {
  height: 100vh;
  overflow-y: auto;
  overflow-x: hidden;
  flex-shrink: 0;
}
.layout-outer:not(.footer-revealed) .layout-sidebar {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  z-index: 10;
}
.layout-outer.footer-revealed .layout-sidebar {
  position: relative !important;
}

.layout-menu {
  position: relative !important;
  top: auto !important;
  bottom: auto !important;
  left: auto !important;
}

/* 右侧只滑 rack representation；sidemenu 固定时留出左边距 */
.layout-page {
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
}
.layout-outer:not(.footer-revealed) .layout-page {
  margin-left: 250px;
}

/* 当右边滚动条滑出整个 rack representation 时，再滑就显示 footer */
.layout-footer {
  flex-shrink: 0;
  width: 100%;
}
</style>