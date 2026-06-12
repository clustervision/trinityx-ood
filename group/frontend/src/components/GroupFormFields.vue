<script setup lang="ts">
import { ref, reactive, watch, computed, nextTick } from 'vue'
import InterfaceRow from './InterfaceRow.vue'
import TextEditorModal from './TextEditorModal.vue'
import { punAppAssetUrl } from '@/utils/publicAssets'
import type { NetworkInterface } from '@/types/network'
import type { Group } from '@/types/group'
import { normalizeGroupName, validateGroupNameInput } from '@/constants/groupName'

const renameIcon = punAppAssetUrl('icons/icon-rename.png')

const props = defineProps({
  groupList: { type: Array as () => string[], required: true },
  mode: { type: String, default: 'add' },
  initialData: { type: Object, default: () => ({}) },
  bmcsetupOptions: { type: Array as () => string[], default: () => [], },
  osimageOptions: { type: Array as () => string[], default: () => [], },
  networkOptions: { type: Array as () => string[], default: () => [], },
  bondModeOptions: { type: Array as () => string[], default: () => [], },
  submitLabel: { type: String, default: 'Submit' },
  hints: { type: Object, default: () => ({}) },
  submitting: { type: Boolean, default: false },
  recordName: { type: String, default: '' },
})

defineEmits(['submit'])

const originalGroupName = ref('')
const nameInlineEdit = ref(false)
const nameDraft = ref('')
const showInterfaces = ref(false)
const showAdvanced = ref(false)
const textEditorOpen = ref(false)
const textEditorTitle = ref('')
const textEditorField = ref('')
const ifaceOptionsIdx = ref(-1)

function makeEmptyIface() {
  return {
    interface: '',
    network: '',
    mtu: '',
    dhcp: 'false',
    bond_mode: '',
    bond_slaves: '',
    vlanid: '',
    options: '',
    vlan_parent: '',
  }
}

const form = reactive({
  name: '',
  newgroupname: '',

  roles: '',
  netboot: '',
  osimage: '',
  scripts: '',

  setupbmc: '',
  bmcsetupname: '',

  domain: '',
  unmanaged_bmc_users: '',

  kerneloptions: '',
  prescript: '',
  partscript: '',
  postscript: '',

  osimagetag: 'default',

  provision_interface: 'BOOTIF',
  provision_fallback: 'http',
  provision_method: 'torrent',

  bootmenu: '',

  comment: '',

  interfaces: [] as NetworkInterface[],
})

function hydrateForm(d: Partial<Group>) {
  if (!d) return

  form.name = d.name || ''
  form.newgroupname = d.newgroupname || ''

  form.roles = d.roles || ''
  form.netboot = normalizeTriState(d.netboot)
  form.osimage = d.osimage || ''
  form.scripts = d.scripts || ''

  form.setupbmc = normalizeTriState(d.setupbmc)
  form.bmcsetupname = d.bmcsetupname || ''

  form.domain = d.domain || ''
  form.unmanaged_bmc_users = d.unmanaged_bmc_users || ''

  form.kerneloptions = d.kerneloptions || ''
  form.prescript = d.prescript || ''
  form.partscript = d.partscript || ''
  form.postscript = d.postscript || ''

  form.osimagetag = d.osimagetag || ''

  form.provision_interface = d.provision_interface || 'BOOTIF'
  form.provision_fallback = d.provision_fallback || 'http'
  form.provision_method = d.provision_method || 'torrent'

  form.bootmenu = normalizeTriState(d.bootmenu)

  form.comment = d.comment || ''

  if (Array.isArray(d.interfaces) && d.interfaces.length) {
    showInterfaces.value = true
    form.interfaces = d.interfaces.map((row: NetworkInterface) => ({
      interface: row.interface || '',
      network: row.network || '',
      mtu: row.mtu || '',
      dhcp: 'false',
      bond_mode: row.bond_mode || '',
      bond_slaves: row.bond_slaves || '',
      vlanid: row.vlanid || '',
      options: row.options || '',
      vlan_parent: row.vlan_parent || '',
    }))
  } else {
    form.interfaces = []
  }

  if (props.mode === 'edit') {
    const n = String(d.name || props.recordName || '').trim()
    if (n) form.name = n
    originalGroupName.value = String(props.recordName || n).trim()
    nameDraft.value = form.name
    nameInlineEdit.value = false
  }
}

