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
    <div class="tx-form-page tx-ospush-page">
      <div v-if="errorMsg" class="alert alert-danger" role="alert">{{ errorMsg }}</div>
      <div v-if="successMsg" class="alert alert-success" role="alert">{{ successMsg }}</div>

      <div class="tx-header">
        <h2 v-if="flow === 'osgrab'" class="tx-title">
          Grab OS Image for Node
          <strong
            class="tx-title-highlight-name"
            :title="displayNameTitle(selectedNode || nodeName)"
          >{{ formatDisplayName(selectedNode || nodeName) }}</strong>
        </h2>
        <h2 v-else class="tx-title">
          Push OS Image for Node
          <strong
            class="tx-title-highlight-name"
            :title="displayNameTitle(selectedNode || nodeName)"
          >{{ formatDisplayName(selectedNode || nodeName) }}</strong>
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

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import BaseModal from './BaseModal.vue'
import {
  fetchNodes,
  fetchNodeOspushData,
  fetchNodeOsgrabData,
  submitOspush,
  submitOsgrab,
} from '../api'
import type { NodeRow, OsPushGrabPayload } from '@/types'
import { displayNameTitle, formatDisplayName } from '@/constants/displayName'

const props = defineProps<{
  flow: 'ospush' | 'osgrab'
  nodeName: string
}>()

const emit = defineEmits<{
  close: []
  saved: []
}>()

const errorMsg = ref('')
const successMsg = ref('')
const loading = ref(true)
const submitting = ref(false)
const selectedNode = ref('')
const selectedOsimage = ref('')
const bare = ref(false)
const noDry = ref(false)
const nodeOptions = ref<string[]>([])
const osimageOptions = ref<string[]>([])

function canonicalName(displayName: unknown): string {
  return String(displayName || '').replace(/\s+\*$/, '').trim()
}

const submitButtonLabel = computed((): string =>
  props.flow === 'osgrab' ? 'Grab OS Image' : 'Push OS Image',
)

function optionList(payload: OsPushGrabPayload, ...keys: string[]): string[] {
  for (const k of keys) {
    const v = (payload as Record<string, unknown>)[k]
    if (Array.isArray(v)) return v as string[]
    if (v && typeof v === 'object' && Array.isArray((v as Record<string, unknown>).options))
      return (v as Record<string, unknown>).options as string[]
  }
  return []
}

function coalesceStr(...vals: unknown[]): string {
  for (const v of vals) {
    if (v == null) continue
    const s = String(v).trim()
    if (s !== '') return s
  }
  return ''
}

function selectedOption(payload: OsPushGrabPayload, ...keys: string[]): string {
  for (const k of keys) {
    const v = (payload as Record<string, unknown>)[k]

    if (v && typeof v === 'object' && !Array.isArray(v) && typeof (v as Record<string, unknown>).selected === 'string') {
      return String((v as Record<string, unknown>).selected).trim()
    }
  }

  return ''
}

async function loadOsFormForNode(name: string) {
  const fetchFn = props.flow === 'osgrab' ? fetchNodeOsgrabData : fetchNodeOspushData
  const payload = await fetchFn(name)
  osimageOptions.value = optionList(payload, 'osimage_list', 'osimage')
  selectedOsimage.value = coalesceStr(selectedOption(payload, 'osimage_list', 'osimage'), payload.data?.osimage)
}

function buildNodeOptionsFromInventory(rows: NodeRow[], preferredCanon: string): string[] {
  const names = new Set<string>()
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

  let rows: NodeRow[] = []
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
    selectedOsimage.value = coalesceStr(selectedOption(payload, 'osimage_list', 'osimage'), payload.data?.osimage)
  } catch (err) {
    errorMsg.value = (err as Error).message || 'Failed to load form data.'
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
    errorMsg.value = (err as Error).message || 'Failed to load OS images for this node.'
  }
}

async function onSubmit() {
  errorMsg.value = ''
  successMsg.value = ''
  submitting.value = true
  const target = selectedNode.value
  const body: Record<string, unknown> = { osimage: selectedOsimage.value }
  if (props.flow === 'osgrab' && bare.value) body.bare = true
  if (noDry.value) body.nodry = true
  try {
    const { ok, data } =
      props.flow === 'osgrab'
        ? await submitOsgrab(target, body)
        : await submitOspush(target, body)
    if (ok || data.status === 'success') {
      successMsg.value = data.message || (props.flow === 'osgrab' ? 'OS grab initiated.' : 'OS push initiated.')
      emit('saved')
    } else {
      errorMsg.value = data.message || 'Request failed.'
    }
  } catch (err) {
    errorMsg.value = (err as Error).message || 'Network error.'
  } finally {
    submitting.value = false
  }
}
</script>
