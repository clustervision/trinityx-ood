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

import { ref, onMounted } from 'vue'
import BaseModal from './BaseModal.vue'
import GroupFormFields from './GroupFormFields.vue'
import {
  fetchGroupResources,
  submitForm
} from '@/services/api'
import { formatGroupNameDisplay, groupNameTitle } from '@/constants/groupName'

const props = defineProps({
  groupName: {
    type: String,
    required: true
  },

  groupList: {
    type: Array as () => string[],
    required: true
  },

  group: {
    type: Object as () => Record<string, any>,
    required: false,
    default: () => ({})
  }
})

const emit = defineEmits([
  'close',
  'saved'
])

const loading = ref(true)
const errorMsg = ref('')
const successMsg = ref('')
const fatalError = ref(false)

const formData = ref({})

const bmcsetupOptions = ref<string[]>([])
const osimageOptions = ref<string[]>([])
const networkOptions = ref<string[]>([])
const bondModeOptions = ref<string[]>([])

const hints = ref<Record<string, string>>({})

const formRef = ref()

onMounted(async () => {

  try {

    const resource_data =
      await fetchGroupResources(props.groupName)

    bmcsetupOptions.value = resource_data.bmcsetup_list?.options || []

    osimageOptions.value = resource_data.osimage_list?.options || []

    networkOptions.value = resource_data.network_list?.options || []

    bondModeOptions.value = resource_data.bond_modes || []

    formData.value = {
      ...props.group,
      bmcsetupname: resource_data.bmcsetup_list?.selected || '',
      osimage: resource_data.osimage_list?.selected || '',
      newgroupname: '',
    }
    buildHints(props.group)

  } catch (err: any) {
    errorMsg.value = err.message || 'Failed to load clone data.'
    fatalError.value = true
  } finally {
    loading.value = false
  }
})

function buildHints(d: any) {
  if (!d) {
    hints.value = {}
    return
  }
  const h: Record<string, string> = {}
  for (
    const name of [
      'osimagetag',
      'provision_interface',
      'provision_fallback',
      'provision_method',
    ]
  ) {

    const s1 = d[name + '_source'] || ''
    const s2 = d['_' + name + '_source'] || ''

    if (s1 || s2) {
      h[name] = '| ' + s1 + s2
    }
  }

  hints.value = h
}

async function onSubmit() {

  if (!formRef.value) return
  errorMsg.value = ''
  successMsg.value = ''

  try {

    const payload = formRef.value.buildPayload()
    // console.log('Submitting clone payload:', payload)
    const result = await submitForm(`/api/v1/clone`, payload)
    if (result.status === true && result.content?.message) {
      successMsg.value = result.content.message
      setTimeout(() => {
        emit('saved')
        emit('close')
      }, 2000)
      return
    }
    errorMsg.value = result.content?.message || 'Clone failed.'
  } catch (err: unknown) {
    if (err instanceof Error) {
      errorMsg.value = err.message
    } else {
      errorMsg.value = 'Unknown error occurred'
    }
  }
}

</script>

<template>
  <BaseModal size="large" @close="$emit('close')">
    <div class="tx-form-page">
      <div v-if="errorMsg" class="alert alert-danger" role="alert">{{ errorMsg }}</div>
      <p v-if="loading" class="tx-loading">Loading...</p>

      <template v-if="!loading && !fatalError">
        <div class="tx-header">
          <h2 class="tx-title">Clone group <strong class="tx-title-highlight-name" :title="groupNameTitle(groupName)">{{ formatGroupNameDisplay(groupName) }}</strong></h2>
        </div>

        <GroupFormFields
          ref="formRef"
          mode="clone"
          :groupList="props.groupList"
          :record-name="props.groupName"
          :initial-data="formData"
          :bmcsetup-options="bmcsetupOptions"
          :osimage-options="osimageOptions"
          :network-options="networkOptions"
          :bond-mode-options="bondModeOptions"
          :hints="hints"
          submit-label="Clone Group"
          @submit="onSubmit"
        />
      </template>
    </div>
  </BaseModal>
</template>

