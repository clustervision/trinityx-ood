<template>
  <div class="tx-field-block tx-osimage-comment-block" style="width: 100%">
    <div class="tx-label-row">
      <span class="tx-label">Comment:</span>
    </div>
    <div class="tx-comment-preview-wrap">
      <textarea
        :value="modelValue"
        class="tx-comment-preview tx-comment-inline-editable"
        rows="4"
        @input="onInput"
      />
      <button
        type="button"
        class="tx-btn-comment-popup-edit tx-btn-comment-popup-floating"
        title="Edit comment in dialog"
        aria-label="Edit comment in dialog"
        @click="openCommentEditDialog"
      >
        <img :src="editIconUrl" alt="" width="20" height="20" />
      </button>
    </div>
  </div>

  <Teleport to="body">
    <div
      v-if="commentEditDialogOpen"
      class="tx-modal-overlay tx-modal-overlay-nested"
      role="presentation"
      @mousedown.self="closeCommentEditDialog"
    >
      <div
        ref="commentEditDialogEl"
        class="tx-modal-container tx-modal-md tx-comment-edit-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="network-comment-edit-title"
        tabindex="-1"
        @keydown.escape.prevent="closeCommentEditDialog"
      >
        <button type="button" class="tx-modal-x" aria-label="Close" @click="closeCommentEditDialog">
          &times;
        </button>
        <div class="tx-form-page">
          <h2 id="network-comment-edit-title" class="tx-title" style="margin-bottom: 1rem">Edit comment</h2>
          <div class="tx-comment-edit-body">
            <textarea v-model="commentEditDraft" rows="14" aria-label="Comment text"></textarea>
          </div>
          <div class="tx-comment-edit-actions">
            <button type="button" class="tx-btn tx-btn-blue" @click="applyCommentEditDialog">OK</button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { punAppAssetUrl } from '@/utils'

const props = defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{ 'update:modelValue': [value: string] }>()

const editIconUrl = punAppAssetUrl('icons/icon-edit.png')
const commentEditDialogOpen = ref(false)
const commentEditDraft = ref('')
const commentEditDialogEl = ref<HTMLElement | null>(null)

function onInput(e: Event) {
  emit('update:modelValue', (e.target as HTMLTextAreaElement).value)
}

function openCommentEditDialog() {
  commentEditDraft.value = props.modelValue ?? ''
  commentEditDialogOpen.value = true
  nextTick(() => {
    commentEditDialogEl.value?.focus?.()
    commentEditDialogEl.value?.querySelector?.('textarea')?.focus?.()
  })
}

function closeCommentEditDialog() {
  commentEditDialogOpen.value = false
}

function applyCommentEditDialog() {
  emit('update:modelValue', commentEditDraft.value)
  closeCommentEditDialog()
}
</script>
