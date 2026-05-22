<template>
  <div class="tx-app-layout">
    <AppHeader />
    <main class="tx-app-main">
      <DnsInventory
        ref="inventoryRef"
        @open-add="addOpen = true"
        @open-edit="openEdit"
        @open-delete="openDelete"
      />
    </main>
    <AppFooter />
  </div>

  <AddDnsModal v-if="addOpen" @close="addOpen = false" @saved="onSaved" />
  <EditDnsModal
    v-if="editOpen && editKey"
    :key="editKey"
    :network="editNetwork"
    :host="editHost"
    @close="closeEdit"
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
import EditDnsModal from './components/EditDnsModal.vue'
import DeleteDnsModal from './components/DeleteDnsModal.vue'

const inventoryRef = ref<{ loadData?: () => void } | null>(null)
const addOpen = ref(false)
const editOpen = ref(false)
const editNetwork = ref('')
const editHost = ref('')
const editKey = ref('')
const deleteOpen = ref(false)
const deleteNetwork = ref('')
const deleteHost = ref('')
const deleteKey = ref('')

function openEdit(network: string, host: string) {
  editNetwork.value = network || ''
  editHost.value = host || ''
  editKey.value = `${editNetwork.value}::${editHost.value}`
  editOpen.value = !!(editNetwork.value && editHost.value)
}

function closeEdit() {
  editOpen.value = false
  editNetwork.value = ''
  editHost.value = ''
  editKey.value = ''
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
  closeEdit()
  inventoryRef.value?.loadData?.()
}

function onDeleted() {
  closeDelete()
  inventoryRef.value?.loadData?.()
}
</script>
