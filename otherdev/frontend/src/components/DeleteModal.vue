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

<script setup lang="ts">

import { ref, onMounted, onBeforeUnmount } from 'vue'
import type { AxiosInstance } from 'axios'
import BaseModal from './BaseModal.vue'
import { formatOtherDevNameDisplay, otherdevNameTitle } from '@/constants/otherdevName'



const props = defineProps<{
  apiClient: AxiosInstance
  otherdevName: string,
}>()

const deleting = ref(false)
const errorMsg = ref('')

const emit = defineEmits<{
  (event: 'close'): void
  (event: 'deleted'): void
}>()

function handleEscKey(event: KeyboardEvent) {
  if (event.key === 'Escape' && !deleting.value) {
    emit('close')
  }
}

async function onDelete() {
  if (deleting.value) return

  deleting.value = true
  errorMsg.value = ''

  try {
    const recordName = encodeURIComponent(props.otherdevName)
    const { data } = await props.apiClient.delete(`/api/v1/delete/${recordName}`)

    if (data.status === true) {
      emit('deleted')
      emit('close')
      return
    }

    errorMsg.value = data.content?.message || 'Delete failed.'
  } catch (err: unknown) {
    errorMsg.value = err instanceof Error ? err.message : 'Unknown error occurred.'
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleEscKey)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleEscKey)
})

</script>


<template>
  <BaseModal size="small" :close-disabled="deleting" @close="$emit('close')">
    <div class="tx-delete-confirm">
      <div v-if="errorMsg" class="alert alert-danger" role="alert">{{ errorMsg }}</div>
      <h3 class="tx-delete-title">Delete Other Device <strong class="tx-title-highlight-name" :title="otherdevNameTitle(otherdevName)">{{ formatOtherDevNameDisplay(otherdevName) }}</strong>?</h3>
      <p class="tx-delete-desc">This action cannot be undone.</p>
      <div class="tx-delete-actions">
        <button type="button" class="tx-btn tx-btn-outline-blue" :disabled="deleting" :class="{ 'tx-btn-disabled': deleting }" @click="$emit('close')">Cancel</button>
        <button type="button" class="tx-btn tx-btn-danger" :disabled="deleting" :class="{ 'tx-btn-disabled': deleting }" @click="onDelete">{{ deleting ? 'Deleting...' : 'Delete' }}</button>
      </div>
    </div>
  </BaseModal>
</template>

