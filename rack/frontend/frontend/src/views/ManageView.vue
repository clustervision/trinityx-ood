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
                   <button class="btn btn-icon btn-sm" title="Edit" @click="$emit('edit-click', item)">
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
import axios from 'axios';

const Url = 'https://yixin3-dev-ctrl001:7755';
const items = ref<any[]>([]);

const props = defineProps<{
  pageType: string 
}>();

// Define Events to tell App.vue what to do
const emit = defineEmits(['add-click', 'edit-click']);

const pageName = computed(() => {
  if (!props.pageType) return '';
  return props.pageType.charAt(0).toUpperCase() + props.pageType.slice(1);
});

// DELETE remains local because it's just an API call
const deleteItem = async (item: any) => {
  if (!confirm(`Are you sure you want to delete ${item.name}?`)) return;

  try {
    let url = '';
    if (props.pageType === 'rack') {
      url =  `/delete_rack/${item.name}`;
    } else {
      url = `/delete_inventory/${item.type}/${item.name}`;
    }

    const response = await axios.get(url);

    if (response.data.status) {
      items.value = items.value.filter(i => i.name !== item.name);
    } else {
      alert(`Failed to delete: ${response.data.message}`);
    }

  } catch (e) {
    console.error("Delete failed", e);
    alert("Network error.");
  }
};

const fetchData = async () => {
  items.value = [];

  try {
    let url = '';
    if (props.pageType === 'rack') {
      url = Url + '/manage_racks';
    } else if (props.pageType === 'inventory') {
      url = Url + '/manage_inventory';
    } else {
      return; 
    }

    const response = await axios.get(url);
    
    if (response.data.status) {
      const rawMsg = response.data.message;
      if (Array.isArray(rawMsg)) {
        const extractedItems: any[] = [];

        rawMsg.forEach((entry: any) => {
          if (entry.name && (entry.size || entry.type)) {
            extractedItems.push(entry);
          } else {
            const innerValues = Object.values(entry);
            extractedItems.push(...innerValues);
          }
        });

        items.value = extractedItems;
      } 
      else if (typeof rawMsg === 'object' && rawMsg !== null) {
         items.value = Object.values(rawMsg);
      }
    }
  } catch (e) {
    console.error("Failed to load table data", e);
  }
};

onMounted(fetchData);
watch(() => props.pageType, fetchData);
</script>