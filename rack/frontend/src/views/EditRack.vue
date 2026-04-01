<template>
  <Teleport to="body">
    <Transition name="mfm-fade">
      <div
        v-if="open"
        ref="overlayRef"
        class="mfm-overlay"
        role="dialog"
        aria-modal="true"
        aria-labelledby="edit-rack-dialog-title"
        tabindex="-1"
        @keydown.esc="closeModal"
      >
        <div class="mfm-backdrop" @click="closeModal" />
        <div class="mfm-dialog" @click.stop>
          <button type="button" class="mfm-close" aria-label="Close" @click="closeModal">
            <i class="bx bx-x" aria-hidden="true"></i>
          </button>

          <h2 id="edit-rack-dialog-title" class="mfm-title">Update Rack — {{ form.name || rackName }}</h2>

          <form class="mfm-form" @submit.prevent="submitForm">
            <div class="mfm-fields-grid">
              <label class="mfm-field mfm-field--readonly">
                <span class="mfm-field-label">NAME:</span>
                <input type="text" v-model="form.name" class="mfm-field-control" readonly />
              </label>
              <label class="mfm-field mfm-field--required">
                <span class="mfm-field-label">ORDER:</span>
                <span class="mfm-select-wrap">
                  <select v-model="form.order" class="mfm-field-control mfm-select" required>
                    <option value="ascending">Ascending (Top To Bottom)</option>
                    <option value="descending">Descending (Bottom To Top)</option>
                  </select>
                  <i class="bx bx-chevron-down mfm-select-chevron" aria-hidden="true"></i>
                </span>
              </label>
              <label class="mfm-field mfm-field--required">
                <span class="mfm-field-label">SIZE:</span>
                <input
                  type="number"
                  v-model="form.size"
                  class="mfm-field-control"
                  :min="hasDevices ? initialSize : 1"
                  max="60"
                  required
                />
              </label>

              <div class="mfm-grid-span-all mfm-hint-row" aria-live="polite">
                <p class="mfm-hint">Max height is 60U.</p>
                <p v-if="hasDevices" class="mfm-hint">Cannot reduce size when rack has devices.</p>
              </div>

              <label class="mfm-field mfm-field--required">
                <span class="mfm-field-label">SITE:</span>
                <input type="text" v-model="form.site" class="mfm-field-control" required />
              </label>
              <label class="mfm-field mfm-field--required">
                <span class="mfm-field-label">ROOM:</span>
                <input type="text" v-model="form.room" class="mfm-field-control" required />
              </label>
              <div class="mfm-grid-spacer" aria-hidden="true" />
            </div>

            <div v-if="errorMessage" class="mfm-error" role="alert">{{ errorMessage }}</div>

            <div class="mfm-footer">
              <button type="submit" class="mfm-submit" :disabled="isSubmitting">
                {{ isSubmitting ? 'Updating...' : 'Update Rack ' + form.name }}
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
const toast = useToast();

const props = withDefaults(
  defineProps<{
    open: boolean;
    rackName: string;
    modalHostActive?: boolean;
  }>(),
  { modalHostActive: true }
);

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void;
  (e: 'close', payload?: { rack?: boolean }): void;
}>();

const isSubmitting = ref(false);
const errorMessage = ref('');
const initialSize = ref(0);
const hasDevices = ref(false);
const overlayRef = ref<HTMLElement | null>(null);

const form = reactive({
  name: '',
  site: '',
  room: '',
  order: '',
  size: '' as string | number,
});

const loadRackData = async () => {
  const rackName = props.rackName;
  if (!rackName || !props.open) return;

  form.name = rackName;
  errorMessage.value = '';

  try {
    const timestamp = new Date().getTime();
    const response = await axios.get(Url + `/show_rack/${rackName}?t=${timestamp}`);
    const rackData = response.data.message;

    if (rackData) {
      form.site = rackData.site || '';
      form.room = rackData.room || '';
      form.order = (rackData.order || 'ascending').toLowerCase();
      form.size = rackData.size;
      initialSize.value = Number(rackData.size) || 0;
      const devices = rackData.devices;
      hasDevices.value = Array.isArray(devices) && devices.length > 0;
    } else {
      errorMessage.value = `Rack '${rackName}' details not found.`;
    }
  } catch (e) {
    console.error('Failed to load rack details', e);
    errorMessage.value = 'Failed to load rack details.';
  }
};

watch(
  () => [props.open, props.rackName] as const,
  async ([isOpen]) => {
    if (isOpen) {
      await loadRackData();
      await nextTick();
      overlayRef.value?.focus({ preventScroll: true });
    }
  }
);

watch(
  () => props.modalHostActive,
  (active) => {
    if (active === false) {
      emit('update:open', false);
      emit('close');
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
  if (hasDevices.value && Number(form.size) < initialSize.value) {
    errorMessage.value = 'Cannot reduce rack size when it already has devices.';
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

    const response = await axios.post(Url + '/change_rack', params);

    if (response.data.status) {
      emit('update:open', false);
      emit('close', { rack: true });
      toast.success(`Rack ${form.name} Updated.`);
    } else {
      errorMessage.value = response.data.message || 'Update failed.';
    }
  } catch (error: any) {
    console.error(error);
    errorMessage.value = error.response?.data?.message || 'Network error.';
  } finally {
    isSubmitting.value = false;
  }
};
</script>
