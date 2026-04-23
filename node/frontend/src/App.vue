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
    :node-name="editNodeName"
    :get-inventory-ipv4="inventoryIpv4Records"
    :inventory-exclude-node-name="editNodeName"
    @close="closeEdit"
    @saved="onNodeSaved"
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
</template>

<script setup>
import { ref } from 'vue'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import NodeInventory from './components/NodeInventory.vue'
import AddNodeModal from './components/AddNodeModal.vue'
import EditNodeModal from './components/EditNodeModal.vue'
import NodePushFlowModal from './components/NodePushFlowModal.vue'
import CloneNodeModal from './components/CloneNodeModal.vue'

const inventoryRef = ref(null)
const addOpen = ref(false)
const editOpen = ref(false)
const editNodeName = ref('')
const pushFlowOpen = ref(false)
const pushFlowType = ref('')
const pushFlowNodeName = ref('')
const cloneOpen = ref(false)
const cloneSourceName = ref('')

function openEdit(name) {
  editNodeName.value = name || ''
  editOpen.value = true
}

function closeEdit() {
  editOpen.value = false
  editNodeName.value = ''
}

function openPushFlow(flow, name) {
  pushFlowType.value = flow
  pushFlowNodeName.value = name || ''
  pushFlowOpen.value = true
}

function closePushFlow() {
  pushFlowOpen.value = false
  pushFlowType.value = ''
  pushFlowNodeName.value = ''
}

function openClone(name) {
  cloneSourceName.value = name || ''
  cloneOpen.value = true
}

function closeClone() {
  cloneOpen.value = false
  cloneSourceName.value = ''
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

function onPushFlowSaved() {
  inventoryRef.value?.loadData?.()
}

function inventoryIpv4Records() {
  return inventoryRef.value?.collectInventoryIpv4Records?.() ?? []
}
</script>
