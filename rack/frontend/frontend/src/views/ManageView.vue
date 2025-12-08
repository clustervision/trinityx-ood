<template>
  <div class="container-fluid flex-grow-1 container-p-y">
    <div class="card">
      <h5 class="card-header">
        Manage {{ pageName }}
        <button class="btn btn-success float-end btn-sm">Add New {{ pageName }}</button>
      </h5>
      <div class="card-body">
        <div class="table-responsive text-nowrap">
          <table class="table table-bordered">
            <thead>
              <tr>
                <th>Name</th>
                <th>Size</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in items" :key="item.name">
                <td>{{ item.name }}</td>
                <td>{{ item.size || 'N/A' }}</td>
                <td>
                   <button class="btn btn-xs btn-primary">Edit</button>
                   <button class="btn btn-xs btn-danger">Delete</button>
                </td>
              </tr>
              <tr v-if="items.length === 0">
                <td colspan="3" class="text-center">No {{ pageName }} Available.</td>
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
  // Extract "rack" or "inventory" from URL
  const page = route.params.page as string;
  pageName.value = page.charAt(0).toUpperCase() + page.slice(1);
  
  try {
    // You need to create this API endpoint in app.py!
    const res = await fetch(`/api/manage/${page}`);
    const data = await res.json();
    items.value = data.items; 
  } catch (e) {
    console.error("Failed to load data", e);
    // Mock data for now so you see SOMETHING
    items.value = [{ name: "Mock-Item-1", size: 42 }];
  }
};

// Fetch data when component loads
onMounted(fetchData);
// Re-fetch if user clicks "Manage Inventory" while on "Manage Rack"
watch(() => route.params.page, fetchData);
</script>