<template>
  <aside id="layout-menu" class="layout-menu menu-vertical menu bg-menu-theme">
    <div class="menu-inner-shadow"></div>

    <ul class="menu-inner py-1">
      <li class="menu-item">
        <a href="javascript:void(0);" class="menu-link" @click="$emit('change-view', 'dashboard')">
          <i class="menu-icon tf-icons bx bx-server"></i>
          <div data-i18n="Analytics">Rack Representation</div>
        </a>
      </li>

      <li class="menu-header small text-uppercase">
        <span class="menu-header-text">Manage</span>
      </li>

      <li class="menu-item">
        <a href="javascript:void(0);" class="menu-link" @click="$emit('change-view', 'manage-rack')">
          <i class="menu-icon tf-icons bx bx-grid-alt"></i>
          <div data-i18n="Rack">Manage Rack Frames</div>
        </a>
      </li>

      <li class="menu-item">
        <a href="javascript:void(0);" class="menu-link" @click="$emit('change-view', 'manage-inventory')">
          <i class="menu-icon tf-icons bx bx-hdd"></i>
          <div data-i18n="Inventory">Manage Inventory</div>
        </a>
      </li>

       <li class="menu-item menu-item-pool open">
        <a href="javascript:void(0);" class="menu-link menu-toggle" @click="showUnassigned = !showUnassigned">
          <i class="menu-icon tf-icons bx bx-unlink"></i>
          <div data-i18n="Unassigned">Unassigned Device Pool</div>
        </a>

        <ul
          class="menu-sub menu-sub-pool ps-3 pe-3 pt-2"
          v-show="showUnassigned"
          style="list-style: none; border: 2px dashed #ddd; width: 240px;"
          @dragover.prevent
          @drop="onDropBackToPool"
        >
          <div v-if="UnassignedNodes.length > 0" class="unassigned-pool-header">
            <input
              v-model="unassignedSearch"
              type="text"
              class="form-control form-control-sm mb-2"
              placeholder="Search devices..."
              style="width: 100%; font-size: 12px;"
            />
          </div>
          <div class="unassigned-pool-list" v-if="UnassignedNodes.length > 0">
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
          <li v-else class="menu-item">
             <a href="javascript:void(0)" class="menu-link">
                <div class="text-muted small text-center p-2">
                  Drag devices here to unassign
                </div>
             </a>
          </li>
        </ul>
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
const UnassignedNodes = ref<any[]>([]);
const showUnassigned = ref(true);
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

const fetchUnassignedNodes = async () => {
  try {
    const response = await axios.get(Url + '/device_pool');
    const data = response.data;
    if (data.message && Array.isArray(data.message)) {
       UnassignedNodes.value = data.message;
    } else {
       UnassignedNodes.value = [];
    }
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
    width: 250px !important;
    min-width: 250px !important;
    max-width: 250px !important;
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  .layout-menu .menu-inner {
    flex: 1 1 auto;
    min-height: 0;
    display: flex;
    flex-direction: column;
  }
  .menu-item .router-link-active { background-color: rgba(67, 89, 113, 0.1); color: #696cff; font-weight: bold; }
  .menu-item-pool {
    flex: 1 1 auto;
    min-height: 0;
    display: flex;
    flex-direction: column;
  }
  .menu-item-pool .menu-link { flex-shrink: 0; }
  .menu-sub-pool {
    flex: 1 1 auto;
    min-height: 0;
    display: flex !important;
    flex-direction: column;
    overflow: hidden;
    transition: all 0.3s ease;
    background-color: transparent;
  }
  .unassigned-pool-header { flex-shrink: 0; }
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
    outline: 2px solid #696cff;
    outline-offset: 2px;
  }
</style>
