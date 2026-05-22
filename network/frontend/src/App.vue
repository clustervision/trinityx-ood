<template>
  <div class="tx-app-layout">
    <AppHeader />
    <main class="tx-app-main">
      <NetworkInventory
        ref="inventoryRef"
        @open-add="addOpen = true"
        @open-edit="openEdit"
        @open-delete="openDelete"
        @open-reserved="openReserved"
        @open-ip-check="openIpCheck"
      />
    </main>
    <AppFooter />
  </div>

  <AddNetworkModal v-if="addOpen" @close="addOpen = false" @saved="onSaved" />
  <EditNetworkModal
    v-if="editOpen && editName"
    :key="editName"
    :network-name="editName"
    @close="closeEdit"
    @saved="onSaved"
    @renamed="onRenamed"
  />
  <DeleteNetworkModal
    v-if="deleteOpen && deleteName"
    :key="'delete:' + deleteName"
    :network-name="deleteName"
    @close="closeDelete"
    @deleted="onDeleteSaved"
  />
  <ReservedIpModal
    v-if="reserveOpen && reserveName"
    :key="'reserve:' + reserveName"
    :network-name="reserveName"
    @close="closeReserved"
  />
  <IpCheckModal
    v-if="ipCheckOpen && ipCheckNetwork"
    :key="'ip:' + ipCheckNetwork"
    :network-name="ipCheckNetwork"
    @close="closeIpCheck"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import NetworkInventory from './components/NetworkInventory.vue'
import AddNetworkModal from './components/AddNetworkModal.vue'
import EditNetworkModal from './components/EditNetworkModal.vue'
import DeleteNetworkModal from './components/DeleteNetworkModal.vue'
import ReservedIpModal from './components/ReservedIpModal.vue'
import IpCheckModal from './components/IpCheckModal.vue'
const inventoryRef = ref<{ loadData?: () => void } | null>(null)
const addOpen = ref(false)
const editOpen = ref(false)
const editName = ref('')
const deleteOpen = ref(false)
const deleteName = ref('')
const reserveOpen = ref(false)
const reserveName = ref('')
const ipCheckOpen = ref(false)
const ipCheckNetwork = ref('')

function openEdit(name: string) {
  editName.value = name || ''
  editOpen.value = !!editName.value
}

function closeEdit() {
  editOpen.value = false
  editName.value = ''
}

function openDelete(name: string) {
  deleteName.value = name || ''
  deleteOpen.value = !!deleteName.value
}

function closeDelete() {
  deleteOpen.value = false
  deleteName.value = ''
}

function openReserved(name: string) {
  reserveName.value = name || ''
  reserveOpen.value = !!reserveName.value
}

function closeReserved() {
  reserveOpen.value = false
  reserveName.value = ''
}

function openIpCheck(name: string) {
  ipCheckNetwork.value = name || ''
  ipCheckOpen.value = !!ipCheckNetwork.value
}

function closeIpCheck() {
  ipCheckOpen.value = false
  ipCheckNetwork.value = ''
}

function onSaved() {
  addOpen.value = false
  closeEdit()
  inventoryRef.value?.loadData?.()
}

function onRenamed(newName: string) {
  if (newName) editName.value = newName
  inventoryRef.value?.loadData?.()
}

function onDeleteSaved() {
  closeDelete()
  inventoryRef.value?.loadData?.()
}
</script>
