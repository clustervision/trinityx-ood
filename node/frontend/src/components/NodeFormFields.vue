<template>
  <form @submit.prevent="$emit('submit')" class="tx-group-form tx-group-form-fixed">
    <div class="tx-add-grid tx-add-form-main tx-node-add-main">
      <div v-if="mode === 'clone'" class="tx-field tx-field-strong">
        <span class="tx-label">Clone Name:</span>
        <input
          v-model="form.newnodename"
          type="text"
          :placeholder="form.name || ''"
          @keypress="noSpaces"
          @blur="onCloneNameBlur"
          maxlength="100"
          required
        />
      </div>
      <div v-else class="tx-field tx-field-strong tx-field-name-with-rename">
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
              maxlength="100"
              required
              aria-label="Node name"
              @keypress="noSpaces"
              @blur="onNameDraftBlur"
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
        <input
          v-else
          type="text"
          v-model="form.name"
          @keypress="noSpaces"
          @blur="onAddNameBlur"
          maxlength="100"
          required
        />
      </div>
      <div class="tx-field tx-field-strong">
        <span class="tx-label">Group:</span>
        <select v-model="form.groupname" :class="{ 'tx-select-placeholder': !form.groupname }">
          <option value="">--- Select ---</option>
          <option v-for="g in groupOptions" :key="g" :value="g">{{ g }}</option>
        </select>
      </div>
      <div class="tx-field tx-field-strong">
        <span class="tx-label">OS Image:</span>
        <select v-model="form.osimage" :class="{ 'tx-select-placeholder': !form.osimage }">
          <option value="">--- Select ---</option>
          <option v-for="o in osimageOptions" :key="o" :value="o">{{ o }}</option>
        </select>
      </div>

      <div class="tx-field tx-tri-field tx-field-match">
        <span class="tx-label">Net Boot:</span>
        <div class="tx-tri-inner">
          <div class="tx-segmented" role="group" aria-label="Net boot">
            <button type="button" class="tx-seg" :class="{ 'is-active': form.netboot === 'true' }" data-v="true" @click="form.netboot = 'true'">YES</button>
            <button type="button" class="tx-seg" :class="{ 'is-active': form.netboot === 'false' }" data-v="false" @click="form.netboot = 'false'">NO</button>
            <button type="button" class="tx-seg tx-seg-tri-inherit" :class="{ 'is-active': form.netboot === '' }" data-v="" @click="form.netboot = ''"> INHERITED (YES) </button>
          </div>
        </div>
      </div>
      <div class="tx-field tx-tri-field tx-field-match">
        <span class="tx-label">Setup BMC:</span>
        <div class="tx-tri-inner">
          <div class="tx-segmented" role="group" aria-label="BMC setup">
            <button type="button" class="tx-seg" :class="{ 'is-active': form.setupbmc === 'true' }" data-v="true" @click="form.setupbmc = 'true'">YES</button>
            <button type="button" class="tx-seg" :class="{ 'is-active': form.setupbmc === 'false' }" data-v="false" @click="form.setupbmc = 'false'">NO</button>
            <button type="button" class="tx-seg tx-seg-tri-inherit" :class="{ 'is-active': form.setupbmc === '' }" data-v="" @click="form.setupbmc = ''"> INHERITED (YES) </button>
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

      <div class="tx-field tx-field-match">
        <span class="tx-label">Switch:</span>
        <select v-model="form.switchname" :class="{ 'tx-select-placeholder': !form.switchname }">
          <option value="">--- Select ---</option>
          <option v-for="s in switchOptions" :key="s" :value="s">{{ s }}</option>
        </select>
      </div>
      <div class="tx-field tx-field-match">
        <span class="tx-label">Switch Port:</span>
        <input type="text" v-model="form.switchport" maxlength="100" />
      </div>
      <div class="tx-field tx-field-match">
        <span class="tx-label">Vendor:</span>
        <input type="text" v-model="form.vendor" maxlength="100" />
      </div>

      <div class="tx-field tx-field-match">
        <span class="tx-label">Scripts:</span>
        <input type="text" v-model="form.scripts" maxlength="100" />
      </div>
      <div class="tx-field tx-field-match">
        <span class="tx-label">Roles:</span>
        <input type="text" v-model="form.roles" maxlength="100" />
      </div>
      <div class="tx-node-iface-btn-wrap">
        <button type="button" class="tx-btn tx-btn-orange tx-btn-block-col" @click="toggleInterfaces">
          {{ showInterfaces ? '- Interfaces' : '+ Interfaces' }}
        </button>
      </div>
    </div>

    <div v-if="showInterfaces" class="tx-interface-section">
      <InterfaceRow
        v-for="(iface, idx) in form.interfaces"
        :key="idx"
        :iface="iface"
        :row-key="idx"
        :all-ifaces="form.interfaces"
        :networks="networkOptions"
        :bond-modes="bondModeOptions"
        :get-inventory-ipv4="getInventoryIpv4"
        :inventory-exclude-node-name="inventoryExcludeNodeName"
        @remove="removeInterface(idx)"
        @add-after="addInterfaceAfter(idx)"
        @open-options-editor="openIfaceOptionsEditor(idx)"
        @update-dhcp="(v) => setIfaceDhcp(idx, v)"
      />
      <div v-if="!form.interfaces.length" class="tx-interface-empty">
        <button type="button" class="tx-btn tx-btn-orange" @click="addInterfaceAfter(-1)">+ Add Interface</button>
      </div>
    </div>

    <div v-if="showAdvanced" class="tx-advanced-body">
      <div class="tx-adv-grid">
        <div class="tx-field tx-field-adv-sys" style="width:100%">
          <span class="tx-label">Domain:</span>
          <input type="text" v-model="form.domain" maxlength="100" style="flex:1" />
        </div>
        <div class="tx-field tx-field-adv-sys" style="width:100%">
          <span class="tx-label">Unmanaged BMC Users:</span>
          <select
            v-model="form.unmanaged_bmc_users"
            style="flex:1"
            :class="{ 'tx-select-placeholder': !form.unmanaged_bmc_users }"
          >
            <option value="">--- Select ---</option>
            <option value="1">1</option>
            <option value="2">2</option>
            <option value="3">3</option>
          </select>
        </div>

        <div class="tx-field tx-field-adv-sys" style="width:100%">
          <span class="tx-label">Asset Tag:</span>
          <input type="text" v-model="form.asset_tag" maxlength="200" style="flex:1" />
        </div>
        <div class="tx-field tx-field-adv-sys" style="width:100%">
          <span class="tx-label">Cloud Name:</span>
          <select
            v-model="form.cloud_name"
            style="flex:1"
            :class="{ 'tx-select-placeholder': !form.cloud_name }"
          >
            <option value="">--- Select ---</option>
            <option v-for="c in cloudnameOptions" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>

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

        <div class="tx-field" style="width:100%">
          <span class="tx-label">OS Image Tag:</span>
          <input type="text" v-model="form.osimagetag" maxlength="100" style="flex:1" />
          <span v-if="hints.osimagetag" class="tx-hint">{{ hints.osimagetag }}</span>
        </div>
        <div class="tx-field" style="width:100%">
          <span class="tx-label">Provision Interface:</span>
          <input type="text" v-model="form.provision_interface" maxlength="100" style="flex:1" />
          <span v-if="hints.provision_interface" class="tx-hint">{{ hints.provision_interface }}</span>
        </div>

        <div class="tx-field" style="width:100%">
          <span class="tx-label">Provision Fallback:</span>
          <input type="text" v-model="form.provision_fallback" maxlength="100" style="flex:1" />
          <span v-if="hints.provision_fallback" class="tx-hint">{{ hints.provision_fallback }}</span>
        </div>
        <div class="tx-field" style="width:100%">
          <span class="tx-label">Provision Method:</span>
          <input type="text" v-model="form.provision_method" maxlength="100" style="flex:1" />
          <span v-if="hints.provision_method" class="tx-hint">{{ hints.provision_method }}</span>
        </div>

        <div class="tx-field" style="width:100%">
          <span class="tx-label">TPM UUID:</span>
          <input type="text" v-model="form.tpm_uuid" maxlength="500" style="flex:1" />
        </div>
        <div class="tx-field" style="width:100%">
          <span class="tx-label">TPM Pubkey:</span>
          <input type="text" v-model="form.tpm_pubkey" maxlength="2000" style="flex:1" />
        </div>
        <div class="tx-field" style="width:100%">
          <span class="tx-label">TPM SHA256:</span>
          <input type="text" v-model="form.tpm_sha256" maxlength="200" style="flex:1" />
        </div>
        <div class="tx-adv-svc-merged" style="width:100%">
          <label class="tx-adv-svc-merged-inner">
            <span class="tx-adv-svc-text">Service:</span>
            <input v-model="form.service" type="checkbox" class="tx-adv-svc-input" />
          </label>
        </div>

        <div class="tx-field-block tx-adv-full">
          <div class="tx-label-row">
            <span class="tx-label">Comment:</span>
          </div>
          <div class="tx-field-block-body">
            <textarea v-model="form.comment" rows="3"></textarea>
            <button type="button" class="tx-expand-text-trigger" @click="openTextEditor('Comment', 'comment')"></button>
          </div>
        </div>
      </div>
    </div>

    <div class="tx-form-footer">
      <button
        type="button"
        class="tx-btn tx-btn-outline-blue tx-btn-advanced-toggle"
        :aria-expanded="showAdvanced"
        @click="showAdvanced = !showAdvanced"
      >
        <span>Advanced</span>
        <span
          class="tx-advanced-chevron"
          :class="{ 'is-open': showAdvanced }"
          aria-hidden="true"
        />
      </button>
      <button type="submit" class="tx-btn tx-btn-blue">{{ submitLabel }}</button>
    </div>

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

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import InterfaceRow from './InterfaceRow.vue'
import TextEditorModal from './TextEditorModal.vue'
import { punAppAssetUrl } from '../utils/publicAssets'

