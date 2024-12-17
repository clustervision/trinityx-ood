<script setup lang="ts">

import 'boxicons'
import './assets/css/core.css';
import './assets/css/theme-default.css';
import './assets/css/app.css';
// import 'bootstrap';

// import 'bootstrap/dist/css/bootstrap.css';
// import {bootstrap} from 'bootstrap/dist/js/bootstrap.bundle.js';
import 'bootstrap/dist/js/bootstrap.bundle.js';
import './assets/js/main.js';
// import './assets/js/app.js';

import TopNavigation from '@/views/TopNavigation.vue';
import SubNavigation from '@/views/SubNavigation.vue';
import FooterBar from '@/views/FooterBar.vue';
import PromQLEditor from '@/components/PromQLEditor.vue';
// import CodeMirrorEditor from '@/components/CodeMirrorEditor.vue';
import CodeMirrorEditor from '@/components/CodeMirrorEditor.vue';
import RuleModals from './components/RuleModals.vue';


import { onMounted, ref } from 'vue';
import { Modal } from 'bootstrap';

const uniqueModal = ref<Modal | null>(null);

const showModal = (id: number) => {
  console.log(id);
  const dymodal = document.getElementById(`rule_modal_${id}`);
  console.log(dymodal);

  if (dymodal) {
    uniqueModal.value = new Modal(dymodal, {
      backdrop: true,
    });
    uniqueModal.value.show();
    console.log(uniqueModal.value);
  } else {
    console.error(`Modal with ID rule_modal_${id} not found`);
  }
};

onMounted(() => {
  console.log('App mounted, ready for modals!');
});

// Reactive variable to keep track of the current mode
const currentMode = ref<'HTML' | 'JSON' | 'YAML'>('HTML');

// Method to handle switching modes
const rule_modal_html = (id: number, mode: number) => {
  currentMode.value = 'HTML';
};

const rule_modal_json = (id: number, mode: number) => {
  currentMode.value = 'JSON';
};

const rule_modal_yaml = (id: number, mode: number) => {
  currentMode.value = 'YAML';
};

const base64String = (row) => {
  const encodedData = btoa(JSON.stringify(row));
  return encodedData;
};
</script>


<template>

  <header>
    <TopNavigation />
    <SubNavigation

      :Content="Content"
      :ContentType="ContentType"
      @showErrorToast="failedToast"
    />
  </header>
  <!-- <PromQLEditor appendTo=".modal-body"><div class="promql"></div></PromQLEditor> -->
