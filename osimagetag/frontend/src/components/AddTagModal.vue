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
  <BaseModal size="medium" @close="$emit('close')">
    <div class="tx-form-page">
      <h2 class="tx-title">Add Tag to OS Image</h2>

      <div v-if="listError" class="alert-danger" style="margin-top:1rem;">
        {{ listError }}
        <button type="button" class="tx-btn tx-btn-outline-blue" style="margin-left:0.75rem;" @click="loadOsimages">
          Retry
        </button>
      </div>
      <div v-if="liveValidationMsg || errorMsg" class="alert-danger" style="margin-top:1rem;">{{ liveValidationMsg || errorMsg }}</div>
      <div v-if="successMsg" class="alert-success" style="margin-top:1rem;">{{ successMsg }}</div>

      <form @submit.prevent="handleSubmit" style="margin-top:1.25rem;">
        <div style="display:flex;flex-direction:column;gap:0.65rem;">
          <div class="tx-field" style="width:100%;">
            <label class="tx-label" for="addOsimage">OS IMAGE</label>
            <select
              id="addOsimage"
              v-model="form.osimage"
              required
              class="tx-field-select tx-field-select-osimage"
              :disabled="osimageLoading"
            >
              <option value="" disabled>
                {{ osimageLoading ? 'Loading…' : 'Select an OS image…' }}
              </option>
              <option v-for="n in osimageOptions" :key="n" :value="n" :title="osimageNameTitle(n)">
                {{ formatOsimageNameDisplay(n) }}
              </option>
            </select>
          </div>
          <p
            v-if="!osimageLoading && !listError && osimageOptions.length > 0"
            class="tx-add-osimage-hint"
          >
            {{ osimageOptions.length }} OS image(s) in Luna — choose one in the list above.
          </p>
          <p
            v-if="!osimageLoading && !listError && osimageOptions.length === 0"
            style="margin:0;color:#888;font-size:0.9rem;"
          >
            No OS images are defined in Luna. Create an OS image first, then add a tag here.
          </p>
          <div class="tx-field" style="width:100%;">
            <label class="tx-label" for="addTag">TAG</label>
            <input id="addTag" v-model="form.tag" type="text" required class="tx-field-input-tag" :class="{ 'input-error': liveValidationMsg }" style="flex:1;" />
          </div>
        </div>
        <div class="tx-form-footer-right">
          <button type="button" class="tx-btn tx-btn-outline-blue" @click="$emit('close')">Cancel</button>
          <button
            type="submit"
            class="tx-btn tx-btn-blue"
            :disabled="submitting || osimageLoading || !osimageOptions.length || Boolean(liveValidationMsg)"
          >
            {{ submitting ? 'Adding...' : 'Add Tag' }}
          </button>
        </div>
      </form>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import BaseModal from './BaseModal.vue'
import { addTagToOsimage, fetchOsimageNames } from '../api'
import { formatOsimageNameDisplay, osimageNameTitle, validateOsimageNameInput } from '../constants/osimageName'
import { validateTagNameInput } from '../constants/tagName'

const emit = defineEmits(['close', 'saved'])

const form = ref({ osimage: '', tag: '' })

const liveValidationMsg = computed(() => {
  const tag = String(form.value.tag || '').trim()
  if (tag) {
    const tagCheck = validateTagNameInput(tag)
    if (!tagCheck.ok) return tagCheck.message
  }
  const img = String(form.value.osimage || '').trim()
  if (img) {
    const imgCheck = validateOsimageNameInput(img)
    if (!imgCheck.ok) return imgCheck.message
  }
  return ''
})
const osimageOptions = ref([])
const osimageLoading = ref(true)
const listError = ref('')
const submitting = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

async function loadOsimages() {
  listError.value = ''
  osimageLoading.value = true
  const { names, error } = await fetchOsimageNames()
  osimageLoading.value = false
  if (error) {
    listError.value = error
    osimageOptions.value = []
    return
  }
  osimageOptions.value = names
}

onMounted(() => {
  loadOsimages()
})

async function handleSubmit() {
  errorMsg.value = ''
  successMsg.value = ''
  const imgCheck = validateOsimageNameInput(form.value.osimage)
  if (!imgCheck.ok) {
    errorMsg.value = imgCheck.message
    return
  }
  const tagCheck = validateTagNameInput(form.value.tag)
  if (!tagCheck.ok) {
    errorMsg.value = tagCheck.message
    return
  }
  form.value.osimage = imgCheck.name
  form.value.tag = tagCheck.name
  submitting.value = true
  try {
    const result = await addTagToOsimage(imgCheck.name, tagCheck.name)
    if (result.ok) {
      successMsg.value = result.data?.message || `Tag ${tagCheck.name} added to ${imgCheck.name}.`
      setTimeout(() => emit('saved'), 600)
    } else {
      errorMsg.value = result.data?.message || result.data?.error || 'Failed to add tag.'
    }
  } catch (e) {
    errorMsg.value = String(e?.message || 'Network error.')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.tx-field-select {
  flex: 1;
  min-width: 0;
  border: none;
  outline: none;
  padding: 0.35rem 0.55rem;
  font-size: 15px;
  background: transparent;
}

.tx-field-select-osimage,
.tx-field-input-tag {
  font-family: "Geist Sans", "Geist", ui-sans-serif, system-ui, sans-serif;
  font-size: 18px;
}

.tx-add-osimage-hint {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
  line-height: 1.35;
}
</style>
