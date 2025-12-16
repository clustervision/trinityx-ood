<template>
  <div class="container-fluid flex-grow-1 container-p-y">
    <div class="card">
      <h5 class="card-header d-flex justify-content-between align-items-center">
        Manage {{ pageName }} Frames
        
        <button 
          v-if="pageType === 'rack'" 
          class="btn btn-success btn-sm" 
          @click="goToAddPage"
        >
          Add New {{ pageName }}
        </button>
      </h5>
      
      <div class="card-body">
        <div class="table-responsive text-nowrap">
          <table class="table table-bordered table-hover table-striped">
            <thead>
              <tr v-if="pageType === 'rack'">
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
                
                <template v-if="pageType === 'rack'">
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
                 <td :colspan="pageType === 'rack' ? 7 : 6" class="text-center">
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
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import type RackView from './RackView.vue';

const Url = 'https://yixin3-dev-ctrl001:7755';
const route = useRoute();
const router = useRouter();
const pageType = ref(''); 
const items = ref<any[]>([]);

const pageName = computed(() => {
  if (!pageType.value) return '';
  return pageType.value.charAt(0).toUpperCase() + pageType.value.slice(1);
});

const goToAddPage = () => {
  router.push(Url + '/change_rack'); 
};

// 1. EDIT ACTION
const editItem = (item: any) => {
  if (pageType.value === 'rack') {
    router.push(Url +`'/change_rack'${item.name}`);
  } else if (pageType.value === 'inventory') {
    router.push(Url+`'/change_rack'${item.name}`);
  }
};

// 2. DELETE ACTION
const deleteItem = async (item: any) => {
  if (!confirm(`Are you sure you want to delete ${item.name}?`)) return;

  try {
    let url = '';
    if (pageType.value === 'rack') {
      url = Url +`/delete_rack/${item.name}`;
    } else {
      url = Url + `/delete_inventory/${item.type}/${item.name}`;
    }

    const response = await axios.get(url);

    if (response.data.status) {
      // Success: Remove item locally to update UI immediately
      items.value = items.value.filter(i => i.name !== item.name);
      // Optional: alert(response.data.message);
    } else {
      alert(`Failed to delete: ${response.data.message}`);
    }

  } catch (e) {
    console.error("Delete failed", e);
    alert("Network error while deleting.");
  }
};

// 3. LOAD DATA
const fetchData = async () => {
  const page = route.params.page as string;
  pageType.value = page;
  items.value = [];

  try {
    let url = '';
    if (page === 'rack') {
      url = Url + '/manage_racks';
    } else if (page === 'inventory') {
      url =Url +  '/manage_inventory';
    } else {
      return; 
    }

    const response = await axios.get(url);
    
    // Check backend status
    if (response.data.status) {
      
      const rawMsg = response.data.message;
      
      if (Array.isArray(rawMsg)) {
        // If Python did .append(list), we get [[obj, obj]]. Flatten handles it.
        items.value = rawMsg.flat(); 
      } else if (typeof rawMsg === 'object') {
          // Fallback if it returns a single dict object instead of list
          items.value = Object.values(rawMsg);
      }
    }

  } catch (e) {
    console.error("Failed to load table data", e);
  }
};

onMounted(fetchData);
watch(() => route.params.page, fetchData);
</script>

<style scoped>
.btn-icon { border: none; background: transparent; }
.bx { font-size: 1.2rem; }
</style>