<template>
  <aside id="layout-menu" class="layout-menu menu-vertical menu bg-menu-theme">
    <div class="menu-inner-shadow"></div>

    <ul class="menu-inner py-1">
      <li class="menu-item side-rack-nav" :class="{ 'is-active': isDashboardActive }">
        <a href="javascript:void(0);" class="menu-link" @click="$emit('change-view', 'dashboard')">
          <i class="menu-icon tf-icons bx bx-server"></i>
          <div data-i18n="Analytics">Rack Representation</div>
        </a>
      </li>

      <li class="menu-item side-rack-nav" :class="{ 'is-active': isManageRackActive }">
        <a href="javascript:void(0);" class="menu-link" @click="$emit('change-view', 'manage-rack')">
          <i class="menu-icon tf-icons bx bx-menu"></i>
          <div data-i18n="Rack">Manage Rack Frames</div>
        </a>
      </li>

      <li class="menu-item side-rack-nav" :class="{ 'is-active': isManageInventoryActive }">
        <a href="javascript:void(0);" class="menu-link" @click="$emit('change-view', 'manage-inventory')">
          <i class="menu-icon tf-icons bx bx-hdd"></i>
          <div data-i18n="Inventory">Manage Inventory</div>
        </a>
      </li>

      <li class="menu-item side-pool-block">
        <div class="side-nav-divider" role="presentation"></div>
        <div class="side-search-wrap">
          <i class="bx bx-search side-search-icon" aria-hidden="true"></i>
          <input
            v-model="unassignedSearch"
            type="search"
            class="side-search-input"
            placeholder="Search Devices"
            autocomplete="off"
          />
        </div>
        <div
          class="side-pool-drop"
          @dragover.prevent
          @drop="onDropBackToPool"
        >
          <div v-if="UnassignedNodes.length > 0" class="unassigned-pool-list">
            <div
              v-for="device in filteredUnassignedNodes"
              :key="device.name"
              class="mb-2 pool-device-wrap"
              :class="{ 'pool-device-selected': selectedPoolNames.has(device.name) }"
              style="width: 138px;"
              :title="device.name"
              @click="onPoolDeviceClick($event, device)"
            >
              <DeviceItem
                :device="device"
                :is-rack-view="false"
                :selected="selectedPoolNames.has(device.name)"
                :selected-devices-for-drag="selectedDevicesForDrag"
                @edit-inventory="onEditInventory"
              />
            </div>
          </div>
          <p v-else class="side-pool-empty">Drag devices here to unassign</p>
        </div>
      </li>
    </ul>
  </aside>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import axios from 'axios';
import DeviceItem from '@/components/DeviceItem.vue';
import { useToast } from 'vue-toastification';
// @ts-ignore
const Url = window.APP_URL;

const props = withDefaults(
  defineProps<{ currentView?: string }>(),
  { currentView: 'dashboard' }
);

const isDashboardActive = computed(() => props.currentView === 'dashboard');
const isManageRackActive = computed(() =>
  ['manage-rack', 'show-rack'].includes(props.currentView)
);
const isManageInventoryActive = computed(() => props.currentView === 'manage-inventory');

const UnassignedNodes = ref<any[]>([]);
const unassignedSearch = ref('');
const toast = useToast();

const filteredUnassignedNodes = computed(() => {
  const q = unassignedSearch.value.trim().toLowerCase();
  if (!q) return UnassignedNodes.value;
  return UnassignedNodes.value.filter((d) => (d.name || '').toLowerCase().includes(q));
});

const selectedPoolNames = ref<Set<string>>(new Set());
const lastClickedIndex = ref<number>(-1);

const selectedDevicesForDrag = computed(() =>
  filteredUnassignedNodes.value.filter((d) => selectedPoolNames.value.has(d.name))
);

