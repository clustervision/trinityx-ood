<script setup lang="ts">
import { ref, computed, reactive, toRaw, watch } from 'vue';
// import CodeMirrorEditor from '@/components/CodeMirrorEditor.vue';
// import PromQLEditor from './PromQLEditor.vue';
// import jsyaml from 'js-yaml';

// interface Row {
//   alert: string;
//   annotations: {
//     description: string;
//   };
//   expr: string;
//   for: string;
//   labels: {
//     category: string;
//     disabled: boolean;
//     nhc: boolean;
//     severity: string;
//   };
// }

// const props = defineProps({
//   configType: {
//     type: String,
//     required: true,
//   },
//   url: {
//     type: String,
//     required: true,
//   },
//   promQLurl: {
//     type: String,
//     required: true,
//   },
//   configuration: Object,
//   save_configuration: {
//     type: Function,
//     required: true,
//   },
//   updateClass: Function,
//   ruleRow: Function,
//   row: {
//     type: Object as () => Row,
//     required: true,
//   },
//   index: {
//     type: Number,
//     required: true
//   },
//   selectedClass: String,
// });

// const new_config = props.configuration;

// // Centralized state for rule data
// const ruleData = reactive({
//   alert: props.row.alert,
//   annotations: { description: props.row.annotations.description },
//   expr: props.row.expr,
//   for: props.row.for || '',
//   labels: {
//     category: props.configType === 'generic' ? 'generic' : 'service',
//     disabled: props.row.labels.disabled || false,
//     nhc: props.row.labels.nhc,
//     severity: props.row.labels.severity
//   },
// });

// watch(
//   () => props.row,
//   (newRow) => {
//     ruleData.alert = newRow.alert;
//     ruleData.annotations.description = newRow.annotations.description;
//     ruleData.expr = newRow.expr;
//     ruleData.for = newRow.for || '';
//     ruleData.labels.disabled = newRow.labels.disabled || false;
//     ruleData.labels.nhc = newRow.labels.nhc;
//     ruleData.labels.category = newRow.labels.category || props.index === 0 ? (props.configType === 'generic' ? 'generic' : 'service') : props.row.labels.category;
//     ruleData.labels.severity = newRow.labels.severity;
//   },
//   { deep: true, immediate: true } // Ensure deep watching and immediate reaction
// );


// // Current mode (HTML, JSON, YAML)
// const currentMode = ref<'HTML' | 'JSON' | 'YAML'>('HTML');

// // Synchronize data from the HTML form
// const syncFromHTML = () => {
//   // ruleData is already reactive and bound to the form inputs via v-model
// };

// const emit = defineEmits(['toast']);

// // Synchronize data from the CodeMirror editor
// const syncFromCodeMirror = (content: string) => {
//   try {
//     if (currentMode.value === 'JSON') {
//       Object.assign(ruleData, JSON.parse(content));
//     } else if (currentMode.value === 'YAML') {
//       Object.assign(ruleData, jsyaml.load(content));
//     }
//   } catch (err: unknown) {
//     if (err instanceof Error) {
//     emit('toast', {message: err.message, toastClass: 'bg-danger'});
//     } else {
//       emit('toast', {message: 'An unknown error occurred', toastClass: 'bg-danger'});
//     }
//   }
// };

// // Switch between modes
// const switchMode = (mode: 'HTML' | 'JSON' | 'YAML') => {
//   if (mode === currentMode.value){
//     emit('toast', {message: `Error: Already in ${mode} Mode, no conversion needed`, toastClass: 'bg-warning'});
//   } else{
//     currentMode.value = mode;
//   }
// };

// const serializedContent = computed(() => {
//   if (currentMode.value === 'JSON') {
//     return JSON.stringify(ruleData, null, 2);
//   } else if (currentMode.value === 'YAML') {
//     return jsyaml.dump(ruleData);
//   }
//   return '';
// });


// const updateRow = (row: object, count: number) => {
//   if (new_config?.groups?.[0]?.rules && count >= 0 && count < new_config.groups[0].rules.length) {
//     new_config.groups[0].rules[count] = row;
//   } else {
//     console.error('Invalid index or rules array not found');
//   }
// };

