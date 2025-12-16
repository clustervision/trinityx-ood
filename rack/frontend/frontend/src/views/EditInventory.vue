<template>
  <div class="container-fluid flex-grow-1 container-p-y">
    <div class="card mb-4">
      <div class="card-header d-flex align-items-center justify-content-between">
        <h5 class="mb-0">Update Inventory - {{ form.name }}</h5>
        <small class="text-muted float-end">Change values here...</small>
         <button class="btn btn-warning" @click="$emit('close')">Back</button>
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
import { ref, reactive, onMounted,watch } from 'vue';
import axios from 'axios';
const Url = 'https://yixin3-dev-ctrl001:7755';


// 1. DEFINE PROPS (Replaces route.params)
const props = defineProps<{
  InventoryName: string // Passed from App.vue
}>();

// 2. DEFINE EMITS (Replaces router.push)
const emit = defineEmits(['close']);

const isSubmitting = ref(false);
const errorMessage = ref('');

const form = reactive({
  name: '',
  type: '',
  height: 1,
  orientation: 'front'
});

// 1. Load Data
const loadInventoryData=async () => {
  const inventoryName = props.InventoryName;
  if (!inventoryName) return ;

  form.name = inventoryName;

  try {
    // No specific /show_inventory endpoint, so we fetch all to find the match
    const response = await axios.get(Url + '/manage_inventory');

    let items = [];
    if (response.data.status && Array.isArray(response.data.message)) {
      items = response.data.message;
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
};

// 2. Submit Update
const submitForm = async () => {
  isSubmitting.value = true;
  try {
    const params = new URLSearchParams();
    params.append('name', form.name);
    params.append('type', form.type);
    params.append('height', form.height.toString());
    params.append('orientation', form.orientation);

    // Backend route: /change_inventory
    const response = await axios.post(Url + '/change_inventory', params);

    if (response.data.status) {
      emit('close');
    } else {
      errorMessage.value = response.data.message || 'Update failed';
    }
  } catch (error: any) {
    errorMessage.value = error.response?.data?.message || "Network error.";
  } finally {
    isSubmitting.value = false;
  }
};

onMounted(() => {
  loadInventoryData();
});

watch(() => props.InventoryName, loadInventoryData);
</script>

<style scoped>
.fs-7 { font-size: 0.85rem; font-weight: 500; color: #566a7f; }
</style>