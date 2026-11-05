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
  <div class="tx-field-block tx-osimage-comment-block" style="width: 100%;">
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
        aria-labelledby="osimage-comment-edit-title"
        tabindex="-1"
        @keydown.escape.prevent="closeCommentEditDialog"
      >
        <button type="button" class="tx-modal-x" aria-label="Close" @click="closeCommentEditDialog">
          &times;
        </button>
        <div class="tx-form-page">
          <h2 id="osimage-comment-edit-title" class="tx-title" style="margin-bottom: 1rem">
            Edit comment
          </h2>
          <textarea v-model="commentEditDraft" rows="14" aria-label="Comment text"></textarea>
          <div class="tx-comment-edit-actions">
            <button type="button" class="tx-btn tx-btn-outline-blue" @click="closeCommentEditDialog">
              Cancel
            </button>
            <button type="button" class="tx-btn tx-btn-blue" @click="applyCommentEditDialog">OK</button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import { publicAssetUrl } from '../utils'

const props = defineProps({
  modelValue: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue'])

const editIconUrl = publicAssetUrl('icons/icon-edit.png')

const commentEditDialogOpen = ref(false)
const commentEditDraft = ref('')
const commentEditDialogEl = ref(null)

function onInput(e) {
  emit('update:modelValue', e.target.value)
}

function openCommentEditDialog() {
  commentEditDraft.value = props.modelValue ?? ''
  commentEditDialogOpen.value = true
  nextTick(() => {
    commentEditDialogEl.value?.focus?.()
    const ta = commentEditDialogEl.value?.querySelector?.('textarea')
    ta?.focus?.()
  })
}

function closeCommentEditDialog() {
  commentEditDialogOpen.value = false
}

function handleEscKey(event) {
  if (event.key === 'Escape' && commentEditDialogOpen.value) {
    event.stopImmediatePropagation()
    closeCommentEditDialog()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleEscKey, true)
})
onUnmounted(() => {
  window.removeEventListener('keydown', handleEscKey, true)
})

function applyCommentEditDialog() {
  emit('update:modelValue', commentEditDraft.value)
  closeCommentEditDialog()
}
</script>