function groupRecordName(): string {
  return String(
    originalGroupName.value || props.recordName || form.name || '',
  ).trim()
}

watch(
  () => props.initialData,
  (d) => {
    hydrateForm(d)
  },
  {
    immediate: true,
    deep: true,
  },
)

function normalizeTriState(v: boolean | string | null | undefined,): string {
  if (
    v === true ||
    v === 'true' ||
    v === 'True'
  ) {
    return 'true'
  }

  if (
    v === false ||
    v === 'false' ||
    v === 'False'
  ) {
    return 'false'
  }

  return ''
}

function toggleInterfaces() {
  showInterfaces.value = !showInterfaces.value

  if (
    showInterfaces.value &&
    form.interfaces.length === 0
  ) {
    form.interfaces.push(makeEmptyIface())
  }
}

function addInterfaceAfter(idx: number) {
  form.interfaces.splice(
    idx + 1,
    0,
    makeEmptyIface(),
  )
}

function removeInterface(idx: number) {
  form.interfaces.splice(idx, 1)
}

function noSpaces(e: KeyboardEvent) {
  if (e.code === 'Space' || e.charCode === 32) {
    e.preventDefault()
  }
}

function startInlineRename() {
  if (props.mode !== 'edit') return
  nameInlineEdit.value = true
  nameDraft.value = form.name || originalGroupName.value
}

function cancelInlineRename() {
  nameInlineEdit.value = false
  nameDraft.value = form.name || originalGroupName.value
  void nextTick(() => {
    const el = document.activeElement
    if (el instanceof HTMLElement) el.blur()
  })
}

function onNameDraftEscape() {
  cancelInlineRename()
}

function openTextEditor(title: string, field: string) {
  ifaceOptionsIdx.value = -1

  textEditorTitle.value = title
  textEditorField.value = field

  textEditorOpen.value = true
}

function openIfaceOptionsEditor(idx: number) {
  ifaceOptionsIdx.value = idx

  textEditorTitle.value = 'Options'
  textEditorField.value = ''

  textEditorOpen.value = true
}

function closeTextEditor() {
  textEditorOpen.value = false
}

const textEditorModalKey = computed(() => {
  return `${ifaceOptionsIdx.value}:${textEditorField.value}`
})

const textEditorModalValue = computed(() => {
  if (ifaceOptionsIdx.value >= 0) {
    return form.interfaces[ifaceOptionsIdx.value]?.options || ''
  }

  return form[textEditorField.value as keyof typeof form] || ''
})

function onTextEditorModalApply(v: string) {
  // ---- Interface editor ----
  if (ifaceOptionsIdx.value >= 0) {
    const idx = ifaceOptionsIdx.value
    const iface = form.interfaces?.[idx]

    if (iface) {
      iface.options = v
    }

    return
  }

  // ---- Form field editor ----
  if (!textEditorField.value) return

  const key = textEditorField.value as keyof typeof form

  if (key in form) {
    form[key] = v as never
  }
}

type UploadField =
  | 'kerneloptions'
  | 'prescript'
  | 'partscript'
  | 'postscript'
  | 'comment'

function looksLikeBinary(buf: ArrayBuffer | null | undefined): boolean {
  if (!buf || !buf.byteLength) return false

  const view = new Uint8Array(buf)
  const n = Math.min(view.length, 65536)

  for (let i = 0; i < n; i++) {
    if (view[i] === 0) return true
  }

  return false
}

function onUploadFile(e: Event, field: UploadField) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  const fr = new FileReader()

  fr.onload = () => {
    const result = fr.result

    if (looksLikeBinary(result as ArrayBuffer | null)) {
      alert('Please choose a text file only.')
      input.value = ''
      return
    }

    if (!result) return

    const text = new TextDecoder('utf-8', { fatal: false }).decode(
      new Uint8Array(result as ArrayBuffer)
    )

    form[field] = text
    input.value = ''
  }

  fr.onerror = () => {
    alert('Could not read the file.')
    input.value = ''
  }

  fr.readAsArrayBuffer(file)
}