// function update_configuration(count: number) {
//   let error = false;
//   if (ruleData.alert === ""){
//     emit('toast', {message: 'Alert Name is required.', toastClass: 'bg-danger'});
//     error = true;
//   }
//   if (ruleData.annotations.description === ""){
//     emit('toast', {message: 'Alert Description is required.', toastClass: 'bg-danger'});
//     error = true;
//   }
//   if (ruleData.expr === ""){
//     emit('toast', {message: 'Alert Expression is required.', toastClass: 'bg-danger'});
//     error = true;
//   }

//   if (error === false){
//     if (ruleData.for === ""){ ruleData.for = "null"; }
//     const rule = toRaw(ruleData);
//     if (count === 0){
//       const add_rule_config = JSON.parse(JSON.stringify(props.configuration));
//       if (add_rule_config?.groups?.[0]?.rules) {
//         add_rule_config.groups[0].rules.push(rule);
//       } else {
//         console.error('Cannot add row: Invalid configuration structure');
//       }
//       props.save_configuration(props.configType, add_rule_config, `rule_modal_${props.configType}_${count}`)

//     } else {
//       updateRow(rule, count-1);
//       props.save_configuration(props.configType, new_config, `rule_modal_${props.configType}_${count}`)
//     }
//   }

// }

// const getComputedDisabled = (status: boolean | undefined) => computed({
//   get: () => status !== true,
//   set: (value: boolean) => {
//     if (value) { status = false; ruleData.labels.disabled = false; } else { status = true; ruleData.labels.disabled = true; }
//   }
// });
</script>

<template>
  <div class="modal fade" id="wizard_modal" tabindex="-1" >
    <div class="modal-dialog modal-xl" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="exampleModalLabel4">Rule Wizard</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div class="container">
            <h3 class="mb-4">Create Monitoring Rule</h3>
            <form>
              <!-- per-metric -->
              <div class="mb-3">
                <label class="form-label">Per-Metric</label>
                <select class="form-select">
                  <option selected disabled>Select metric type</option>
                  <option>per-GPU</option>
                  <option>per-Disk</option>
                  <option>per-NIC</option>
                </select>
              </div>

              <!-- group granularity & operator -->
              <div class="row mb-3">
                <div class="col-md-6">
                  <label class="form-label">Group Granularity</label>
                  <select class="form-select">
                    <option selected disabled>Select granularity</option>
                    <option>per-metric</option>
                    <option>per-hostname</option>
                    <option>per-group</option>
                    <option>global</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Grouping Operator</label>
                  <select class="form-select">
                    <option selected disabled>Select operator</option>
                    <option>max</option>
                    <option>min</option>
                    <option>avg</option>
                  </select>
                </div>
              </div>

              <!-- Select category -->
              <div class="mb-3">
                <label class="form-label">Select Category</label>
                <select class="form-select">
                  <option selected disabled>Select category</option>
                  <option>node</option>
                  <option>ipmi</option>
                  <option>infiniband</option>
                </select>
              </div>

              <!-- Select metric -->
              <div class="mb-3">
                <label class="form-label">Select Metric</label>
                <select class="form-select">
                  <option selected disabled>Select metric</option>
                  <option>temperature</option>
                  <option>fan_speed</option>
                  <option>power_usage</option>
                </select>
              </div>

              <!-- Filter key & value -->
              <div class="row mb-3">
                <div class="col-md-6">
                  <label class="form-label">Filter Key</label>
                  <select class="form-select">
                    <option selected disabled>Select filter key</option>
                    <option>luna_group</option>
                    <option>hostname</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Filter Value</label>
                  <select class="form-select">
                    <option selected disabled>Select filter value</option>
                    <option>controller</option>
                    <option>compute</option>
                    <option>gpu</option>
                  </select>
                </div>
              </div>

              <!-- Operator -->
              <div class="mb-3">
                <label class="form-label">Select Operator</label>
                <select class="form-select">
                  <option selected disabled>Select comparison</option>
                  <option>&gt;</option>
                  <option>&lt;</option>
                  <option>&gt;=</option>
                  <option>&lt;=</option>
                  <option>=</option>
                </select>
              </div>

              <!-- Threshold -->
              <div class="mb-3">
                <label class="form-label">Threshold</label>
                <input type="number" class="form-control" placeholder="Enter threshold value">
              </div>
              </form>
              </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Close</button>
          <button type="button" class="btn btn-primary">Save Rule</button>
        </div>
      </div>
    </div>
  </div>
</template>