const renameIcon = punAppAssetUrl('icon-rename.png')
import type { NodeFormInterface, NodeFormData, InventoryIpv4Record } from '@/types'

const props = withDefaults(defineProps<{
  mode?: 'add' | 'edit' | 'clone'
  initialData?: Record<string, unknown>
  groupOptions?: string[]
  switchOptions?: string[]
  bmcsetupOptions?: string[]
  osimageOptions?: string[]
  networkOptions?: string[]
  bondModeOptions?: string[]
  cloudnameOptions?: string[]
  submitLabel?: string
  hints?: Record<string, string>
  getInventoryIpv4?: (() => InventoryIpv4Record[]) | null
  inventoryExcludeNodeName?: string
}>(), {
  mode: 'add',
  initialData: () => ({}),
  groupOptions: () => [],
  switchOptions: () => [],
  bmcsetupOptions: () => [],
  osimageOptions: () => [],
  networkOptions: () => [],
  bondModeOptions: () => [],
  cloudnameOptions: () => [],
  submitLabel: 'Add Node',
  hints: () => ({}),
  getInventoryIpv4: null,
  inventoryExcludeNodeName: '',
})

const emit = defineEmits<{
  submit: []
}>()

const showInterfaces = ref(false)
const showAdvanced = ref(false)
const originalNodeName = ref('')
const nameInlineEdit = ref(false)
const nameDraft = ref('')
const textEditorOpen = ref(false)
const textEditorTitle = ref('')
const textEditorField = ref('')
const ifaceOptionsIdx = ref(-1)

