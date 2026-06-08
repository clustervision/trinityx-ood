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
              <button type="button" class="tx-name-link" :title="row.name" @click="$emit('edit', row)">
                <span class="tx-cell-ellipsis tx-cell-truncate-js">{{ row.name }}</span>
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
