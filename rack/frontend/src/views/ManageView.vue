<template>
  <div class="container-fluid flex-grow-1 container-p-y manage-page">
    <div class="manage-page-card">
      <div class="manage-page-header">
        <h5 class="manage-page-title">Manage {{ pageName }} Frames</h5>
      </div>

      <div class="manage-page-body">
        <div v-if="loading" class="d-flex align-items-center justify-content-center p-5">
          <div class="spinner-border text-primary" role="status"></div>
        </div>
        <div v-else class="manage-table-shell">
          <div class="table-responsive text-nowrap">
            <table class="table table-hover table-striped manage-data-table">
            <thead>
              <tr v-if="props.pageType === 'rack'">
                <th class="text-center">No.</th>
                <th class="text-center">NAME</th>
                <th class="text-center">SIZE</th>
                <th class="text-center">ORDER</th>
                <th class="text-center">ROOM</th>
                <th class="text-center">SITE</th>
                <th class="text-center">ACTIONS</th>
              </tr>

              <tr v-else>
                <th class="text-center">No.</th>
                <th class="text-center">NAME</th>
                <th class="text-center">TYPE</th>
                <th class="text-center">HEIGHT</th>
                <th class="text-center">ORIENTATION</th>
                <th class="text-center">ACTIONS</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in items" :key="index">
                <td class="text-center">{{ index + 1 }}</td>

                <template v-if="props.pageType === 'rack'">
                   <td class="text-center">{{ item.name }}</td>
                   <td class="text-center">{{ item.size }}</td>
                   <td class="text-center">{{ item.order }}</td>
                   <td class="text-center">{{ item.room || '-' }}</td>
                   <td class="text-center">{{ item.site || '-' }}</td>
                </template>

                <template v-else>
                   <td class="text-center">{{ item.name }}</td>
                   <td class="text-center">{{ item.type }}</td>
                   <td class="text-center">{{ item.height }}</td>
                   <td class="text-center">{{ item.orientation }}</td>
                </template>

                <td class="text-center">
                   <a
                     v-if="props.pageType === 'rack'"
                     href="javascript:void(0);"
                     class="me-2"
                     title="Show"
                     @click="$emit('show-click', item)"
                   >
                     <i class='bx bx-info-circle text-info fs-4'></i>
                   </a>

                   <a href="javascript:void(0);" class="me-2" title="Edit" @click="$emit('edit-click', item)">
                     <i class='bx bx-edit text-primary fs-4'></i>
                   </a>

                   <a href="javascript:void(0);" title="Delete" @click="deleteItem(item)">
                     <i class='bx bx-trash text-danger fs-4'></i>
                   </a>
                </td>
              </tr>
              <tr v-if="items.length === 0">
                 <td :colspan="props.pageType === 'rack' ? 7 : 6" class="text-center">
                    No {{ pageName }} Available.
                 </td>
              </tr>
            </tbody>
            </table>
          </div>
        </div>
        <div v-if="props.pageType === 'rack'" class="manage-page-actions">
          <button type="button" class="manage-add-btn" @click="addRackOpen = true">
            Add Rack
          </button>
        </div>
      </div>
    </div>

    <AddRack
      v-if="props.pageType === 'rack'"
      v-model:open="addRackOpen"
      @close="onAddRackClose"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import AddRack from '@/views/AddRack.vue';
import axios from 'axios';
import {useToast} from "vue-toastification"

//@ts-ignore
const Url = window.APP_URL;
const items = ref<any[]>([]);
const loading = ref(true);
const toast = useToast();
const props = withDefaults(
  defineProps<{
    pageType: string;
    /** When false (e.g. navigated away), close rack add modal — Teleport ignores parent v-show. */
    modalHostActive?: boolean;
  }>(),
  { modalHostActive: true }
);

const emit = defineEmits(['edit-click', 'show-click', 'inventory-updated', 'rack-deleted', 'rack-added']);

const addRackOpen = ref(false);

const onAddRackClose = (payload?: { rack?: boolean }) => {
  if (payload?.rack) {
    emit('rack-added');
  }
};

const pageName = computed(() => {
  if (!props.pageType) return '';
  return props.pageType.charAt(0).toUpperCase() + props.pageType.slice(1);
});

const deleteItem = async (item: any) => {
  const confirmText = props.pageType === 'rack'
    ? `Are you sure you want to delete Rack ${item.name}?`
    : `Are you sure you want to unassign ${item.name} and return it to the pool?`;
  if (!confirm(confirmText)) return;

  const previousItems = [...items.value];

  if (props.pageType === 'rack') {
    try {
      const rackRes = await axios.get(Url + `/show_rack/${item.name}`);
      const rackData = rackRes.data?.message;
      const devices = rackData?.devices;
      const hasDevices = Array.isArray(devices) && devices.length > 0;
      if (hasDevices) {
        toast.error(`Cannot delete Rack ${item.name}: it has devices. Remove all devices first.`);
        return;
      }
    } catch (e) {
      console.error("Failed to check rack contents", e);
      toast.error("Could not verify rack contents.");
      return;
    }
  }

  items.value = items.value.filter(i => String(i.name) !== String(item.name));

  try {
    const timestamp = new Date().getTime();

    if (props.pageType === 'rack') {
      const deleteUrl = Url + `/delete_rack/${item.name}?t=${timestamp}`;
      await axios.get(deleteUrl);
      toast.success(`Rack ${item.name} is deleted.`);
      emit('rack-deleted');
    } else {

      const payload = {
        name: item.name,
        type: item.type || 'node'
      };
      const doubleEncoded = JSON.stringify(JSON.stringify(payload));

      await axios.post(
        Url + `/update_inventory?t=${timestamp}`,
        doubleEncoded,
        { headers: { 'Content-Type': 'application/json' } }
      );
      toast.success(`${item.name} returned to device pool.`);
    }
    emit('inventory-updated');
    console.log("Action confirmed by backend.");

  } catch (e: any) {
    console.error("Action failed", e);
    items.value = previousItems;
    toast.error("Failed to process request.");
  }
};

