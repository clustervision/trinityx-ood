<template>
  <BaseModal size="large" nested @close="$emit('close')">
    <div class="tx-text-editor">
      <div class="tx-text-editor-header">
        <h3 class="tx-text-editor-title">{{ title }}</h3>
        <div class="tx-text-editor-actions">
          <label class="tx-upload-pill">
            <input
              type="file"
              accept=".txt,.text,.sh,.cfg,.conf,.yaml,.yml,.json,.xml,.md,.csv,.ini,.env,.log,.pem,.key,.crt,text/plain"
              @change="onFileUpload"
            />
            <span>Upload</span>
          </label>
        </div>
      </div>
      <textarea
        ref="textareaRef"
        v-model="content"
        class="tx-text-editor-area"
        rows="18"
        spellcheck="false"
      ></textarea>
      <div class="tx-text-editor-footer">
        <button type="button" class="tx-btn tx-btn-blue" @click="apply">Apply</button>
      </div>
    </div>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import BaseModal from './BaseModal.vue'

const props = withDefaults(
  defineProps<{
    title?: string
    modelValue?: string
  }>(),
  {
    title: 'Edit Content',
    modelValue: '',
  },
)

const emit = defineEmits<{
  close: []
  saved: [value: string]
}>()

const content = ref(props.modelValue)
const textareaRef = ref<HTMLTextAreaElement | null>(null)

watch(
  () => props.modelValue,
  (v) => {
    content.value = v
  },
)

onMounted(() => {
  textareaRef.value?.focus()
})

function apply() {
  emit('saved', content.value)
  emit('close')
}

function onFileUpload(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    content.value = String(reader.result ?? '')
    input.value = ''
  }
  reader.onerror = () => {
    alert('Could not read the file.')
    input.value = ''
  }
  reader.readAsText(file)
}
</script>
