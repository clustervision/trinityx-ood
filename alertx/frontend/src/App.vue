<script setup lang="ts">

import 'boxicons'
import './assets/core.css';
import './assets/theme-default.css';
import './assets/app.css';
import './assets/main.js';

import TopNavigation from '@/views/TopNavigation.vue';
import TabOverview from './views/TabOverview.vue';
import TabStatus from './views/TabStatus.vue';
import TabConfiguration from './views/TabConfiguration.vue';
import TabNodes from './views/TabNodes.vue';
import TabService from './views/TabService.vue';
import FooterBar from '@/views/FooterBar.vue';
import { Modal } from 'bootstrap';

const promQLurl = ref(window.PROMQL_URL || import.meta.env.VITE_PROMQL_URL);
const alertURL = ref(window.ALERT_URL || import.meta.env.VITE_ALERT_URL);
const statusAPI = promQLurl.value+'/api/v1/rules';
const GenericRulesFile = "/trinity/local/etc/prometheus_server/rules/trix.generic.rules";
const ServiceRulesFile = "/trinity/local/etc/prometheus_server/rules/trix.service.rules";

onMounted(() => {
});

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
    <TopNavigation :url = "url" />
  </header>
  <!-- <div class="container-xxl flex-grow-1 container-p-y">
    <div class="card"> -->

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

        <div class="col-xl-12">
        <div class="nav-align-top mb-6">
          <ul class="nav nav-pills mb-4 nav-fill tab-bar" role="tablist">
            <li class="nav-item mb-1 mb-sm-0" role="presentation">
              <button type="button" class="nav-link active" role="tab" data-bs-toggle="tab" data-bs-target="#tab-overview" aria-controls="tab-overview" aria-selected="true">
                <span class="d-none d-sm-block"><box-icon name='detail' class="align-text-bottom icon-color"></box-icon> Overview</span>
              </button>
            </li>
            <li class="nav-item mb-1 mb-sm-0" role="presentation">
              <button type="button" class="nav-link" role="tab" data-bs-toggle="tab" data-bs-target="#tab-alerts" aria-controls="tab-alerts" aria-selected="true">
                <span class="d-none d-sm-block"><box-icon name='stats' class="align-text-bottom icon-color"></box-icon> Alerts</span>
              </button>
            </li>
            <li class="nav-item mb-1 mb-sm-0" role="presentation">
              <button type="button" class="nav-link" role="tab" data-bs-toggle="tab" data-bs-target="#tab-rules" aria-controls="tab-rules" aria-selected="false" tabindex="-1">
                <span class="d-none d-sm-block"><box-icon name='bracket' class="align-text-bottom icon-color"></box-icon> Generic Rules</span>
              </button>
            </li>
            <li class="nav-item" role="presentation">
              <button type="button" class="nav-link" role="tab" data-bs-toggle="tab" data-bs-target="#tab-hardware" aria-controls="tab-hardware" aria-selected="false" tabindex="-1">
                <span class="d-none d-sm-block"><box-icon name='desktop' class="align-text-bottom icon-color"></box-icon> Node H/W</span>
              </button>
            </li>
            <li class="nav-item" role="presentation">
              <button type="button" class="nav-link" role="tab" data-bs-toggle="tab" data-bs-target="#tab-service" aria-controls="tab-service" aria-selected="false" tabindex="-1">
                <span class="d-none d-sm-block"><box-icon name='wrench' class="align-text-bottom icon-color"></box-icon> Services</span>
              </button>
            </li>
          </ul>
          <div class="tab-content">
            <div class="tab-pane fade active show" id="tab-overview" role="tabpanel">
              <TabOverview :url = "url" :alertURL = "alertURL" :statusAPI = "statusAPI" @update:showSpinner="updateShowSpinner" />
            </div>
            <div class="tab-pane fade" id="tab-alerts" role="tabpanel">
              <TabStatus :url = "url" :alertURL = "alertURL" :statusAPI = "statusAPI" @update:showSpinner="updateShowSpinner" />
            </div>
            <div class="tab-pane fade" id="tab-rules" role="tabpanel">
              <TabConfiguration
                :rulesFile = "GenericRulesFile"
                :save_configuration = "save_configuration"
                :update_configuration = "update_configuration"
                :Content="GenericContent"
                :ContentType="ContentType"
                @Toast="Toast"
                :url = "url"
                :promQLurl = "promQLurl"
                :configuration = "generic_config"
                :updateClass = "updateClass"
                :ruleRow = "ruleRow"
                :selectedClass = "selectedClass"
              />

            </div>
            <div class="tab-pane fade" id="tab-hardware" role="tabpanel">
              <TabNodes :url = "url" :promQLurl = "promQLurl" />
            </div>
            <div class="tab-pane fade" id="tab-service" role="tabpanel">
              <TabService
                :rulesFile = "ServiceRulesFile"
                :save_configuration = "save_configuration"
                :update_configuration = "update_configuration"
                :Content="ServiceContent"
                :ContentType="ContentType"
                @Toast="Toast"
                :url = "url"
                :promQLurl = "promQLurl"
                :configuration = "service_config"
                :updateClass = "updateClass"
                :ruleRow = "ruleRow"
                :selectedClass = "selectedClass"
              />
            </div>
          </div>
        </div>
      </div>


        <FooterBar :url = "url" />
        <div class="content-backdrop fade"></div>
      </div>
    </div>
    <div class="layout-overlay layout-menu-toggle"></div>
  </div>

