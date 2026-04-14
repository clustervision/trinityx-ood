<template>
  <BaseModal size="large" @close="$emit('close')">
    <div class="tx-text-editor">
      <div class="tx-text-editor-header">
        <h3 class="tx-text-editor-title">{{ title }}</h3>
        <div class="tx-text-editor-actions">
          <label class="tx-upload-pill">
            <input
              type="file"
              accept=".txt,.text,.sh,.cfg,.conf,.yaml,.yml,.json,.xml,.md,.csv,.ini,.env,.log,text/plain"
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

<script setup>
import { ref, onMounted } from 'vue'
import BaseModal from './BaseModal.vue'

const props = defineProps({
  title: { type: String, default: 'Edit text' },
  modelValue: { type: String, default: '' },
})
const emit = defineEmits(['close', 'update:modelValue'])

const content = ref(props.modelValue)
const textareaRef = ref(null)

onMounted(() => {
  if (textareaRef.value) textareaRef.value.focus()
})

function apply() {
  emit('update:modelValue', content.value)
  emit('close')
}

function looksLikeBinary(buf) {
  if (!buf || !buf.byteLength) return false
  const view = new Uint8Array(buf)
  const n = Math.min(view.length, 65536)
  for (let i = 0; i < n; i++) {
    if (view[i] === 0) return true
  }
  return false
}

function onFileUpload(e) {
  const file = e.target.files?.[0]
  if (!file) return
  const fr = new FileReader()
  fr.onload = () => {
    if (looksLikeBinary(fr.result)) {
      alert('Please choose a text file only. Binary files are not supported.')
      e.target.value = ''
      return
    }
    content.value = new TextDecoder('utf-8', { fatal: false }).decode(new Uint8Array(fr.result))
    e.target.value = ''
  }
  fr.onerror = () => {
    alert('Could not read the file.')
    e.target.value = ''
  }
  fr.readAsArrayBuffer(file)
}
</script>
