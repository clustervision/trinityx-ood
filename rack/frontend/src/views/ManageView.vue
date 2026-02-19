<template>
  <div class="container-fluid flex-grow-1 container-p-y">
    <div class="card">
      <h5 class="card-header d-flex justify-content-between align-items-center">
        Manage {{ pageName }} Frames

        <button
          v-if="props.pageType === 'rack'"
          class="btn btn-success btn-sm"
          @click="$emit('add-click')"
        >
          Add New {{ pageName }}
        </button>
      </h5>

      <div class="card-body">
        <div v-if="loading" class="d-flex align-items-center justify-content-center p-5">
          <div class="spinner-border text-primary" role="status"></div>
        </div>
        <div v-else class="table-responsive text-nowrap">
          <table class="table table-bordered table-hover table-striped">
            <thead>
              <tr v-if="props.pageType === 'rack'">
                <th class="text-center">S. No.</th>
                <th class="text-center">NAME</th>
                <th class="text-center">SIZE</th>
                <th class="text-center">ORDER</th>
                <th class="text-center">ROOM</th>
                <th class="text-center">SITE</th>
                <th class="text-center">ACTIONS</th>
              </tr>

              <tr v-else>
                <th class="text-center">S. No.</th>
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
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import axios from 'axios';
import {useToast} from "vue-toastification"

//@ts-ignore
const Url = window.APP_URL;
const items = ref<any[]>([]);
const loading = ref(true);
const toast = useToast();
const props = defineProps<{
  pageType: string
}>();

const emit = defineEmits(['add-click', 'edit-click', 'show-click', 'inventory-updated', 'rack-deleted']);

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
       alert("Failed to process request.");
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

const refresh = () => fetchData();

defineExpose({ refresh });
onMounted(fetchData);
</script>

<style scoped>
.fs-4 { font-size: 1.3rem !important; }
a { text-decoration: none; }
a:hover { opacity: 0.8; }
</style>
