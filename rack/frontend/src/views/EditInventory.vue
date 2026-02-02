<template>
  <div class="container-fluid flex-grow-1 container-p-y">
    <div class="card mb-4">
      <div class="card-header d-flex align-items-center justify-content-between">
        <h5 class="mb-0">Update Inventory - {{ form.name }}</h5>
         <button class="btn btn-warning" @click="$emit('close')">Back</button>
      </div>

      <div class="card-body">
        <div v-if="isAssigned" class="alert alert-warning mb-3">
          <i class='bx bx-lock-alt'></i>
          This device is currently placed in a rack. Data cannot be changed.
        </div>
        <form @submit.prevent="submitForm">

          <div class="row mb-3">
            <label class="col-sm-2 col-form-label text-uppercase fs-7">Name</label>
            <div class="col-sm-10">
              <input
                type="text"
                v-model="form.name"
                class="form-control bg-light"
                :disabled="isAssigned"
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
                :disabled="isAssigned"
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
                :disabled="isAssigned"
              />
            </div>
          </div>

          <div class="row mb-3">
            <label class="col-sm-2 col-form-label text-uppercase fs-7">Inventory Orientation</label>
            <div class="col-sm-10">
              <select
                v-model="form.orientation"
                class="form-select"
                required
                :disabled="isAssigned"
              >
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
                :disabled="isSubmitting || isAssigned"
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
import { ref, reactive, onMounted,watch, useAttrs } from 'vue';
import axios from 'axios';
import { useToast } from 'vue-toastification';

//@ts-ignore
const Url = window.APP_URL;
const toast = useToast();
const isAssigned = ref(false);
const props = defineProps<{
  inventoryName: string;
}>();


// Note: Ensure you have 'inventory-updated' here if you need the parent to refresh
const emit = defineEmits(['close', 'inventory-updated']);

const isSubmitting = ref(false);
const errorMessage = ref('');

const form = reactive({
  name: '',
  type: '',
  height: 1,
  orientation: 'front'
});


const loadInventoryData=async () => {
  const inventoryName = props.inventoryName;
  if (!inventoryName) return ;

  form.name = inventoryName;

  try {
    const response = await axios.get(Url + '/manage_inventory');

    let items = [];
    if (response.data.status && Array.isArray(response.data.message)) {
      items = response.data.message;
    }

    const target = items.find((i: any) => i.name === inventoryName);

    if (target) {
      form.type = target.type;
      form.height = parseInt(target.height) || 1;
      form.orientation = target.orientation || 'front';
    } else {
      errorMessage.value = `Inventory item '${inventoryName}' not found.`;
    }
    const poolResponse = await axios.get(Url + '/device_pool');
    const poolItems = poolResponse.data.message || [];

    const isInPool = poolItems.find((p: any) => p.name === inventoryName);
    isAssigned.value = !isInPool;
  } catch (e) {
    console.error("Failed to load details", e);
    errorMessage.value = "Failed to load details.";
  }
};

const submitForm = async () => {
  // MODIFIED: Guard Clause - Totally forbid action if assigned
  if (isAssigned.value) {
    errorMessage.value = "Action Forbidden: This device is currently in a rack.";
    return;
  }

  isSubmitting.value = true;
  try {
    const params = new URLSearchParams();
    params.append('name', form.name);
    params.append('type', form.type);
    params.append('height', form.height.toString());
    params.append('orientation', form.orientation);

    const response = await axios.post(Url + '/change_inventory', params);

    if (response.data.status) {
      emit('inventory-updated'); // Ensure pool refreshes
      emit('close');
      toast.success(`${form.name} Updated.`);
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

watch(() => props.inventoryName, loadInventoryData);
</script>

<style scoped>
.fs-7 { font-size: 0.85rem; font-weight: 500; color: #566a7f; }
</style>
