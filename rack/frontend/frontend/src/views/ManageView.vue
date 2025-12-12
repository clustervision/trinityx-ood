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
import { parseHtmlToData } from '@/utils/rackHelpers';

const route = useRoute();
const router = useRouter();
const pageType = ref(''); 
const items = ref<any[]>([]);

const pageName = computed(() => {
  if (!pageType.value) return '';
  return pageType.value.charAt(0).toUpperCase() + pageType.value.slice(1);
});

const goToAddPage = () => {
  // Suggestion: Use lowercase 'rack' to avoid backend case-sensitivity issues
  router.push('/edit/rack'); 
};

// 1. EDIT ACTION
// In src/views/ManageView.vue

const editItem = (item: any) => {
  if (pageType.value === 'rack') {
    router.push(`/edit/rack/${item.name}`);
  } else if (pageType.value === 'inventory') {
    router.push(`/edit/inventory/${item.name}`);
  }
};

// 2. DELETE ACTION (FIXED LOGIC)
const deleteItem = async (item: any) => {
  if (!confirm(`Are you sure you want to delete ${item.name}?`)) return;

  const nameToCheck = item.name;

  try {
    let url = '';
    if (pageType.value === 'rack') {
      url = `/delete/rack/${item.name}`;
    } else {
      url = `/delete/inventory/${item.name}/${item.type}`;
    }

    // FIX: Use 'fetch', not 'fetchData'
    const res = await fetch(url);

    // Because your backend returns the HTML of the list page (redirect),
    // we use that HTML to verify if the item is actually gone.
    const htmlResponse = await res.text();
    const currentItems = parseHtmlToData(htmlResponse);
    
    // Check if the item is still in the list returned by the server
    const stillExists = currentItems.find((i: any) => i.name === nameToCheck);

    if (!stillExists) {
      // Success: Update the view with the new list
      items.value = currentItems;
      // Optional: alert(`${nameToCheck} deleted successfully.`);
    } else {
      // Failure: The backend refused to delete it (e.g., Rack not empty)
      alert(`Failed to delete '${nameToCheck}'. The server did not remove it (Rack might not be empty).`);
    }

  } catch (e) {
    console.error("Delete failed", e);
    alert("Network error while deleting.");
  }
};

// 3. LOAD DATA
// src/views/ManageView.vue

const fetchData = async () => {
  const page = route.params.page as string;
  pageType.value = page;
  items.value = [];

  try {
    // We accept both JSON and HTML because we aren't sure which one your specific backend version sends
    const res = await fetch(`/manage/${page}`, { 
      headers: { 'Accept': 'application/json, text/html' } 
    });
    
    const contentType = res.headers.get('content-type');
    
    // CASE A: Backend returns JSON (wrapper)
    if (contentType && contentType.includes('application/json')) {
      const json = await res.json();
      
      if (page === 'inventory') {
        items.value = json.inventory || [];
      } 
      else if (page === 'rack') {
        // THIS WAS MISSING! 
        // If rack returns JSON, the HTML table is inside json.data
        if (json.data) {
          items.value = parseHtmlToData(json.data);
        }
      }
    } 
    // CASE B: Backend returns raw HTML
    else {
      const html = await res.text();
      items.value = parseHtmlToData(html);
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