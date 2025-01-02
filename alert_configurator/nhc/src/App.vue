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
            <div class="spinner-border spinner-border-lg text-success" style="width: 10rem; height: 10rem" role="status">
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
                <RuleModals
                  :promQLurl = "promQLurl"
                  :configuration="configuration"
                  :save_configuration = "save_configuration"
                  :updateClass = "updateClass"
                  :base64String="base64String"
                  :ruleRow = "ruleRow"
                  :row = "{'alert': '', 'annotations': {'description': ''}, 'for': '', 'expr': '', 'labels': {'_trix_status': false, 'nhc': 'no', 'severity': 'info'}}"
                  :index = 0
                  :selectedClass="selectedClass"
                  @Toast="Toast"
                />
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
                      <td>
                        <a href="#"  @click.prevent="showModal(index + 1)">{{ row.alert }}</a>
                        <input type="hidden" :id="`rule_name_${index + 1}`" :value="`${row.alert}`" />
                        <input type="hidden" :id="`rule_description_${index + 1}`" :value="`${row.annotations.description}`" />
                        <input type="hidden" :id="`rule_for_${index + 1}`" :value="`${row.for}`" />
                        <input type="hidden" :id="`editor_${index + 1}`" :value="`${row.expr}`" />
                      </td>
                      <td>
                        <div class="form-check form-switch mb-2">
                          <input class="form-check-input" type="checkbox" v-model="row.labels._trix_status" @click="update_configuration(index + 1);" :id="`rule_status_${index + 1}`" />
                          <label class="form-check-label" :for="`rule_status_${index + 1}`">{{ row.labels._trix_status ? 'ON' : 'OFF' }}</label>
                        </div>
                      </td>
                      <td>
                        <div class="form-check form-switch mb-2">
                          <input class="form-check-input" type="checkbox" v-model="row.labels.nhc" @click="update_configuration(index + 1);" :id="`rule_nhc_${index + 1}`" data-toggle="switch" :true-value="'yes'" false-value="no" />
                          <label class="form-check-label" :for="`rule_nhc_${index + 1}`">{{ row.labels.nhc === 'yes' ? 'ON' : 'OFF' }}</label>
                        </div>
                      </td>
                      <td>
                        <select :id="`severity_${index + 1}`" @change="update_configuration(index + 1);" v-model="row.labels.severity" :class="['form-select', 'form-select-sm', row.labels.severity === 'critical' ? 'btn-dark' : 'btn-' + row.labels.severity]">
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
                        <button style="display: inline-block;" class="tooltip-modal-link" @click.prevent="deleteRule(index);" id="actions" data-bs-toggle="tooltip" data-bs-offset="0,4" data-bs-placement="top" data-bs-html="true" data-bs-original-title="<i class='bx bxs-arrow-from-left bx-xs'></i> <span>Delete This Rule</span>">
                          <box-icon name='trash' color="red" size="md" ></box-icon>
                        </button>
                        <RuleModals
                          :promQLurl = "promQLurl"
                          :configuration="configuration"
                          :save_configuration = "save_configuration"
                          :updateClass = "updateClass"
                          :base64String="base64String"
                          :ruleRow = "ruleRow"
                          :row = "row"
                          :index = index+1
                          :selectedClass="selectedClass"
                          @Toast="Toast"
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

import { ref, onMounted, reactive, toRaw } from 'vue';
import jsyaml from 'js-yaml';
import axios from 'axios';

const selectedClass = ref('btn-primary');
const classMap = {
  critical: 'btn-dark',
  danger: 'btn-danger',
  warning: 'btn-warning',
  info: 'btn-info',
} as const;
type ClassMapKey = keyof typeof classMap;

function updateClass(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target && target.value) {
    const value: ClassMapKey = target.value as ClassMapKey;
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

let configurationData = await fetchRules();
let configuration = reactive(configurationData);

async function saveRules(content: JSON) {
  try {
    const response = await axios.post(url + '/save_config', content);
    // console.log(url + '/save_config');
    // console.log(content);
    // console.log(response.status);
    // console.log(response.data.response);
    return {"status": response.status, "message": response.data.response};
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      return {
        status: error.response?.status || 500,
        message: error.response?.data || 'An error occurred during the request.',
      };
    } else {
      return {
        status: 500,
        message: 'An unknown error occurred.',
      };
    }
  }
}

