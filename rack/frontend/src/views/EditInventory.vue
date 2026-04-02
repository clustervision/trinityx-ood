<template>
  <Teleport to="body">
    <Transition name="mfm-fade">
      <div
        v-if="open"
        ref="overlayRef"
        class="mfm-overlay"
        role="dialog"
        aria-modal="true"
        aria-labelledby="edit-inv-dialog-title"
        tabindex="-1"
        @keydown.esc="closeModal"
      >
        <div class="mfm-backdrop" @click="closeModal" />
        <div class="mfm-dialog" @click.stop>
          <button type="button" class="mfm-close" aria-label="Close" @click="closeModal">
            <i class="bx bx-x" aria-hidden="true"></i>
          </button>

          <h2 id="edit-inv-dialog-title" class="mfm-title">Update Inventory — {{ form.name || inventoryName }}</h2>

          <form class="mfm-form" @submit.prevent="submitForm">
            <div v-if="isAssigned" class="mfm-banner">
              <i class="bx bx-lock-alt" aria-hidden="true"></i>
              This device is currently placed in a rack. Data cannot be changed.
            </div>

            <div class="mfm-fields-grid mfm-fields-grid--2">
              <label class="mfm-field" :class="isAssigned ? 'mfm-field--readonly' : 'mfm-field--optional'">
                <span class="mfm-field-label">NAME:</span>
                <input v-model="form.name" type="text" class="mfm-field-control" :disabled="isAssigned" />
              </label>
              <label class="mfm-field" :class="isAssigned ? 'mfm-field--readonly' : 'mfm-field--optional'">
                <span class="mfm-field-label">TYPE:</span>
                <input v-model="form.type" type="text" class="mfm-field-control" :disabled="isAssigned" />
              </label>
              <label class="mfm-field" :class="isAssigned ? 'mfm-field--readonly' : 'mfm-field--required'">
                <span class="mfm-field-label">HEIGHT:</span>
                <input
                  v-model.number="form.height"
                  type="number"
                  class="mfm-field-control"
                  :min="heightMin"
                  max="8"
                  :required="!isAssigned"
                  :disabled="isAssigned"
                />
              </label>
              <label class="mfm-field" :class="isAssigned ? 'mfm-field--readonly' : 'mfm-field--required'">
                <span class="mfm-field-label">ORIENTATION:</span>
                <span class="mfm-select-wrap">
                  <select
                    v-model="form.orientation"
                    class="mfm-field-control mfm-select"
                    :required="!isAssigned"
                    :disabled="isAssigned"
                  >
                    <option value="front">Front Side</option>
                    <option value="back">Back Side</option>
                  </select>
                  <i class="bx bx-chevron-down mfm-select-chevron" aria-hidden="true"></i>
                </span>
              </label>
            </div>

            <p v-if="!isAssigned && isOtherDevices" class="mfm-hint">
              otherdevices: 0U (pool only) or 1–8U. Max 8U.
            </p>
            <p v-else-if="!isAssigned" class="mfm-hint">Height 1–8U (other types cannot be 0).</p>

            <div v-if="errorMessage" class="mfm-error" role="alert">{{ errorMessage }}</div>

            <div class="mfm-footer">
              <button type="submit" class="mfm-submit" :disabled="isSubmitting || isAssigned">
                {{ isSubmitting ? 'Updating...' : 'Update Inventory ' + form.name }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, reactive, watch, nextTick, computed } from 'vue';
import axios from 'axios';
import { useToast } from 'vue-toastification';
import { deviceHeightU, isOtherDevicesType } from '@/utils/deviceKind';

//@ts-ignore
const Url = window.APP_URL;
const toast = useToast();

const props = withDefaults(
  defineProps<{
    open: boolean;
    inventoryName: string;
    modalHostActive?: boolean;
  }>(),
  { modalHostActive: true }
);

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void;
  (e: 'close', payload?: { inventory?: boolean }): void;
  (e: 'inventory-updated'): void;
}>();

const isAssigned = ref(false);
const isSubmitting = ref(false);
const errorMessage = ref('');
const overlayRef = ref<HTMLElement | null>(null);

const form = reactive({
  name: '',
  type: '',
  height: 1,
  orientation: 'front',
});

const isOtherDevices = computed(() => isOtherDevicesType(form.type));
const heightMin = computed(() => (isOtherDevices.value ? 0 : 1));

const loadInventoryData = async () => {
  const inventoryName = props.inventoryName;
  if (!inventoryName || !props.open) return;

  form.name = inventoryName;
  errorMessage.value = '';

  try {
    const response = await axios.get(Url + '/manage_inventory');

    let items: any[] = [];
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
    console.error('Failed to load details', e);
    errorMessage.value = 'Failed to load details.';
  }
};

watch(
  () => [props.open, props.inventoryName] as const,
  async ([isOpen]) => {
    if (isOpen) {
      await loadInventoryData();
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

watch(
  () => form.type,
  (t, prev) => {
    if (!isOtherDevicesType(t) && isOtherDevicesType(prev) && deviceHeightU(form.height) === 0) {
      form.height = 1;
    }
  }
);

const closeModal = () => {
  emit('update:open', false);
  emit('close');
};

const submitForm = async () => {
  if (isAssigned.value) {
    errorMessage.value = 'Action Forbidden: This device is currently in a rack.';
    return;
  }
  const h = parseInt(String(form.height), 10);
  const minH = isOtherDevicesType(form.type) ? 0 : 1;
  if (isNaN(h) || h < minH || h > 8) {
    errorMessage.value =
      minH === 0
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
      emit('update:open', false);
      emit('close', { inventory: true });
      toast.success(`${form.name} Updated.`);
    } else {
      errorMessage.value = response.data.message || 'Update failed';
    }
  } catch (error: any) {
    errorMessage.value = error.response?.data?.message || 'Network error.';
  } finally {
    isSubmitting.value = false;
  }
};
</script>
