<template>
  <div class="container-fluid flex-grow-1 container-p-y">
    <div class="card">
      <h5 class="card-header d-flex justify-content-between align-items-center">
        Manage {{ pageName }}
        <button class="btn btn-success btn-sm">Add New {{ pageName }}</button>
      </h5>
      <div class="card-body">
        <div class="table-responsive text-nowrap">
          <table class="table table-bordered table-hover table-striped">
            <thead>
              <tr>
                <th class="text-center">Name</th>
                <th class="text-center">Type</th>
                <th class="text-center">Height</th>
                <th class="text-center">Orientation</th>
                <th class="text-center">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in items" :key="index">
                <td class="text-center">{{ item.name }}</td>
                <td class="text-center">{{ item.type }}</td>
                <td class="text-center">{{ item.height }}</td>
                <td class="text-center">{{ item.orientation }}</td>
                <td class="text-center">
                   <button class="btn btn-icon btn-sm" title="Edit">
                     <i class='bx bx-edit text-primary'></i>
                   </button>
                   <button class="btn btn-icon btn-sm" title="Delete">
                     <i class='bx bx-trash text-danger'></i>
                   </button>
                </td>
              </tr>
              <tr v-if="items.length === 0">
                <td colspan="5" class="text-center">No {{ pageName }} Available.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const pageName = ref('');
const items = ref<any[]>([]);

const fetchData = async () => {
  const page = route.params.page as string;
  pageName.value = page.charAt(0).toUpperCase() + page.slice(1);
  
  // Clear previous items
  items.value = [];

  try {
    // 1. Fetch from the specific manage endpoint
    const res = await fetch(`/manage/${page}`);
    
    if (!res.ok) throw new Error("Backend connection failed");

    const json = await res.json();
    
    // 2. LOGIC: Decide which data to show based on the page
    if (page === 'inventory') {
      // The backend sends the list in the 'inventory' key
      items.value = json.inventory || [];
    } 
    else if (page === 'rack') {
      // CURRENT PROBLEM: Your /manage/rack endpoint returns empty data.
      // WORKAROUND: We will fetch from /api/racks instead for now.
      const fallbackRes = await fetch('/api/racks');
      const fallbackJson = await fallbackRes.json();
      
      // Convert the Rack Object (Dictionary) into a List for the table
      // Backend sends: { "Rack1": {size:42}, "Rack2": {size:42} }
      if (fallbackJson.racks) {
        items.value = Object.keys(fallbackJson.racks).map(key => ({
          name: key,
          type: 'Rack Frame',
          height: fallbackJson.racks[key].size + 'U',
          orientation: 'Vertical'
        }));
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
/* Add some spacing to icons */
.btn-icon { border: none; background: transparent; }
.bx { font-size: 1.2rem; }
</style>