const fetchData = async () => {
  const key = props.pageType === 'rack' ? 'rack' : props.pageType === 'inventory' ? 'inventory' : null;
  if (!key) return;

  loading.value = true;
  try {
    const timestamp = Date.now();
    const fetchUrl = key === 'rack' ? Url + `/manage_racks?t=${timestamp}` : Url + `/manage_inventory?t=${timestamp}`;
    const response = await axios.get(fetchUrl);
    const rawMsg = response.data.message;
    if (Array.isArray(rawMsg)) {
      const out: any[] = [];
      rawMsg.forEach((entry: any) => {
        if (entry.name && (entry.size || entry.type)) out.push(entry);
        else out.push(...Object.values(entry));
      });
      items.value = out;
    } else if (typeof rawMsg === 'object' && rawMsg !== null) {
      items.value = Object.values(rawMsg);
    } else {
      items.value = [];
    }
  } catch (e) {
    console.error("Failed to load table data", e);
    items.value = [];
  } finally {
    loading.value = false;
  }
};

onMounted(fetchData);

watch(() => props.pageType, fetchData);

watch(
  () => props.modalHostActive,
  (active) => {
    if (active === false) {
      addRackOpen.value = false;
    }
  }
);

defineExpose({ refresh: fetchData });
</script>

<style scoped>
.manage-page-card {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
  overflow: hidden;
}

.manage-page-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e2e8f0;
  background: #fff;
}

.manage-page-title {
  margin: 0;
  font-family: var(--font-geist, 'Geist', sans-serif);
  font-weight: 500;
  font-size: 1.125rem;
  color: #5376ea;
}

.manage-add-btn {
  margin: 0;
  padding: 0.45rem 1.25rem;
  font-family: var(--font-geist, 'Geist', sans-serif);
  font-weight: 500;
  font-size: 0.875rem;
  line-height: 1.25;
  color: #fff;
  background: #5376ea;
  border: 1px solid #5376ea;
  border-radius: 8px;
  cursor: pointer;
  box-shadow: none;
  transition: background 0.15s ease, border-color 0.15s ease;
}

.manage-add-btn:hover {
  background: #3e66d6;
  border-color: #3e66d6;
  color: #fff;
}

.manage-add-btn:focus {
  outline: none;
  box-shadow: 0 0 0 0.2rem rgba(62, 102, 214, 0.35);
}

.manage-page-body {
  padding: 1rem 1.25rem 1.25rem;
}

.manage-page-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 1rem;
  padding-top: 0.25rem;
}

.manage-table-shell {
  --manage-table-border: #d8e6fd;
  --manage-table-border-width: 2px;
  --manage-table-radius: 6px;
  border: none;
  border-radius: var(--manage-table-radius);
  overflow: hidden;
}

.manage-table-shell .table-responsive {
  margin-bottom: 0;
}

/* separate + 0 spacing: every grid line is full width; corners can be rounded */
.manage-data-table {
  margin-bottom: 0;
  border-collapse: separate !important;
  border-spacing: 0 !important;
}

.manage-data-table > tbody {
  border-top: none !important;
}

.manage-data-table > :not(caption) > * > * {
  border-style: solid;
  border-color: var(--manage-table-border, #d8e6fd);
  border-width: 0;
  border-right-width: var(--manage-table-border-width, 2px);
  border-bottom-width: var(--manage-table-border-width, 2px);
}

.manage-data-table > thead > tr:first-child > th {
  border-top-width: var(--manage-table-border-width, 2px);
}

.manage-data-table > thead > tr > th:first-child,
.manage-data-table > tbody > tr > td:first-child {
  border-left-width: var(--manage-table-border-width, 2px);
}

.manage-data-table thead tr:first-child th:first-child {
  border-top-left-radius: var(--manage-table-radius, 6px);
}

.manage-data-table thead tr:first-child th:last-child {
  border-top-right-radius: var(--manage-table-radius, 6px);
}

.manage-data-table tbody tr:last-child td:first-child {
  border-bottom-left-radius: var(--manage-table-radius, 6px);
}

.manage-data-table tbody tr:last-child td:last-child {
  border-bottom-right-radius: var(--manage-table-radius, 6px);
}

.manage-data-table thead th {
  font-family: var(--font-geist, 'Geist', system-ui, sans-serif);
  font-weight: 500;
  font-size: 1.0625rem;
  color: #5376ea;
  vertical-align: middle;
}

.manage-data-table tbody td {
  font-family: var(--font-geist, 'Geist', system-ui, sans-serif);
  font-weight: 500;
  font-size: 1rem;
  vertical-align: middle;
}
</style>
