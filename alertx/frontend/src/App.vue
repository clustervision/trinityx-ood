<script setup lang="ts">

import 'boxicons'
import './assets/css/core.css';
import './assets/css/theme-default.css';
import './assets/css/app.css';
import './assets/js/main.js';

import TopNavigation from '@/views/TopNavigation.vue';
import SubNavigation from '@/views/SubNavigation.vue';
import FooterBar from '@/views/FooterBar.vue';
import RuleModals from './components/RuleModals.vue';
import { Modal } from 'bootstrap';

const promQLurl = ref(window.PROMQL_URL || import.meta.env.VITE_PROMQL_URL);
const rulesFile = ref("/trinity/local/etc/prometheus_server/rules/trix.rules");
const uniqueModal = ref<Modal | null>(null);

const showModal = (id: number) => {
  const dymodal = document.getElementById(`rule_modal_${id}`);
  if (dymodal) {
    uniqueModal.value = new Modal(dymodal, {
      backdrop: true,
    });
    uniqueModal.value.show();
  } else {
    console.error(`Modal with ID rule_modal_${id} not found`);
  }
};

onMounted(() => {
});

const base64String = (row: string) => {
  const encodedData = btoa(JSON.stringify(row));
  return encodedData;
};
</script>

<style lang="css">
.spinner-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.8);
  z-index: 1050; /* Ensure it appears above other elements */
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-link .icon-color {
  fill: white; /* Default icon color for inactive tabs */
}

.nav-link.active .icon-color {
  fill: white; /* Icon color for active tabs */
}


.d-none {
  color:  white;
}


.nav-pills .nav-link.active, .nav-pills .nav-link.active:hover, .nav-pills .nav-link.active:focus {
  font-weight: bold;
}







.tab-bar {
    background-color: #563d7c;
    position: relative;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
}

.manage-li{
  color: white;
  padding-left: 1rem;
  padding-right: 1rem;
}

</style>

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
        <div v-if="showSpinner" id="spinner-overlay" class="spinner-overlay">
          <div id="spinner" class="d-flex justify-content-center">
            <div class="spinner-border spinner-border-lg text-success" style="width: 10rem; height: 10rem" role="status">
              <span class="visually-hidden">Saving Configuration...</span>
            </div>
          </div>
        </div>





      <div class="row">
        <div class="col-xl-12">
        <div class="nav-align-top mb-6">
          <ul class="nav nav-pills mb-4 nav-fill tab-bar" role="tablist">
            <li class="manage-li">
              <span class="d-none d-sm-block align-text-bottom">Manage Node Health Checks</span>
            </li>
            <li class="nav-item mb-1 mb-sm-0" role="presentation">
              <button type="button" class="nav-link active" role="tab" data-bs-toggle="tab" data-bs-target="#navs-pills-justified-home" aria-controls="navs-pills-justified-home" aria-selected="true">
                <span class="d-none d-sm-block"><box-icon name='stats' class="align-text-bottom icon-color"></box-icon> Status</span>
              </button>
            </li>
            <li class="nav-item mb-1 mb-sm-0" role="presentation">
              <button type="button" class="nav-link" role="tab" data-bs-toggle="tab" data-bs-target="#navs-pills-justified-profile" aria-controls="navs-pills-justified-profile" aria-selected="false" tabindex="-1">
                <span class="d-none d-sm-block"><box-icon name='bracket' class="align-text-bottom icon-color"></box-icon> Configuration</span>
              </button>
            </li>
            <li class="nav-item" role="presentation">
              <button type="button" class="nav-link" role="tab" data-bs-toggle="tab" data-bs-target="#navs-pills-justified-messages" aria-controls="navs-pills-justified-messages" aria-selected="false" tabindex="-1">
                <span class="d-none d-sm-block"><box-icon name='desktop' class="align-text-bottom icon-color"></box-icon> Node H/W</span>
              </button>
            </li>
          </ul>
          <div class="tab-content">
            <div class="tab-pane fade active show" id="navs-pills-justified-home" role="tabpanel">
              <p>
                Icing pastry pudding oat cake. Lemon drops cotton candy caramels cake caramels sesame snaps powder. Bear
                claw
                candy topping.
              </p>
              <p class="mb-0">
                Tootsie roll fruitcake cookie. Dessert topping pie. Jujubes wafer carrot cake jelly. Bonbon jelly-o
                jelly-o ice
                cream jelly beans candy canes cake bonbon. Cookie jelly beans marshmallow jujubes sweet.
              </p>
            </div>
            <div class="tab-pane fade" id="navs-pills-justified-profile" role="tabpanel">
              <p>
                Donut dragée jelly pie halvah. Danish gingerbread bonbon cookie wafer candy oat cake ice cream. Gummies
                halvah
                tootsie roll muffin biscuit icing dessert gingerbread. Pastry ice cream cheesecake fruitcake.
              </p>
              <p class="mb-0">
                Jelly-o jelly beans icing pastry cake cake lemon drops. Muffin muffin pie tiramisu halvah cotton candy
                liquorice caramels.
              </p>
            </div>
            <div class="tab-pane fade" id="navs-pills-justified-messages" role="tabpanel">
              <p>
                Oat cake chupa chups dragée donut toffee. Sweet cotton candy jelly beans macaroon gummies cupcake gummi
                bears
                cake chocolate.
              </p>
              <p class="mb-0">
                Cake chocolate bar cotton candy apple pie tootsie roll ice cream apple pie brownie cake. Sweet roll icing
                sesame snaps caramels danish toffee. Brownie biscuit dessert dessert. Pudding jelly jelly-o tart brownie
                jelly.
              </p>
            </div>
          </div>
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
                  <tbody v-for="(groups, groupsIndex) in configuration.groups" :key="groups.name">
                    <tr v-for="(row, index) in groups.rules" :key="index">
                      <th scope="row">{{ index + 1 }}</th>
                      <td>{{ groups.name }}</td>
                      <td>
                        <a href="#"  @click.prevent="showModal(index + 1)">{{ row.alert }}</a>
                        <input type="hidden" :id="`group_name_${groupsIndex + 1}`" :value="`${groups.name}`" />
                        <input type="hidden" :id="`rule_name_${index + 1}`" :value="`${row.alert}`" />
                        <input type="hidden" :id="`rule_description_${index + 1}`" :value="`${row.annotations.description}`" />
                        <input type="hidden" :id="`rule_for_${index + 1}`" :value="`${row.for}`" />
                        <input type="hidden" :id="`rule_editor_${index + 1}`" :value="`${row.expr}`" />
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
                          :configuration = "configuration"
                          :save_configuration = "save_configuration"
                          :updateClass = "updateClass"
                          :base64String = "base64String"
                          :ruleRow = "ruleRow"
                          :row = "row"
                          :index = index+1
                          :selectedClass = "selectedClass"
                          @Toast = "Toast"
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
url = window.APP_URL || import.meta.env.VITE_APP_URL;