function nonEmptyTrimmed(value: unknown): string | null {
  if (value == null) return null
  const s = String(value).trim()
  return s !== '' ? s : null
}

function buildPayload() {
  let urlRecordKey: string
  let groupDisplayName: string

  if (props.mode === 'clone') {
    groupDisplayName = String(form.newgroupname || '').trim()
    urlRecordKey = groupDisplayName
  } else if (props.mode === 'edit') {
    groupDisplayName =
      nameInlineEdit.value
        ? normalizeGroupName(nameDraft.value)
        : (form.name || '').trim()
    urlRecordKey =
      (originalGroupName.value || '').trim() || groupDisplayName
  } else {
    groupDisplayName = (form.name || '').trim()
    urlRecordKey = groupDisplayName
  }

  const cleanedInterfaces = form.interfaces
    .map((iface) => {
      const row: Record<string, unknown> = {}
      const ifaceName = nonEmptyTrimmed(iface.interface)
      const net = nonEmptyTrimmed(iface.network)
      if (ifaceName) row.interface = ifaceName
      if (net) row.network = net
      const mtu = nonEmptyTrimmed(iface.mtu)
      if (mtu) row.mtu = mtu
      const vlanid = nonEmptyTrimmed(iface.vlanid)
      if (vlanid) row.vlanid = vlanid
      const vlanParent = nonEmptyTrimmed(iface.vlan_parent)
      if (vlanParent) row.vlan_parent = vlanParent
      const bondMode = nonEmptyTrimmed(iface.bond_mode)
      if (bondMode) row.bond_mode = bondMode
      const bondSlaves = nonEmptyTrimmed(iface.bond_slaves)
      if (bondSlaves) row.bond_slaves = bondSlaves
      const opts = nonEmptyTrimmed(iface.options)
      if (opts) row.options = opts
      return row
    })
    .filter((row) => Object.keys(row).length > 0)

  const groupPayload: Record<string, unknown> = { name: groupDisplayName, }

  if (form.setupbmc !== '') { groupPayload.setupbmc = form.setupbmc === 'true' ? 'True' : 'False' }
  const domain = nonEmptyTrimmed(form.domain)
  if (domain) groupPayload.domain = domain
  const kerneloptions = nonEmptyTrimmed(form.kerneloptions)
  if (kerneloptions) groupPayload.kerneloptions = kerneloptions
  const prescript = nonEmptyTrimmed(form.prescript)
  if (prescript) groupPayload.prescript = prescript
  const partscript = nonEmptyTrimmed(form.partscript)
  if (partscript) groupPayload.partscript = partscript
  const postscript = nonEmptyTrimmed(form.postscript)
  if (postscript) groupPayload.postscript = postscript
  if (form.netboot !== '') { groupPayload.netboot = form.netboot === 'true' ? 'True' : 'False' }
  if (form.bootmenu !== '') { groupPayload.bootmenu = form.bootmenu === 'true' ? 'True' : 'False' }
  const comment = nonEmptyTrimmed(form.comment)
  if (comment) groupPayload.comment = comment
  const roles = nonEmptyTrimmed(form.roles)
  if (roles) groupPayload.roles = roles
  const scripts = nonEmptyTrimmed(form.scripts)
  if (scripts) groupPayload.scripts = scripts
  const provisionInterface = nonEmptyTrimmed(form.provision_interface)
  if (provisionInterface) groupPayload.provision_interface = provisionInterface
  const provisionMethod = nonEmptyTrimmed(form.provision_method)
  if (provisionMethod) groupPayload.provision_method = provisionMethod
  const provisionFallback = nonEmptyTrimmed(form.provision_fallback)
  if (provisionFallback) groupPayload.provision_fallback = provisionFallback
  const unmanagedBmc = nonEmptyTrimmed(form.unmanaged_bmc_users)
  if (unmanagedBmc) groupPayload.unmanaged_bmc_users = unmanagedBmc
  const osimage = nonEmptyTrimmed(form.osimage)
  if (osimage) groupPayload.osimage = osimage
  if (cleanedInterfaces.length) { groupPayload.interfaces = cleanedInterfaces }
  const bmcsetupname = nonEmptyTrimmed(form.bmcsetupname)
  if (bmcsetupname) groupPayload.bmcsetupname = bmcsetupname
  const osimagetag = nonEmptyTrimmed(form.osimagetag)
  if (osimagetag) groupPayload.osimagetag = osimagetag

  return { config: { group: { [urlRecordKey]: groupPayload, }, }, }
}

