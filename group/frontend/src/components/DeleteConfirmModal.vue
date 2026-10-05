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
import { ref } from 'vue'
import BaseModal from './BaseModal.vue'
import { deleteGroup } from '@/services/api'
import { formatGroupNameDisplay, groupNameTitle } from '@/constants/groupName'

const props = defineProps({
  groupName: { type: String, required: true },
})
const emit = defineEmits(['close', 'deleted'])

const deleting = ref(false)
const errorMsg = ref('')

async function onDelete() {
  if (deleting.value) return

  deleting.value = true
  errorMsg.value = ''

  try {
    await deleteGroup(props.groupName)
    emit('deleted')
    emit('close')
  } catch (err: unknown) {
    if (err instanceof Error) {
      errorMsg.value = err.message
    } else {
      errorMsg.value = 'Delete failed.'
    }
  } finally {
    deleting.value = false
  }
}

</script>


<template>
  <BaseModal size="small" @close="$emit('close')">
    <div class="tx-delete-confirm">
      <div v-if="errorMsg" class="alert alert-danger" role="alert">{{ errorMsg }}</div>
      <h3 class="tx-delete-title">Delete group <strong class="tx-title-highlight-name" :title="groupNameTitle(groupName)">{{ formatGroupNameDisplay(groupName) }}</strong>?</h3>
      <p class="tx-delete-desc">This action cannot be undone.</p>
      <div class="tx-delete-actions">
        <button type="button" class="tx-btn tx-btn-outline-blue" @click="$emit('close')">Cancel</button>
        <button type="button" class="tx-btn tx-btn-danger" :disabled="deleting" @click="onDelete">
          {{ deleting ? 'Deleting...' : 'Delete' }}
        </button>
      </div>
    </div>
  </BaseModal>
</template>

