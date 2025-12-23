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

const Url = 'https://yixin3-dev-ctrl001:7755';
const items = ref<any[]>([]);
const toast = useToast()
const props = defineProps<{
  pageType: string 
}>();

const emit = defineEmits(['add-click', 'edit-click', 'show-click']);

const pageName = computed(() => {
  if (!props.pageType) return '';
  return props.pageType.charAt(0).toUpperCase() + props.pageType.slice(1);
});

const deleteItem = async (item: any) => {
  if (!confirm(`Are you sure you want to delete ${item.name}?`)) return;

  const previousItems = [...items.value]; 
  items.value = items.value.filter(i => String(i.name) !== String(item.name));

  try {
    const timestamp = new Date().getTime();
    let deleteUrl = '';
    
    if (props.pageType === 'rack') {
      deleteUrl = Url + `/delete_rack/${item.name}?t=${timestamp}`;
    } else {
      deleteUrl = Url + `/delete_inventory/${item.type}/${item.name}?t=${timestamp}`;
    }
    await axios.get(deleteUrl);
    if (deleteUrl === Url + `/delete_rack/${item.name}?t=${timestamp}`)
      toast.success(`Rack Delete\n Rack ${item.name} is deleted.`);
    else
      toast.success(`Rack Update\n${item.name} Removed from Rack\.`);
    console.log("Delete confirmed by backend.");

  } catch (e: any) {
    // Check if it is the "CORS Success" case
    // (Axios reports "Network Error" when CORS blocks a 200 OK response)
    // if (e.message === "Network Error" && !e.response) {
    //    console.warn("Backend deleted it (Status 200), but Browser blocked the receipt. Keeping it deleted.");
    // } 
    // else {
       console.error("Delete failed", e);
       items.value = previousItems; 
       alert("Failed to delete. The item has been restored.");
    // }
  }
};

const fetchData = async () => {
  items.value = [];
  try {
    const timestamp = new Date().getTime();
    let fetchUrl = '';
    if (props.pageType === 'rack') fetchUrl = Url + `/manage_racks?t=${timestamp}`;
    else if (props.pageType === 'inventory') fetchUrl = Url + `/manage_inventory?t=${timestamp}`;
    else return;

    const response = await axios.get(fetchUrl);
    
    const rawMsg = response.data.message;
    if (Array.isArray(rawMsg)) {
        const extractedItems: any[] = [];
        rawMsg.forEach((entry: any) => {
          if (entry.name && (entry.size || entry.type)) extractedItems.push(entry);
          else extractedItems.push(...Object.values(entry));
        });
        items.value = extractedItems;
    } else if (typeof rawMsg === 'object' && rawMsg !== null) {
         items.value = Object.values(rawMsg);
    }

  } catch (e) {
    console.error("Failed to load table data", e);
  }
};

onMounted(fetchData);
watch(() => props.pageType, fetchData);
</script>

<style scoped>
.fs-4 { font-size: 1.3rem !important; }
a { text-decoration: none; }
a:hover { opacity: 0.8; }
</style>