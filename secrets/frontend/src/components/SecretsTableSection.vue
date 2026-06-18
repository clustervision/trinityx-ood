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
  <section class="tx-secrets-pane">
    <h2 class="tx-title tx-pane-title">{{ title }}</h2>
    <label class="tx-inline-search" style="margin-bottom: 0.5rem">
      <span class="tx-inline-search-label">Search:</span>
      <input :value="search" class="tx-inline-search-input" @input="$emit('update:search', ($event.target as HTMLInputElement).value)" />
    </label>
    <div class="tx-inventory-table-wrap">
      <table class="tx-inventory-table tx-secrets-table">
        <thead>
          <tr>
            <th class="tx-th-regular">Name</th>
            <th class="tx-th-regular">{{ ownerHeader }}</th>
            <th class="tx-th-regular">Path</th>
            <th class="tx-th-regular">Content</th>
            <th class="tx-th-regular tx-th-actions">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="`${row.entity}-${row.owner}-${row.name}`">
            <td>
              <button type="button" class="tx-name-link" :title="secretNameTitle(row.name)" @click="$emit('edit', row)">
                <span class="tx-cell-ellipsis tx-cell-truncate-js">{{ formatSecretNameDisplay(row.name) }}</span>
              </button>
            </td>
            <td><span class="tx-cell-ellipsis">{{ row.owner }}</span></td>
            <td><span class="tx-cell-ellipsis">{{ row.path }}</span></td>
            <td class="tx-secret-content-cell">
              <div class="tx-secret-content-display">
                <span class="tx-secret-masked">***</span>
                <button
                  type="button"
                  class="tx-icon-act tx-icon-link"
                  title="Edit content"
                  @click="$emit('edit-content', row)"
                >
                  <img :src="actionIcons.edit" alt="Edit content" width="28" height="28" />
                </button>
              </div>
            </td>
            <td class="tx-col-actions">
              <div class="tx-action-icons">
                <button type="button" class="tx-icon-act tx-icon-clone" title="Clone" @click="$emit('clone', row)">
                  <img :src="actionIcons.clone" alt="Clone" width="28" height="28" />
                </button>
                <button type="button" class="tx-icon-act tx-icon-danger" title="Delete" @click="$emit('delete', row)">
                  <img :src="actionIcons.delete" alt="Delete" width="28" height="28" />
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="rows.length === 0">
            <td colspan="5">{{ emptyText }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup lang="ts">
import { actionIcons } from '@/utils/assetImg'
import { formatSecretNameDisplay, secretNameTitle } from '@/constants/secretName'
import type { SecretRecord } from '@/types'

defineProps<{
  title: string
  ownerHeader: string
  rows: SecretRecord[]
  search: string
  emptyText: string
}>()

defineEmits<{
  'update:search': [value: string]
  edit: [row: SecretRecord]
  'edit-content': [row: SecretRecord]
  clone: [row: SecretRecord]
  delete: [row: SecretRecord]
}>()
</script>
