<script setup lang="ts">

import { ref, watch, computed, onMounted, onBeforeUnmount } from 'vue'
import type { AxiosInstance } from 'axios'
import BaseModal from './BaseModal.vue'

interface MemberSetup {
  members?: unknown
}

interface MemberApiResponse {
  content?: {
    config?: {
      bmcsetup?: Record<string, MemberSetup>
    }
  }
}

const props = withDefaults(defineProps<{
  apiClient: AxiosInstance
  bmcName: string
}>(), {
  bmcName: ''
})

const emit = defineEmits<{
  (event: 'close'): void
}>()

const loading = ref(false)
const errorMsg = ref('')
const infoMsg = ref('')
const members = ref<string[]>([])

const modalTitle = computed(() => `BMC Members: ${props.bmcName || 'Unknown BMC Setup'}`)

function handleEscKey(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    emit('close')
  }
}

function getMembersFromResponse(payload: unknown): string[] {
  const data = payload as MemberApiResponse
  const bmcsetup = data.content?.config?.bmcsetup

  if (!bmcsetup) {
    return []
  }

  const sourceByName = bmcsetup[props.bmcName]
  const directMembers = sourceByName?.members

  if (Array.isArray(directMembers)) {
    return directMembers.map((node) => String(node))
  }

  const firstSetup = Object.values(bmcsetup)[0]
  const fallbackMembers = firstSetup?.members

  if (Array.isArray(fallbackMembers)) {
    return fallbackMembers.map((node) => String(node))
  }

  return []
}

async function loadMembers() {
  errorMsg.value = ''
  infoMsg.value = ''
  members.value = []

  const bmcName = props.bmcName.trim()

  if (!bmcName) {
    errorMsg.value = 'BMC setup name is missing.'
    return
  }

  loading.value = true

  try {
    const { data } = await props.apiClient.get(
      `/api/v1/member/${encodeURIComponent(bmcName)}`,
      { validateStatus: () => true }
    )

    if (data.status === true) {
      members.value = getMembersFromResponse(data)

      if (members.value.length === 0) {
        infoMsg.value = `BMC Setup ${bmcName} does not have any member node.`
      }

      return
    }

    members.value = []
    infoMsg.value = data.content?.message || `BMC Setup ${bmcName} does not have any member node.`
  } catch (err: unknown) {
    members.value = []
    errorMsg.value = err instanceof Error ? err.message : 'Unknown error occurred while loading BMC members.'
  } finally {
    loading.value = false
  }
}

watch(
  () => props.bmcName,
  () => {
    loadMembers()
  },
  { immediate: true }
)

onMounted(() => {
  window.addEventListener('keydown', handleEscKey)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleEscKey)
})
</script>

<template>
  <BaseModal size="small" @close="emit('close')">
    <div class="tx-form-page tx-member-modal-page">
      <div class="tx-header tx-member-modal-header">
        <h2 class="tx-title">{{ modalTitle }}</h2>
      </div>
      <div v-if="errorMsg" class="alert-danger" role="alert">{{ errorMsg }}</div>
      <div v-if="infoMsg && !errorMsg" class="tx-member-empty">{{ infoMsg }}</div>
      <p v-if="loading" class="tx-loading">Loading members...</p>

      <div v-if="!loading && members.length > 0" class="tx-inventory-table-wrap tx-member-table-wrap">
        <table class="tx-inventory-table tx-member-table">
          <thead>
            <tr>
              <th class="tx-th-regular tx-th-sep-blue tx-member-sno-col"><span class="tx-th-label-clip">S. NO</span></th>
              <th class="tx-th-regular tx-th-sep-blue"><span class="tx-th-label-clip">NODE NAME</span></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(node, index) in members" :key="`${node}-${index}`">
              <td class="tx-td-sep-blue tx-member-sno-cell">{{ index + 1 }}</td>
              <td class="tx-td-sep-blue"><span class="tx-cell-ellipsis" :title="node">{{ node }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="tx-form-footer tx-member-footer">
        <span class="tx-member-count">{{ members.length }} member{{ members.length === 1 ? '' : 's' }}</span>
        <button type="button" class="tx-btn tx-btn-blue" @click="emit('close')">Close</button>
      </div>
    </div>
  </BaseModal>
</template>