const textEditorModalKey = computed(
  () => `${ifaceOptionsIdx.value}:${textEditorField.value}`,
)

const textEditorModalValue = computed((): string => {
  if (ifaceOptionsIdx.value >= 0) {
    return form.interfaces[ifaceOptionsIdx.value]?.options ?? ''
  }
  const f = textEditorField.value
  return f && (form as Record<string, unknown>)[f] != null ? String((form as Record<string, unknown>)[f]) : ''
})

function makeEmptyIface(): NodeFormInterface {
  return {
    interface: '',
    network: '',
    ipaddress: '',
    mtu: '',
    dhcp: 'false',
    bond_mode: '',
    bond_slaves: '',
    vlanid: '',
    options: '',
    vlan_parent: '',
    macaddress: '',
  }
}

const form: NodeFormData = reactive({
  name: '',
  newnodename: '',
  groupname: '',
  osimage: '',
  netboot: '',
  setupbmc: '',
  bmcsetupname: '',
  switchname: '',
  switchport: '',
  vendor: '',
  scripts: '',
  roles: '',
  domain: '',
  unmanaged_bmc_users: '',
  asset_tag: '',
  cloud_name: '',
  kerneloptions: '',
  prescript: '',
  partscript: '',
  postscript: '',
  osimagetag: '',
  provision_interface: '',
  provision_fallback: '',
  provision_method: '',
  tpm_uuid: '',
  tpm_pubkey: '',
  tpm_sha256: '',
  service: false,
  comment: '',
  interfaces: [],
})

function triValue(v: unknown): string {
  if (v === true || v === 'True' || v === 'true') return 'true'
  if (v === false || v === 'False' || v === 'false') return 'false'
  return ''
}

