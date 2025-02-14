<script setup lang="ts">
import { ref, computed, reactive, toRaw, watch } from 'vue';
import CodeMirrorEditor from '@/components/CodeMirrorEditor.vue';
import PromQLEditor from './PromQLEditor.vue';
import jsyaml from 'js-yaml';

interface Row {
  alert: string;
  annotations: {
    description: string;
  };
  expr: string;
  for: string;
  labels: {
    category: string;
    disabled: boolean;
    nhc: boolean;
    severity: string;
  };
}

const props = defineProps({
  url: {
    type: String,
    required: true,
  },
  promQLurl: {
    type: String,
    required: true,
  },
  configuration: Object,
  save_configuration: {
    type: Function,
    required: true,
  },
  updateClass: Function,
  ruleRow: Function,
  row: {
    type: Object as () => Row,
    required: true,
  },
  index: {
    type: Number,
    required: true
  },
  selectedClass: String,
});

const new_config = props.configuration;

// Centralized state for rule data
const ruleData = reactive({
  alert: props.row.alert,
  annotations: { description: props.row.annotations.description },
  expr: props.row.expr,
  for: props.row.for || '',
  labels: {
    category: props.row.labels.category,
    disabled: props.row.labels.disabled || false,
    nhc: props.row.labels.nhc,
    severity: props.row.labels.severity
  },
});

watch(
  () => props.row,
  (newRow) => {
    ruleData.alert = newRow.alert;
    ruleData.annotations.description = newRow.annotations.description;
    ruleData.expr = newRow.expr;
    ruleData.for = newRow.for || '';
    ruleData.labels.disabled = newRow.labels.disabled || false;
    ruleData.labels.nhc = newRow.labels.nhc;
    ruleData.labels.severity = newRow.labels.severity;
  },
  { deep: true, immediate: true } // Ensure deep watching and immediate reaction
);


// Current mode (HTML, JSON, YAML)
const currentMode = ref<'HTML' | 'JSON' | 'YAML'>('HTML');

// Synchronize data from the HTML form
const syncFromHTML = () => {
  // ruleData is already reactive and bound to the form inputs via v-model
};

const emit = defineEmits(['toast']);

// Synchronize data from the CodeMirror editor
const syncFromCodeMirror = (content: string) => {
  try {
    if (currentMode.value === 'JSON') {
      Object.assign(ruleData, JSON.parse(content));
    } else if (currentMode.value === 'YAML') {
      Object.assign(ruleData, jsyaml.load(content));
    }
  } catch (err: unknown) {
    if (err instanceof Error) {
    emit('toast', {message: err.message, toastClass: 'bg-danger'});
    } else {
      emit('toast', {message: 'An unknown error occurred', toastClass: 'bg-danger'});
    }
  }
};

// Switch between modes
const switchMode = (mode: 'HTML' | 'JSON' | 'YAML') => {
  if (mode === currentMode.value){
    emit('toast', {message: `Error: Already in ${mode} Mode, no conversion needed`, toastClass: 'bg-warning'});
  } else{
    currentMode.value = mode;
  }
};

const serializedContent = computed(() => {
  if (currentMode.value === 'JSON') {
    return JSON.stringify(ruleData, null, 2);
  } else if (currentMode.value === 'YAML') {
    return jsyaml.dump(ruleData);
  }
  return '';
});


const updateRow = (row: object, count: number) => {
  if (new_config?.groups?.[0]?.rules && count >= 0 && count < new_config.groups[0].rules.length) {
    new_config.groups[0].rules[count] = row;
  } else {
    console.error('Invalid index or rules array not found');
  }
};

function update_configuration(count: number) {
  let error = false;
  if (ruleData.alert === ""){
    emit('toast', {message: 'Alert Name is required.', toastClass: 'bg-danger'});
    error = true;
  }
  if (ruleData.annotations.description === ""){
    emit('toast', {message: 'Alert Description is required.', toastClass: 'bg-danger'});
    error = true;
  }
  if (ruleData.expr === ""){
    emit('toast', {message: 'Alert Expression is required.', toastClass: 'bg-danger'});
    error = true;
  }

  if (error === false){
    if (ruleData.for === ""){ ruleData.for = "null"; }
    const rule = toRaw(ruleData);
    if (count === 0){
      const add_rule_config = JSON.parse(JSON.stringify(props.configuration));
      if (add_rule_config?.groups?.[0]?.rules) {
        add_rule_config.groups[0].rules.push(rule);
      } else {
        console.error('Cannot add row: Invalid configuration structure');
      }
      props.save_configuration(add_rule_config, `rule_modal_${count}`)

    } else {
      updateRow(rule, count-1);
      props.save_configuration(new_config, `rule_modal_${count}`)
    }
  }

}

const getComputedDisabled = (status: boolean | undefined) => computed({
  get: () => status !== true,
  set: (value: boolean) => {
    if (value) { status = false; ruleData.labels.disabled = false; } else { status = true; ruleData.labels.disabled = true; }
  }
});
</script>

