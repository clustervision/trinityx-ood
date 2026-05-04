<script setup lang="ts">
import { ref } from 'vue'

import AppHeader from '@/components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import GroupInventory from './components/GroupInventory.vue'
import EditGroupModal from './components/EditGroupModal.vue'
import AddGroupModal from './components/AddGroupModal.vue'
import CloneGroupModal from './components/CloneGroupModal.vue'
import PushOsModal from './components/PushOsModal.vue'
import DeleteConfirmModal from './components/DeleteConfirmModal.vue'
import { fetchResources } from '@/services/api'
/** -----------------------
 * Types
 * ---------------------- */
type ModalType = 'add' | 'edit' | 'clone' | 'ospush' | 'delete' | null

interface InventoryRefType {
  loadData?: () => void
}

/** -----------------------
 * State
 * ---------------------- */
const activeModal = ref<ModalType>(null)
const selectedGroup = ref<string>('')
const inventoryRef = ref<InventoryRefType | null>(null)

/** -----------------------
 * UI Actions
 * ---------------------- */
function openModal(type: ModalType, groupName?: string) {
  selectedGroup.value = groupName ?? ''
  activeModal.value = type
  // if (type === 'add') {
  //   const resource_data = fetchResources();
  //   console.log(resource_data);
  // }

}

function closeModal() {
  activeModal.value = null
  selectedGroup.value = ''
}

function onSaved() {
  closeModal()
  inventoryRef.value?.loadData?.()
}
</script>

<template>
  <div class="tx-app-layout">
    <AppHeader />

    <main class="tx-app-main">
      <GroupInventory
        ref="inventoryRef"
        @open-add="openModal('add')"
        @open-edit="openModal('edit', $event)"
        @clone="openModal('clone', $event)"
        @ospush="openModal('ospush', $event)"
        @delete="openModal('delete', $event)"
      />
    </main>

    <AppFooter />
  </div>

  <!-- Modals -->
  <EditGroupModal
    v-if="activeModal === 'edit'"
    :group-name="selectedGroup"
    @close="closeModal"
    @saved="onSaved"
  />

  <AddGroupModal
    v-if="activeModal === 'add'"
    @close="closeModal"
    @saved="onSaved"
  />

  <CloneGroupModal
    v-if="activeModal === 'clone'"
    :group-name="selectedGroup"
    @close="closeModal"
    @saved="onSaved"
  />

  <PushOsModal
    v-if="activeModal === 'ospush'"
    :group-name="selectedGroup"
    @close="closeModal"
    @saved="onSaved"
  />

  <DeleteConfirmModal
    v-if="activeModal === 'delete'"
    :group-name="selectedGroup"
    @close="closeModal"
    @deleted="onSaved"
  />
</template>
