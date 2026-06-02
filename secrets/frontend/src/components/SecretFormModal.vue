<template>
  <BaseModal @close="$emit('close')">
    <div class="tx-form-page">
      <h2 class="tx-title" style="margin-bottom: 0.75rem">{{ title }}</h2>
      <div class="tx-fields" style="display: grid; grid-template-columns: 1fr; gap: 0.75rem">
        <label class="tx-field">
          <span class="tx-label">Entity</span>
          <select v-model="local.entity">
            <option value="group">group</option>
            <option value="node">node</option>
          </select>
        </label>
        <label class="tx-field"><span class="tx-label">Group/Node</span><input v-model="local.owner" maxlength="200" /></label>
        <label class="tx-field"><span class="tx-label">Name</span><input v-model="local.name" maxlength="200" /></label>
        <label class="tx-field"><span class="tx-label">Path</span><input v-model="local.path" maxlength="200" /></label>
        <label class="tx-field-block">
          <div class="tx-label-row"><span class="tx-label">Content</span></div>
          <textarea v-model="local.content" rows="6"></textarea>
        </label>
      </div>
      <p v-if="error" class="alert-danger">{{ error }}</p>
      <div class="tx-form-footer-right">
        <button class="tx-btn tx-btn-outline-blue" @click="$emit('close')">Cancel</button>
        <button class="tx-btn tx-btn-blue" @click="submit">{{ submitText }}</button>
      </div>
    </div>
  </BaseModal>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import BaseModal from './BaseModal.vue'
import type { SecretFormState } from '@/types'
import { validateSecretNameInput } from '@/constants/secretName'

const props = defineProps<{
  title: string
  submitText: string
  initial: SecretFormState
}>()
const emit = defineEmits<{ close: []; submit: [SecretFormState] }>()

const local = reactive<SecretFormState>({ ...props.initial })
const error = ref('')

watch(
  () => props.initial,
  (v) => {
    Object.assign(local, v)
    error.value = ''
  },
  { deep: true },
)

function submit() {
  if (!local.owner.trim()) {
    error.value = 'Group/Node name is required.'
    return
  }
  const check = validateSecretNameInput(local.name)
  if (!check.ok) {
    error.value = check.message
    return
  }
  error.value = ''
  emit('submit', { ...local, name: check.name })
}
</script>
