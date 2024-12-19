<script setup lang="ts">
import { ref, computed, reactive } from 'vue';
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
    _trix_status: boolean;
    nhc: string;
    severity: string;
  };
}

const props = defineProps({
  promQLurl: {
    type: String,
    required: true,
  },
  update_configuration: Function,
  updateClass: Function,
  base64String: {
    type: Function,
    required: true,
  },
  rule_modal_html: Function,
  rule_modal_json: Function,
  rule_modal_yaml: Function,
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


// Centralized state for rule data
const ruleData = reactive({
  alert: props.row.alert,
  annotations: { description: props.row.annotations.description },
  expr: props.row.expr,
  for: props.row.for,
  labels: {
    _trix_status: props.row.labels._trix_status,
    nhc: props.row.labels.nhc,
    severity: props.row.labels.severity
  },
});

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

const toggleNHC = () => {
  ruleData.labels.nhc = ruleData.labels.nhc === 'yes' ? 'no' : 'yes';
};

</script>

<template>
  <div class="modal fade" v-bind:id="`rule_modal_${index + 1}`" tabindex="-1" aria-hidden="true" >
    <div class="modal-dialog modal-xl" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="exampleModalLabel4">RULE: {{ row.alert }}</h5>
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
            <div :id="`model-form_${index + 1}`">
              <div class="row g-6">
                <div class="col mb-0">
                  <label :for="`rule_name_${index + 1}`" class="form-label">Rule Name</label>
                  <input type="text" v-model="ruleData.alert" :id="`rule_name_${index + 1}`" class="form-control" placeholder="Enter Name"/>
                </div>
              </div>
              <div class="row">
                <div class="col mb-6">
                  <label :for="`rule_description_${index + 1}`" class="form-label">Rule Description</label>
                  <input type="text" v-model="ruleData.annotations.description" :id="`rule_description_${index + 1}`" class="form-control" placeholder="Enter Name" />
                </div>
              </div>
              <div class="row">
                <div class="col mb-0">
                  <label :for="`rule_for_${index + 1}`" class="form-label">Rule For</label>
                  <input type="text" v-model="ruleData.for" :id="`rule_for_${index + 1}`" class="form-control" placeholder="Enter For"  />
                </div>
              </div>
              <div class="row">
                <div class="col mb-6">
                  <label :for="`exprInput_${index + 1}`" class="form-label">Rule Expr</label>
                  <PromQLEditor :promQLurl="promQLurl" :editor-id="`editor_${index + 1}`" v-model:editorRule="ruleData.expr"><div class="promql"></div></PromQLEditor>
                </div>
              </div>
              <div class="row">
                <div class="col mb-0">
                  <label :for="`rule_status_${index + 1}`" class="form-label">Enable</label>
                  <div class="form-check form-switch ">
                    <input v-model="ruleData.labels._trix_status" type="checkbox" :id="`rule_status_${index + 1}`" class="form-check-input" :checked="ruleData.labels._trix_status !== false">
                    <label :id="`rule_status_label_${index + 1}`" :for="`rule_status_${index + 1}`" class="form-check-label">{{ ruleData.labels._trix_status ? 'ON' : 'OFF' }}</label>
                  </div>
                </div>
                <div class="col mb-6">
                  <label :for="`rule_nhc_${index + 1}`" class="form-label">Rule NHC</label>
                  <div class="form-check form-switch ">
                    <input type="checkbox" @click.prevent="toggleNHC" :id="`rule_nhc_${index + 1}`" class="form-check-input" :checked="ruleData.labels.nhc === 'yes'" />
                    <label :id="`rule_nhc_label_${index + 1}`" :for="`rule_nhc_${index + 1}`" class="form-check-label">{{ ruleData.labels.nhc === 'yes' ? 'ON' : 'OFF' }}</label>
                  </div>
                </div>
                <div class="col mb-6">
                  <label :for="`rule_severity_${index + 1}`" class="form-label">Set Priority</label>
                  <select v-model="ruleData.labels.severity" :id="`rule_severity_${index + 1}`" :class="['form-select', 'form-select-sm', ruleData.labels.severity === 'critical' ? 'btn-dark' : ruleData.labels.severity ? 'btn-' + ruleData.labels.severity : 'btn-primary']">
                    <option class="btn-primary" value="">Set Priority</option>
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
          <button type="button" @click.prevent="update_configuration('save', $event.target, index + 1, base64String(ruleData));" class="btn btn-primary">Save Rule</button>
        </div>
      </div>
    </div>
  </div>
</template>