function comparableSnapshot() {
  const payload = { ...form }
  if (props.mode === 'edit' && nameInlineEdit.value) {
    payload.name = normalizeGroupName(nameDraft.value)
  }
  return JSON.stringify(payload)
}

defineExpose({
  form,
  buildPayload,
  comparableSnapshot,
})

const liveNameValidationMsg = computed(() => {
  if (props.mode === 'clone') {
    const n = String(form.newgroupname || '').trim()
    if (!n) return ''
    const check = validateGroupNameInput(n)
    if (!check.ok) return check.message
    if (props.groupList.includes(check.name)) return 'Group name already exists'
    return ''
  }
  if (props.mode === 'add') {
    const n = String(form.name || '').trim()
    if (!n) return ''
    const check = validateGroupNameInput(n)
    if (!check.ok) return check.message
    if (props.groupList.includes(check.name)) return 'Group name already exists'
    return ''
  }
  if (props.mode === 'edit' && nameInlineEdit.value) {
    const n = String(nameDraft.value || '').trim()
    if (!n) return ''
    const check = validateGroupNameInput(n)
    if (!check.ok) return check.message
    const orig = normalizeGroupName(originalGroupName.value)
    if (check.name && check.name !== orig && props.groupList.includes(check.name)) {
      return 'Group name already exists'
    }
    return ''
  }
  return ''
})

const isSubmitDisabled = computed(() => Boolean(liveNameValidationMsg.value))

</script>