function ifaceDhcpString(v: unknown): string {
  if (v === true || v === 1 || v === '1') return 'true'
  if (v === false || v === 0 || v === '0') return 'false'
  const s = String(v ?? '').trim().toLowerCase()
  if (s === 'true' || s === 'yes' || s === 'on') return 'true'
  return 'false'
}

function hydrateForm(d: Record<string, unknown> | null) {
  if (!d) return
  form.name = String(d.name || '')
  form.newnodename =
    d.newnodename != null && d.newnodename !== ''
      ? String(d.newnodename)
      : (d.newname != null ? String(d.newname) : '')
  form.groupname = d.groupname != null && d.groupname !== '' ? String(d.groupname) : (d.group != null ? String(d.group) : '')
  form.osimage = String(d.osimage || '')
  form.netboot = triValue(d.netboot)
  form.setupbmc = triValue(d.setupbmc)
  form.bmcsetupname = d.bmcsetupname != null && d.bmcsetupname !== ''
    ? String(d.bmcsetupname)
    : (d.bmcsetup != null ? String(d.bmcsetup) : '')
  form.switchname = d.switchname != null && d.switchname !== ''
    ? String(d.switchname)
    : (d.switch != null ? String(d.switch) : '')
  form.switchport = d.switchport != null ? String(d.switchport) : ''
  form.vendor = d.vendor != null ? String(d.vendor) : ''
  form.scripts = d.scripts != null ? String(d.scripts) : ''
  form.roles = d.roles != null ? String(d.roles) : ''
  form.domain = d.domain != null ? String(d.domain) : ''
  form.unmanaged_bmc_users = d.unmanaged_bmc_users != null ? String(d.unmanaged_bmc_users) : ''
  form.asset_tag = d.asset_tag != null ? String(d.asset_tag) : ''
  form.cloud_name =
    d.cloud_name != null && d.cloud_name !== ''
      ? String(d.cloud_name)
      : (d.cloudname != null ? String(d.cloudname) : '')
  form.kerneloptions = d.kerneloptions != null ? String(d.kerneloptions) : ''
  form.prescript = d.prescript != null ? String(d.prescript) : ''
  form.partscript = d.partscript != null ? String(d.partscript) : ''
  form.postscript = d.postscript != null ? String(d.postscript) : ''
  const otag = d.osimagetag != null && d.osimagetag !== 'default' ? String(d.osimagetag) : ''
  form.osimagetag = otag
  form.provision_interface = d.provision_interface != null ? String(d.provision_interface) : ''
  form.provision_fallback = d.provision_fallback != null ? String(d.provision_fallback) : ''
  form.provision_method = d.provision_method != null ? String(d.provision_method) : ''
  form.tpm_uuid = d.tpm_uuid != null ? String(d.tpm_uuid) : ''
  form.tpm_pubkey = d.tpm_pubkey != null ? String(d.tpm_pubkey) : ''
  form.tpm_sha256 = d.tpm_sha256 != null ? String(d.tpm_sha256) : ''
  {
    const s = d.service
    form.service = s === true || s === 'true' || s === 1 || s === '1' || s === 'on'
  }
  form.comment = d.comment != null ? String(d.comment) : ''
  const rawIfaces = d.interfaces as Record<string, unknown>[] | undefined
  if (Array.isArray(rawIfaces) && rawIfaces.length) {
    form.interfaces = rawIfaces.map((row): NodeFormInterface => ({
      interface: (row.interface as string) || '',
      network: (row.network as string) || '',
      ipaddress: row.ipaddress != null ? String(row.ipaddress) : '',
      mtu: (row.mtu as string | number) || '',
      dhcp: ifaceDhcpString(row.dhcp),
      bond_mode: (row.bond_mode as string) || '',
      bond_slaves: (row.bond_slaves as string) || '',
      vlanid: (row.vlanid as string | number) || '',
      options: (row.options as string) || '',
      vlan_parent: (row.vlan_parent as string) || '',
      macaddress: row.macaddress != null ? String(row.macaddress) : '',
    }))
  } else {
    form.interfaces = []
  }
  if (props.mode === 'edit') {
    const n = form.name || ''
    originalNodeName.value = n
    nameDraft.value = n
    nameInlineEdit.value = false
  }
}

watch(() => props.initialData, (d: Record<string, unknown>) => hydrateForm(d), { immediate: true, deep: true })

