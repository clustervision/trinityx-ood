<template>
  <form @submit.prevent="$emit('submit')" class="tx-group-form tx-group-form-fixed">
    <!-- 3-column top grid -->
    <div class="tx-add-grid tx-add-form-main">
      <!-- Column 1 -->
      <div class="tx-add-col">
        <div class="tx-field tx-field-strong" v-if="mode === 'clone'">
          <span class="tx-label">Clone Name:</span>
          <input type="text" :value="form.name" readonly />
        </div>
        <div class="tx-field tx-field-strong">
          <span class="tx-label">{{ mode === 'clone' ? 'New Group Name:' : 'Name:' }}</span>
          <input
            v-if="mode === 'edit'"
            type="text"
            :value="form.name"
            readonly
          />
          <input
            v-else-if="mode === 'clone'"
            type="text"
            v-model="form.newgroupname"
            @keypress="noSpaces"
            maxlength="100"
            required
          />
          <input
            v-else
            type="text"
            v-model="form.name"
            @keypress="noSpaces"
            maxlength="100"
            required
          />
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
                <button type="button" class="tx-seg" :class="{ 'is-active': form.netboot === 'false' }" data-v="false" @click="form.netboot = 'false'">NO</button>
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
              <button type="button" class="tx-seg" :class="{ 'is-active': form.setupbmc === 'true' }" data-v="true" @click="form.setupbmc = 'true'">YES</button>
              <button type="button" class="tx-seg" :class="{ 'is-active': form.setupbmc === 'false' }" data-v="false" @click="form.setupbmc = 'false'">NO</button>
              <button type="button" class="tx-seg" :class="{ 'is-active': form.setupbmc === '' }" data-v="" @click="form.setupbmc = ''">DEFAULT (YES)</button>
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
        <button type="button" class="tx-btn tx-btn-orange tx-btn-block-col" @click="toggleInterfaces">
          {{ showInterfaces ? '- Interfaces' : '+ Interfaces' }}
        </button>
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
        @update-dhcp="setInterfaceDhcp(idx, $event)"
      />
      <div v-if="!form.interfaces.length" class="tx-interface-empty">
        <button type="button" class="tx-btn tx-btn-orange" @click="addInterfaceAfter(-1)">+ Add Interface</button>
      </div>
    </div>

    <!-- Footer row: Advanced + Submit -->
    <div class="tx-form-footer">
      <button type="button" class="tx-btn tx-btn-outline-blue" @click="showAdvanced = !showAdvanced">
        Advanced {{ showAdvanced ? '\u25B4' : '\u25BE' }}
      </button>
      <button type="submit" class="tx-btn tx-btn-blue">{{ submitLabel }}</button>
    </div>

    <!-- Advanced Section -->
    <div v-if="showAdvanced" class="tx-advanced-body">
      <div class="tx-adv-grid">
        <!-- Domain -->
        <div class="tx-field tx-field-adv-sys" style="width:100%">
          <span class="tx-label">Domain:</span>
          <input type="text" v-model="form.domain" maxlength="100" style="flex:1" />
        </div>
        <!-- Unmanaged BMC Users -->
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
        <div class="tx-field" style="width:100%">
          <span class="tx-label">OS Image Tag:</span>
          <input type="text" v-model="form.osimagetag" maxlength="100" style="flex:1" />
          <span v-if="hints.osimagetag" class="tx-hint">{{ hints.osimagetag }}</span>
        </div>
        <!-- Provision Interface -->
        <div class="tx-field" style="width:100%">
          <span class="tx-label">Provision Interface:</span>
          <input type="text" v-model="form.provision_interface" maxlength="100" style="flex:1" />
          <span v-if="hints.provision_interface" class="tx-hint">{{ hints.provision_interface }}</span>
        </div>

        <!-- Provision Fallback -->
        <div class="tx-field" style="width:100%">
          <span class="tx-label">Provision Fallback:</span>
          <input type="text" v-model="form.provision_fallback" maxlength="100" style="flex:1" />
          <span v-if="hints.provision_fallback" class="tx-hint">{{ hints.provision_fallback }}</span>
        </div>
        <!-- Provision Method -->
        <div class="tx-field" style="width:100%">
          <span class="tx-label">Provision Method:</span>
          <input type="text" v-model="form.provision_method" maxlength="100" style="flex:1" />
          <span v-if="hints.provision_method" class="tx-hint">{{ hints.provision_method }}</span>
        </div>

        <!-- Comment (full width) -->
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

      <!-- Second submit at bottom of advanced -->
      <div class="tx-form-footer">
        <span></span>
        <button type="submit" class="tx-btn tx-btn-blue">{{ submitLabel }}</button>
      </div>
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

<script setup>
import { ref, reactive, watch, computed } from 'vue'
import InterfaceRow from './InterfaceRow.vue'
import TextEditorModal from './TextEditorModal.vue'

const props = defineProps({
  mode: { type: String, default: 'add' },
  initialData: { type: Object, default: () => ({}) },
  bmcsetupOptions: { type: Array, default: () => [] },
  osimageOptions: { type: Array, default: () => [] },
  networkOptions: { type: Array, default: () => [] },
  bondModeOptions: { type: Array, default: () => [] },
  submitLabel: { type: String, default: 'Submit' },
  hints: { type: Object, default: () => ({}) },
})

defineEmits(['submit'])

const showInterfaces = ref(false)
const showAdvanced = ref(false)
const textEditorOpen = ref(false)
const textEditorTitle = ref('')
const textEditorField = ref('')
const ifaceOptionsIdx = ref(-1)

const textEditorModalKey = computed(
  () => `${ifaceOptionsIdx.value}:${textEditorField.value}`,
)

