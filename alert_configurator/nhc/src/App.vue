<script setup lang="ts">

import 'boxicons'
import './assets/css/core.css';
import './assets/css/theme-default.css';
import './assets/css/app.css';
import './assets/js/main.js';
// import './assets/js/app.js';

import TopNavigation from '@/views/TopNavigation.vue';
import SubNavigation from '@/views/SubNavigation.vue';
import FooterBar from '@/views/FooterBar.vue';
import PromQLEditor from '@/components/PromQLEditor.vue';
import RuleModals from './components/RuleModals.vue';

import { Modal } from 'bootstrap';


const promQLurl = ref("https://vmware-controller1.cluster:9090");
const rulesFile = ref("/trinity/local/etc/prometheus_server/rules/trix.rules");
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
    // console.log(uniqueModal.value);
  } else {
    console.error(`Modal with ID rule_modal_${id} not found`);
  }
};

onMounted(() => {
  // console.log('App mounted, ready for modals!');
});

const currentMode = ref<'HTML' | 'JSON' | 'YAML'>('HTML');
const rule_modal_html = (id: number, mode: number) => {
  currentMode.value = 'HTML';
};

const rule_modal_json = (id: number, mode: number) => {
  currentMode.value = 'JSON';
};

const rule_modal_yaml = (id: number, mode: number) => {
  currentMode.value = 'YAML';
};

const base64String = (row: string) => {
  const encodedData = btoa(JSON.stringify(row));
  return encodedData;
};
</script>


<template>

  <header>
    <TopNavigation />
    <SubNavigation
      :rulesFile = "rulesFile"
      :save_configuration = "save_configuration"
      :Content="Content"
      :ContentType="ContentType"
      @Toast="Toast"
    />
  </header>

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
                            </div>
                            <div class="row">
                              <div class="col mb-6">
                                <label for="exprInput_0" class="form-label">Rule Expr</label>
                                <PromQLEditor :promQLurl="promQLurl" editor-id="editor_0" editor-rule=""><div class="promql"></div></PromQLEditor>
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
                          <button type="button" @click="add_rule('save', $event.target, 0, 'save');" class="btn btn-primary">Save Rule</button>
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
                        <!-- :currentMode="currentMode" -->
                        <RuleModals
                          :promQLurl = "promQLurl"
                          :update_configuration="update_configuration"
                          :updateClass = "updateClass"
                          :base64String="base64String"

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
        </div>
        <FooterBar />
        <div class="content-backdrop fade"></div>
      </div>
    </div>
    <div class="layout-overlay layout-menu-toggle"></div>
  </div>


  <div v-if="showToast" :class="`bs-toast toast toast-placement-ex m-2 fade ${toastClass} top-0 end-0 show`" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="2000">
    <div class="toast-header">
      <i class="bx bx-bell me-2"></i>
      <div class="me-auto fw-medium">Configuration</div>
      <small>0 seconds ago</small>
      <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>
    <div class="toast-body">{{ toastMessage }}</div>
  </div>

</template>

<script lang="ts">

import { ref, onMounted } from 'vue';
import jsyaml from 'js-yaml';
import axios from 'axios';

const isChecked = ref(false);
const isCheckedNHC = ref("no");
const selectedClass = ref('btn-primary');
const classMap = {
  critical: 'btn-dark',
  danger: 'btn-danger',
  warning: 'btn-warning',
  info: 'btn-info',
}

function updateClass(event: Event) {
  if (event.target){
    const value = event.target.value;
    selectedClass.value = classMap[value] || 'btn-primary';
  }

}

let url: string
url = window.location.href;
url = url.replace('#', '');
url = 'http://vmware-controller1.cluster:7755';

async function fetchRules() {
  const response = await axios.get(url + '/get_rules');
  return response.data;
}

async function saveRules() {
  try {
    const response = await axios.post(url + '/save_config', configuration);
    return {"status": response.status, "message": response.data.response};
  } catch (error: unknown) {
    return {
      status: error.response?.status || 500,
      message: error.response?.data || 'An error occurred during the request.',
    };
  }
}

const configuration = await fetchRules();


// console.log(configuration);

const ruleRow = (row: any, mode: string) => {
  let response;
  const rule = {
    "alert": row.alert,
    "annotations": {
      "description": row.annotations.description
    },
    "for": row.for,
    "expr": row.expr,
    "labels": {
      "_trix_status": row.labels._trix_status,
      "nhc": row.labels.nhc,
      "severity": row.labels.severity
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
      showToast: false,
      toastClass: '',
      toastMessage: '',
      configuration,
      activeButton: 1,
      previousButton: null,
      Content: JSON.stringify(configuration, null, 2),
      ContentType: "JSON",
    };
  },
  methods: {

    Toast(message: unknown, toastClass: string) {
      this.showToast = true;
      if (typeof message === 'string') {
        this.toastMessage = message;
        this.toastClass = toastClass;
      } else {
        this.toastMessage = message.message;
        this.toastClass = message.toastClass;
      }
      setTimeout(() => {
        this.showToast = false;
      }, 2000);
    },


    update_configuration(key: string, element: Event, count: string, form_rule: string) {
      console.log(key);
      console.log(element);
      console.log(count);
      console.log(form_rule);
    },

    async save_configuration() {
      const response = await saveRules();
      this.toastMessage = response.message;
      if (response.status === 200){
        this.toastClass = "bg-success";
      } else if (response.status === 400){
        this.toastClass = "bg-warning";
      } else{
        this.toastClass = "bg-danger";
      }
      this.Toast(this.toastMessage, this.toastClass);
      console.log(response);

  }

  },
};

</script>
