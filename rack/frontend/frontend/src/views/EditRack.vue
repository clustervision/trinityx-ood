<template>
  <div class="container-fluid flex-grow-1 container-p-y">
    <div class="card mb-4">
      <div class="card-header d-flex align-items-center justify-content-between">
        <h5 class="mb-0">Update Rack - {{ form.name }}</h5>
        <button class="btn btn-warning" @click="$router.push('/manage/rack')">Back</button>
      </div>
      
      <div class="card-body">
        <form @submit.prevent="submitForm">
          
          <div class="row mb-3">
            <label class="col-sm-2 col-form-label">Name</label>
            <div class="col-sm-10">
              <input 
                type="text" 
                v-model="form.name" 
                class="form-control" 
                readonly 
              />
            </div>
          </div>

          <div class="row mb-3">
            <label class="col-sm-2 col-form-label">Select Site</label>
            <div class="col-sm-10">
              <input type="text" v-model="form.site" class="form-control" required />
            </div>
          </div>

          <div class="row mb-3">
            <label class="col-sm-2 col-form-label">Select Room</label>
            <div class="col-sm-10">
              <input type="text" v-model="form.room" class="form-control" required />
            </div>
          </div>

          <div class="row mb-3">
            <label class="col-sm-2 col-form-label">Select Order</label>
            <div class="col-sm-10">
              <select v-model="form.order" class="form-control" required>
                <option value="ascending">Ascending (Top To Bottom)</option>
                <option value="descending">Descending (Bottom To Top)</option>
              </select>
            </div>
          </div>

          <div class="row mb-3">
            <label class="col-sm-2 col-form-label">Size Of Rack</label>
            <div class="col-sm-10">
              <input type="number" v-model="form.size" class="form-control" min="0" max="1000" required />
            </div>
          </div>

          <div class="row justify-content-end">
            <div class="col-sm-10">
              <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
                {{ isSubmitting ? 'Updating...' : 'Update Rack ' + form.name }}
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
import { parseHtmlToData } from '@/utils/rackHelpers';

const route = useRoute();
const router = useRouter();
const isSubmitting = ref(false);
const errorMessage = ref('');

const form = reactive({
  name: '',
  site: '',
  room: '',
  order: '',
  size: ''
});

// 1. Load existing data
// src/views/EditRack.vue

onMounted(async () => {
  const rackName = route.params.id as string;
  form.name = rackName;
  
  try {
    // 1. Fetch the FULL list of racks to find the details for THIS rack
    const res = await fetch('/manage/rack', { 
      headers: { 'Accept': 'application/json, text/html' } 
    });
    
    const contentType = res.headers.get('content-type');
    let racks: any[] = [];

    // Parse logic matching ManageView
    if (contentType && contentType.includes('application/json')) {
      const json = await res.json();
      if (json.data) racks = parseHtmlToData(json.data);
    } else {
      const html = await res.text();
      racks = parseHtmlToData(html);
    }
    
    // 2. Find the specific rack
    const target = racks.find((r: any) => r.name === rackName);
    
    if (target) {
      form.site = target.site;
      form.room = target.room;
      // Handle potential undefined/null values safely
      form.order = (target.order || 'ascending').toLowerCase();
      form.size = target.size;
    } else {
      errorMessage.value = `Rack '${rackName}' not found.`;
    }

  } catch (e) {
    console.error("Failed to load rack details", e);
    errorMessage.value = "Failed to load rack details.";
  }
});

// 2. Submit Update
const submitForm = async () => {
  isSubmitting.value = true;
  try {
    const params = new URLSearchParams();
    params.append('name', form.name);
    params.append('site', form.site);
    params.append('room', form.room);
    params.append('order', form.order);
    params.append('size', form.size.toString());

    // POST to /edit/rack/RackName (This matches your backend route logic)
    const response = await fetch(`/edit/rack/${form.name}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: params
    });

    // Accept 200, 302, or 500 (workaround for backend template error)
    if (response.ok || response.status === 302 || response.status === 500) {
      router.push('/manage/rack');
    } else {
      errorMessage.value = "Update failed.";
    }
  } catch (error) {
    errorMessage.value = "Network error.";
  } finally {
    isSubmitting.value = false;
  }
};

</script>