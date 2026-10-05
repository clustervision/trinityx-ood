<!--
  This code is part of the TrinityX software suite
  Copyright (C) 2026  ClusterVision Solutions b.v.

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <https://www.gnu.org/licenses/>

  @author      Yixin Zhang
  @copyright   Copyright 2026, Luna2 Project[OOD]
  @license     GPL
  @version     2.0
  @maintainer  Yixin Zhang
  @email       yixin.zhang@clustervision.com
  @status      Development
-->

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