<!-- </div>
</div> -->
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

const url = window.APP_URL || import.meta.env.VITE_APP_URL;

function deepClean(obj: unknown): unknown {
  if (Array.isArray(obj)) {
    return obj.map(deepClean).filter((item) => item !== null);
  } else if (obj !== null && typeof obj === "object") {
    return Object.fromEntries(
      Object.entries(obj)
        .filter(([, value]) => value !== null && value !== "null")
        .map(([key, value]) => [key, deepClean(value)])
    );
  }
  return obj;
}

async function saveRules(content: JSON) {
  const cleanedData = deepClean(content);
  try {
    const response = await axios.post(url + '/save_config', cleanedData);
    return {"status": response.status, "message": response.data.response};
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      console.log(error);
      return {
        status: error.response?.status || 500,
        message: error.response?.data.response || 'An error occurred during the request.',
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
        category: string;
        disabled: boolean;
        nhc: boolean;
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
    disabled: string;
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
      "disabled": row.labels.disabled,
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

  data() {
    return {
      showToast: false,
      toastClass: '',
      toastMessage: '',
      configuration: reactive<Configuration>({ groups: [] }),
      generic_config: reactive<Configuration>({ groups: [] }),
      service_config: reactive<Configuration>({ groups: [] }),
      activeButton: 1,
      previousButton: null,
      Content: JSON.stringify({}, null, 2),
      GenericContent: JSON.stringify({}, null, 2),
      ServiceContent: JSON.stringify({}, null, 2),
      ContentType,
      showSpinner: false,
    };
  },
  async created() {
    await this.fetchRules();
  },

  methods: {

    async fetchRules() {
      try {
        const response = await axios.get(url + '/get_rules');
        this.configuration =  reactive(response.data);
        this.configuration = { ...this.configuration };
        this.generic_config = this.splitConfiguration('generic');
        this.service_config = this.splitConfiguration('service');
        this.Content = JSON.stringify({ ...this.configuration }, null, 2);
        this.GenericContent = JSON.stringify({ ...this.generic_config }, null, 2);
        this.ServiceContent = JSON.stringify({ ...this.service_config }, null, 2);
      } catch (error: unknown) {
        if (axios.isAxiosError(error)) {
          this.toastMessage = error.response?.data.response || error.message;
        } else {
          this.toastMessage = 'An unknown error occurred.';
        }
        this.Toast(`ERROR :: While Getting Rules ${this.toastMessage}`, "bg-danger");
      }
      return this.configuration;
    },

    splitConfiguration(category: string) {
      return {
        groups: this.configuration.groups
          .map(group => ({
            ...group,
            rules: group.rules.filter(rule => rule.labels.category === category)
          }))
          // .filter(group => group.rules.length > 0)
      };
    },

    mergeConfigurations(generic_config: object, service_config: object) {
      const configuration = {
        groups: [
          {
            name: "trinityx",
            rules: [...(generic_config as Configuration).groups[0].rules, ...(service_config as Configuration).groups[0].rules]
          }
        ]
      };
      return configuration;
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

    updateShowSpinner(value: boolean){
      this.showSpinner = value;
    },

    update_configuration(configType:string, count: number) {
      let status: boolean =  false;
      let nhc: boolean =  false;
      let severity: string = "info";

      const alertElement = document.getElementById(`${configType}_rule_name_${count}`);
      const alert = (alertElement as HTMLInputElement).value;

      const descriptionElement = document.getElementById(`${configType}_rule_description_${count}`);
      const description = (descriptionElement as HTMLInputElement).value;

      const forElement = document.getElementById(`${configType}_rule_for_${count}`);
      const for_val = (forElement as HTMLInputElement).value;

      const exprElement = document.getElementById(`${configType}_rule_editor_${count}`);
      const expr = (exprElement as HTMLInputElement).value;

      const categoryElement = document.getElementById(`${configType}_rule_category_${count}`);
      const category = (categoryElement as HTMLInputElement).value;

      const statusElement = document.getElementById(`${configType}_rule_status_${count}`);
      if (statusElement) {
        const status_value = (statusElement as HTMLInputElement).checked;
        if(status_value === true){ status = false; } else { status = true; }
      }

      const nhcElement = document.getElementById(`${configType}_rule_nhc_${count}`);
      nhc = (nhcElement as HTMLInputElement).checked;


      const severityElement = document.getElementById(`${configType}_severity_${count}`);
      if (severityElement) { severity = (severityElement as HTMLInputElement).value; }

      // this.configuration.groups[0].rules[count - 1].alert                    = alert;
      // this.configuration.groups[0].rules[count - 1].annotations.description  = description;
      // this.configuration.groups[0].rules[count - 1].for                      = for_val;
      // this.configuration.groups[0].rules[count - 1].expr                     = expr;
      // this.configuration.groups[0].rules[count - 1].labels.category          = category;
      // this.configuration.groups[0].rules[count - 1].labels.disabled          = status;
      // this.configuration.groups[0].rules[count - 1].labels.nhc               = nhc;
      // this.configuration.groups[0].rules[count - 1].labels.severity          = severity;

      // this.save_configuration(configType, this.configuration, 'On Page')

      if (configType === "generic"){
        this.generic_config.groups[0].rules[count - 1].alert                    = alert;
        this.generic_config.groups[0].rules[count - 1].annotations.description  = description;
        this.generic_config.groups[0].rules[count - 1].for                      = for_val;
        this.generic_config.groups[0].rules[count - 1].expr                     = expr;
        this.generic_config.groups[0].rules[count - 1].labels.category          = category;
        this.generic_config.groups[0].rules[count - 1].labels.disabled          = status;
        this.generic_config.groups[0].rules[count - 1].labels.nhc               = nhc;
        this.generic_config.groups[0].rules[count - 1].labels.severity          = severity;

        this.save_configuration(configType, this.generic_config, 'On Page')

      } else {

        this.service_config.groups[0].rules[count - 1].alert                    = alert;
        this.service_config.groups[0].rules[count - 1].annotations.description  = description;
        this.service_config.groups[0].rules[count - 1].for                      = for_val;
        this.service_config.groups[0].rules[count - 1].expr                     = expr;
        this.service_config.groups[0].rules[count - 1].labels.category          = category;
        this.service_config.groups[0].rules[count - 1].labels.disabled          = status;
        this.service_config.groups[0].rules[count - 1].labels.nhc               = nhc;
        this.service_config.groups[0].rules[count - 1].labels.severity          = severity;

        this.save_configuration(configType, this.service_config, 'On Page')

      }
    },

    async save_configuration(configType:string, newContent: unknown, modalID: string) {
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
        if (configType === "generic"){
          content = this.mergeConfigurations(content, JSON.parse(JSON.stringify(this.service_config)));
        } else {
          content = this.mergeConfigurations(JSON.parse(JSON.stringify(this.generic_config)), content);
        }
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