const onPoolDeviceClick = (event: MouseEvent, device: any) => {
  const list = filteredUnassignedNodes.value;
  const currentIndex = list.findIndex((d) => d.name === device.name);
  if (currentIndex < 0) return;

  if (event.shiftKey) {
    const anchor = lastClickedIndex.value >= 0 ? lastClickedIndex.value : currentIndex;
    const start = Math.min(anchor, currentIndex);
    const end = Math.max(anchor, currentIndex);
    const next = new Set(selectedPoolNames.value);
    for (let i = start; i <= end; i++) {
      next.add(list[i].name);
    }
    selectedPoolNames.value = next;
    lastClickedIndex.value = currentIndex;
  } else if (event.ctrlKey || event.metaKey) {
    const next = new Set(selectedPoolNames.value);
    if (next.has(device.name)) next.delete(device.name);
    else next.add(device.name);
    selectedPoolNames.value = next;
    lastClickedIndex.value = currentIndex;
  } else {
    selectedPoolNames.value = new Set([device.name]);
    lastClickedIndex.value = currentIndex;
  }
};

watch(
  () => UnassignedNodes.value.map((n) => n.name),
  (names) => {
    const nameSet = new Set(names);
    const next = new Set<string>();
    selectedPoolNames.value.forEach((n) => {
      if (nameSet.has(n)) next.add(n);
    });
    if (next.size !== selectedPoolNames.value.size) selectedPoolNames.value = next;
  }
);

const emit = defineEmits(['change-view', 'pool-updated', 'edit-inventory']);

const onEditInventory = (device: { name: string }) => {
  emit('edit-inventory', device.name);
};

function normalizeDevicePoolMessage(raw: unknown): any[] {
  if (Array.isArray(raw)) return raw;
  if (raw && typeof raw === 'object') return Object.values(raw as Record<string, unknown>);
  return [];
}

const fetchUnassignedNodes = async () => {
  try {
    const response = await axios.get(Url + '/device_pool');
    const data = response.data;
    UnassignedNodes.value = normalizeDevicePoolMessage(data?.message);
  } catch (error) {
    console.error("Failed to load Unassigned Inventory:", error);
    UnassignedNodes.value = [];
  }
};

const onDropBackToPool = async (event: DragEvent) => {
  const data = event.dataTransfer?.getData('application/json');
  if (!data) return;
  const parsed = JSON.parse(data);

  if (parsed.multi === true && Array.isArray(parsed.devices)) {
    return;
  }

  const device = parsed;
  const isRack = 'size' in device || device.type === 'rack';
  if (device.dragSource === 'pool') return;

  UnassignedNodes.value.push(device);

  try {
    const timestamp = new Date().getTime();
    const payload = {
      name: device.name,
      type: isRack ?'rack':(device.type || 'node')
    };
    const doubleEncoded = JSON.stringify(JSON.stringify(payload));

    await axios.post(
      Url + `/update_inventory?t=${timestamp}`,
      doubleEncoded,
      { headers: { 'Content-Type': 'application/json' } }
    );

    emit('pool-updated');
    if (device.type === 'rack')
      toast.success(`Rack Update\n Rack ${device.name} is deleted.`);
    else
      toast.success(`Rack Update\n${device.name} Removed from Rack`);
  } catch (e) {
    console.error("Failed to unassign device", e);
    alert("Failed to return device to pool.");
    fetchUnassignedNodes();
  }
};


const removeNode = (deviceName: string) => {
  UnassignedNodes.value = UnassignedNodes.value.filter(n => n.name !== deviceName);
};

defineExpose({ fetchUnassignedNodes, removeNode });

onMounted(() => {
  fetchUnassignedNodes();
});
</script>

