<template>
  <div class="tx-app-layout">
    <AppHeader />
    <main class="tx-app-main">
      <section class="tx-shell tx-inventory-page">
        <div class="tx-header">
          <h1 class="tx-title">Secrets</h1>
          <div class="tx-header-actions">
            <button class="tx-btn tx-btn-blue" @click="openAdd">Add Secret</button>
            <button class="tx-btn tx-btn-help">?</button>
            <label class="tx-inline-search">
              <span class="tx-inline-search-label">SHOW:</span>
              <select v-model="scope" class="tx-inline-search-input">
                <option value="all">All Secrets</option>
                <option value="group">Group Secrets</option>
                <option value="node">Node Secrets</option>
              </select>
            </label>
          </div>
        </div>

        <p v-if="error" class="alert-danger">{{ error }}</p>
        <p v-if="success" class="alert-success">{{ success }}</p>

        <div class="tx-secrets-split" :class="{ 'tx-secrets-split-single': scope !== 'all' }">
          <section class="tx-secrets-pane" v-if="scope !== 'node'">
            <h2 class="tx-title tx-pane-title">Group Secrets</h2>
            <label class="tx-inline-search" style="margin-bottom: 0.5rem">
              <span class="tx-inline-search-label">Search:</span>
              <input v-model="groupSearch" class="tx-inline-search-input" />
            </label>
            <div class="tx-inventory-table-wrap">
              <table class="tx-inventory-table tx-secrets-table">
                <thead>
                  <tr><th class="tx-th-regular">Name</th><th class="tx-th-regular">Group</th><th class="tx-th-regular">Path</th><th class="tx-th-regular">Content</th><th class="tx-th-regular tx-th-actions">Actions</th></tr>
                </thead>
                <tbody>
                  <tr v-for="row in groupRows" :key="`g-${row.owner}-${row.name}`">
                    <td><span class="tx-cell-ellipsis">{{ row.name }}</span></td>
                    <td><span class="tx-cell-ellipsis">{{ row.owner }}</span></td>
                    <td><span class="tx-cell-ellipsis">{{ row.path }}</span></td>
                    <td><span class="tx-cell-ellipsis" :title="row.content">{{ preview(row.content) }}</span></td>
                    <td class="tx-col-actions"><div class="tx-action-icons"><button class="tx-icon-act tx-icon-link" @click="openEdit(row)">✎</button><button class="tx-icon-act tx-icon-clone" @click="openClone(row)">⧉</button><button class="tx-icon-act tx-icon-danger" @click="openDelete(row)">🗑</button></div></td>
                  </tr>
                  <tr v-if="groupRows.length === 0"><td colspan="5">There are no Group Secrets</td></tr>
                </tbody>
              </table>
            </div>
          </section>

          <section class="tx-secrets-pane" v-if="scope !== 'group'">
            <h2 class="tx-title tx-pane-title">Node Secrets</h2>
            <label class="tx-inline-search" style="margin-bottom: 0.5rem">
              <span class="tx-inline-search-label">Search:</span>
              <input v-model="nodeSearch" class="tx-inline-search-input" />
            </label>
            <div class="tx-inventory-table-wrap">
              <table class="tx-inventory-table tx-secrets-table">
                <thead>
                  <tr><th class="tx-th-regular">Name</th><th class="tx-th-regular">Node</th><th class="tx-th-regular">Path</th><th class="tx-th-regular">Content</th><th class="tx-th-regular tx-th-actions">Actions</th></tr>
                </thead>
                <tbody>
                  <tr v-for="row in nodeRows" :key="`n-${row.owner}-${row.name}`">
                    <td><span class="tx-cell-ellipsis">{{ row.name }}</span></td>
                    <td><span class="tx-cell-ellipsis">{{ row.owner }}</span></td>
                    <td><span class="tx-cell-ellipsis">{{ row.path }}</span></td>
                    <td><span class="tx-cell-ellipsis" :title="row.content">{{ preview(row.content) }}</span></td>
                    <td class="tx-col-actions"><div class="tx-action-icons"><button class="tx-icon-act tx-icon-link" @click="openEdit(row)">✎</button><button class="tx-icon-act tx-icon-clone" @click="openClone(row)">⧉</button><button class="tx-icon-act tx-icon-danger" @click="openDelete(row)">🗑</button></div></td>
                  </tr>
                  <tr v-if="nodeRows.length === 0"><td colspan="5">There are no Node Secrets</td></tr>
                </tbody>
              </table>
            </div>
          </section>
        </div>
      </section>
    </main>
    <AppFooter />
  </div>

  <SecretFormModal v-if="addOpen" mode="add" title="Add Secret" :initial="emptyForm" @close="closeAll" @submit="onAdd" />
  <SecretFormModal v-if="editOpen" mode="edit" title="Edit Secret" :initial="formState" @close="closeAll" @submit="onEdit" />
  <SecretFormModal v-if="cloneOpen" mode="clone" title="Clone Secret" :initial="formState" @close="closeAll" @submit="onClone" />
  <DeleteSecretModal v-if="deleteOpen && current" :item="current" @close="closeAll" @confirm="onDelete" />
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import SecretFormModal from './components/SecretFormModal.vue'
import DeleteSecretModal from './components/DeleteSecretModal.vue'
import { addSecret, cloneSecret, deleteSecret, fetchSecrets, updateSecret } from './api'
import type { SecretFormState, SecretRecord } from './types'