<template>
  <div class="modal fade" v-bind:id="`rule_modal_${index}`" tabindex="-1" aria-hidden="true" >
    <div class="modal-dialog modal-xl" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="exampleModalLabel4">RULE: {{ index === 0 ? 'Add a new Rule' : row.alert }}</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div class="row">
            <div class="col mb-12">
              <button type="button" class="btn btn-secondary btn-sm" @click.prevent="switchMode('HTML')">HTML View</button>&nbsp;
              <button type="button" class="btn btn-primary btn-sm" @click.prevent="switchMode('JSON')">JSON View</button>&nbsp;
              <button type="button" class="btn btn-warning btn-sm" @click.prevent="switchMode('YAML')">YAML View</button><br />
            </div>
          </div>
          <CodeMirrorEditor v-if="currentMode !== 'HTML'" @update:Content="syncFromCodeMirror" ref="codeMirrorRef" editorHeight="300" :Content="serializedContent" :ContentType="currentMode" @Toast="$emit('toast', $event)" />
          <form v-if="currentMode === 'HTML'" @input="syncFromHTML" >
            <div :id="`model-form_${index}`">
              <div class="row g-6">
                <div class="col mb-0">
                  <label :for="`rule_name_${index}`" class="form-label">Rule Name</label>
                  <input type="text" v-model="ruleData.alert" :id="`rule_name_${index}`" class="form-control" placeholder="Enter Rule Name" required/>
                </div>
              </div>
              <div class="row">
                <div class="col mb-6">
                  <label :for="`rule_description_${index}`" class="form-label">Rule Description</label>
                  <input type="text" v-model="ruleData.annotations.description" :id="`rule_description_${index}`" class="form-control" required placeholder="Enter Rule Description" />
                </div>
              </div>
              <div class="row">
                <div class="col mb-0">
                  <label :for="`rule_for_${index}`" class="form-label">Rule For</label>
                  <input type="text" v-model="ruleData.for" :id="`rule_for_${index}`" class="form-control" placeholder="Enter Rule For"  />
                </div>
              </div>
              <div class="row">
                <div class="col mb-6">
                  <label :for="`exprInput_${index}`" class="form-label">Rule Expr</label>
                  <PromQLEditor :url = "url" :promQLurl="promQLurl" :editor-id="`editor_${index}`" v-model:editorRule="ruleData.expr"><div class="promql"></div></PromQLEditor>
                  <input type="hidden" v-model="ruleData.expr" :id="`rule_editor__${index}`" required class="form-control" />
                </div>
              </div>
              <div class="row">
                <div class="col mb-6">
                  <label :for="`rule_category_${index}`" class="form-label">Rule Category</label>
                  <select v-model="ruleData.labels.category" disabled :id="`rule_category_${index}`" :class="[
                      'form-select',
                      'form-select-sm',
                      ruleData.labels.category === 'generic' ? 'btn-info' :
                      ruleData.labels.category === 'service' ? 'btn-warning' :
                      ruleData.labels.category === 'hardware' ? 'btn-dark' :
                      'btn-primary'
                    ]">
                    <option class="btn-primary" value="">Set Category</option>
                    <option class="btn-info" value="generic" :selected="ruleData.labels.category === 'generic'">Generic</option>
                    <option class="btn-warning" value="service" :selected="ruleData.labels.category === 'service'">Service</option>
                    <option class="btn-dark" value="hardware" :selected="ruleData.labels.category === 'hardware'">Hardware</option>
                  </select>
                </div>
                <div class="col mb-0">
                  <label :for="`rule_status_${index}`" class="form-label">Enable</label>
                  <div class="form-check form-switch ">
                    <input v-model="getComputedDisabled(ruleData.labels.disabled).value" type="checkbox" :id="`rule_status_${index}`" class="form-check-input" >
                    <label :id="`rule_status_label_${index}`" :for="`rule_status_${index}`" class="form-check-label">{{ ruleData.labels.disabled !== true ? 'ON' : 'OFF' }}</label>
                  </div>
                </div>
                <div class="col mb-6">
                  <label :for="`rule_nhc_${index}`" class="form-label">Rule NHC</label>
                  <div class="form-check form-switch ">
                    <input type="checkbox" v-model="ruleData.labels.nhc" :id="`rule_nhc_${index}`" class="form-check-input" data-toggle="switch" :true-value=true :false-value=false />
                    <label :id="`rule_nhc_label_${index}`" :for="`rule_nhc_${index}`" class="form-check-label">{{ ruleData.labels.nhc === true ? 'ON' : 'OFF' }}</label>
                  </div>
                </div>
                <div class="col mb-6">
                  <label :for="`rule_severity_${index}`" class="form-label">Set Severity</label>
                  <select v-model="ruleData.labels.severity" :id="`rule_severity_${index}`" :class="['form-select', 'form-select-sm', ruleData.labels.severity === 'critical' ? 'btn-dark' : ruleData.labels.severity ? 'btn-' + ruleData.labels.severity : 'btn-primary']">
                    <option class="btn-primary" value="">Set Severity</option>
                    <option class="btn-dark" value="critical" :selected="ruleData.labels.severity === 'critical'">Critical</option>
                    <option class="btn-danger" value="danger" :selected="ruleData.labels.severity === 'danger'">Danger</option>
                    <option class="btn-warning" value="warning" :selected="ruleData.labels.severity === 'warning'">Warning</option>
                    <option class="btn-info" value="info" :selected="ruleData.labels.severity === 'info'">Informational</option>
                  </select>
                </div>
              </div>
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Close</button>
          <button type="button" @click.prevent="update_configuration(index);" class="btn btn-primary">Save Rule</button>
        </div>
      </div>
    </div>
  </div>
</template>
