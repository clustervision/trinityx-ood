<script setup lang="ts">
import { ref, onMounted } from 'vue'
import BaseModal from './BaseModal.vue'
import { fetchGroupResources, submitForm, checkStatus } from '@/services/api'
import type { OSPush } from '@/types/ospush'
const props = defineProps({
  groupName: { type: String, required: true },
  group: {
    type: Object as () => Record<string, any>,
    required: false,
    default: () => ({})
  }
})
const emit = defineEmits(['close', 'saved'])

const runtimeLogs = ref<string[]>([])
const showRuntimeLogs = ref(false)
const errorMsg = ref('')
const successMsg = ref('')
const submitting = ref(false)
// const selectedGroup = ref('')
const selectedOsimage = ref('')
const noDry = ref(false)
// const groupOptions = ref([])
// const osimageOptions = ref([])
const osimageOptions = ref<string[]>([])

function sleep(ms: number) {
  return new Promise((resolve) =>
    setTimeout(resolve, ms)
  )
}



onMounted(async () => {
  try {
    const resource_data = await fetchGroupResources(props.groupName)
    // console.log(resource_data);
    osimageOptions.value = resource_data.osimage_list?.options || []
    selectedOsimage.value = resource_data.osimage_list?.selected || ''
    // console.log(osimageOptions.value);
    // console.log(props.groupName);
  } catch (err: unknown) {
    if (err instanceof Error) {
      errorMsg.value = err.message
    } else {
      errorMsg.value = String(err) || 'Failed to load push data.'
    }
  }
})

function buildGroupPayload(name: string, data: any) {
  return { config: { group: { [name]: data } } }
}


async function pollRequestStatus(requestId: string) {
  while (true) {
    try {
      const result = await checkStatus(requestId)
      // console.log(result);
      const status_code = result.status_code || ''
      const msg = result.content?.message || ''
      if (msg.trim()) {
        // runtimeLogs.value.push(msg)
        msg.split(';;').map((m: string) => m.trim()).filter((m: string) => Boolean(m)).forEach((m: string) => { runtimeLogs.value.push(m) })
      }
      // console.log(msg);
      await sleep(3000)
      if (status_code === 404) { break }
    } catch (err: any) {
      if (err?.response?.status === 404 || err?.status === 404) {
        runtimeLogs.value.push('Request completed.')
        break
      }
      runtimeLogs.value.push('Status polling failed.')
      break
    }
  }
}



async function onSubmit() {
  errorMsg.value = ''
  successMsg.value = ''
  submitting.value = true

  try {
     const payload: OSPush = {
      name: props.groupName,
      osimage: selectedOsimage.value || null,
      nodry: noDry.value ? 'true' : null,
    }
    const requestBody = buildGroupPayload(props.groupName, payload)
    const result = await submitForm(`/api/v1/ospush/${encodeURIComponent(props.groupName)}`, requestBody)
    if (result.status === true) {
      successMsg.value = result.content?.message || 'OS push initiated.'
      showRuntimeLogs.value = true
      runtimeLogs.value = []
      runtimeLogs.value.push(result.content?.message || '')
      const requestId = result.content?.request_id
      if (requestId) {
        pollRequestStatus(requestId)
      } else {
        errorMsg.value = result.content?.message || 'Push failed.'
      }

      // optional: auto close after success
      // setTimeout(() => {
      //   emit('saved')
      //   emit('close')
      // }, 2000)

    } else {
      errorMsg.value =
        result.content?.message || 'Push failed.'
    }

  } catch (err: unknown) {
    if (err instanceof Error) {
      errorMsg.value = err.message
    } else {
      errorMsg.value = String(err) || 'Network error.'
    }
  } finally {
    submitting.value = false
  }
}
</script>

<style lang="css">
#run-time-body {
    background-color: black;
    color: antiquewhite;
}

</style>
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

<br />
    <div v-if="showRuntimeLogs" class="modal-body" id="run-time-body">
      <pre id="run-time-logs">
        <template  v-for="(log, idx) in runtimeLogs" :key="idx">
          <span :style="{ color: log.includes('[ FAILED ]') || log.includes('[ error ]') ? 'red' : 'yellow' }">{{ log }}</span>
        </template>
      </pre>
    </div>

  </BaseModal>
</template>
