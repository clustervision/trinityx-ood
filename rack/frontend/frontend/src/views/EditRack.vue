<template>
  <div class="container-fluid flex-grow-1 container-p-y">
    <div class="card mb-4">
      <div class="card-header d-flex align-items-center justify-content-between">
        <h5 class="mb-0">Update Rack - {{ form.name }}</h5>
        
        <button class="btn btn-warning" @click="$emit('close')">Back</button>
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
import { ref, reactive, onMounted, watch } from 'vue';
import axios from 'axios';
import { useToast } from 'vue-toastification';

const Url = 'https://yixin3-dev-ctrl001:7755';
const toast = useToast()
// 1. DEFINE PROPS (Replaces route.params)
const props = defineProps<{
  rackName: string // Passed from App.vue
}>();

// 2. DEFINE EMITS (Replaces router.push)
const emit = defineEmits(['close']);

const isSubmitting = ref(false);
const errorMessage = ref('');

const form = reactive({
  name: '',
  site: '',
  room: '',
  order: '',
  size: ''
});

// Load Data Function
const loadRackData = async () => {
  // Use prop instead of route param
  const rackName = props.rackName;
  if (!rackName) return;

  form.name = rackName;
  
  try {
    const timestamp = new Date().getTime();
    const response = await axios.get(Url + `/show_rack/${props.rackName}?t=${timestamp}`);
    const rackData = response.data.message; 

    if (rackData) {
      form.site = rackData.site || '';
      form.room = rackData.room || '';
      form.order = (rackData.order || 'ascending').toLowerCase();
      form.size = rackData.size;
    } else {
      errorMessage.value = `Rack '${rackName}' details not found.`;
    }

  } catch (e) {
    console.error("Failed to load rack details", e);
    errorMessage.value = "Failed to load rack details.";
  }
};

onMounted(() => {
  loadRackData();
});

// Optional: Watch prop if the component stays open while ID changes
watch(() => props.rackName, loadRackData);

const submitForm = async () => {
  isSubmitting.value = true;
  errorMessage.value = '';

  try {
    const params = new URLSearchParams();
    params.append('name', form.name);
    params.append('site', form.site);
    params.append('room', form.room);
    params.append('order', form.order);
    params.append('size', form.size.toString());

    const response = await axios.post(Url + '/change_rack', params);

    if (response.data.status) {
      // 3. EMIT CLOSE ON SUCCESS (Parent will switch view back)
      emit('close');
      toast.success(`Rack ${form.name} Updated.`);
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