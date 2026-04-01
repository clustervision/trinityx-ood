<template>
  <Teleport to="body">
    <Transition name="mfm-fade">
      <div
        v-if="open"
        ref="overlayRef"
        class="mfm-overlay"
        role="dialog"
        aria-modal="true"
        aria-labelledby="add-rack-dialog-title"
        tabindex="-1"
        @keydown.esc="closeModal"
      >
        <div class="mfm-backdrop" @click="closeModal" />
        <div class="mfm-dialog" @click.stop>
          <button type="button" class="mfm-close" aria-label="Close" @click="closeModal">
            <i class="bx bx-x" aria-hidden="true"></i>
          </button>

          <h2 id="add-rack-dialog-title" class="mfm-title">Add Rack</h2>

          <form class="mfm-form" @submit.prevent="submitForm">
            <div class="mfm-fields-grid">
              <label class="mfm-field mfm-field--required">
                <span class="mfm-field-label">NAME:</span>
                <input
                  v-model="form.name"
                  type="text"
                  class="mfm-field-control"
                  maxlength="100"
                  required
                  autocomplete="off"
                />
              </label>
              <label class="mfm-field mfm-field--required">
                <span class="mfm-field-label">ORDER:</span>
                <span class="mfm-select-wrap">
                  <select v-model="form.order" class="mfm-field-control mfm-select" required>
                    <option value="" disabled>--- Select ---</option>
                    <option value="ascending">Ascending (Top To Bottom)</option>
                    <option value="descending">Descending (Bottom To Top)</option>
                  </select>
                  <i class="bx bx-chevron-down mfm-select-chevron" aria-hidden="true"></i>
                </span>
              </label>
              <label class="mfm-field mfm-field--required">
                <span class="mfm-field-label">SIZE:</span>
                <input
                  v-model="form.size"
                  type="number"
                  class="mfm-field-control"
                  min="1"
                  max="60"
                  required
                  placeholder="| Max: 60U"
                />
              </label>

              <label class="mfm-field mfm-field--optional">
                <span class="mfm-field-label">SITE:</span>
                <input
                  v-model="form.site"
                  type="text"
                  class="mfm-field-control"
                  maxlength="100"
                  autocomplete="off"
                />
              </label>
              <label class="mfm-field mfm-field--optional">
                <span class="mfm-field-label">ROOM:</span>
                <input
                  v-model="form.room"
                  type="text"
                  class="mfm-field-control"
                  maxlength="100"
                  autocomplete="off"
                />
              </label>
              <div class="mfm-grid-spacer" aria-hidden="true" />
            </div>

            <div v-if="errorMessage" class="mfm-error" role="alert">
              {{ errorMessage }}
            </div>

            <div class="mfm-footer">
              <button type="submit" class="mfm-submit" :disabled="isSubmitting">
                {{ isSubmitting ? 'Adding...' : 'Add Rack' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, reactive, watch, nextTick } from 'vue';
import axios from 'axios';
import { useToast } from 'vue-toastification';

//@ts-ignore
const Url = window.APP_URL;

const props = defineProps<{ open: boolean }>();
const emit = defineEmits<{
  (e: 'update:open', value: boolean): void;
  (e: 'close', payload?: { rack?: boolean }): void;
}>();

const toast = useToast();
const isSubmitting = ref(false);
const errorMessage = ref('');
const overlayRef = ref<HTMLElement | null>(null);

const emptyForm = () => ({
  name: '',
  site: '',
  room: '',
  order: '',
  size: '' as string | number,
});

const form = reactive(emptyForm());

const resetForm = () => {
  Object.assign(form, emptyForm());
  errorMessage.value = '';
};

watch(
  () => props.open,
  async (isOpen) => {
    if (isOpen) {
      resetForm();
      await nextTick();
      overlayRef.value?.focus({ preventScroll: true });
    }
  }
);

const closeModal = () => {
  emit('update:open', false);
  emit('close');
};

const submitForm = async () => {
  isSubmitting.value = true;
  errorMessage.value = '';

  if (!String(form.name).trim()) {
    errorMessage.value = 'Name is required.';
    isSubmitting.value = false;
    return;
  }

  if (/\s/.test(form.name)) {
    errorMessage.value = 'Rack Name must not contain spaces.';
    isSubmitting.value = false;
    return;
  }

  if (!form.order) {
    errorMessage.value = 'Order is required.';
    isSubmitting.value = false;
    return;
  }

  if (form.size === '' || form.size === null) {
    errorMessage.value = 'Size is required.';
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
    params.append('site', String(form.site ?? '').trim());
    params.append('room', String(form.room ?? '').trim());
    params.append('order', form.order);
    params.append('size', form.size.toString());

    const response = await axios.post(Url + '/change_rack', params);

    if (response.data.status) {
      emit('update:open', false);
      emit('close', { rack: true });
      toast.success(`Add Rack ${form.name} as New Rack`);
      resetForm();
    } else {
      errorMessage.value = response.data.message || 'Failed to add rack';
    }
  } catch (error: any) {
    console.error(error);
    errorMessage.value = error.response?.data?.message || 'Network error occurred.';
  } finally {
    isSubmitting.value = false;
  }
};
</script>