<!--  :CodeMirrorEditor="CodeMirrorEditor" -->
  <!-- <PromQLEditor><div class="promql"></div></PromQLEditor> -->
  <div class="layout-wrapper layout-content-navbar">
    <div class="layout-container">
      <div class="content-wrapper">
        <div id="spinner-overlay" class="spinner-overlay">
          <div id="spinner" class="d-flex justify-content-center">
            <div
              class="spinner-border spinner-border-lg text-success"
              style="width: 10rem; height: 10rem"
              role="status"
            >
              <span class="visually-hidden">Saving Configuration...</span>
            </div>
          </div>
        </div>

        <div class="container-xxl flex-grow-1 container-p-y" style="max-width: none">
          <h4 class="fw-bold py-3 mb-4">
            <span class="text-muted fw-light"> Monitoring /</span> Alert Configurator
          </h4>
          <div class="card">
            <h5 class="card-header">Rules</h5>
            <div class="card-body">
              <div class="table-responsive text-nowrap">





                <!-- <div v-for="row in tableRows" :key="row.id">
                  <div class="modal fade" v-bind:id="`rule_modal_${row.id}`" tabindex="-1" aria-hidden="true" >
                    <div class="modal-dialog modal-xl" role="document">
                      <div class="modal-content">
                        <div class="modal-header">
                          <h5 class="modal-title" id="exampleModalLabel4">RULE: {{ row.alert }}</h5>
                          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                          <div class="row">
                            <div class="col mb-12">
                              <button type="button" :id="`button_html_${row.id}`" @click="rule_modal_html(row.id, 1);" class="btn btn-secondary btn-sm">Switch to HTML Mode</button>
                              <button type="button" :id="`button_json_${row.id}`" @click="rule_modal_json(row.id, 2);" class="btn btn-primary btn-sm">Switch to JSON Mode</button>
                              <button type="button" :id="`button_yaml_${row.id}`" @click="rule_modal_yaml(row.id, 3);" class="btn btn-warning btn-sm">Switch to YAML Mode</button>
                            </div>
                          </div>
                          <div v-if="currentMode === 'JSON'">
                            <CodeMirrorEditor :editorHeight="300" :Content="ruleRow(row, 'JSON')" ContentType="JSON" @showErrorToast="$emit('showErrorToast', $event)" />
                          </div>
                          <div v-if="currentMode === 'YAML'">
                            <CodeMirrorEditor :editorHeight="300" :Content="ruleRow(row, 'YAML')" ContentType="YAML" @showErrorToast="$emit('showErrorToast', $event)" />
                          </div>
                          <div v-if="currentMode === 'HTML'">
                            <div :id="`model-form_${row.id}`">
                              <div class="row g-6">
                                <div class="col mb-0">
                                  <label :for="`rule_name_${row.id}`" class="form-label">Rule Name</label>
                                  <input type="text" :id="`rule_name_${row.id}`" class="form-control" placeholder="Enter Name" :value="`${row.alert}`" />
                                </div>
                              </div>
                              <div class="row">
                                <div class="col mb-6">
                                  <label :for="`rule_description_${row.id}`" class="form-label">Rule Description</label>
                                  <input type="text" :id="`rule_description_${row.id}`" class="form-control" placeholder="Enter Name" :value="`${row.description}`" />
                                </div>
                              </div>
                              <div class="row">
                                <div class="col mb-0">
                                  <label :for="`rule_for_${row.id}`" class="form-label">Rule For</label>
                                  <input type="text" :id="`rule_for_${row.id}`" class="form-control" placeholder="Enter For" :value="`${row.for}`" />
                                </div>
                                <div class="col mb-6">
                                  <label :for="`exprInput_${row.id}`" class="form-label">Rule Expr</label>
                                  <PromQLEditor :editor-id="`editor_${row.id}`" :editor-rule="`${row.expr}`"><div class="promql"></div></PromQLEditor>
                                </div>
                              </div>
                              <div class="row">
                                <div class="col mb-0">
                                  <label :for="`rule_status_${row.id}`" class="form-label">Enable</label>
                                  <div class="form-check form-switch ">
                                    <input type="checkbox" @click="update_configuration('status', $event.target, row.id, row.btoa_rule);" :id="`rule_status_${row.id}`" class="form-check-input" :checked="row._trix_status !== false">
                                    <label :id="`rule_status_label_${row.id}`" :for="`rule_status_${row.id}`" class="form-check-label">{{ row._trix_status ? 'ON' : 'OFF' }}</label>
                                  </div>
                                </div>
                                <div class="col mb-6">
                                  <label :for="`rule_nhc_${row.id}`" class="form-label">Rule NHC</label>
                                  <div class="form-check form-switch ">
                                    <input type="checkbox" @click="update_configuration('nhc', $event.target, row.id, row.btoa_rule);" :id="`rule_nhc_${row.id}`" class="form-check-input" :checked="row.nhc === 'yes'" />
                                    <label :id="`rule_nhc_label_${row.id}`" :for="`rule_nhc_${row.id}`" class="form-check-label">{{ row.nhc === 'yes' ? 'ON' : 'OFF' }}</label>
                                  </div>
                                </div>
                                <div class="col mb-6">
                                  <label :for="`rule_severity_${row.id}`" class="form-label">Set Priority</label>
                                  <select :id="`rule_severity_${row.id}`" @change="update_configuration('severity', $event.target, row.id, row.btoa_rule);" v-model="row.severity" :class="['form-select', 'form-select-sm', row.severity === 'critical' ? 'btn-dark' : 'btn-' + row.severity]">
                                    <option class="btn-primary">Set Priority</option>
                                    <option class="btn-dark" value="critical" :selected="row.severity === 'critical'">Critical</option>
                                    <option class="btn-danger" value="danger" :selected="row.severity === 'danger'">Danger</option>
                                    <option class="btn-warning" value="warning" :selected="row.severity === 'warning'">Warning</option>
                                    <option class="btn-info" value="info" :selected="row.severity === 'info'">Informational</option>
                                  </select>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                        <div class="modal-footer">
                          <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Close</button>
                          <button type="button" @click="update_configuration('save', $event.target, row.id, row.btoa_rule);" class="btn btn-primary">Save Rule</button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div> -->




                  <div class="modal fade" id="add_rule_rule_modal" tabindex="-1" aria-hidden="true">
                    <div class="modal-dialog modal-xl" role="document">
                      <div class="modal-content">
                        <div class="modal-header">
                          <h5 class="modal-title" id="exampleModalLabel4">Add New Alert Rule</h5>
                          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                          <div class="row">
                            <div class="col mb-12">
                              <button type="button" id="button_html_0" @click="rule_modal_html(0, 1);" class="btn btn-secondary btn-sm">Switch to HTML Mode</button>
                              <button type="button" id="button_json_0" @click="rule_modal_json(0, 2);" class="btn btn-primary btn-sm">Switch to JSON Mode</button>
                              <button type="button" id="button_yaml_0" @click="rule_modal_yaml(0, 3);" class="btn btn-warning btn-sm">Switch to YAML Mode</button>
                              <div id="ruleEditor_0" style="display: none; height: 300px; border: 1px solid #ddd;"></div>
                            </div>
                          </div>
                          <div id="model-form_0">
                            <div class="row g-6">
                              <div class="col mb-0">
                                <label for="rule_name_0" class="form-label">Rule Name</label>
                                <input type="text" id="rule_name_0" class="form-control" placeholder="Enter Name" />
                              </div>
                            </div>
                            <div class="row">
                              <div class="col mb-6">
                                <label for="rule_description_0" class="form-label">Rule Description</label>
                                <input type="text" id="rule_description_0" class="form-control" placeholder="Enter Name" />
                              </div>
                            </div>
                            <div class="row">
                              <div class="col mb-0">
                                <label for="rule_for_0" class="form-label">Rule For</label>
                                <input type="text" id="rule_for_0" class="form-control" placeholder="Enter For" />
                              </div>
                              <div class="col mb-6">
                                <label for="exprInput_0" class="form-label">Rule Expr</label>
                                <PromQLEditor editor-id="editor_0" editor-rule=""><div class="promql"></div></PromQLEditor>
                              </div>
                            </div>
                            <div class="row">
                               <div class="col mb-0">
                                <label for="rule_status_0" class="form-label">Enable</label>
                                <div class="form-check form-switch ">
                                  <input type="checkbox" v-model="isChecked" id="rule_status_0" class="form-check-input">
                                  <label id="rule_status_label_0" for="rule_status_0" class="form-check-label">{{ isChecked ? 'ON' : 'OFF' }}</label>
                                </div>
                              </div>
                              <div class="col mb-6">
                                <label for="rule_nhc_0" class="form-label">Rule NHC</label>
                                <div class="form-check form-switch ">
                                  <input type="checkbox" id="rule_nhc_0" v-model="isCheckedNHC"  class="form-check-input">
                                  <label id="rule_nhc_label_0" for="rule_nhc_0" class="form-check-label">{{ isCheckedNHC ? 'ON' : 'OFF' }}</label>
                                </div>
                              </div>
                              <div class="col mb-6">
                                <label for="rule_severity_0" class="form-label">Set Priority</label>
                                <select id="rule_severity_0" @change="updateClass" :class="['form-select', 'form-select-sm', selectedClass]">
                                  <option class="btn-primary">Set Priority</option>
                                  <option class="btn-dark" value="critical">Critical</option>
                                  <option class="btn-danger" value="danger">Danger</option>
                                  <option class="btn-warning" value="warning">Warning</option>
                                  <option class="btn-info" value="info">Informational</option>
                                </select>
                              </div>
                            </div>
                          </div>
                        </div>
                        <div class="modal-footer">
                          <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Close</button>
                          <button type="button" @click="add_rule('save', $event.target, add_count, 'save');" class="btn btn-primary">Save Rule</button>
                        </div>
                      </div>
                    </div>
                  </div>



                <table id="alert-table" class="table table-bordered table-striped table-hover table-responsive">
                  <thead>
                    <tr>
                      <th scope="col">#</th>
                      <th scope="col">Group</th>
                      <th scope="col">Rule</th>
                      <th scope="col">Enable</th>
                      <th scope="col">NHC</th>
                      <th scope="col">Priority</th>
                      <th scope="col">Actions</th>
                    </tr>
                  </thead>
                  <tbody v-for="groups in configuration.groups" :key="groups">
                    <tr v-for="(row, index) in groups.rules" :key="index">
                      <th scope="row">{{ index + 1 }}</th>
                      <td>{{ groups.name }}</td>
                      <td><a href="#"  @click.prevent="showModal(index + 1)"   >{{ row.alert }}</a></td>
                      <td>
                        <div class="form-check form-switch mb-2">
                          <input class="form-check-input" type="checkbox" :checked="row.labels._trix_status !== false" @click="update_configuration('status', $event.target, index + 1, base64String(row));" id="rule_status">
                          <label class="form-check-label" for="rule_status" :id="`#rule_status_text_${index + 1}`">{{ row.labels._trix_status ? 'ON' : 'OFF' }}</label>
                        </div>
                      </td>
                      <td>
                        <div class="form-check form-switch mb-2">
                          <input class="form-check-input" @click="update_configuration('nhc', $event.target, index + 1, base64String(row));" type="checkbox" id="rule_nhc" :checked="row.labels.nhc === 'yes'">
                          <label class="form-check-label" for="rule_nhc" :id="`rule_nhc_text_${index + 1}`">{{ row.labels.nhc === 'yes' ? 'ON' : 'OFF' }}</label>
                        </div>
                      </td>
                      <td>
                        <select :id="`severity_${index + 1}`" @click="update_configuration('severity', $event.target, index + 1, base64String(row));" v-model="row.labels.severity" :class="['form-select', 'form-select-sm', row.labels.severity === 'critical' ? 'btn-dark' : 'btn-' + row.labels.severity]">
                          <option class="btn-primary" value="">Set Priority</option>
                          <option class="btn-dark" value="critical" :selected="row.labels.severity === 'critical'">Critical</option>
                          <option class="btn-danger" value="danger" :selected="row.labels.severity === 'danger'">Danger</option>
                          <option class="btn-warning" value="warning" :selected="row.labels.severity === 'warning'">Warning</option>
                          <option class="btn-info" value="info" :selected="row.labels.severity === 'info'">Informational</option>
                        </select>
                      </td>
                      <td>
                        <div style="display: inline-block;" class="tooltip-wrapper" data-bs-toggle="tooltip" data-bs-html="true" data-bs-original-title="<i class='bx bxs-arrow-from-left bx-xs'></i> <span>Edit This Rule</span>">
                          <button class="tooltip-modal-link" id="actions" :data-bs-target="`#rule_modal_${index + 1}`" data-bs-toggle="modal">
                            <box-icon name='edit' color="#696cff" size="md"></box-icon>
                          </button>
                        </div>
                        <button style="display: inline-block;" class="tooltip-modal-link" @click="update_configuration('delete', $event.target, index + 1, base64String(row));" id="actions" data-bs-toggle="tooltip" data-bs-offset="0,4" data-bs-placement="top" data-bs-html="true" data-bs-original-title="<i class='bx bxs-arrow-from-left bx-xs'></i> <span>Delete This Rule</span>">
                          <box-icon name='trash' color="red" size="md" ></box-icon>
                        </button>
                        <RuleModals
                          :update_configuration="update_configuration"
                          :base64String="base64String"
                          :currentMode="currentMode"
                          :rule_modal_html="rule_modal_html"
                          :rule_modal_json="rule_modal_json"
                          :rule_modal_yaml="rule_modal_yaml"
                          :ruleRow = "ruleRow"
                          :row = "row"
                          :index = index
                           />
                      </td>


                    </tr>
                  </tbody>






                </table>
              </div>
            </div>
          </div>
          <!--/ Bordered Table -->
        </div>
        <!-- / Content -->
        <FooterBar />
        <div class="content-backdrop fade"></div>
      </div>
    </div>
    <div class="layout-overlay layout-menu-toggle"></div>
  </div>








  <div v-if="showSuccessToast" class="bs-toast toast toast-placement-ex m-2 fade bg-success top-0 end-0 show" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="2000">
    <div class="toast-header">
      <i class="bx bx-bell me-2"></i>
      <div class="me-auto fw-medium">Configuration</div>
      <small>0 seconds ago</small>
      <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>
    <div class="toast-body">Configuration Saved successfully.</div>
  </div>

  <div v-if="showfailedToast" class="bs-toast toast toast-placement-ex m-2 fade bg-danger top-0 end-0 show" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="2000">
    <div class="toast-header">
      <i class="bx bx-bell me-2"></i>
      <div class="me-auto fw-medium">Configuration</div>
      <small>0 seconds ago</small>
      <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>
    <div class="toast-body">{{ toastMessage }}</div>
  </div>

  <div v-if="showwarningToast" class="bs-toast toast toast-placement-ex m-2 fade bg-warning top-0 end-0 show" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="2000">
    <div class="toast-header">
      <i class="bx bx-bell me-2"></i>
      <div class="me-auto fw-medium">Configuration</div>
      <small>0 seconds ago</small>
      <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>
    <div class="toast-body"></div>
  </div>


  <div>
    <div v-for="count in editorCount" :key="count" :id="`ruleEditor_${count}`" class="editor"></div>
  </div>



