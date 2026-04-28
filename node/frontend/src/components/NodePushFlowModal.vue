<template>
  <BaseModal size="wide" @close="$emit('close')">
    <div class="tx-form-page tx-ospush-page">
      <div v-if="errorMsg" class="alert alert-danger" role="alert">{{ errorMsg }}</div>
      <div v-if="successMsg" class="alert alert-success" role="alert">{{ successMsg }}</div>

      <div class="tx-header">
        <h2 v-if="flow === 'osgrab'" class="tx-title">
          Grab OS Image for Node <span class="tx-title-node-name">{{ selectedNode || nodeName }}</span>
        </h2>
        <h2 v-else class="tx-title">
          Push OS Image for Node <span class="tx-title-node-name">{{ selectedNode || nodeName }}</span>
        </h2>
      </div>

      <p v-if="loading" class="tx-loading">Loading...</p>
      <form v-else @submit.prevent="onSubmit">
        <div class="tx-fields">
          <div class="tx-field tx-field-strong">
            <span class="tx-label">NODE:</span>
            <select
              v-model="selectedNode"
              required
              :class="{ 'tx-select-placeholder': !selectedNode }"
              @change="onNodeChange"
            >
              <option value="">--- Select ---</option>
              <option v-for="n in nodeOptions" :key="n" :value="n">{{ n }}</option>
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
import { fetchNodes, fetchNodeOspushData, fetchNodeOsgrabData, submitNodeForm } from '../api.js'

const props = defineProps({
  /** 'ospush' | 'osgrab' — push/grab for a chosen node (inventory row opens modal with that node pre-selected). */
  flow: { type: String, required: true },
  nodeName: { type: String, required: true },
})

const emit = defineEmits(['close', 'saved'])

const errorMsg = ref('')
const successMsg = ref('')
const loading = ref(true)
const submitting = ref(false)
const selectedNode = ref('')
const selectedOsimage = ref('')
const bare = ref(false)
const noDry = ref(false)
const nodeOptions = ref([])
const osimageOptions = ref([])

function canonicalName(displayName) {
  return String(displayName || '').replace(/\s+\*$/, '').trim()
}

const submitButtonLabel = computed(() =>
  props.flow === 'osgrab' ? 'Grab OS Image' : 'Push OS Image',
)

/** Payload may use `key: [...]` or `key: { options: [...] }`. */
function optionList(payload, ...keys) {
  for (const k of keys) {
    const v = payload[k]
    if (Array.isArray(v)) return v
    if (v && typeof v === 'object' && Array.isArray(v.options)) return v.options
  }
  return []
}

function coalesceStr(...vals) {
  for (const v of vals) {
    if (v == null) continue
    const s = String(v).trim()
    if (s !== '') return s
  }
  return ''
}

async function loadOsFormForNode(name) {
  const fetchFn = props.flow === 'osgrab' ? fetchNodeOsgrabData : fetchNodeOspushData
  const payload = await fetchFn(name)
  osimageOptions.value = optionList(payload, 'osimage_list', 'osimage')
  selectedOsimage.value = coalesceStr(payload.osimage_list?.selected, payload.data?.osimage)
}

function buildNodeOptionsFromInventory(rows, preferredCanon) {
  const names = new Set()
  for (const row of rows) {
    const c = canonicalName(row?.name)
    if (c) names.add(c)
  }
  if (preferredCanon) names.add(preferredCanon)
  return [...names].sort((a, b) => a.localeCompare(b, undefined, { sensitivity: 'base' }))
}

onMounted(async () => {
  loading.value = true
  errorMsg.value = ''
  const preferred = canonicalName(props.nodeName)
  const fetchFn = props.flow === 'osgrab' ? fetchNodeOsgrabData : fetchNodeOspushData

  let rows = []
  try {
    const inventory = await fetchNodes()
    rows = inventory.nodes || []
  } catch {
    /* list endpoint can fail independently; still allow push/grab form for current node */
  }

  try {
    const payload = await fetchFn(preferred || props.nodeName)
    nodeOptions.value = buildNodeOptionsFromInventory(rows, preferred)
    if (!nodeOptions.value.length && preferred) nodeOptions.value = [preferred]
    selectedNode.value =
      preferred && nodeOptions.value.includes(preferred)
        ? preferred
        : nodeOptions.value[0] || preferred || ''
    osimageOptions.value = optionList(payload, 'osimage_list', 'osimage')
    selectedOsimage.value = coalesceStr(payload.osimage_list?.selected, payload.data?.osimage)
  } catch (err) {
    errorMsg.value = err.message || 'Failed to load form data.'
    nodeOptions.value = buildNodeOptionsFromInventory(rows, preferred)
    if (!nodeOptions.value.length && preferred) nodeOptions.value = [preferred]
    selectedNode.value = preferred || nodeOptions.value[0] || ''
  } finally {
    loading.value = false
  }
})

async function onNodeChange() {
  if (!selectedNode.value) return
  errorMsg.value = ''
  try {
    await loadOsFormForNode(selectedNode.value)
  } catch (err) {
    errorMsg.value = err.message || 'Failed to load OS images for this node.'
  }
}

async function onSubmit() {
  errorMsg.value = ''
  successMsg.value = ''
  submitting.value = true
  const target = selectedNode.value
  const fd = new FormData()
  fd.append('name', target)
  fd.append('osimage', selectedOsimage.value)
  if (props.flow === 'osgrab' && bare.value) fd.append('bare', 'true')
  if (noDry.value) fd.append('nodry', 'true')
  const path =
    props.flow === 'osgrab'
      ? `/osgrab/${encodeURIComponent(target)}`
      : `/ospush/${encodeURIComponent(target)}`
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
