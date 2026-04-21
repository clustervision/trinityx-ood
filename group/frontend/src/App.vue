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

<script setup>
import { ref } from 'vue'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import GroupInventory from './components/GroupInventory.vue'
import EditGroupModal from './components/EditGroupModal.vue'
import AddGroupModal from './components/AddGroupModal.vue'
import CloneGroupModal from './components/CloneGroupModal.vue'
import PushOsModal from './components/PushOsModal.vue'
import DeleteConfirmModal from './components/DeleteConfirmModal.vue'

const activeModal = ref(null)
const selectedGroup = ref('')
const inventoryRef = ref(null)

function openModal(type, groupName) {
  selectedGroup.value = groupName || ''
  activeModal.value = type
}

function closeModal() {
  activeModal.value = null
  selectedGroup.value = ''
}

function onSaved() {
  closeModal()
  if (inventoryRef.value?.loadData) {
    inventoryRef.value.loadData()
  }
}
</script>
