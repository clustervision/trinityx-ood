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
  const target = deleteTarget.value
  if (target && inventoryRef.value?.removeTag) {
    inventoryRef.value.removeTag(target.osimage, target.name)
  }
  closeDelete()
  inventoryRef.value?.loadData?.({ silent: true })
}

function onSaved() {
  addOpen.value = false
  inventoryRef.value?.loadData?.()
}
</script>
