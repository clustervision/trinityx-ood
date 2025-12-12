<template>
  <div class="container-fluid flex-grow-1 container-p-y">
    <div class="card mb-4">
      <div class="card-header d-flex align-items-center justify-content-between">
        <h5 class="mb-0">Update Inventory - {{ form.name }}</h5>
        <small class="text-muted float-end">Change values here...</small>
        <button class="btn btn-warning" @click="$router.push('/manage/inventory')">
          Back
        </button>
      </div>
      
      <div class="card-body">
        <form @submit.prevent="submitForm">
          
          <div class="row mb-3">
            <label class="col-sm-2 col-form-label text-uppercase fs-7">Name</label>
            <div class="col-sm-10">
              <input 
                type="text" 
                v-model="form.name" 
                class="form-control bg-light" 
                readonly 
              />
            </div>
          </div>

          <div class="row mb-3">
            <label class="col-sm-2 col-form-label text-uppercase fs-7">Select Type</label>
            <div class="col-sm-10">
              <input 
                type="text" 
                v-model="form.type" 
                class="form-control bg-light" 
                readonly 
              />
            </div>
          </div>

          <div class="row mb-3">
            <label class="col-sm-2 col-form-label text-uppercase fs-7">Inventory Height</label>
            <div class="col-sm-10">
              <input 
                type="number" 
                v-model="form.height" 
                class="form-control" 
                min="1" 
                max="80" 
                required 
              />
            </div>
          </div>

          <div class="row mb-3">
            <label class="col-sm-2 col-form-label text-uppercase fs-7">Inventory Orientation</label>
            <div class="col-sm-10">
              <select v-model="form.orientation" class="form-select" required>
                <option value="front">Front Side</option>
                <option value="back">Back Side</option>
              </select>
            </div>
          </div>

          <div class="row mt-4">
            <div class="col-sm-10 offset-sm-2">
              <button 
                type="submit" 
                class="btn btn-primary" 
                :disabled="isSubmitting"
              >
                {{ isSubmitting ? 'Updating...' : 'Update Inventory ' + form.name }}
              </button>
            </div>
          </div>

          <div v-if="errorMessage" class="alert alert-danger mt-3">{{ errorMessage }}</div>

        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
// Import helper to reuse parsing logic
import { parseHtmlToData } from '@/utils/rackHelpers'; 

const route = useRoute();
const router = useRouter();
const isSubmitting = ref(false);
const errorMessage = ref('');

const form = reactive({
  name: '',
  type: '',
  height: 1,
  orientation: 'front'
});

// 1. Load Data
onMounted(async () => {
  const inventoryName = route.params.id as string;
  form.name = inventoryName;

  try {
    // Fetch the full inventory list to find this specific item
    // (Since we don't have a single-item API endpoint)
    const res = await fetch('/manage/inventory', { 
      headers: { 'Accept': 'application/json, text/html' } 
    });

    const contentType = res.headers.get('content-type');
    let items: any[] = [];

    if (contentType && contentType.includes('application/json')) {
      const json = await res.json();
      // Handle Inventory format
      items = json.inventory || [];
    } else {
      // Fallback for HTML
      const html = await res.text();
      items = parseHtmlToData(html);
    }

    // Find the item
    const target = items.find((i: any) => i.name === inventoryName);
    
    if (target) {
      form.type = target.type;
      form.height = parseInt(target.height) || 1;
      form.orientation = target.orientation || 'front';
    } else {
      errorMessage.value = `Inventory item '${inventoryName}' not found.`;
    }

  } catch (e) {
    console.error("Failed to load details", e);
    errorMessage.value = "Failed to load details.";
  }
});

// 2. Submit Update
const submitForm = async () => {
  isSubmitting.value = true;
  try {
    const params = new URLSearchParams();
    // The backend expects these specific field names based on 'change.html'
    params.append('name', form.name);
    params.append('type', form.type);
    params.append('height', form.height.toString());
    params.append('orientation', form.orientation);

    // POST to /edit/inventory/nodeName
    const response = await fetch(`/edit/inventory/${form.name}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: params
    });

    if (response.ok || response.status === 302 || response.status === 500) {
      router.push('/manage/inventory');
    } else {
      const text = await response.text();
      errorMessage.value = `Update failed: ${text}`;
    }
  } catch (error) {
    errorMessage.value = "Network error.";
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
/* Minor styling tweaks to match screenshot labels */
.fs-7 { font-size: 0.85rem; font-weight: 500; color: #566a7f; }
</style>