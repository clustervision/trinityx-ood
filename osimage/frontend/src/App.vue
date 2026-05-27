<template>
  <div class="tx-app-layout">
    <AppHeader />
    <main class="tx-app-main">
      <OsimageInventory
        ref="inventoryRef"
        @open-add="addOpen = true"
        @open-edit="openEdit"
        @open-clone="openClone"
        @open-delete="openDelete"
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
  <DeleteOsimageModal
    v-if="deleteOpen && deleteImageName"
    :key="'delete:' + deleteImageName"
    :image-name="deleteImageName"
    @close="closeDelete"
    @deleted="onDeleteSaved"
  />
</template>

<script setup>
import { ref, nextTick } from 'vue'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import OsimageInventory from './components/OsimageInventory.vue'
import AddOsimageModal from './components/AddOsimageModal.vue'
import EditOsimageModal from './components/EditOsimageModal.vue'
import CloneOsimageModal from './components/CloneOsimageModal.vue'
import DeleteOsimageModal from './components/DeleteOsimageModal.vue'

const inventoryRef = ref(null)
const addOpen = ref(false)
const editOpen = ref(false)
const editName = ref('')
const cloneOpen = ref(false)
const cloneSourceName = ref('')
const deleteOpen = ref(false)
const deleteImageName = ref('')

function openEdit(name) {
  editName.value = name || ''
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
  editName.value = ''
  blurInventoryNameFocus()
}

function openClone(name) {
  cloneSourceName.value = name || ''
  cloneOpen.value = true
}

function closeClone() {
  cloneOpen.value = false
  cloneSourceName.value = ''
}

function openDelete(name) {
  deleteImageName.value = name || ''
  deleteOpen.value = !!deleteImageName.value
}

function closeDelete() {
  deleteOpen.value = false
  deleteImageName.value = ''
}

function onDeleteSaved() {
  closeDelete()
  inventoryRef.value?.loadData?.()
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