const rows = ref<SecretRecord[]>([])
const error = ref('')
const success = ref('')
const scope = ref<'all' | 'group' | 'node'>('all')
const groupSearch = ref('')
const nodeSearch = ref('')
const current = ref<SecretRecord | null>(null)
const addOpen = ref(false)
const editOpen = ref(false)
const cloneOpen = ref(false)
const deleteOpen = ref(false)

const emptyForm: SecretFormState = { entity: 'group', owner: '', name: '', path: '', content: '' }
const formState = ref<SecretFormState>({ ...emptyForm })

const groupRows = computed(() => filterRows('group', groupSearch.value))
const nodeRows = computed(() => filterRows('node', nodeSearch.value))

function filterRows(entity: 'group' | 'node', q: string): SecretRecord[] {
  const text = q.trim().toLowerCase()
  return rows.value.filter((r) => {
    if (r.entity !== entity) return false
    if (!text) return true
    return [r.name, r.owner, r.path, r.content].join(' ').toLowerCase().includes(text)
  })
}

function preview(content: string): string {
  return content.length > 30 ? `${content.slice(0, 27)}...` : content
}

function openAdd() {
  formState.value = { ...emptyForm }
  addOpen.value = true
}
function openEdit(item: SecretRecord) {
  current.value = item
  formState.value = { ...item }
  editOpen.value = true
}
function openClone(item: SecretRecord) {
  current.value = item
  formState.value = { ...item, name: `${item.name}-copy` }
  cloneOpen.value = true
}
function openDelete(item: SecretRecord) {
  current.value = item
  deleteOpen.value = true
}
function closeAll() {
  addOpen.value = false
  editOpen.value = false
  cloneOpen.value = false
  deleteOpen.value = false
}

async function load() {
  const res = await fetchSecrets()
  rows.value = res.rows
  error.value = res.error
}

async function onAdd(form: SecretFormState) {
  await handleAction(() => addSecret(form), 'Secret added.')
}
async function onEdit(form: SecretFormState) {
  if (!current.value) return
  await handleAction(() => updateSecret(current.value!, form), 'Secret updated.')
}
async function onClone(form: SecretFormState) {
  if (!current.value) return
  await handleAction(() => cloneSecret(current.value!, form), 'Secret cloned.')
}
async function onDelete() {
  if (!current.value) return
  await handleAction(() => deleteSecret(current.value!.entity, current.value!.owner, current.value!.name), 'Secret deleted.')
}

async function handleAction(action: () => Promise<void>, msg: string) {
  try {
    error.value = ''
    success.value = ''
    await action()
    success.value = msg
    closeAll()
    await load()
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Request failed.'
  }
}

void load()
</script>
