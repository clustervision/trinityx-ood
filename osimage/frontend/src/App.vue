<template>
  <div class="tx-app-layout">
    <AppHeader />
    <main class="tx-app-main">
      <OsimageInventory
        ref="inventoryRef"
        @open-add="addOpen = true"
        @open-edit="openEdit"
        @open-clone="openClone"
      />
    </main>
    <AppFooter />
  </div>

  <AddOsimageModal
    v-if="addOpen"
    @close="addOpen = false"
    @saved="onSaved"
  />
  <EditOsimageModal
    v-if="editOpen && editName"
    :key="editName"
    :image-name="editName"
    @close="closeEdit"
    @saved="onSaved"
    @renamed="onRenamed"
  />
  <CloneOsimageModal
    v-if="cloneOpen && cloneSourceName"
    :key="'clone:' + cloneSourceName"
    :source-name="cloneSourceName"
    @close="closeClone"
    @saved="onCloneSaved"
  />
</template>

<script setup>
import { ref } from 'vue'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import OsimageInventory from './components/OsimageInventory.vue'
import AddOsimageModal from './components/AddOsimageModal.vue'
import EditOsimageModal from './components/EditOsimageModal.vue'
import CloneOsimageModal from './components/CloneOsimageModal.vue'

const inventoryRef = ref(null)
const addOpen = ref(false)
const editOpen = ref(false)
const editName = ref('')
const cloneOpen = ref(false)
const cloneSourceName = ref('')

function openEdit(name) {
  editName.value = name || ''
  editOpen.value = true
}

function closeEdit() {
  editOpen.value = false
  editName.value = ''
}

function openClone(name) {
  cloneSourceName.value = name || ''
  cloneOpen.value = true
}

function closeClone() {
  cloneOpen.value = false
  cloneSourceName.value = ''
}

function onSaved() {
  addOpen.value = false
  closeEdit()
  inventoryRef.value?.loadData?.()
}

function onRenamed(newName) {
  if (newName) editName.value = newName
  inventoryRef.value?.loadData?.()
}

function onCloneSaved() {
  closeClone()
  inventoryRef.value?.loadData?.()
}
</script>
