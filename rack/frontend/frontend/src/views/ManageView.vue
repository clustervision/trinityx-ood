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
                   <td class="text-center">{{ item.order}}</td>
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
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const pageType = ref(''); 
const items = ref<any[]>([]);

const pageName = computed(() => {
  if (!pageType.value) return '';
  return pageType.value.charAt(0).toUpperCase() + pageType.value.slice(1);
});

const fetchData = async () => {
  const page = route.params.page as string;
  pageType.value = page;
  items.value = [];

  try {
    const res = await fetch(`/manage/${page}`);
    const json = await res.json();
    
    if (page === 'inventory') {
      items.value = json.inventory || [];
    } 
    else if (page === 'rack') {
      if (json.data) {
        items.value = parseHtmlToData(json.data);
      } else {
        console.warn("Backend returned no data field.");
      }
    }
  } catch (e) {
    console.error("Failed to load table data", e);
  }
};

const goToAddPage = () => {
  router.push('/edit/Rack'); 
};

function parseHtmlToData(htmlString: string) {
  const parser = new DOMParser();
  const doc = parser.parseFromString(htmlString, 'text/html');
  const rows = doc.querySelectorAll('tr'); 
  const parsedData: any[] = [];

  rows.forEach((row) => {
    const cells = row.querySelectorAll('td');
    if (cells.length > 1) {
      parsedData.push({
        name: cells[1]?.innerText.trim(),
        size: cells[2]?.innerText.trim(),
        order: cells[3]?.innerText.trim(),
        room: cells[4]?.innerText.trim(),
        site: cells[5]?.innerText.trim(),
      });
    }
  });

  return parsedData;
}

onMounted(fetchData);
watch(() => route.params.page, fetchData);
</script>

<style scoped>
.btn-icon { border: none; background: transparent; }
.bx { font-size: 1.2rem; }
</style>