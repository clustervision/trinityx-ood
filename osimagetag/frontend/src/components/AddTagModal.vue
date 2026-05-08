<template>
  <BaseModal size="medium" @close="$emit('close')">
    <div class="tx-form-page">
      <h2 class="tx-title">Add Tag to OS Image</h2>

      <div v-if="errorMsg" class="alert-danger" style="margin-top:1rem;">{{ errorMsg }}</div>
      <div v-if="successMsg" class="alert-success" style="margin-top:1rem;">{{ successMsg }}</div>

      <form @submit.prevent="handleSubmit" style="margin-top:1.25rem;">
        <div style="display:flex;flex-direction:column;gap:0.65rem;">
          <div class="tx-field" style="width:100%;">
            <label class="tx-label" for="addOsimage">OS IMAGE</label>
            <input id="addOsimage" v-model="form.osimage" type="text" required style="flex:1;" />
          </div>
          <div class="tx-field" style="width:100%;">
            <label class="tx-label" for="addTag">TAG</label>
            <input id="addTag" v-model="form.tag" type="text" required style="flex:1;" />
          </div>
        </div>
        <div class="tx-form-footer-right">
          <button type="button" class="tx-btn tx-btn-outline-blue" @click="$emit('close')">Cancel</button>
          <button type="submit" class="tx-btn tx-btn-blue" :disabled="submitting">
            {{ submitting ? 'Adding...' : 'Add Tag' }}
          </button>
        </div>
      </form>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref } from 'vue'
import BaseModal from './BaseModal.vue'
import { addTagToOsimage } from '../api'

const emit = defineEmits(['close', 'saved'])

const form = ref({ osimage: '', tag: '' })
const submitting = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

async function handleSubmit() {
  errorMsg.value = ''
  successMsg.value = ''
  const osimage = form.value.osimage.trim()
  const tag = form.value.tag.trim()
  if (!osimage || !tag) {
    errorMsg.value = 'OS Image and Tag are required.'
    return
  }
  submitting.value = true
  try {
    const result = await addTagToOsimage(osimage, tag)
    if (result.ok) {
      successMsg.value = result.data?.message || `Tag ${tag} added to ${osimage}.`
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
