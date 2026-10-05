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
