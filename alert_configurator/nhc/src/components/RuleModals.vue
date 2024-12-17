<script setup lang="ts">
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

defineProps({
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
              <button type="button" :id="`button_html_${index + 1}`" @click="rule_modal_html(index + 1, 1);" class="btn btn-secondary btn-sm">HTML View</button> &nbsp;
              <button v-if="currentMode === 'HTML'" type="button" :id="`button_json_${index + 1}`" @click="rule_modal_json(index + 1, 2);" class="btn btn-dark btn-sm">Raw</button>
              <CodeMirrorEditor v-if="currentMode !== 'HTML'" editorHeight="300" :Content="ruleRow(row, currentMode)" ContentType="JSON" @Toast="$emit('Toast', $event)" />
            </div>
          </div>

          <div v-if="currentMode === 'HTML'">
            <div :id="`model-form_${index + 1}`">
              <div class="row g-6">
                <div class="col mb-0">
                  <label :for="`rule_name_${index + 1}`" class="form-label">Rule Name</label>
                  <input type="text" :id="`rule_name_${index + 1}`" class="form-control" placeholder="Enter Name" :value="`${row.alert}`" />
                </div>
              </div>
              <div class="row">
                <div class="col mb-6">
                  <label :for="`rule_description_${index + 1}`" class="form-label">Rule Description</label>
                  <input type="text" :id="`rule_description_${index + 1}`" class="form-control" placeholder="Enter Name" :value="`${row.annotations.description}`" />
                </div>
              </div>
              <div class="row">
                <div class="col mb-0">
                  <label :for="`rule_for_${index + 1}`" class="form-label">Rule For</label>
                  <input type="text" :id="`rule_for_${index + 1}`" class="form-control" placeholder="Enter For" :value="`${row.for}`" />
                </div>
              </div>
              <div class="row">
                <div class="col mb-6">
                  <label :for="`exprInput_${index + 1}`" class="form-label">Rule Expr</label>
                  <PromQLEditor :promQLurl="promQLurl" :editor-id="`editor_${index + 1}`" :editor-rule="`${row.expr}`"><div class="promql"></div></PromQLEditor>
                </div>
              </div>
              <div class="row">
                <div class="col mb-0">
                  <label :for="`rule_status_${index + 1}`" class="form-label">Enable</label>
                  <div class="form-check form-switch ">
                    <input type="checkbox" @click="update_configuration('status', $event.target, index + 1, base64String(row));" :id="`rule_status_${index + 1}`" class="form-check-input" :checked="row.labels._trix_status !== false">
                    <label :id="`rule_status_label_${index + 1}`" :for="`rule_status_${index + 1}`" class="form-check-label">{{ row.labels._trix_status ? 'ON' : 'OFF' }}</label>
                  </div>
                </div>
                <div class="col mb-6">
                  <label :for="`rule_nhc_${index + 1}`" class="form-label">Rule NHC</label>
                  <div class="form-check form-switch ">
                    <input type="checkbox" @click="update_configuration('nhc', $event.target, index + 1, base64String(row));" :id="`rule_nhc_${index + 1}`" class="form-check-input" :checked="row.labels.nhc === 'yes'" />
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
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Close</button>
          <button type="button" @click="update_configuration('save', $event.target, index + 1, base64String(row));" class="btn btn-primary">Save Rule</button>
        </div>
      </div>
    </div>
  </div>
</template>
