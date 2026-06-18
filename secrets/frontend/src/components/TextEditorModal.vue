<!--
  This code is part of the TrinityX software suite
  Copyright (C) 2026  ClusterVision Solutions b.v.

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <https://www.gnu.org/licenses/>

  @author      Yixin Zhang
  @copyright   Copyright 2026, Luna2 Project[OOD]
  @license     GPL
  @version     2.0
  @maintainer  Yixin Zhang
  @email       yixin.zhang@clustervision.com
  @status      Development
-->

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
