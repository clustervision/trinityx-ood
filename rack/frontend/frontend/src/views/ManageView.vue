<template>
  <div class="container-fluid flex-grow-1 container-p-y">
    <div class="card">
      <h5 class="card-header d-flex justify-content-between align-items-center">
        Manage {{ pageName }} Frames
        
        <button 
          v-if="props.pageType === 'rack'" 
          class="btn btn-success btn-sm" 
          @click="router.push('/edit/Rack')"
        >
          Add New {{ pageName }}
        </button>
      </h5>
      
      <div class="card-body">
        <div class="table-responsive text-nowrap">
          <table class="table table-bordered table-hover table-striped">
            <thead>
              <tr v-if="props.pageType === 'rack'">
                <th class="text-center">S. No.</th>
                <th class="text-center">Name</th>
                <th class="text-center">Size</th>
                <th class="text-center">Order</th>
                <th class="text-center">Room</th>
                <th class="text-center">Site</th> 
                <th class="text-center">Actions</th>
              </tr>

              <tr v-else>
                <th class="text-center">S. No.</th>
                <th class="text-center">Name</th>
                <th class="text-center">Type</th>
                <th class="text-center">Height</th>
                <th class="text-center">Orientation</th>
                <th class="text-center">Actions</th>
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
                   <button class="btn btn-icon btn-sm" title="Edit" @click="editItem(item)">
                     <i class='bx bx-edit text-primary'></i>
                   </button>
                   <button class="btn btn-icon btn-sm" title="Delete" @click="deleteItem(item)">
                     <i class='bx bx-trash text-danger'></i>
                   </button>
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
import { useRouter } from 'vue-router';
import axios from 'axios';

const Url = 'https://yixin3-dev-ctrl001:7755';
const router = useRouter();
const items = ref<any[]>([]);

// Define props to receive data from App.vue
const props = defineProps<{
  pageType: string // 'rack' or 'inventory'
}>();

const pageName = computed(() => {
  if (!props.pageType) return '';
  return props.pageType.charAt(0).toUpperCase() + props.pageType.slice(1);
});

// 1. EDIT ACTION (Fixed Routes)
const editItem = (item: any) => {
  if (props.pageType === 'rack') {
    // Navigate to Frontend Route: /edit/rack/:id
    router.push(`/edit/rack/${item.name}`);
  } else if (props.pageType === 'inventory') {
    // Navigate to Frontend Route: /edit/inventory/:id
    router.push(`/edit/inventory/${item.name}`);
  }
};

// 2. DELETE ACTION
const deleteItem = async (item: any) => {
  if (!confirm(`Are you sure you want to delete ${item.name}?`)) return;

  try {
    let deleteUrl = '';
    // Use props.pageType here
    if (props.pageType === 'rack') {
      deleteUrl = Url + `/delete_rack/${item.name}`;
    } else {
      deleteUrl = Url + `/delete_inventory/${item.type}/${item.name}`;
    }

    const response = await axios.get(deleteUrl);

    if (response.data.status) {
      items.value = items.value.filter(i => i.name !== item.name);
    } else {
      alert(`Failed to delete: ${response.data.message}`);
    }

  } catch (e) {
    console.error("Delete failed", e);
    alert("Network error while deleting.");
  }
};

// 3. LOAD DATA (Fixed Logic)
const fetchData = async () => {
  items.value = [];
  
  // ERROR WAS HERE: 'page' was undefined. Switched to 'props.pageType'
  try {
    let apiUrl = '';
    if (props.pageType === 'rack') {
      apiUrl = Url + '/manage_racks';
    } else if (props.pageType === 'inventory') {
      apiUrl = Url + '/manage_inventory';
    } else {
      return; 
    }

    const response = await axios.get(apiUrl);
    
    if (response.data.status) {
      const rawMsg = response.data.message;
      if (Array.isArray(rawMsg)) {
        items.value = rawMsg.flat(); 
      } else if (typeof rawMsg === 'object') {
        items.value = Object.values(rawMsg);
      }
    }
  } catch (e) {
    console.error("Failed to load table data", e);
  }
};

onMounted(fetchData);

// Watch for changes in the prop (in case user switches menu items rapidly)
watch(() => props.pageType, fetchData);
</script>

<style scoped>
.btn-icon { border: none; background: transparent; }
.bx { font-size: 1.2rem; }
</style>