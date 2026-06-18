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

<template>
  <BaseModal size="wide" @close="$emit('close')">
    <div class="tx-form-page">
      <h2 class="tx-title">
        Tag Detail: <span class="tx-tag-detail-name">{{ displayName }}</span>
      </h2>

      <div v-if="errorMsg" class="alert-danger" style="margin-top:1rem;">{{ errorMsg }}</div>
      <div v-if="loading" class="tx-loading">Loading...</div>

      <div v-if="!loading && Object.keys(detail).length" style="margin-top:1.25rem;">
        <table class="tx-inventory-table" style="width:100%;">
          <tbody>
            <tr v-for="(value, key) in detail" :key="key">
              <td style="font-weight:600;text-align:left;padding:0.5rem 0.75rem;background:#E6EEFF;color:#5376EA;text-transform:uppercase;width:200px;">
                {{ key }}
              </td>
              <td style="text-align:left;padding:0.5rem 0.75rem;">
                <template v-if="value == null || value === ''">
                  <span class="tx-na-box">NONE</span>
                </template>
                <template v-else-if="key === 'osimage'">
                  <span class="tx-cell-ellipsis" :title="osimageNameTitle(value)">{{ formatOsimageNameDisplay(value) }}</span>
                </template>
                <template v-else-if="key === 'name'">
                  <span class="tx-cell-ellipsis" :title="tagNameTitle(value)">{{ formatTagNameDisplay(value) }}</span>
                </template>
                <template v-else>{{ value }}</template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="tx-form-footer-right">
        <button type="button" class="tx-btn tx-btn-outline-blue" @click="$emit('close')">Close</button>
      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import BaseModal from './BaseModal.vue'
import { fetchOsimageTagDetail } from '../api'
import { formatOsimageNameDisplay, osimageNameTitle } from '../constants/osimageName'
import { formatTagNameDisplay, tagNameTitle } from '../constants/tagName'

const props = defineProps({
  /** Inventory row: needs `osimage` and `name` (Luna detail API scopes by OS image, not tag name). */
  row: { type: Object, required: true },
})
defineEmits(['close'])

const loading = ref(true)
const errorMsg = ref('')
const detail = ref({})

const displayName = computed(() => formatTagNameDisplay(props.row?.name))

function rowAsDetail(r) {
  if (!r || typeof r !== 'object') return {}
  const { osimage, name, kernelfile, initrdfile, imagefile, path, nodes, groups } = r
  return { osimage, name, kernelfile, initrdfile, imagefile, path, nodes, groups }
}

onMounted(async () => {
  detail.value = rowAsDetail(props.row)
  try {
    const osimage = String(props.row?.osimage ?? '').trim()
    const tagName = String(props.row?.name ?? '').trim()
    const result = await fetchOsimageTagDetail(osimage, tagName)
    if (result.error) {
      errorMsg.value = result.error
    } else if (result.tag && Object.keys(result.tag).length) {
      detail.value = result.tag
    }
  } catch (e) {
    errorMsg.value = String(e?.message || 'Failed to load detail.')
  } finally {
    loading.value = false
  }
})
</script>