<template>
  <form @submit.prevent="$emit('submit')" class="tx-group-form tx-group-form-fixed">
    <!-- 3-column top grid -->
    <div v-if="liveNameValidationMsg" class="alert alert-danger" role="alert">{{ liveNameValidationMsg }}</div>
    <div class="tx-add-grid tx-add-form-main">
      <!-- Column 1 -->

      <div class="tx-add-col">
        <div v-if="mode === 'clone'" class="tx-field tx-field-strong">
          <span class="tx-label">Clone Name:</span>
          <input type="text" v-model="form.newgroupname" autocomplete="off" :class="{ 'input-error': liveNameValidationMsg }" @keypress="noSpaces" required />
        </div>
        <div v-else class="tx-field tx-field-strong" :class="{ 'tx-field-name-with-rename': mode === 'edit' }">
          <span class="tx-label">Name:</span>
          <div v-if="mode === 'edit'" class="tx-name-input-wrap">
            <template v-if="!nameInlineEdit">
              <input
                type="text"
                class="tx-name-input-readonly"
                :value="form.name"
                readonly
              />
              <button
                type="button"
                class="tx-btn-rename"
                title="Edit name"
                aria-label="Edit name"
                @click="startInlineRename"
              >
                <img :src="renameIcon" alt="" width="20" height="20" />
              </button>
            </template>
            <template v-else>
              <input
                v-model="nameDraft"
                type="text"
                class="tx-name-input-editing"
                :class="{ 'input-error': liveNameValidationMsg }"
                required
                aria-label="Group name"
                @keypress="noSpaces"
                @keydown.escape.stop="onNameDraftEscape"
              />
              <button
                type="button"
                class="tx-btn-rename tx-btn-rename-cancel-char"
                title="Stop editing name"
                aria-label="Stop editing name"
                @click="cancelInlineRename"
              >
                ×
              </button>
            </template>
          </div>
          <input v-else type="text" v-model="form.name" :class="{ 'input-error': liveNameValidationMsg }" @keypress="noSpaces" required />
        </div>
        <template v-if="mode === 'clone'">
          <div class="tx-add-form-clone-roles-netboot tx-add-form-main">
            <div class="tx-field tx-field-match">
              <span class="tx-label">Roles:</span>
              <input type="text" v-model="form.roles" maxlength="100" />
            </div>
            <div class="tx-field tx-tri-field tx-field-match">
              <span class="tx-label">Net Boot:</span>
              <div class="tx-tri-inner">
                <div class="tx-segmented" role="group" aria-label="Net boot">
                  <button type="button" class="tx-seg" :class="{ 'is-active': form.netboot === 'true' }" data-v="true" @click="form.netboot = 'true'">YES</button>
                  <button type="button" class="tx-seg" :class="{ 'is-active': form.netboot === 'false' }" data-v="false" @click="form.netboot = 'false'">NO</button>
                  <button type="button" class="tx-seg" :class="{ 'is-active': form.netboot === '' }" data-v="" @click="form.netboot = ''">DEFAULT (YES)</button>
                </div>
              </div>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="tx-field tx-field-match">
            <span class="tx-label">Roles:</span>
            <input type="text" v-model="form.roles" maxlength="100" />
          </div>
          <div class="tx-field tx-tri-field tx-field-match">
            <span class="tx-label">Net Boot:</span>
            <div class="tx-tri-inner">
              <div class="tx-segmented" role="group" aria-label="Net boot">
                <button type="button" class="tx-seg" :class="{ 'is-active': form.netboot === 'true' }" data-v="true" @click="form.netboot = 'true'">YES</button>
                <button type="button" class="tx-seg" :class="{ 'is-active': form.netboot === 'false' }" data-v="false" @click="form.netboot = 'false'" >NO</button>
                <button type="button" class="tx-seg" :class="{ 'is-active': form.netboot === '' }" data-v="" @click="form.netboot = ''">DEFAULT (YES)</button>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- Column 2 -->
      <div class="tx-add-col">
        <div class="tx-field tx-field-strong">
          <span class="tx-label">OS Image:</span>
          <select v-model="form.osimage" :class="{ 'tx-select-placeholder': !form.osimage }">
            <option value="">--- Select ---</option>
            <option v-for="o in osimageOptions" :key="o" :value="o">{{ o }}</option>
          </select>
        </div>
        <div class="tx-field tx-field-match">
          <span class="tx-label">Scripts:</span>
          <input type="text" v-model="form.scripts" maxlength="100" />
        </div>
      </div>

      <!-- Column 3 -->
      <div class="tx-add-col">
        <div class="tx-field tx-tri-field tx-field-match">
          <span class="tx-label">Setup BMC:</span>
          <div class="tx-tri-inner">
            <div class="tx-segmented" role="group" aria-label="BMC setup">
              <button type="button" class="tx-seg" :class="{ 'is-active': form.setupbmc === 'true' }" data-v="true" @click="form.setupbmc = 'true'">TRUE</button>
              <button type="button" class="tx-seg" :class="{ 'is-active': form.setupbmc === 'false' }" data-v="false" @click="form.setupbmc = 'false'">FALSE</button>
              <button type="button" class="tx-seg" :class="{ 'is-active': form.setupbmc === '' }" data-v="" @click="form.setupbmc = ''">DEFAULT (TRUE)</button>
            </div>
          </div>
        </div>
        <div class="tx-field tx-field-match">
          <span class="tx-label">BMC Setup:</span>
          <select v-model="form.bmcsetupname" :class="{ 'tx-select-placeholder': !form.bmcsetupname }">
            <option value="">--- Select ---</option>
            <option v-for="b in bmcsetupOptions" :key="b" :value="b">{{ b }}</option>
          </select>
        </div>
        <button type="button" class="tx-btn tx-btn-orange tx-btn-block-col" @click="toggleInterfaces">{{ showInterfaces ? '- Interfaces' : '+ Interfaces' }}</button>
      </div>
    </div>

    <!-- Interface Section -->
    <div v-if="showInterfaces" class="tx-interface-section">
      <InterfaceRow
        v-for="(iface, idx) in form.interfaces"
        :key="idx"
        :iface="iface"
        :row-key="idx"
        :networks="networkOptions"
        :bond-modes="bondModeOptions"
        @remove="removeInterface(idx)"
        @add-after="addInterfaceAfter(idx)"
        @open-options-editor="openIfaceOptionsEditor(idx)"
        @update-dhcp="
          (v: string) => {
            const iface = form.interfaces[idx]
            if (!iface) return
            iface.dhcp = v
          }
        "
      />
      <div v-if="!form.interfaces.length" class="tx-interface-empty">
        <button type="button" class="tx-btn tx-btn-orange" @click="addInterfaceAfter(-1)">+ Add Interface</button>
      </div>
    </div>

    <!-- Advanced Section -->
    <div v-if="showAdvanced" class="tx-advanced-body">
      <div class="tx-adv-grid">
        <!-- Domain -->
        <div class="tx-field tx-field-adv-sys" style="width: 100%">
          <span class="tx-label">Domain:</span>
          <input type="text" v-model="form.domain" maxlength="100" style="flex: 1" />
        </div>
        <!-- Unmanaged BMC Users -->
        <div class="tx-field tx-field-adv-sys" style="width: 100%">
          <span class="tx-label">Unmanaged BMC Users:</span>
          <select v-model="form.unmanaged_bmc_users" style="flex: 1" :class="{ 'tx-select-placeholder': !form.unmanaged_bmc_users }">
            <option value="">--- Select ---</option>
            <option value="1">1</option>
            <option value="2">2</option>
            <option value="3">3</option>
          </select>
        </div>

        <!-- Kernel Options | OS IMAGE -->
        <div class="tx-field-block">
          <div class="tx-label-row">
            <span class="tx-adv-heading">
              <span class="tx-label-title-blue">KERNEL OPTIONS</span>
              <span class="tx-label-title-sep"> | </span>
              <span class="tx-label-title-black">OS IMAGE</span>
            </span>
            <label class="tx-upload-pill">
              <input type="file" accept=".txt,.text,.sh,.cfg,.conf,.yaml,.yml,.json,.xml,.md,.csv,.ini,.env,.log,text/plain" @change="onUploadFile($event, 'kerneloptions')" />
              <span>Upload</span>
            </label>
          </div>
          <div class="tx-field-block-body">
            <textarea v-model="form.kerneloptions" rows="3"></textarea>
            <button type="button" class="tx-expand-text-trigger" @click="openTextEditor('Kernel Options | OS Image', 'kerneloptions')"></button>
          </div>
        </div>

        <!-- Pre Script | DEFAULT -->
        <div class="tx-field-block">
          <div class="tx-label-row">
            <span class="tx-adv-heading">
              <span class="tx-label-title-blue">PRE SCRIPT</span>
              <span class="tx-label-title-sep"> | </span>
              <span class="tx-label-title-black">DEFAULT</span>
            </span>
            <label class="tx-upload-pill">
              <input type="file" accept=".txt,.text,.sh,.cfg,.conf,.yaml,.yml,.json,.xml,.md,.csv,.ini,.env,.log,text/plain" @change="onUploadFile($event, 'prescript')" />
              <span>Upload</span>
            </label>
          </div>
          <div class="tx-field-block-body">
            <textarea v-model="form.prescript" rows="3"></textarea>
            <button type="button" class="tx-expand-text-trigger" @click="openTextEditor('Pre Script | Default', 'prescript')"></button>
          </div>
        </div>

        <!-- Part Script | GROUP -->
        <div class="tx-field-block">
          <div class="tx-label-row">
            <span class="tx-adv-heading">
              <span class="tx-label-title-blue">PART SCRIPT</span>
              <span class="tx-label-title-sep"> | </span>
              <span class="tx-label-title-black">GROUP</span>
            </span>
            <label class="tx-upload-pill">
              <input type="file" accept=".txt,.text,.sh,.cfg,.conf,.yaml,.yml,.json,.xml,.md,.csv,.ini,.env,.log,text/plain" @change="onUploadFile($event, 'partscript')" />
              <span>Upload</span>
            </label>
          </div>
          <div class="tx-field-block-body">
            <textarea v-model="form.partscript" rows="3"></textarea>
            <button type="button" class="tx-expand-text-trigger" @click="openTextEditor('Part Script | Group', 'partscript')"></button>
          </div>
        </div>

        <!-- Post Script | GROUP -->
        <div class="tx-field-block">
          <div class="tx-label-row">
            <span class="tx-adv-heading">
              <span class="tx-label-title-blue">POST SCRIPT</span>
              <span class="tx-label-title-sep"> | </span>
              <span class="tx-label-title-black">GROUP</span>
            </span>
            <label class="tx-upload-pill">
              <input type="file" accept=".txt,.text,.sh,.cfg,.conf,.yaml,.yml,.json,.xml,.md,.csv,.ini,.env,.log,text/plain" @change="onUploadFile($event, 'postscript')" />
              <span>Upload</span>
            </label>
          </div>
          <div class="tx-field-block-body">
            <textarea v-model="form.postscript" rows="3"></textarea>
            <button type="button" class="tx-expand-text-trigger" @click="openTextEditor('Post Script | Group', 'postscript')"></button>
          </div>
        </div>

        <!-- OS Image Tag -->
        <div class="tx-field" style="width: 100%">
          <span class="tx-label">OS Image Tag:</span>
          <input type="text" v-model="form.osimagetag" maxlength="100" style="flex: 1" />
          <span v-if="hints.osimagetag" class="tx-hint">{{ hints.osimagetag }}</span>
        </div>
        <!-- Provision Interface -->
        <div class="tx-field" style="width: 100%">
          <span class="tx-label">Provision Interface:</span>
          <input type="text" v-model="form.provision_interface" maxlength="100" style="flex: 1" />
          <span v-if="hints.provision_interface" class="tx-hint">{{ hints.provision_interface }}</span>
        </div>

        <!-- Provision Fallback -->
        <div class="tx-field" style="width: 100%">
          <span class="tx-label">Provision Fallback:</span>
          <input type="text" v-model="form.provision_fallback" maxlength="100" style="flex: 1" />
          <span v-if="hints.provision_fallback" class="tx-hint">{{  hints.provision_fallback }}</span>
        </div>
        <!-- Provision Method -->
        <div class="tx-field" style="width: 100%">
          <span class="tx-label">Provision Method:</span>
          <input type="text" v-model="form.provision_method" maxlength="100" style="flex: 1" />
          <span v-if="hints.provision_method" class="tx-hint">{{ hints.provision_method }}</span>
        </div>

        <!-- Comment (full width) -->
        <div class="tx-field-block tx-adv-full">
          <div class="tx-label-row">
            <span class="tx-label">Comment:</span>
            <label class="tx-upload-pill">
              <input type="file" accept=".txt,.text,.sh,.cfg,.conf,.yaml,.yml,.json,.xml,.md,.csv,.ini,.env,.log,text/plain" @change="onUploadFile($event, 'comment')" />
              <span>Upload</span>
            </label>
          </div>
          <div class="tx-field-block-body">
            <textarea v-model="form.comment" rows="3"></textarea>
            <button type="button" class="tx-expand-text-trigger" @click="openTextEditor('Comment', 'comment')"></button>
          </div>
        </div>
      </div>
    </div>

    <!-- Single footer: Advanced + submit always at bottom of form -->
    <div class="tx-form-footer">
      <button type="button" class="tx-btn tx-btn-outline-blue" @click="showAdvanced = !showAdvanced">Advanced {{ showAdvanced ? '\u25B4' : '\u25BE' }}</button>
      <button
        type="submit"
        :disabled="isSubmitDisabled || submitting"
        class="tx-btn tx-btn-blue"
        :class="{ 'tx-btn-disabled': isSubmitDisabled || submitting }"
      >
        {{ submitLabel }}
      </button>
    </div>

    <!-- Text Editor Modal -->
    <TextEditorModal
      v-if="textEditorOpen"
      :key="textEditorModalKey"
      :title="textEditorTitle"
      :model-value="textEditorModalValue"
      @update:model-value="onTextEditorModalApply"
      @close="closeTextEditor"
    />
  </form>
</template>