function toggleInterfaces() {
  showInterfaces.value = !showInterfaces.value
  if (showInterfaces.value && form.interfaces.length === 0) {
    form.interfaces.push(makeEmptyIface())
  }
}

function addInterfaceAfter(idx: number) {
  form.interfaces.splice(idx + 1, 0, makeEmptyIface())
}

function removeInterface(idx: number) {
  form.interfaces.splice(idx, 1)
}

function setIfaceDhcp(idx: number, v: string) {
  const row = form.interfaces[idx]
  if (row) row.dhcp = v
}

function noSpaces(e: KeyboardEvent) {
  if (e.charCode === 32) e.preventDefault()
}

function normalizeLunaNodeName(s: unknown): string {
  return String(s ?? '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9.-]/g, '')
}

function onNameDraftBlur() {
  nameDraft.value = normalizeLunaNodeName(nameDraft.value)
}

function onAddNameBlur() {
  form.name = normalizeLunaNodeName(form.name)
}

function onCloneNameBlur() {
  form.newnodename = normalizeLunaNodeName(form.newnodename)
}

function startInlineRename() {
  if (props.mode !== 'edit') return
  nameInlineEdit.value = true
  nameDraft.value = form.name || originalNodeName.value
}

function cancelInlineRename() {
  nameInlineEdit.value = false
  nameDraft.value = form.name || originalNodeName.value
}

function getPendingRename(): { oldName: string; newName: string } | null {
  if (props.mode !== 'edit' || !nameInlineEdit.value) return null
  const oRaw = (originalNodeName.value || '').trim()
  const n = normalizeLunaNodeName(nameDraft.value)
  if (!n) return null
  if (n === normalizeLunaNodeName(oRaw)) return null
  return { oldName: oRaw, newName: n }
}

function applyRenamedInForm(newName: string) {
  const s = (newName || '').trim()
  if (!s) return
  form.name = s
  originalNodeName.value = s
  nameDraft.value = s
  nameInlineEdit.value = false
}

function openTextEditor(title: string, field: string) {
  ifaceOptionsIdx.value = -1
  textEditorTitle.value = title
  textEditorField.value = field
  textEditorOpen.value = true
}

function openIfaceOptionsEditor(idx: number) {
  textEditorField.value = ''
  textEditorTitle.value = 'Options'
  ifaceOptionsIdx.value = idx
  textEditorOpen.value = true
}

function closeTextEditor() {
  textEditorOpen.value = false
  ifaceOptionsIdx.value = -1
}

function onTextEditorModalApply(v: string | null) {
  const ifaceIdx = ifaceOptionsIdx.value
  if (ifaceIdx >= 0) {
    const ifaceRow = form.interfaces[ifaceIdx]
    if (ifaceRow) ifaceRow.options = v != null ? String(v) : ''
  } else if (textEditorField.value) {
    ;(form as Record<string, unknown>)[textEditorField.value] = v
  }
}

function looksLikeBinary(buf: ArrayBuffer | null): boolean {
  if (!buf || !buf.byteLength) return false
  const view = new Uint8Array(buf)
  const n = Math.min(view.length, 65536)
  for (let i = 0; i < n; i++) {
    if (view[i] === 0) return true
  }
  return false
}

function onUploadFile(e: Event, field: string) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  const fr = new FileReader()
  fr.onload = () => {
    if (looksLikeBinary(fr.result as ArrayBuffer)) {
      alert('Please choose a text file only.')
      input.value = ''
      return
    }
    ;(form as Record<string, unknown>)[field] = new TextDecoder('utf-8', { fatal: false }).decode(new Uint8Array(fr.result as ArrayBuffer))
    input.value = ''
  }
  fr.onerror = () => {
    alert('Could not read the file.')
    input.value = ''
  }
  fr.readAsArrayBuffer(file)
}

/**
 * UI state field names on `form` -> Luna node config column names (Flask + daemon; see sortby in constant.py).
 * Mismatched names cause "400 - Columns are incorrect" from the daemon.
 */
const SCALAR_TO_POST_KEY: Record<string, string> = {
  groupname: 'group',
  bmcsetupname: 'bmcsetup',
  switchname: 'switch',
  asset_tag: 'assettag',
  cloud_name: 'cloud',
}

/**
 * Luna node columns (trinityx OOD sortby + rename). Omit keys not listed — e.g. `domain`
 * is group-level in API docs and triggers 400 "Columns are incorrect" on node POST.
 */
