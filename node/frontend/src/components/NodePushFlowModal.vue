<template>
  <BaseModal size="wide" @close="$emit('close')">
    <div class="tx-form-page tx-ospush-page">
      <div v-if="errorMsg" class="alert alert-danger" role="alert">{{ errorMsg }}</div>
      <div v-if="successMsg" class="alert alert-success" role="alert">{{ successMsg }}</div>

      <div class="tx-header">
        <h2 v-if="flow === 'osgrab'" class="tx-title">
          Grab OS Image for Node <span class="tx-title-node-name">{{ nodeName }}</span>
        </h2>
        <h2 v-else class="tx-title">
          Push OS Image for Node <span class="tx-title-node-name">{{ nodeName }}</span>
        </h2>
      </div>

      <form @submit.prevent="onSubmit">
        <div class="tx-fields">
          <div class="tx-field tx-field-strong">
            <span class="tx-label">GROUP:</span>
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
          <div v-if="flow === 'osgrab'" class="tx-field tx-field-match tx-field-nodry">
            <span class="tx-label">Bare:</span>
            <input type="checkbox" v-model="bare" />
          </div>
          <div class="tx-field tx-field-match tx-field-nodry">
            <span class="tx-label">No Dry:</span>
            <input type="checkbox" v-model="noDry" />
          </div>
        </div>
        <div class="tx-form-footer">
          <span></span>
          <button type="submit" class="tx-btn tx-btn-blue" :disabled="submitting">{{ submitButtonLabel }}</button>
        </div>
      </form>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import BaseModal from './BaseModal.vue'
import { fetchNodeOspushData, fetchNodeOsgrabData, submitNodeForm } from '../api.js'

const props = defineProps({
  /** 'ospush' | 'osgrab' — same form layout and POST fields as group PushOsModal */
  flow: { type: String, required: true },
  nodeName: { type: String, required: true },
})

const emit = defineEmits(['close', 'saved'])

const errorMsg = ref('')
const successMsg = ref('')
const submitting = ref(false)
const selectedGroup = ref('')
const selectedOsimage = ref('')
const bare = ref(false)
const noDry = ref(false)
const groupOptions = ref([])
const osimageOptions = ref([])

const submitButtonLabel = computed(() =>
  props.flow === 'osgrab' ? 'Grab OS Image' : 'Push OS Image',
)

onMounted(async () => {
  try {
    const fetchFn = props.flow === 'osgrab' ? fetchNodeOsgrabData : fetchNodeOspushData
    const payload = await fetchFn(props.nodeName)
    groupOptions.value = payload.group_list?.options || []
    osimageOptions.value = payload.osimage_list?.options || []
    selectedGroup.value = payload.group_list?.selected || ''
    selectedOsimage.value = payload.osimage_list?.selected || ''
  } catch (err) {
    errorMsg.value = err.message || 'Failed to load form data.'
  }
})

async function onSubmit() {
  errorMsg.value = ''
  successMsg.value = ''
  submitting.value = true
  const fd = new FormData()
  fd.append('name', selectedGroup.value)
  fd.append('osimage', selectedOsimage.value)
  if (props.flow === 'osgrab' && bare.value) fd.append('bare', 'true')
  if (noDry.value) fd.append('nodry', 'true')
  const path =
    props.flow === 'osgrab'
      ? `/osgrab/${encodeURIComponent(props.nodeName)}`
      : `/ospush/${encodeURIComponent(props.nodeName)}`
  try {
    const { ok, data } = await submitNodeForm(path, fd)
    if (ok || data.status === 'success') {
      successMsg.value = data.message || (props.flow === 'osgrab' ? 'OS grab initiated.' : 'OS push initiated.')
      emit('saved')
    } else {
      errorMsg.value = data.message || 'Request failed.'
    }
  } catch (err) {
    errorMsg.value = err.message || 'Network error.'
  } finally {
    submitting.value = false
  }
}
</script>
