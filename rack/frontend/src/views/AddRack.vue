<template>
  <div class="container-fluid flex-grow-1 container-p-y">
    <div class="card mb-4">
      <div class="card-header d-flex align-items-center justify-content-between">
        <h5 class="mb-0 add-rack-title">Add Rack</h5>

        <button type="button" class="btn btn-warning" @click="$emit('close')">Back</button>
      </div>

      <div class="card-body add-rack-form-body">
        <form @submit.prevent="submitForm">

          <div class="row mb-3">
            <label class="col-sm-2 col-form-label">Name</label>
            <div class="col-sm-10">
              <input
                type="text"
                v-model="form.name"
                class="form-control"
                maxlength="100"
                required
                placeholder="Enter rack name (e.g., Rack01)"
              />
            </div>
          </div>

          <div class="row mb-3">
            <label class="col-sm-2 col-form-label">Select Site</label>
            <div class="col-sm-10">
              <input
                type="text"
                v-model="form.site"
                class="form-control"
                maxlength="100"
                required
                placeholder="Enter site name"
              />
            </div>
          </div>

          <div class="row mb-3">
            <label class="col-sm-2 col-form-label">Select Room</label>
            <div class="col-sm-10">
              <input
                type="text"
                v-model="form.room"
                class="form-control"
                maxlength="100"
                required
                placeholder="Enter room name"
              />
            </div>
          </div>

          <div class="row mb-3">
            <label class="col-sm-2 col-form-label">Select Order</label>
            <div class="col-sm-10">
              <select v-model="form.order" class="form-control" required>
                <option value="" disabled>Select Order for Rack</option>
                <option value="ascending">Ascending (Top To Bottom)</option>
                <option value="descending">Descending (Bottom To Top)</option>
              </select>
            </div>
          </div>

          <div class="row mb-3">
            <label class="col-sm-2 col-form-label">Size Of Rack</label>
            <div class="col-sm-10">
              <input
                type="number"
                v-model="form.size"
                class="form-control"
                min="1"
                max="60"
                required
              />
              <small class="text-muted">Max height is 60U.</small>
            </div>
          </div>

          <div class="row justify-content-end">
            <div class="col-sm-10">
              <button type="submit" class="btn btn-primary add-rack-submit-btn" :disabled="isSubmitting">
                {{ isSubmitting ? 'Adding...' : 'Add Rack' }}
              </button>
            </div>
          </div>

          <div v-if="errorMessage" class="alert alert-danger mt-3" role="alert">
            {{ errorMessage }}
          </div>

        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import axios from 'axios';
import { useToast } from 'vue-toastification';

//@ts-ignore
const Url = window.APP_URL;

// 1. DEFINE EMITS (To communicate with Parent)
const emit = defineEmits(['close']);
const toast = useToast();
const isSubmitting = ref(false);
const errorMessage = ref('');

// Reactive form data
const form = reactive({
  name: '',
  site: '',
  room: '',
  order: '',
  size: '',
});

const submitForm = async () => {
  isSubmitting.value = true;
  errorMessage.value = '';

  if (/\s/.test(form.name)) {
      errorMessage.value = 'Rack Name must not contain spaces.';
      isSubmitting.value = false;
      return;
  }

  if (Number(form.size) <= 0) {
    errorMessage.value = 'Rack Size must be greater than 0.';
    isSubmitting.value = false;
    return;
  }
  if (Number(form.size) > 60) {
    errorMessage.value = 'Rack size cannot exceed 60U.';
    isSubmitting.value = false;
    return;
  }
  try {
    const params = new URLSearchParams();
    params.append('name', form.name);
    params.append('site', form.site);
    params.append('room', form.room);
    params.append('order', form.order);
    params.append('size', form.size.toString());

    // Backend route
    const response = await axios.post(Url + '/change_rack', params);

    if (response.data.status) {
      emit('close', { rack: true });
      toast.success(`Add Rack ${form.name} as New Rack`);
    } else {
      errorMessage.value = response.data.message || 'Failed to add rack';
    }
  } catch (error: any) {
    console.error(error);
    errorMessage.value = error.response?.data?.message || "Network error occurred.";
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.add-rack-title {
  font-family: var(--font-geist, 'Geist', sans-serif);
  font-weight: 500;
  color: #5376ea;
}

.add-rack-submit-btn {
  font-family: var(--font-geist, 'Geist', sans-serif);
  font-weight: 500;
}

.add-rack-submit-btn:hover:not(:disabled) {
  background-color: #3e66d6 !important;
  border-color: #3e66d6 !important;
}

.add-rack-form-body,
.add-rack-form-body :deep(.col-form-label),
.add-rack-form-body :deep(.form-control),
.add-rack-form-body :deep(small) {
  font-family: var(--font-geist, 'Geist', system-ui, sans-serif);
  font-weight: 400;
}
</style>