<style scoped>
  .layout-menu {
    --side-h-inset: 12px;
    --side-border-width: 3px;
    width: 232px !important;
    min-width: 232px !important;
    max-width: 232px !important;
    height: 100%;
    display: flex;
    flex-direction: column;
    box-sizing: border-box;
  }
  .layout-menu .menu-inner {
    flex: 1 1 auto;
    min-height: 0;
    display: flex;
    flex-direction: column;
    box-sizing: border-box;
    width: 100%;
    max-width: 100%;
  }
  /* core.css fixes .menu-item at 16.25rem; narrow sidebar clips — pin to menu width */
  .layout-menu :deep(.menu-inner > .menu-item),
  .layout-menu :deep(.menu-inner > .menu-header) {
    width: 100% !important;
    max-width: 100%;
    box-sizing: border-box;
  }
  .menu-item .router-link-active { background-color: rgba(67, 89, 113, 0.1); color: #696cff; font-weight: bold; }

  /* Between Manage Inventory and Search Devices */
  .side-nav-divider {
    flex-shrink: 0;
    height: 0;
    margin: 0 0 10px;
    border: 0;
    border-top: 2px dashed rgba(83, 118, 234, 0.5);
  }

  .side-pool-block {
    flex: 1 1 auto;
    min-height: 0;
    display: flex;
    flex-direction: column;
    gap: 10px;
    list-style: none;
    margin: 0;
    padding: 0 var(--side-h-inset);
    box-sizing: border-box;
    width: 100%;
  }

  .side-search-wrap {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 10px;
    min-height: 36px;
    box-sizing: border-box;
    border-radius: 10px;
    border: var(--side-border-width) solid #5376ea;
    background: #fff;
    flex-shrink: 0;
    width: 100%;
  }

  .side-search-icon {
    font-size: 1rem;
    color: #5376ea;
    flex-shrink: 0;
  }

  .side-search-input {
    flex: 1;
    min-width: 0;
    border: none;
    outline: none;
    background: transparent;
    font-family: var(--font-geist, 'Geist', system-ui, sans-serif);
    font-weight: 400;
    font-size: 0.8125rem;
    color: #334155;
  }

  .side-search-input::placeholder {
    color: #94a3b8;
  }

  .side-pool-drop {
    flex: 1 1 auto;
    min-height: 120px;
    border-radius: 10px;
    border: none;
    background: #fafbfd;
    padding: 8px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    box-sizing: border-box;
    width: 100%;
  }

  .unassigned-pool-list {
    overflow-y: auto;
    overflow-x: hidden;
    flex: 1 1 auto;
    min-height: 0;
    -webkit-overflow-scrolling: touch;
  }
  .pool-device-wrap {
    cursor: grab;
    border-radius: 4px;
  }
  .pool-device-selected {
    outline: 2px solid #5376ea;
    outline-offset: 2px;
  }

  .side-pool-empty {
    margin: auto;
    padding: 16px 8px;
    text-align: center;
    font-size: 0.8125rem;
    color: #94a3b8;
    font-family: var(--font-geist, 'Geist', system-ui, sans-serif);
    font-weight: 400;
  }

  :deep(.side-rack-nav > .menu-link) {
    margin: 4px var(--side-h-inset) !important;
    padding: 5px 8px !important;
    min-height: 0 !important;
    border-radius: 10px !important;
    font-family: var(--font-geist, 'Geist', system-ui, sans-serif) !important;
    font-weight: 500 !important;
    font-size: 0.8125rem !important;
    line-height: 1.25 !important;
    background-color: #fff !important;
    color: #5376ea !important;
    border: var(--side-border-width) solid #d0d7e2 !important;
    box-shadow: none !important;
    box-sizing: border-box !important;
  }

  :deep(.side-rack-nav:not(.is-active) > .menu-link:hover) {
    background-color: #f8fafc !important;
    color: #5376ea !important;
    border-color: #c5d0de !important;
  }

  :deep(.side-rack-nav.is-active > .menu-link) {
    background-color: #eef3ff !important;
    color: #5376ea !important;
    border: var(--side-border-width) solid #5376ea !important;
  }

  :deep(.side-rack-nav .menu-icon) {
    color: #5376ea !important;
    font-size: 1.1rem !important;
  }
</style>
