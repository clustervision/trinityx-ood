<script setup lang="ts">
import { ref, computed } from 'vue';
import CodeMirrorEditor from '@/components/CodeMirrorEditor.vue';
import PromQLEditor from './PromQLEditor.vue';

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
  currentMode: String,
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
});




import jsyaml from 'js-yaml';

// Centralized state for rule data
// const ruleData = ref({
//   alert: '',
//   annotations: { description: '' },
//   expr: '',
//   for: '',
//   labels: { _trix_status: false, nhc: 'no', severity: 'info' },
// });

let ruleData = {
  alert: props.row.alert,
  annotations: { description: props.row.annotations.description },
  expr: props.row.expr,
  for: props.row.for,
  labels: { _trix_status: props.row.labels._trix_status, nhc: props.row.labels.nhc, severity: props.row.labels.severity },
};

// Current mode (HTML, JSON, YAML)
const currentMode = ref<'HTML' | 'JSON' | 'YAML'>('HTML');

// Computed property to serialize ruleData into the appropriate format for CodeMirror
// const serializedRuleData = computed(() => {
//   if (currentMode.value === 'JSON') {
//     return JSON.stringify(ruleData.value, null, 2);
//   } else if (currentMode.value === 'YAML') {
//     return jsyaml.dump(ruleData.value);
//   }
//   return ''; // Empty for non-editor modes
// });

// Synchronize data from the HTML form
const syncFromHTML = () => {
  console.log('HTML Form updated:', ruleData);
  // ruleData is already reactive and bound to the form inputs via v-model
};

// Synchronize data from the CodeMirror editor
const syncFromCodeMirror = (content: string) => {
  console.warn('content:', content);
  console.log('currentMode.value:', currentMode.value);
  try {
    if (currentMode.value === 'JSON') {
      // ruleData.value = JSON.parse(content);
      ruleData = JSON.stringify(content, null, 2);
    } else if (currentMode.value === 'YAML') {
      ruleData = jsyaml.load(content);
    }
  } catch (err) {
    console.error('Failed to parse content:', err);
    // $emit('Toast', { message: 'Error parsing content', toastClass: 'bg-danger' });
  }
};

