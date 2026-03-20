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
                v-model.number="form.height"
                class="form-control"
                :min="heightMin"
                max="8"
                required
                :disabled="isAssigned"
              />
              <small v-if="isOtherDevices" class="text-muted">otherdevices: 0U (pool only) or 1–8U. Max 8U.</small>
              <small v-else class="text-muted">Height 1–8U (other types cannot be 0).</small>
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
import { ref, reactive, onMounted, watch, computed } from 'vue';
import axios from 'axios';
import { useToast } from 'vue-toastification';
import { deviceHeightU, isOtherDevicesType } from '@/utils/deviceKind';

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

const isOtherDevices = computed(() => isOtherDevicesType(form.type));
const heightMin = computed(() => (isOtherDevices.value ? 0 : 1));


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
      const parsedH = parseInt(String(target.height), 10);
      const defaultH = isOtherDevicesType(target.type) ? 0 : 1;
      form.height = Number.isFinite(parsedH) ? parsedH : defaultH;
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
  const h = parseInt(String(form.height), 10);
  const minH = isOtherDevicesType(form.type) ? 0 : 1;
  if (isNaN(h) || h < minH || h > 8) {
    errorMessage.value = minH === 0
      ? 'For otherdevices, height must be between 0 and 8U. Other types: 1–8U.'
      : 'Device height must be between 1 and 8U.';
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
      emit('inventory-updated');
      emit('close', { inventory: true });
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

watch(
  () => form.type,
  (t, prev) => {
    if (!isOtherDevicesType(t) && isOtherDevicesType(prev) && deviceHeightU(form.height) === 0) {
      form.height = 1;
    }
  }
);
</script>

<style scoped>
.fs-7 { font-size: 0.85rem; font-weight: 500; color: #566a7f; }
</style>
