<template>
  <div class="tx-app-layout">
    <AppHeader />
    <main class="tx-app-main">
      <OsimageTagInventory
        ref="inventoryRef"
        @open-add="addOpen = true"
        @open-detail="openDetail"
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
</template>

<script setup>
import { ref } from 'vue'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import OsimageTagInventory from './components/OsimageTagInventory.vue'
import AddTagModal from './components/AddTagModal.vue'
import TagDetailModal from './components/TagDetailModal.vue'

const inventoryRef = ref(null)
const addOpen = ref(false)
const detailOpen = ref(false)
const detailRow = ref(null)

function openDetail(row) {
  detailRow.value = row && typeof row === 'object' ? row : null
  detailOpen.value = !!detailRow.value
}

function closeDetail() {
  detailOpen.value = false
  detailRow.value = null
}

function onSaved() {
  addOpen.value = false
  inventoryRef.value?.loadData?.()
}
</script>