</template>

<!-- <style lang="css">
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background-color: #fff;
  padding: 20px;
  border-radius: 5px;
}
</style> -->
<script lang="ts">

import { ref, onMounted, onBeforeUnmount, reactive } from 'vue';
import { EditorState } from '@codemirror/state';
import { javascript } from '@codemirror/lang-javascript';
import { oneDark } from '@codemirror/theme-one-dark';
import {basicSetup} from 'codemirror';
import {EditorView} from '@codemirror/view';
import jsyaml from 'js-yaml';
import axios from 'axios';
// import { bootstrap, Modal, } from 'bootstrap/dist/js/bootstrap.bundle.min.js';
// import { bootstrap, Modal } from 'bootstrap';
// console.log(bootstrap.Modal);
// console.log(bootstrap.Modal);

interface TableRow {
  id: number;
  group: string;
  alert: string;
  description: string;
  btoa_rule: string;
  for: string;
  expr: string;
  _trix_status: boolean;
  nhc: string;
  severity: string;
}
const tableRows = ref<TableRow[]>([]);
let add_count = 0;

const isChecked = ref(false);
const isCheckedNHC = ref("no");
const selectedClass = ref('btn-primary');
const classMap = {
  critical: 'btn-dark',
  danger: 'btn-danger',
  warning: 'btn-warning',
  info: 'btn-info',
}

