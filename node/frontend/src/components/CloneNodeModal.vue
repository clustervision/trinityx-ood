<template>
  <BaseModal size="large" @close="$emit('close')">
    <div class="tx-form-page">
      <div v-if="errorMsg" class="alert alert-danger" role="alert">{{ errorMsg }}</div>
      <p v-if="loading" class="tx-loading">Loading...</p>

      <template v-if="!loading && !fatalError">
        <div class="tx-header tx-form-header-with-icon">
          <img :src="cloneIconSrc" alt="" class="tx-form-header-icon" width="36" height="36" />
          <h2 class="tx-title">
            Clone node <strong class="tx-title-highlight-name">{{ sourceNodeName }}</strong>
          </h2>
        </div>

        <NodeFormFields
          ref="formRef"
          mode="clone"
          :initial-data="formData"
          :group-options="groupOptions"
          :switch-options="switchOptions"
          :bmcsetup-options="bmcsetupOptions"
          :osimage-options="osimageOptions"
          :network-options="networkOptions"
          :bond-mode-options="bondModeOptions"
          :hints="hints"
          submit-label="Clone Node"
          @submit="onSubmit"
        />
      </template>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import BaseModal from './BaseModal.vue'
import NodeFormFields from './NodeFormFields.vue'
import { fetchNodeCloneData, submitNodeForm } from '../api.js'
import { assetImgUrl } from '../utils/assetImg.js'

const props = defineProps({
  sourceNodeName: { type: String, required: true },
})
const emit = defineEmits(['close', 'saved'])

const cloneIconSrc = assetImgUrl('icon-clone.png')

const loading = ref(true)
const errorMsg = ref('')
const fatalError = ref(false)
const formData = ref({})
const groupOptions = ref([])
const switchOptions = ref([])
const bmcsetupOptions = ref([])
const osimageOptions = ref([])
const networkOptions = ref([])
const bondModeOptions = ref([])
const hints = ref({})
const formRef = ref(null)

function optionList(payload, ...keys) {
  for (const k of keys) {
    const v = payload[k]
    if (Array.isArray(v)) return v
    if (v && typeof v === 'object' && Array.isArray(v.options)) return v.options
  }
  return []
}

function buildHints(d) {
  const h = {}
  for (const name of ['osimagetag', 'provision_interface', 'provision_fallback', 'provision_method']) {
    const s1 = d[name + '_source'] || ''
    const s2 = d['_' + name + '_source'] || ''
    if (s1 || s2) h[name] = '| ' + s1 + s2
  }
  hints.value = h
}

onMounted(async () => {
  try {
    const payload = await fetchNodeCloneData(props.sourceNodeName)
    if (!payload.data || payload.data.name == null || payload.data.name === '') {
      errorMsg.value = 'This node is not available at this moment.'
      fatalError.value = true
      return
    }
    formData.value = payload.data
    groupOptions.value = optionList(payload, 'group_list', 'groups', 'groupname_list')
    switchOptions.value = optionList(payload, 'switch_list', 'switchname_list', 'switches')
    bmcsetupOptions.value = optionList(payload, 'bmcsetup_list', 'bmcsetupname_list')
    osimageOptions.value = optionList(payload, 'osimage_list', 'osimage')
    networkOptions.value = optionList(payload, 'network_list', 'network')
    bondModeOptions.value = payload.bond_modes || payload.bond_mode_list?.options || []
    buildHints(payload.data)
  } catch (err) {
    errorMsg.value = err.message || 'Failed to load clone data.'
    fatalError.value = true
  } finally {
    loading.value = false
  }
})

async function onSubmit() {
  if (!formRef.value) return
  const fd = formRef.value.buildFormData()
  errorMsg.value = ''
  try {
    const { ok, data } = await submitNodeForm(`/clone/${encodeURIComponent(props.sourceNodeName)}`, fd)
    if (ok || data.status === 'success') {
      emit('saved')
      emit('close')
    } else {
      errorMsg.value = data.message || 'Clone failed.'
    }
  } catch (err) {
    errorMsg.value = err.message || 'Network error.'
  }
}
</script>