interface RuleRow {
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

const ruleRow = (row: RuleRow, mode: string) => {
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

const ContentType: 'JSON' | 'YAML' = 'JSON';


export default {
  components: {
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
      ContentType,
    };
  },
  methods: {

    Toast(message: unknown, toastClass: string) {
      this.showToast = true;
      if (typeof message === 'string') {
        this.toastMessage = message;
        this.toastClass = toastClass;
      } else if (typeof message === 'object' && message !== null && 'message' in message && 'toastClass' in message) {
        this.toastMessage = (message as { message: string }).message;
        this.toastClass = (message as { toastClass: string }).toastClass;
      } else {
        this.toastMessage = 'Unknown message: '+message;
        this.toastClass = 'bg-dark';
      }
      setTimeout(() => {
        this.showToast = false;
      }, 2000);
    },

    deleteRule(count: number) {
      configuration.groups[0].rules.splice(count, 1);
      this.save_configuration(configuration, 'On Page')
    },

    update_configuration(count: number) {
      let status: any;
      let nhc: any;
      let severity: any;

      const alertElement = document.getElementById(`rule_name_${count}`);
      const alert = (alertElement as HTMLInputElement).value;

      const descriptionElement = document.getElementById(`rule_description_${count}`);
      const description = (descriptionElement as HTMLInputElement).value;

      const forElement = document.getElementById(`rule_for_${count}`);
      const for_val = (forElement as HTMLInputElement).value;

      const exprElement = document.getElementById(`editor_${count}`);
      const expr = (exprElement as HTMLInputElement).value;


      const statusElement = document.getElementById(`rule_status_${count}`);
      if (statusElement) { status = (statusElement as HTMLInputElement).checked; }

      const nhcElement = document.getElementById(`rule_nhc_${count}`);
      if (nhcElement) {
        nhc = (nhcElement as HTMLInputElement).checked;
        if(nhc === true){ nhc = 'yes'; } else { nhc = 'no'; }
      }

      const severityElement = document.getElementById(`severity_${count}`);
      if (severityElement) { severity = (severityElement as HTMLInputElement).value; }

      configuration.groups[0].rules[count - 1].alert                    = alert;
      configuration.groups[0].rules[count - 1].annotations.description  = description;
      configuration.groups[0].rules[count - 1].for                      = for_val;
      configuration.groups[0].rules[count - 1].expr                     = expr;
      configuration.groups[0].rules[count - 1].labels._trix_status      = status;
      configuration.groups[0].rules[count - 1].labels.nhc               = nhc;
      configuration.groups[0].rules[count - 1].labels.severity          = severity;


      // const rule: RuleRow = {
      //   'alert': configuration.groups[0].rules[count - 1].alert,
      //   'annotations': {'description': configuration.groups[0].rules[count - 1].annotations.description},
      //   'for': configuration.groups[0].rules[count - 1].for,
      //   'expr': configuration.groups[0].rules[count - 1].expr,
      //   'labels': {
      //     '_trix_status': status,
      //     'nhc': nhc,
      //     'severity': severity,
      //   }
      // };


      // console.log(rule);
      this.save_configuration(configuration, 'On Page')
    },

    async save_configuration(newContent: string, modalID: string) {
      let content;
      if (typeof newContent === 'object'){
        newContent = toRaw(newContent);
        content = JSON.stringify(newContent);
      } else { content = newContent; }

      try {
        content = jsyaml.load(content);
      } catch(YAMLerror: unknown){
        if (YAMLerror instanceof Error) {
          this.Toast(this.toastMessage=YAMLerror.message, this.toastClass='bg-danger');
        } else {
          this.Toast(this.toastMessage='An unknown error occurred', this.toastClass='bg-danger');
        }
        try {
          content = JSON.parse(content);
        } catch(JSONerror: unknown){
          if (JSONerror instanceof Error) {
            this.Toast(this.toastMessage= JSONerror.message, this.toastClass='bg-danger');
          } else {
            this.Toast(this.toastMessage='An unknown error occurred', this.toastClass='bg-danger');
          }
          content = false;
        }
      }

      console.log(content);
      console.log(typeof content);
      if (content){
        const response = await saveRules(content);
        this.toastMessage = response.message;
        if (response.status === 200){
          this.toastClass = "bg-success";
          const modal = document.getElementById(modalID);
          if (modal){
            const bootstrapModal = Modal.getInstance(modal);
            bootstrapModal?.hide();
          } else {
            // this.Toast(this.toastMessage=`Modal with ID '${modalID}' not found.`, this.toastClass='bg-danger');
          }
        } else if (response.status === 400){
          this.toastClass = "bg-warning";
        } else{
          this.toastClass = "bg-danger";
        }
        this.Toast(this.toastMessage, this.toastClass);
      }
  }

  },
};

</script>