function updateClass(event) {
  const value = event.target.value;
  selectedClass.value = classMap[value] || 'btn-primary'; // Default to primary if no match
}

let url = window.location.href;
url = url.replace('#', '');
url = 'http://vmware-controller1.cluster:7755';

async function fetchRules(url: URL) {
  console.log(url);
  const response = await axios.get(url + '/get_rules');
  return response.data;
}

let configuration = await fetchRules(url);

console.log(configuration);

const ruleRow = (row: any, mode: string) => {
  let response;
  const rule = {
    "alert": row.alert,
    "annotations": {
      "description": row.description
    },
    "for": row.for,
    "expr": row.expr,
    "labels": {
      "_trix_status": row._trix_status,
      "nhc": row.nhc,
      "severity": row.severity
    }

  };
  if (mode === "JSON"){
    response = JSON.stringify(rule, null, 2);
  } else if (mode === "YAML"){
    response = jsyaml.dump(rule);
}
  return response;
};




export default {

  components: {
    PromQLEditor,
    SubNavigation,
  },


  data() {

    return {
      // configuration: null,
      configuration,
      activeButton: 1,
      previousButton: null,
      // showModal: false,
      // uniqueModal: null,
      showSuccessToast: false,
      showfailedToast: false,
      toastMessage: '',
      showwarningToast: false,
      Content: JSON.stringify(configuration, null, 2),
      // Content: JSON.stringify({"key": "value"}, null, 2),
      ContentType: "JSON",
      // CodeMirrorEditor,
      // yamlContent: jsyaml.dump(configuration),
    };
  },
  async mounted() {
    try {
      // configuration = await fetchRules(url);
      // const response = await axios.get(url+ '/get_rules');
      let count = 1;
      // console.log(configuration);
      // console.log(response.data);
      // console.log('{\n  "key": "value"\n}');
      // console.log(JSON.stringify(fetchRules(url)));
      // response.data.groups.forEach((group) => {
      configuration.groups.forEach((group) => {
        group.rules.forEach((rule) => {
          const row: TableRow = {
            id: count,
            group: group.name,
            alert: rule.alert,
            description: rule.annotations.description,
            for: rule.for,
            expr: rule.expr,
            btoa_rule: btoa(JSON.stringify(rule)),
            _trix_status: rule.labels._trix_status,
            nhc: rule.labels.nhc,
            severity: rule.labels.severity,
          }
          tableRows.value.push(row);
          console.log(row);

          count++;
        })
      })
      add_count = count + 1;
      // console.log(count);
      // console.log(add_count);

    //   const modalTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="modal"]'));
    // const modalList = modalTriggerList.map(modalTriggerEl => new bootstrap.Modal(modalTriggerEl));
    // console.log(modalTriggerList);
    // console.log(modalList);


      // const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
      // const tooltipList = tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

      // const modalTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="modal"]'))
      // const modalList = modalTriggerList.map(modalTriggerEl => new bootstrap.Modal(modalTriggerEl))


    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {

    }
  },
  methods: {
//     showModal(id:string) {
//       console.log(id);
//       const dymodal  = document.getElementById(`rule_modal_${id}`);
//       console.log(dymodal);
//       // this.uniqueModal = new bootstrap.Modal(document.getElementById(`rule_modal_${id}`), {
//         this.uniqueModal = new Modal(document.getElementById(`rule_modal_${id}`), {
//         backdrop: true
// });
//       console.log( this.uniqueModal);
//       this.uniqueModal.show();
//     },

    successToast() {
      this.showSuccessToast = true;
      setTimeout(() => {
        this.showSuccessToast = false;
      }, 2000);
    },

    failedToast(message) {
      this.toastMessage = message;
      this.showfailedToast = true;
      setTimeout(() => {
        this.showfailedToast = false;
      }, 2000);
    },

    warningToast() {
      this.showwarningToast = true;
      setTimeout(() => {
        this.showwarningToast = false;
      }, 2000);
    },

    // clearTable() {
    //   this.tableRows = [];
    //   this.$refs.modalContainer.innerHTML = '';
    // },

    // openModal() {
    //   this.showModal = true;
    //   this.$nextTick(() => {
    //     const parentElement = document.querySelector('.promql');
    //     console.log(this.showModal);
    //     console.log(parentElement);
    //   });
    // },

    // ... methods to show other toasts
  },
};





// // Reactive storage for multiple editors
// const editorInstances = ref<Map<number, EditorView>>(new Map());
// const editorCount = ref<number[]>([1, 2]); // Example: Two editors (IDs: ruleEditor_1, ruleEditor_2)

// // Function to initialize or update an editor
// const setupEditor = (count: number, content: string, mode: any) => {
//   const editorId = `ruleEditor_${count}`;
//   const editorElement = document.getElementById(editorId);

//   if (!editorElement) {
//     console.error(`Editor container with ID '${editorId}' not found.`);
//     return;
//   }

//   if (!editorInstances.value.has(count)) {
//     // Initialize a new CodeMirror instance
//     const state = EditorState.create({
//       doc: content,
//       extensions: [basicSetup, oneDark, mode],
//     });

//     const editor = new EditorView({
//       state,
//       parent: editorElement,
//     });

//     editorInstances.value.set(count, editor);
//   } else {
//     // Update existing editor instance
//     const editor = editorInstances.value.get(count);
//     if (editor) {
//       const state = EditorState.create({
//         doc: content,
//         extensions: [basicSetup, oneDark, mode],
//       });
//       editor.setState(state);
//     }
//   }
//   return editorInstances.value.get(count) || null;
// };

// // Function to open an editor by count
// const openEditor = (count: number) => {
//   const editorId = `ruleEditor_${count}`;
//   const editorContainer = document.getElementById(editorId);

//   // Ensure container visibility
//   if (editorContainer) {
//     editorContainer.style.display = 'block';
//     editorContainer.style.height = '300px';
//     editorContainer.style.width = '100%';
//   } else {
//     console.error('Editor container not found for count:', count);
//     return null;
//   }

//   if (editorInstances.value.has(count)) {
//     const editor = editorInstances.value.get(count);
//     if (editor) {
//       editor.focus(); // Focus the editor for usability
//       return editor;
//     }
//   }

//   // If the editor doesn't exist, set it up
//   return setupEditor(count, '', javascript());
// };

// // Lifecycle hooks
// onMounted(() => {

//   const uniqueModal = ref<Modal | null>(null);

//     const showModal = (id: string) => {
//       console.log(id);
//       const dymodal = document.getElementById(`rule_modal_${id}`);
//       console.log(dymodal);

//       if (dymodal) {
//         uniqueModal.value = new Modal(dymodal, {
//           backdrop: true,
//         });
//         uniqueModal.value.show();
//         console.log(uniqueModal.value);
//       } else {
//         console.error(`Modal with ID rule_modal_${id} not found`);
//       }
//     };
//   });

  // const dymodal = document.getElementById(`rule_modal_${id}`);
  // console.log(dymodal);
  // Example: Setup and open editors for the existing counts
  // editorCount.value.forEach((count) => openEditor(count));


  // const tooltipLinks = document.querySelectorAll('.tooltip-modal-link');
  // tooltipLinks.forEach(link => {
  //   new bootstrap.Tooltip(link); // This will work after the type installation
  // });


// onBeforeUnmount(() => {
//   // Clean up editor instances
//   editorInstances.value.forEach((editor) => editor.destroy());
//   editorInstances.value.clear();
// });

function update_configuration(key, element, count, form_rule) {
  console.log(key);
  console.log(element);
  console.log(count);
  console.log(form_rule);
}

// const toastMessage = ref<string>(''); // Reactive toast message
// const showToast = ref<boolean>(false); // Reactive visibility state for the toast

// const displayToast = (message: string) => {
//   toastMessage.value = message;
//   showToast.value = true;

//   // Automatically hide the toast after 10 seconds
//   setTimeout(() => {
//     showToast.value = false;
//   }, 10000);
// };



// const formValues = reactive<Record<number, any>>({});

// function getLatestValues(count: number) {
//   return {
//     alert: formValues[count]?.ruleName || '',
//     annotations: { description: formValues[count]?.description || '' },
//     for: formValues[count]?.ruleFor || '',
//     expr: formValues[count]?.expr || '',
//     labels: {
//       _trix_status: formValues[count]?.ruleStatus || false,
//       nhc: formValues[count]?.nhc ? 'yes' : 'no',
//       severity: formValues[count]?.severity || '',
//     },
//   };
// }


// function setupEventListeners(count: number) {
//   const updateFormValues = (key: string, value: any) => {
//     if (!formValues[count]) {
//       formValues[count] = {};
//     }
//     formValues[count][key] = value;
//   };

//   // Attach Vue event listeners in your component's template for `v-model` bindings:
//   // Example: `<input v-model="formValues[count].ruleName" />`
// }



// function setupHTML(count: number, jsonData: any) {
//   if (!formValues[count]) {
//     formValues[count] = {};
//   }

//   formValues[count].ruleName = jsonData.alert || '';
//   formValues[count].description = jsonData.annotations?.description || '';
//   formValues[count].ruleFor = jsonData.for || '';
//   formValues[count].expr = jsonData.expr || '';
//   formValues[count].ruleStatus = jsonData.labels?._trix_status || false;
//   formValues[count].nhc = jsonData.labels?.nhc === 'yes';
//   formValues[count].severity = jsonData.labels?.severity || '';
// }



// function rule_modal_html(count: number, buttonNumber: number) {
//   const jsonData = jsyaml.load(editorInstances.value[count].state.doc.toString());
//   setupHTML(count, jsonData);
//   activeButton.value = buttonNumber;
// }


// function rule_modal_json(count: number, buttonNumber: number) {
//   if (previousButton.value === 1) {
//     const content = getLatestValues(count);
//     setupEditor(count, JSON.stringify(content, null, 2), javascript());
//   } else {
//     const jsonData = jsyaml.load(editorInstances.value[count].state.doc.toString());
//     setupEditor(count, JSON.stringify(jsonData, null, 2), javascript());
//   }
//   activeButton.value = buttonNumber;
// }


// function rule_modal_yaml(count: number, buttonNumber: number) {
//   if (previousButton.value === 1) {
//     const content = getLatestValues(count);
//     const yamlContent = jsyaml.dump(content);
//     setupEditor(count, yamlContent, 'yaml');
//   } else {
//     try {
//       const currentContent = editorInstances.value[count].state.doc.toString();
//       const jsonData = JSON.parse(currentContent);
//       const yamlContent = jsyaml.dump(jsonData);
//       setupEditor(count, yamlContent, 'yaml');
//     } catch (e) {
//       const currentContent = editorInstances.value[count].state.doc.toString();
//       setupEditor(count, currentContent, 'yaml');
//     }
//   }
//   activeButton.value = buttonNumber;
// }

// document.addEventListener('DOMContentLoaded', () => {
//   const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
//   tooltipTriggerList.forEach((tooltipTriggerEl) => {
//     new bootstrap.Tooltip(tooltipTriggerEl);
//   });
// });
</script>
