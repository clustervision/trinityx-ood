<template>
  <BaseModal size="wide" @close="$emit('close')">
    <div class="tx-form-page tx-ospush-page">
      <div v-if="errorMsg" class="alert alert-danger" role="alert">{{ errorMsg }}</div>
      <div v-if="successMsg" class="alert alert-success" role="alert">{{ successMsg }}</div>

      <div class="tx-header">
        <h2 class="tx-title">Push OS Image for Group <strong class="tx-title-highlight-name">{{ groupName }}</strong></h2>
      </div>

      <form @submit.prevent="onSubmit">
        <div class="tx-fields">
          <div class="tx-field tx-field-strong">
            <span class="tx-label">Node:</span>
            <select v-model="selectedGroup" required :class="{ 'tx-select-placeholder': !selectedGroup }">
              <option value="">--- Select ---</option>
              <option v-for="g in groupOptions" :key="g" :value="g">{{ g }}</option>
            </select>
          </div>
          <div class="tx-field tx-field-strong">
            <span class="tx-label">OS Image:</span>
            <select v-model="selectedOsimage" :class="{ 'tx-select-placeholder': !selectedOsimage }">
              <option value="">--- Select ---</option>
              <option v-for="o in osimageOptions" :key="o" :value="o">{{ o }}</option>
            </select>
          </div>
          <div class="tx-field tx-field-match tx-field-nodry">
            <span class="tx-label">No Dry:</span>
            <input type="checkbox" v-model="noDry" />
          </div>
        </div>
        <div class="tx-form-footer">
          <span></span>
          <button type="submit" class="tx-btn tx-btn-blue" :disabled="submitting">Push OS Image</button>
        </div>
      </form>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import BaseModal from './BaseModal.vue'
import { fetchOspushData, submitForm } from '../api.js'

const props = defineProps({
  groupName: { type: String, required: true },
})
const emit = defineEmits(['close', 'saved'])

const errorMsg = ref('')
const successMsg = ref('')
const submitting = ref(false)
const selectedGroup = ref('')
const selectedOsimage = ref('')
const noDry = ref(false)
const groupOptions = ref([])
const osimageOptions = ref([])

onMounted(async () => {
  try {
    const payload = await fetchOspushData(props.groupName)
    groupOptions.value = payload.group_list?.options || []
    osimageOptions.value = payload.osimage_list?.options || []
    selectedGroup.value = payload.group_list?.selected || props.groupName
    selectedOsimage.value = payload.osimage_list?.selected || ''
  } catch (err) {
    errorMsg.value = err.message || 'Failed to load push data.'
  }
})

async function onSubmit() {
  errorMsg.value = ''
  successMsg.value = ''
  submitting.value = true
  const fd = new FormData()
  fd.append('name', selectedGroup.value)
  fd.append('osimage', selectedOsimage.value)
  if (noDry.value) fd.append('nodry', 'true')
  try {
    const { ok, data } = await submitForm(`/ospush/${encodeURIComponent(props.groupName)}`, fd)
    if (ok || data.status === 'success') {
      successMsg.value = data.message || 'OS push initiated.'
    } else {
      errorMsg.value = data.message || 'Push failed.'
    }
  } catch (err) {
    errorMsg.value = err.message || 'Network error.'
  } finally {
    submitting.value = false
  }
}
</script>