const textEditorModalValue = computed(() => {
  if (ifaceOptionsIdx.value >= 0) {
    return form.interfaces[ifaceOptionsIdx.value]?.options ?? ''
  }
  const f = textEditorField.value
  return f && form[f] != null ? String(form[f]) : ''
})

function triValue(v) {
  if (v === true || v === 'True' || v === 'true') return 'true'
  if (v === false || v === 'False' || v === 'false') return 'false'
  return ''
}

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
  osimagetag: '',
  provision_interface: '',
  provision_fallback: '',
  provision_method: '',
  comment: '',
  interfaces: [],
})

function hydrateForm(d) {
  if (!d) return
  form.name = d.name || ''
  form.newgroupname = d.newgroupname || ''
  form.roles = d.roles != null ? String(d.roles) : ''
  form.netboot = triValue(d.netboot)
  form.osimage = d.osimage || ''
  form.scripts = d.scripts != null ? String(d.scripts) : ''
  form.setupbmc = triValue(d.setupbmc)
  form.bmcsetupname = d.bmcsetupname || ''
  form.domain = d.domain != null ? String(d.domain) : ''
  form.unmanaged_bmc_users = d.unmanaged_bmc_users != null ? String(d.unmanaged_bmc_users) : ''
  form.kerneloptions = d.kerneloptions != null ? String(d.kerneloptions) : ''
  form.prescript = d.prescript != null ? String(d.prescript) : ''
  form.partscript = d.partscript != null ? String(d.partscript) : ''
  form.postscript = d.postscript != null ? String(d.postscript) : ''
  const otag = d.osimagetag != null && d.osimagetag !== 'default' ? d.osimagetag : ''
  form.osimagetag = otag
  form.provision_interface = d.provision_interface != null ? String(d.provision_interface) : ''
  form.provision_fallback = d.provision_fallback != null ? String(d.provision_fallback) : ''
  form.provision_method = d.provision_method != null ? String(d.provision_method) : ''
  form.comment = d.comment != null ? String(d.comment) : ''
  if (Array.isArray(d.interfaces) && d.interfaces.length) {
    form.interfaces = d.interfaces.map((row) => ({
      interface: row.interface || '',
      network: row.network || '',
      mtu: row.mtu || '',
      dhcp: (row.dhcp === true || row.dhcp === 'True') ? 'true' : 'false',
      bond_mode: row.bond_mode || '',
      bond_slaves: row.bond_slaves || '',
      vlanid: row.vlanid || '',
      options: row.options || '',
      vlan_parent: row.vlan_parent || '',
    }))
  } else {
    form.interfaces = []
  }
}

watch(() => props.initialData, (d) => hydrateForm(d), { immediate: true, deep: true })

function toggleInterfaces() {
  showInterfaces.value = !showInterfaces.value
  if (showInterfaces.value && form.interfaces.length === 0) {
    form.interfaces.push(makeEmptyIface())
  }
}

function addInterfaceAfter(idx) {
  form.interfaces.splice(idx + 1, 0, makeEmptyIface())
}

function removeInterface(idx) {
  form.interfaces.splice(idx, 1)
}

function setInterfaceDhcp(idx, value) {
  const row = form.interfaces[idx]
  if (!row) return
  row.dhcp = value
}

function noSpaces(e) {
  if (e.charCode === 32) e.preventDefault()
}

function openTextEditor(title, field) {
  ifaceOptionsIdx.value = -1
  textEditorTitle.value = title
  textEditorField.value = field
  textEditorOpen.value = true
}

function openIfaceOptionsEditor(idx) {
  textEditorField.value = ''
  textEditorTitle.value = 'Options'
  ifaceOptionsIdx.value = idx
  textEditorOpen.value = true
}

function closeTextEditor() {
  textEditorOpen.value = false
  ifaceOptionsIdx.value = -1
}

function onTextEditorModalApply(v) {
  if (ifaceOptionsIdx.value >= 0 && form.interfaces[ifaceOptionsIdx.value]) {
    form.interfaces[ifaceOptionsIdx.value].options = v != null ? String(v) : ''
  } else if (textEditorField.value) {
    form[textEditorField.value] = v
  }
}

function looksLikeBinary(buf) {
  if (!buf || !buf.byteLength) return false
  const view = new Uint8Array(buf)
  const n = Math.min(view.length, 65536)
  for (let i = 0; i < n; i++) {
    if (view[i] === 0) return true
  }
  return false
}

function onUploadFile(e, field) {
  const file = e.target.files?.[0]
  if (!file) return
  const fr = new FileReader()
  fr.onload = () => {
    if (looksLikeBinary(fr.result)) {
      alert('Please choose a text file only.')
      e.target.value = ''
      return
    }
    form[field] = new TextDecoder('utf-8', { fatal: false }).decode(new Uint8Array(fr.result))
    e.target.value = ''
  }
  fr.onerror = () => {
    alert('Could not read the file.')
    e.target.value = ''
  }
  fr.readAsArrayBuffer(file)
}

function buildFormData() {
  const fd = new FormData()
  const fields = [
    'name', 'roles', 'netboot', 'osimage', 'scripts', 'setupbmc', 'bmcsetupname',
    'domain', 'unmanaged_bmc_users', 'kerneloptions', 'prescript', 'partscript',
    'postscript', 'osimagetag', 'provision_interface', 'provision_fallback',
    'provision_method', 'comment',
  ]
  if (props.mode === 'clone') {
    fields.push('newgroupname')
  }
  for (const f of fields) {
    if (form[f] != null) fd.append(f, form[f])
  }
  for (const iface of form.interfaces) {
    for (const k of Object.keys(iface)) {
      fd.append(k, iface[k] != null ? String(iface[k]) : '')
    }
  }
  return fd
}

defineExpose({ form, buildFormData })
</script>
