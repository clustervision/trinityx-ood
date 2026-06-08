<template>
  <BaseModal size="wide" @close="$emit('close')">
    <div class="tx-form-page tx-secret-form">
      <div class="tx-secret-form-header">
        <div class="tx-secret-form-header-title-row">
          <h2 class="tx-title">{{ title }}</h2>
          <div v-if="mode !== 'edit'" class="tx-secret-entity-choice" role="radiogroup" aria-label="Secret target">
            <label class="tx-secret-entity-option">
              <input v-model="local.entity" type="radio" value="group" />
              <span>For Group</span>
            </label>
            <label class="tx-secret-entity-option">
              <input v-model="local.entity" type="radio" value="node" />
              <span>For Node</span>
            </label>
          </div>
        </div>
      </div>

      <div class="tx-secret-form-row tx-add-form-main">
        <label class="tx-field tx-field-strong">
          <span class="tx-label">Name</span>
          <input v-model="local.name" maxlength="200" autocomplete="off" />
        </label>
        <label class="tx-field tx-field-strong">
          <span class="tx-label">{{ ownerLabel }}</span>
          <select
            v-model="local.owner"
            :disabled="mode === 'edit'"
            :class="{ 'tx-select-placeholder': !local.owner }"
          >
            <option value="" disabled>--- Select ---</option>
            <option v-for="name in ownerOptions" :key="name" :value="name">{{ name }}</option>
          </select>
        </label>
        <label class="tx-field tx-field-strong">
          <span class="tx-label">Path</span>
          <input v-model="local.path" maxlength="200" autocomplete="off" />
        </label>
      </div>

      <label class="tx-field-block">
        <div class="tx-label-row">
          <span class="tx-label">Content</span>
          <label class="tx-upload-pill">
            <input type="file" accept="text/*,.txt,.pem,.key,.crt,.json,.yaml,.yml,.env,.sh,.cfg,.ini" @change="onUpload" />
            <span>Upload</span>
          </label>
        </div>
        <div class="tx-field-block-body tx-secret-content-field">
          <span class="tx-secret-masked">***</span>
          <button
            type="button"
            class="tx-secret-content-edit"
            title="Edit content"
            @click="contentEditorOpen = true"
          >
            <img :src="actionIcons.edit" alt="Edit content" width="28" height="28" />
          </button>
        </div>
      </label>

      <TextEditorModal
        v-if="contentEditorOpen"
        nested
        title="Edit Content"
        :model-value="local.content"
        @saved="onContentSaved"
        @close="contentEditorOpen = false"
      />

      <p v-if="loadError" class="alert-danger">{{ loadError }}</p>
      <p v-if="error" class="alert-danger">{{ error }}</p>

      <div class="tx-form-footer-right">
        <button type="button" class="tx-btn tx-btn-blue" @click="submit">{{ submitLabel }}</button>
      </div>
    </div>
  </BaseModal>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import BaseModal from './BaseModal.vue'
import TextEditorModal from './TextEditorModal.vue'
import { fetchGroupNames, fetchNodeNames } from '@/api'
import { actionIcons } from '@/utils/assetImg'
import type { SecretEntity, SecretFormState } from '@/types'
import { validateSecretNameInput } from '@/constants/secretName'

const props = defineProps<{
  title: string
  mode: 'add' | 'edit' | 'clone'
  initial: SecretFormState
}>()
const emit = defineEmits<{ close: []; submit: [SecretFormState] }>()

const local = reactive<SecretFormState>({ ...props.initial })
const error = ref('')
const loadError = ref('')
const groupNames = ref<string[]>([])
const nodeNames = ref<string[]>([])
const contentEditorOpen = ref(false)

const ownerLabel = computed(() => (local.entity === 'node' ? 'Node' : 'Group'))
const ownerOptions = computed(() => (local.entity === 'node' ? nodeNames.value : groupNames.value))
const submitLabel = computed(() => {
  if (props.mode === 'edit') return 'Save Secret'
  if (props.mode === 'clone') return local.entity === 'node' ? 'Clone Node Secret' : 'Clone Group Secret'
  return local.entity === 'node' ? 'Add Node Secret' : 'Add Group Secret'
})

watch(
  () => props.initial,
  (v) => {
    Object.assign(local, v)
    error.value = ''
    contentEditorOpen.value = false
  },
  { deep: true },
)

watch(
  () => local.entity,
  (entity, prev) => {
    if (props.mode === 'edit' || entity === prev) return
    if (!ownerOptions.value.includes(local.owner)) local.owner = ''
  },
)

async function loadOwners() {
  loadError.value = ''
  try {
    const [groups, nodes] = await Promise.all([fetchGroupNames(), fetchNodeNames()])
    groupNames.value = groups
    nodeNames.value = nodes
  } catch (e) {
    loadError.value = e instanceof Error ? e.message : 'Failed to load group/node list.'
  }
}

onMounted(() => {
  void loadOwners()
})

function onContentSaved(value: string) {
  local.content = value
  contentEditorOpen.value = false
}

function onUpload(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    local.content = String(reader.result ?? '')
  }
  reader.onerror = () => {
    error.value = 'Failed to read uploaded file.'
  }
  reader.readAsText(file)
  input.value = ''
}

function submit() {
  if (!local.owner.trim()) {
    error.value = `${ownerLabel.value} is required.`
    return
  }
  const check = validateSecretNameInput(local.name)
  if (!check.ok) {
    error.value = check.message
    return
  }
  error.value = ''
  emit('submit', { ...local, entity: local.entity as SecretEntity, name: check.name })
}
</script>