const LUNA_NODE_SCALAR_KEYS = new Set([
  'name',
  'hostname',
  'group',
  'osimage',
  'osimagetag',
  'kerneloptions',
  'vendor',
  'assettag',
  'position',
  'switch',
  'switchport',
  'cloud',
  'setupbmc',
  'bmcsetup',
  'unmanaged_bmc_users',
  'netboot',
  'bootmenu',
  'service',
  'roles',
  'scripts',
  'prescript_source',
  'prescript',
  'partscript_source',
  'partscript',
  'postscript_source',
  'postscript',
  'provision_interface',
  'provision_method',
  'provision_fallback',
  'tpm_uuid',
  'tpm_pubkey',
  'tpm_sha256',
  'comment',
  'macaddress',
  'newnodename',
])

/** JSON body for /api/v1/* (interfaces as array — not flattened like FormData). */
function buildLunaNodeRecord(): Record<string, unknown> {
  const record: Record<string, unknown> = {}
  const baseScalars: string[] = [
    'name', 'groupname', 'roles', 'netboot', 'osimage', 'scripts', 'setupbmc', 'bmcsetupname',
    'switchname', 'switchport', 'vendor',
    'unmanaged_bmc_users', 'asset_tag', 'cloud_name', 'kerneloptions', 'prescript', 'partscript',
    'postscript', 'osimagetag', 'provision_interface', 'provision_fallback',
    'provision_method', 'tpm_uuid', 'tpm_pubkey', 'tpm_sha256', 'comment',
  ]
  const isClone = props.mode === 'clone'
  const scalarFields = isClone ? [...baseScalars, 'newnodename'] : baseScalars
  for (const f of scalarFields) {
    const v = (form as Record<string, unknown>)[f]
    if (v == null) continue
    let out: string | boolean = String(v)
    if (typeof v === 'string') {
      if (f === 'newnodename' && isClone) {
        out = normalizeLunaNodeName(v)
      } else if (f === 'name' && props.mode === 'add') {
        out = normalizeLunaNodeName(v)
      }
      if (isClone && typeof out === 'string' && out.trim() === '') continue
    }
    const postKey = SCALAR_TO_POST_KEY[f as keyof typeof SCALAR_TO_POST_KEY] || f
    if (!LUNA_NODE_SCALAR_KEYS.has(postKey)) continue
    record[postKey] = out
  }
  if (!isClone && form.service) record.service = true
  record.interfaces = form.interfaces.map((iface) => {
    const row: Record<string, unknown> = {}
    for (const [k, val] of Object.entries(iface)) {
      row[k] = val != null ? String(val) : ''
    }
    return row
  })
  return record
}

function buildFormData(): FormData {
  const fd = new FormData()
  const baseScalars: string[] = [
    'name', 'groupname', 'roles', 'netboot', 'osimage', 'scripts', 'setupbmc', 'bmcsetupname',
    'switchname', 'switchport', 'vendor',
    'unmanaged_bmc_users', 'asset_tag', 'cloud_name', 'kerneloptions', 'prescript', 'partscript',
    'postscript', 'osimagetag', 'provision_interface', 'provision_fallback',
    'provision_method', 'tpm_uuid', 'tpm_pubkey', 'tpm_sha256', 'comment',
  ]
  const isClone = props.mode === 'clone'
  const scalarFields = isClone ? [...baseScalars, 'newnodename'] : baseScalars
  for (const f of scalarFields) {
    const v = (form as Record<string, unknown>)[f]
    if (v == null) continue
    let out = String(v)
    if (typeof v === 'string') {
      if (f === 'newnodename' && isClone) {
        out = normalizeLunaNodeName(v)
      } else if (f === 'name' && props.mode === 'add') {
        out = normalizeLunaNodeName(v)
      }
      if (isClone && out.trim() === '') continue
    }
    const postKey = SCALAR_TO_POST_KEY[f as keyof typeof SCALAR_TO_POST_KEY] || f
    if (!LUNA_NODE_SCALAR_KEYS.has(postKey)) continue
    fd.append(postKey, out)
  }
  if (!isClone && form.service) fd.append('service', 'true')
  for (const iface of form.interfaces) {
    for (const [k, val] of Object.entries(iface)) {
      fd.append(k, val != null ? String(val) : '')
    }
  }
  return fd
}

defineExpose({ form, buildFormData, buildLunaNodeRecord, getPendingRename, applyRenamedInForm })
</script>