// Switch between modes
const switchMode = (mode: 'HTML' | 'JSON' | 'YAML') => {
  currentMode.value = mode;
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

              <button @click="switchMode('HTML')">HTML View</button>
              <button @click="switchMode('JSON')">JSON View</button>
              <button @click="switchMode('YAML')">YAML View</button>


              <!-- <CodeMirrorEditor  /> -->
              <button type="button" :id="`button_html_${index + 1}`" @click="rule_modal_html(index + 1, 1);" class="btn btn-secondary btn-sm">HTML View</button> &nbsp;
              <!-- <button v-if="currentMode === 'HTML'" type="button" :id="`button_json_${index + 1}`" @click="logEditorContainer(props, index + 1, 2);" class="btn btn-dark btn-sm">Raw</button> -->
              <button v-if="currentMode === 'HTML'" type="button" :id="`button_json_${index + 1}`" @click="rule_modal_json(index + 1, 2);" class="btn btn-dark btn-sm">Raw</button>
              <!-- <CodeMirrorEditor v-if="currentMode !== 'HTML'" @update:Content="syncFromCodeMirror" ref="codeMirrorRef" editorHeight="300" :Content="ruleRow(row, currentMode)" ContentType="JSON" @Toast="$emit('Toast', $event)" /> -->
              <CodeMirrorEditor v-if="currentMode !== 'HTML'" @update:Content="syncFromCodeMirror" ref="codeMirrorRef" editorHeight="300" :Content="ruleRow(row, currentMode)" ContentType="JSON" @Toast="$emit('Toast', $event)" />
            </div>
          </div>

          <form v-if="currentMode === 'HTML'" @input="syncFromHTML" >
            <div :id="`model-form_${index + 1}`">
              <div class="row g-6">
                <div class="col mb-0">
                  <label :for="`rule_name_${index + 1}`" class="form-label">Rule Name</label>
                  <!-- <input type="text" v-model="ruleData.alert" :id="`rule_name_${index + 1}`" class="form-control" placeholder="Enter Name" :value="`${row.alert}`" /> -->
                  <input type="text" v-model="ruleData.alert" :id="`rule_name_${index + 1}`" class="form-control" placeholder="Enter Name"/>
                </div>
              </div>
              <div class="row">
                <div class="col mb-6">
                  <label :for="`rule_description_${index + 1}`" class="form-label">Rule Description</label>
                  <!-- <input type="text" v-model="ruleData.annotations.description" :id="`rule_description_${index + 1}`" class="form-control" placeholder="Enter Name" :value="`${row.annotations.description}`" /> -->
                  <input type="text" v-model="ruleData.annotations.description" :id="`rule_description_${index + 1}`" class="form-control" placeholder="Enter Name" />
                </div>
              </div>
              <div class="row">
                <div class="col mb-0">
                  <label :for="`rule_for_${index + 1}`" class="form-label">Rule For</label>
                  <!-- <input type="text" v-model="ruleData.for" :id="`rule_for_${index + 1}`" class="form-control" placeholder="Enter For" :value="`${row.for}`" /> -->
                  <input type="text" v-model="ruleData.for" :id="`rule_for_${index + 1}`" class="form-control" placeholder="Enter For"  />
                </div>
              </div>
              <div class="row">
                <div class="col mb-6">
                  <label :for="`exprInput_${index + 1}`" class="form-label">Rule Expr</label>
                  <!-- <PromQLEditor v-model="ruleData.expr" :promQLurl="promQLurl" :editor-id="`editor_${index + 1}`" :editor-rule="`${row.expr}`"><div class="promql"></div></PromQLEditor> -->
                </div>
              </div>
              <div class="row">
                <div class="col mb-0">
                  <label :for="`rule_status_${index + 1}`" class="form-label">Enable</label>
                  <div class="form-check form-switch ">
                    <input v-model="ruleData.labels._trix_status" type="checkbox" @click="update_configuration('status', $event.target, index + 1, base64String(row));" :id="`rule_status_${index + 1}`" class="form-check-input" :checked="row.labels._trix_status !== false">
                    <label :id="`rule_status_label_${index + 1}`" :for="`rule_status_${index + 1}`" class="form-check-label">{{ row.labels._trix_status ? 'ON' : 'OFF' }}</label>
                  </div>
                </div>
                <div class="col mb-6">
                  <label :for="`rule_nhc_${index + 1}`" class="form-label">Rule NHC</label>
                  <div class="form-check form-switch ">
                    <input v-model="ruleData.labels.nhc" type="checkbox" @click="update_configuration('nhc', $event.target, index + 1, base64String(row));" :id="`rule_nhc_${index + 1}`" class="form-check-input" :checked="row.labels.nhc === 'yes'" />
                    <label :id="`rule_nhc_label_${index + 1}`" :for="`rule_nhc_${index + 1}`" class="form-check-label">{{ row.labels.nhc === 'yes' ? 'ON' : 'OFF' }}</label>
                  </div>
                </div>
                <div class="col mb-6">
                  <label :for="`rule_severity_${index + 1}`" class="form-label">Set Priority</label>
                  <select :id="`rule_severity_${index + 1}`" @change="update_configuration('severity', $event.target, index + 1, base64String(row));" :v-model="row.labels.severity" :class="['form-select', 'form-select-sm', row.labels.severity === 'critical' ? 'btn-dark' : 'btn-' + row.labels.severity]">
                    <option class="btn-primary">Set Priority</option>
                    <option class="btn-dark" value="critical" :selected="row.labels.severity === 'critical'">Critical</option>
                    <option class="btn-danger" value="danger" :selected="row.labels.severity === 'danger'">Danger</option>
                    <option class="btn-warning" value="warning" :selected="row.labels.severity === 'warning'">Warning</option>
                    <option class="btn-info" value="info" :selected="row.labels.severity === 'info'">Informational</option>
                  </select>
                </div>
              </div>
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Close</button>
          <button type="button" @click="update_configuration('save', $event.target, index + 1, base64String(row));" class="btn btn-primary">Save Rule</button>
        </div>
      </div>
    </div>
  </div>
</template>
