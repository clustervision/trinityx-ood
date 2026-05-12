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
    v-if="detailOpen && detailName"
    :key="detailName"
    :tag-name="detailName"
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
const detailName = ref('')

function openDetail(name) {
  detailName.value = name || ''
  detailOpen.value = true
}

function closeDetail() {
  detailOpen.value = false
  detailName.value = ''
}

function onSaved() {
  addOpen.value = false
  inventoryRef.value?.loadData?.()
}
</script>
