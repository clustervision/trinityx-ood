<template>
  <div class="container-fluid flex-grow-1 container-p-y">
    <div class="card">
      <h5 class="card-header d-flex justify-content-between align-items-center">
        Manage {{ pageName }}
        
        <button v-if="pageType === 'rack'" class="btn btn-success btn-sm">
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
                <th class="text-center">Room</th> <th class="text-center">Site</th> <th class="text-center">Actions</th>
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
                   <td class="text-center">{{ item.order || 'Ascending' }}</td>
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
                   <button class="btn btn-icon btn-sm" title="Edit">
                     <i class='bx bx-edit text-primary'></i>
                   </button>
                   <button class="btn btn-icon btn-sm" title="Delete">
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
import { useRoute } from 'vue-router';

const route = useRoute();
const pageType = ref(''); 
const items = ref<any[]>([]);

const pageName = computed(() => {
  return pageType.value === 'rack' ? 'Rack Frames' : 'Inventory';
});

const fetchData = async () => {
  const page = route.params.page as string;
  pageType.value = page;
  items.value = [];

  try {
    const res = await fetch(`/manage/${page}`);
    const json = await res.json();
    
    if (page === 'inventory') {
      // Backend already sends this correctly
      items.value = json.inventory || [];
    } 
    else if (page === 'rack') {
      // THIS IS WHERE WE NEED THE BACKEND FIX
      // Currently json.racks is missing. Once they add it, this will work:
      if (json.racks) {
        items.value = Object.keys(json.racks).map(key => ({
          name: key,
          size: json.racks[key].size,
          order: json.racks[key].order,
          room: json.racks[key].room,
          site: json.racks[key].site
        }));
      } else {
        console.warn("Backend did not return 'racks' list.");
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