async function saveRules(content: JSON) {
  try {
    const response = await axios.post(url + '/save_config', content);
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
interface Configuration {
  groups: Array<{
    name: string;
    rules: Array<{
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
    }>;
  }>;
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
      configuration: reactive<Configuration>({ groups: [] }),
      activeButton: 1,
      previousButton: null,
      Content: JSON.stringify({}, null, 2),
      ContentType,
      showSpinner: false,
    };
  },
  async created() {
    await this.fetchRules();
  },

  methods: {

    async fetchRules() {
      const response = await axios.get(url + '/get_rules');
      this.configuration =  reactive(response.data);
      this.configuration = { ...this.configuration };
      this.Content = JSON.stringify({ ...this.configuration }, null, 2);
      return this.configuration;
    },

    Toast(message: unknown, toastClass: string) {
      this.showToast = true;
      this.showSpinner = true;
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
        this.showSpinner = false;
      }, 3000);

    },

    deleteRule(count: number) {
      this.configuration.groups[0].rules.splice(count, 1);
      this.save_configuration(this.configuration, 'On Page')
    },

    update_configuration(count: number) {
      let status: boolean = false;
      let nhc: string =  "no";
      let severity: string = "info";

      const alertElement = document.getElementById(`rule_name_${count}`);
      const alert = (alertElement as HTMLInputElement).value;

      const descriptionElement = document.getElementById(`rule_description_${count}`);
      const description = (descriptionElement as HTMLInputElement).value;

      const forElement = document.getElementById(`rule_for_${count}`);
      const for_val = (forElement as HTMLInputElement).value;

      const exprElement = document.getElementById(`rule_editor_${count}`);
      const expr = (exprElement as HTMLInputElement).value;


      const statusElement = document.getElementById(`rule_status_${count}`);
      if (statusElement) { status = (statusElement as HTMLInputElement).checked; }

      const nhcElement = document.getElementById(`rule_nhc_${count}`);
      if (nhcElement) {
        const nhc_value = (nhcElement as HTMLInputElement).checked;
        if(nhc_value === true){ nhc = 'yes'; } else { nhc = 'no'; }
      }

      const severityElement = document.getElementById(`severity_${count}`);
      if (severityElement) { severity = (severityElement as HTMLInputElement).value; }

      this.configuration.groups[0].rules[count - 1].alert                    = alert;
      this.configuration.groups[0].rules[count - 1].annotations.description  = description;
      this.configuration.groups[0].rules[count - 1].for                      = for_val;
      this.configuration.groups[0].rules[count - 1].expr                     = expr;
      this.configuration.groups[0].rules[count - 1].labels._trix_status      = status;
      this.configuration.groups[0].rules[count - 1].labels.nhc               = nhc;
      this.configuration.groups[0].rules[count - 1].labels.severity          = severity;

      this.save_configuration(this.configuration, 'On Page')
    },

    async save_configuration(newContent: unknown, modalID: string) {
      let content: unknown;
      if (typeof newContent === 'object'){
        newContent = toRaw(newContent);
        content = JSON.stringify(newContent);
      } else { content = newContent; }

      try {
        content = jsyaml.load(content as string);
      } catch(YAMLerror: unknown){
        if (YAMLerror instanceof Error) {
          this.Toast(this.toastMessage=YAMLerror.message, this.toastClass='bg-danger');
        } else {
          this.Toast(this.toastMessage='An unknown error occurred', this.toastClass='bg-danger');
        }
        try {
          content = JSON.parse(content as string);
        } catch(JSONerror: unknown){
          if (JSONerror instanceof Error) {
            this.Toast(this.toastMessage= JSONerror.message, this.toastClass='bg-danger');
          } else {
            this.Toast(this.toastMessage='An unknown error occurred', this.toastClass='bg-danger');
          }
          content = false;
        }
      }


      if (content){
        const response = await saveRules(content as JSON);
        this.toastMessage = response.message;
        if (response.status === 200){
          this.toastClass = "bg-success";
          const modal = document.getElementById(modalID);
          if (modal){
            const bootstrapModal = Modal.getInstance(modal);
            bootstrapModal?.hide();
          }
          this.fetchRules();
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
