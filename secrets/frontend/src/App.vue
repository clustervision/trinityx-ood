<template>
  <div class="tx-app-layout">
    <AppHeader />
    <main class="tx-app-main">
      <section class="tx-shell tx-inventory-page">
        <div class="tx-header">
          <h1 class="tx-title">Secrets</h1>
          <div class="tx-header-actions">
            <button class="tx-btn tx-btn-blue" @click="openAdd">Add Secret</button>
            <button class="tx-btn tx-btn-help" type="button" title="Help" @click="helpOpen = true">?</button>
            <div class="tx-inline-search">
              <span class="tx-inline-search-label">SHOW:</span>
              <select v-model="scope" class="tx-inline-search-input tx-inline-search-select">
                <option value="all">All Secrets</option>
                <option value="group">Group Secrets</option>
                <option value="node">Node Secrets</option>
              </select>
            </div>
          </div>
        </div>

        <p v-if="error" class="alert-danger">{{ error }}</p>
        <p v-if="success" class="alert-success">{{ success }}</p>

        <div class="tx-secrets-split" :class="{ 'tx-secrets-split-single': scope !== 'all' }">
          <SecretsTableSection
            v-if="scope !== 'node'"
            title="Group Secrets"
            owner-header="Group"
            :rows="groupRows"
            v-model:search="groupSearch"
            empty-text="There are no Group Secrets"
            @edit="openEdit"
            @edit-content="openContentEdit"
            @clone="openClone"
            @delete="openDelete"
          />
          <SecretsTableSection
            v-if="scope !== 'group'"
            title="Node Secrets"
            owner-header="Node"
            :rows="nodeRows"
            v-model:search="nodeSearch"
            empty-text="There are no Node Secrets"
            @edit="openEdit"
            @edit-content="openContentEdit"
            @clone="openClone"
            @delete="openDelete"
          />
        </div>
      </section>
    </main>
    <AppFooter />
  </div>

  <Teleport to="body">
    <div v-if="helpOpen" class="tx-modal-overlay" @mousedown.self="helpOpen = false">
      <div class="tx-help-dialog" role="dialog" aria-labelledby="secrets-help-title">
        <button type="button" class="tx-modal-x" aria-label="Close" @click="helpOpen = false">&times;</button>
        <h2 id="secrets-help-title" class="tx-help-title">How to use Secrets</h2>
        <h3 class="tx-help-section-title">Main page</h3>
        <ul class="tx-help-list">
          <li><strong>SHOW</strong> — Filter by all secrets, group secrets, or node secrets.</li>
          <li><strong>Search</strong> — Filter each table as you type.</li>
        </ul>
        <h3 class="tx-help-section-title">Secret actions</h3>
        <ul class="tx-help-list">
          <li><strong>Add Secret</strong> — Create a new group or node secret.</li>
          <li><strong>Edit</strong> — Click a secret name to update metadata.</li>
          <li><strong>Edit Content</strong> — Open the secret value in the text editor.</li>
          <li><strong>Clone</strong> — Duplicate a secret with a new name.</li>
          <li><strong>Delete</strong> — Remove a secret.</li>
        </ul>
      </div>
    </div>
  </Teleport>

  <SecretFormModal v-if="addOpen" mode="add" title="Add Secret" :initial="emptyForm" @close="closeAll" @submit="onAdd" />
  <SecretFormModal v-if="editOpen" mode="edit" title="Edit Secret" :initial="formState" @close="closeAll" @submit="onEdit" />
  <SecretFormModal v-if="cloneOpen" mode="clone" title="Clone Secret" :initial="formState" @close="closeAll" @submit="onClone" />
  <DeleteSecretModal v-if="deleteOpen && current" :item="current" @close="closeAll" @confirm="onDelete" />
  <TextEditorModal
    v-if="contentEditOpen && contentEditRow"
    title="Edit Content"
    :model-value="contentEditValue"
    @saved="onContentSaved"
    @close="closeContentEdit"
  />
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import SecretFormModal from './components/SecretFormModal.vue'
import DeleteSecretModal from './components/DeleteSecretModal.vue'
import SecretsTableSection from './components/SecretsTableSection.vue'
import TextEditorModal from './components/TextEditorModal.vue'
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
const contentEditOpen = ref(false)
const contentEditRow = ref<SecretRecord | null>(null)
const contentEditValue = ref('')
const helpOpen = ref(false)

const emptyForm: SecretFormState = { entity: 'group', owner: '', name: '', path: '', content: '' }
const formState = ref<SecretFormState>({ ...emptyForm })

const groupRows = computed(() => filterRows('group', groupSearch.value))
const nodeRows = computed(() => filterRows('node', nodeSearch.value))

function filterRows(entity: 'group' | 'node', q: string): SecretRecord[] {
  const text = q.trim().toLowerCase()
  return rows.value.filter((r) => {
    if (r.entity !== entity) return false
    if (!text) return true
    return [r.name, r.owner, r.path].join(' ').toLowerCase().includes(text)
  })
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
function openContentEdit(item: SecretRecord) {
  contentEditRow.value = item
  contentEditValue.value = item.content
  contentEditOpen.value = true
}
function closeContentEdit() {
  contentEditOpen.value = false
  contentEditRow.value = null
  contentEditValue.value = ''
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

async function onContentSaved(value: string) {
  const row = contentEditRow.value
  closeContentEdit()
  if (!row) return
  await handleAction(() => updateSecret(row, { ...row, content: value }), 'Secret content updated.')
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
