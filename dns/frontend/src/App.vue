<template>
  <div class="tx-app-layout">
    <AppHeader />
    <main class="tx-app-main">
      <DnsInventory
        ref="inventoryRef"
        @open-add="addOpen = true"
        @open-update="openUpdate"
        @open-delete="openDelete"
      />
    </main>
    <AppFooter />
  </div>

  <AddDnsModal v-if="addOpen" @close="addOpen = false" @saved="onSaved" />
  <UpdateDnsModal
    v-if="updateOpen && updateKey"
    :key="updateKey"
    :network="updateNetwork"
    :host="updateHost"
    @close="closeUpdate"
    @saved="onSaved"
  />
  <DeleteDnsModal
    v-if="deleteOpen && deleteKey"
    :key="'del:' + deleteKey"
    :network="deleteNetwork"
    :host="deleteHost"
    @close="closeDelete"
    @deleted="onDeleted"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import DnsInventory from './components/DnsInventory.vue'
import AddDnsModal from './components/AddDnsModal.vue'
import UpdateDnsModal from './components/UpdateDnsModal.vue'
import DeleteDnsModal from './components/DeleteDnsModal.vue'

const inventoryRef = ref<{ loadData?: () => void } | null>(null)
const addOpen = ref(false)
const updateOpen = ref(false)
const updateNetwork = ref('')
const updateHost = ref('')
const updateKey = ref('')
const deleteOpen = ref(false)
const deleteNetwork = ref('')
const deleteHost = ref('')
const deleteKey = ref('')

function openUpdate(network: string, host: string) {
  updateNetwork.value = network || ''
  updateHost.value = host || ''
  updateKey.value = `${updateNetwork.value}::${updateHost.value}`
  updateOpen.value = !!(updateNetwork.value && updateHost.value)
}

function closeUpdate() {
  updateOpen.value = false
  updateNetwork.value = ''
  updateHost.value = ''
  updateKey.value = ''
}

function openDelete(network: string, host: string) {
  deleteNetwork.value = network || ''
  deleteHost.value = host || ''
  deleteKey.value = `${deleteNetwork.value}::${deleteHost.value}`
  deleteOpen.value = !!(deleteNetwork.value && deleteHost.value)
}

function closeDelete() {
  deleteOpen.value = false
  deleteNetwork.value = ''
  deleteHost.value = ''
  deleteKey.value = ''
}

function onSaved() {
  addOpen.value = false
  closeUpdate()
  inventoryRef.value?.loadData?.()
}

function onDeleted() {
  closeDelete()
  inventoryRef.value?.loadData?.()
}
</script>
