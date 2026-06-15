<template>
  <div class="tx-app-layout">
    <AppHeader />
    <main class="tx-app-main">
      <OsimageTagInventory
        ref="inventoryRef"
        @open-add="addOpen = true"
        @open-detail="openDetail"
        @open-delete="openDelete"
      />
    </main>
    <AppFooter />
  </div>

  <AddTagModal
    v-if="addOpen"
    @close="addOpen = false"
    @saved="onSaved"
  />
  <TagDetailModal
    v-if="detailOpen && detailRow"
    :key="`${detailRow.osimage || ''}-${detailRow.name || ''}`"
    :row="detailRow"
    @close="closeDetail"
  />
  <DeleteOsimageTagModal
    v-if="deleteOpen && deleteTarget"
    :key="`del:${deleteTarget.osimage}-${deleteTarget.name}`"
    :osimage="deleteTarget.osimage"
    :tag-name="deleteTarget.name"
    @close="closeDelete"
    @deleted="onDeleteSaved"
  />
</template>

<script setup>
import { ref } from 'vue'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import OsimageTagInventory from './components/OsimageTagInventory.vue'
import AddTagModal from './components/AddTagModal.vue'
import TagDetailModal from './components/TagDetailModal.vue'
import DeleteOsimageTagModal from './components/DeleteOsimageTagModal.vue'

const inventoryRef = ref(null)
const addOpen = ref(false)
const detailOpen = ref(false)
const detailRow = ref(null)
const deleteOpen = ref(false)
const deleteTarget = ref(null)

function openDetail(row) {
  detailRow.value = row && typeof row === 'object' ? row : null
  detailOpen.value = !!detailRow.value
}

function closeDetail() {
  detailOpen.value = false
  detailRow.value = null
}

function openDelete(row) {
  if (!row || !row.osimage || !row.name) {
    deleteTarget.value = null
    deleteOpen.value = false
    return
  }
  deleteTarget.value = { osimage: String(row.osimage), name: String(row.name) }
  deleteOpen.value = true
}

function closeDelete() {
  deleteOpen.value = false
  deleteTarget.value = null
}

function onDeleteSaved() {
  closeDelete()
  inventoryRef.value?.loadData?.()
}

function onSaved() {
  addOpen.value = false
  inventoryRef.value?.loadData?.()
}
</script>
