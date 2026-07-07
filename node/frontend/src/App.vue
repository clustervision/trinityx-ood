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
  <div class="tx-app-layout">
    <AppHeader />
    <main class="tx-app-main">
      <NodeInventory
        ref="inventoryRef"
        @open-add="addOpen = true"
        @open-edit="openEdit"
        @open-clone="openClone"
        @open-ospush="(n) => openPushFlow('ospush', n)"
        @open-osgrab="(n) => openPushFlow('osgrab', n)"
        @open-delete="openDelete"
      />
    </main>
    <AppFooter />
  </div>

  <AddNodeModal
    v-if="addOpen"
    :get-inventory-ipv4="inventoryIpv4Records"
    @close="addOpen = false"
    @saved="onNodeSaved"
  />
  <EditNodeModal
    v-if="editOpen && editNodeName"
    :key="editNodeName"
    :node-name="editNodeName"
    :get-inventory-ipv4="inventoryIpv4Records"
    :inventory-exclude-node-name="editNodeName"
    @close="closeEdit"
    @saved="onNodeSaved"
    @renamed="onNodeRenamed"
  />
  <NodePushFlowModal
    v-if="pushFlowOpen && pushFlowType && pushFlowNodeName"
    :key="pushFlowType + ':' + pushFlowNodeName"
    :flow="pushFlowType"
    :node-name="pushFlowNodeName"
    @close="closePushFlow"
    @saved="onPushFlowSaved"
  />
  <CloneNodeModal
    v-if="cloneOpen && cloneSourceName"
    :key="'clone:' + cloneSourceName"
    :source-node-name="cloneSourceName"
    :get-inventory-ipv4="inventoryIpv4Records"
    :inventory-exclude-node-name="cloneSourceName"
    @close="closeClone"
    @saved="onCloneSaved"
  />
  <DeleteNodeModal
    v-if="deleteOpen && deleteNodeName"
    :key="'delete:' + deleteNodeName"
    :node-name="deleteNodeName"
    @close="closeDelete"
    @deleted="onDeleteSaved"
  />
</template>

<script setup lang="ts">

import { ref, nextTick } from 'vue'
import type { InventoryIpv4Record } from '@/types'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import NodeInventory from './components/NodeInventory.vue'
import AddNodeModal from './components/AddNodeModal.vue'
import EditNodeModal from './components/EditNodeModal.vue'
import NodePushFlowModal from './components/NodePushFlowModal.vue'
import CloneNodeModal from './components/CloneNodeModal.vue'
import DeleteNodeModal from './components/DeleteNodeModal.vue'

type PushFlowType = 'ospush' | 'osgrab'
const inventoryRef = ref<InstanceType<typeof NodeInventory> | null>(null)
const addOpen = ref(false)
const editOpen = ref(false)
const editNodeName = ref('')
const pushFlowOpen = ref(false)
const pushFlowType = ref<PushFlowType | ''>('')
const pushFlowNodeName = ref('')
const cloneOpen = ref(false)
const cloneSourceName = ref('')
const deleteOpen = ref(false)
const deleteNodeName = ref('')

function openEdit(name: string) {
  editNodeName.value = name || ''
  editOpen.value = true
}

function blurInventoryNameFocus() {
  void nextTick(() => {
    const el = document.activeElement
    if (el instanceof HTMLElement && el.closest('.tx-name-link')) el.blur()
  })
}

function closeEdit() {
  editOpen.value = false
  editNodeName.value = ''
  blurInventoryNameFocus()
}

function openPushFlow(flow: PushFlowType, name: string) {
  pushFlowType.value = flow
  pushFlowNodeName.value = name || ''
  pushFlowOpen.value = true
}

function closePushFlow() {
  pushFlowOpen.value = false
  pushFlowType.value = ''
  pushFlowNodeName.value = ''
}

function openClone(name: string) {
  cloneSourceName.value = name || ''
  cloneOpen.value = true
}

function closeClone() {
  cloneOpen.value = false
  cloneSourceName.value = ''
}

function openDelete(name: string) {
  deleteNodeName.value = name || ''
  deleteOpen.value = !!deleteNodeName.value
}

function closeDelete() {
  deleteOpen.value = false
  deleteNodeName.value = ''
}

function onDeleteSaved() {
  closeDelete()
  inventoryRef.value?.loadData?.()
}

function onCloneSaved() {
  closeClone()
  inventoryRef.value?.loadData?.()
}

function onNodeSaved() {
  addOpen.value = false
  closeEdit()
  inventoryRef.value?.loadData?.()
}

function onNodeRenamed(newName: string) {
  if (newName) editNodeName.value = newName
  inventoryRef.value?.loadData?.()
}

function onPushFlowSaved() {
  inventoryRef.value?.loadData?.()
}

function inventoryIpv4Records(): InventoryIpv4Record[] {
  return inventoryRef.value?.collectInventoryIpv4Records?.() ?? []
}
</script>
