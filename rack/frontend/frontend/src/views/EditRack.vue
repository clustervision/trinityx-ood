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
import axios from 'axios';
const Url = 'https://yixin3-dev-ctrl001:7755';


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
onMounted(async () => {
  const rackName = route.params.id as string;
  form.name = rackName;
  
  try {
    // New Backend Route: /show_rack/<rack_name>
    const response = await axios.get(Url + `/show_rack/${rackName}`);
    
    // structure: { message: { name: '...', site: '...', ... } }
    const rackData = response.data.message; 

    if (rackData) {
      form.site = rackData.site || '';
      form.room = rackData.room || '';
      form.order = (rackData.order || 'ascending').toLowerCase();
      form.size = rackData.size;
    } else {
      errorMessage.value = `Rack '${rackName}' details not found in response.`;
    }

  } catch (e) {
    console.error("Failed to load rack details", e);
    errorMessage.value = "Failed to load rack details.";
  }
});

// 2. Submit Update
const submitForm = async () => {
  isSubmitting.value = true;
  errorMessage.value = '';

  try {
    // Backend expects Form Data (request.form)
    const params = new URLSearchParams();
    params.append('name', form.name);
    params.append('site', form.site);
    params.append('room', form.room);
    params.append('order', form.order);
    params.append('size', form.size.toString());

    const response = await axios.post(Url + '/change_rack', params);

    // Backend returns { status: true, message: '...' }
    if (response.data.status) {
      router.push(Url+'/manage_racks');
    } else {
      errorMessage.value = response.data.message || "Update failed.";
    }
  } catch (error: any) {
    console.error(error);
    errorMessage.value = error.response?.data?.message || "Network error.";
  } finally {
    isSubmitting.value = false;
  }
};
</script>