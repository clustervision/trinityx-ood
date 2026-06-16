<script setup lang="ts">

import StatusAlerts from '@/components/StatusAlerts.vue';
import AlertsSilence from '@/components/AlertsSilence.vue';

</script>

<script lang="ts">

import { defineComponent, nextTick } from "vue";
import { Modal } from 'bootstrap';
import axios, { AxiosError } from 'axios';

interface Alerts {
  activeAt: string;
  annotations: {description: string};
  labels: {
    alertname: string,
    exporter: string,
    hostname: string,
    category: string;
    class: string;
    instance: string,
    job: string,
    luna_group: string,
    disabled: boolean | null,
    nhc: boolean | null,
    severity: string
  };
  state: string;
  value: string;
};

interface AlertRules {
  duration: number;
  evaluationTime: number;
  health: string;
  keepFiringFor: number;
  lastEvaluation: string;
  name: string;
  query: string;
  state: string;
  type: string;
  labels: {
    severity: string,
    category: string,
    nhc: boolean | null,
  };
  annotations: {description: string};
  alerts: Array<{
    activeAt: string;
    annotations: {description: string};
    labels: {
      alertname: string,
      exporter: string,
      hostname: string,
      instance: string,
      job: string,
      luna_group: string,
      disabled: boolean | null,
      nhc: boolean | null,
      severity: string
    };
    state: string;
    value: string;
  }>;
};

interface Prometheus {
  evaluationTime: number;
  file: string;
  interval: number;
  lastEvaluation: string;
  limit: number;
  name: string;
  rules: AlertRules[];
};

interface AlertManager {
  annotations: {description: string;};
  endsAt: string;
  fingerprint: string;
  receivers: [{name: string;}],
  startsAt: string;
  status: {
    inhibitedBy: [];
    silencedBy: [];
    state: string;
  },
  updatedAt: string;
  generatorURL: string;
  labels: {
    alertname: string;
    category: string;
    cluster: string;
    exporter: string;
    hostname: string;
    job: string;
    luna_group: string;
    nhc: boolean | null;
    severity: string;
    disabled: boolean | null;
  }
};

const severity_order = { 'critical': 1, 'danger': 2, 'warning': 3, 'info': 4, 'none': 5 };

export default defineComponent({
  props: {
    isActive: {
      type: Boolean,
      required: true,
      default: false,
    },
    
  isModalOpen: Boolean,
    url: {
      type: String,
      required: true,
    },
    statusAPI: {
      type: String,
      required: true,
    },
    alertURL: {
      type: String,
      required: true,
    },
    silenceAPI: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      silenceMessages: [] as string[],
      dataFrom: '',
      selectedRows: [] as Array<{ alert: string; hostname: string }>,
      rows: [] as {alert: string; nhc: boolean; state: string; severity: keyof typeof severity_order; eventTime: string; hostname: string; exporter: string; job: string; rule: AlertRules[]; alerts: Alerts[]; }[],
      alerts: [],
      noRowsAlertManager: '',
      noRowsPrometheus: '',
      noRowsTypeAlertManager: '',
      noRowsTypePrometheus: '',
      showPopup: false,
      intervalId: null as number | null,
      autoReload: true,
      selectedRow: null as null | {
        alert: string;
        nhc: boolean;
        state: string;
        severity: keyof typeof severity_order;
        eventTime: string;
        hostname: string;
        exporter: string;
        job: string;
        rule: AlertRules[];
        alerts: Alerts[];
      },
    };
  },

  // watch: {
  //   async isActive(newValue) {
  //     if (newValue) {
  //       await this.fetchAlerts();
  //       if (this.autoReload) {
  //         this.startAutoReload();
  //       }
  //     } else {
  //       this.stopAutoReload();
  //     }
  //   },
  // },

  watch: {
  async isActive(newValue) {
    if (newValue && !this.isModalOpen) {
      await this.fetchAlerts();
      if (this.autoReload) {
        this.startAutoReload();
      }
    } else {
      this.stopAutoReload();
    }
  },
  isModalOpen(newValue) {
    if (!newValue) {
      // modal closed → re-run isActive watcher logic
      if (this.isActive) {
        this.fetchAlerts();
        if (this.autoReload) {
          this.startAutoReload();
        }
      }
    } else {
      this.stopAutoReload();
    }
  }
},

  async mounted() {
    if (this.isActive) {
      await this.fetchAlerts();
      if (this.autoReload) {
        this.startAutoReload();
      }
    }
  },

  beforeUnmount() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
  },

  methods: {

    clearRows() {
      this.rows = [];
    },

    handleSilenceMessage(msg: string) {
      this.silenceMessages.push(msg);
      this.selectedRows = [];
      setTimeout(() => {
        this.silenceMessages = this.silenceMessages.filter(m => m !== msg);
      }, 10000);
    },

    getRowIdentifier(alert:string, hostname:string) {
      return {alert: alert, hostname: hostname};
    },

    silentAlerts() {
      if (this.selectedRows.length > 0) {
        const modalEl = document.getElementById("silenceAlerts");
        if (modalEl) {
          const bootstrapModal = Modal.getInstance(modalEl) || new Modal(modalEl);
          bootstrapModal.show();
        } else {
          console.error("Modal element not found");
        }
      } else {
        alert("Please select at least one alert to make it silent or active.");
      }
    },

    toggleAll(event: Event) {
      const input = event.target as HTMLInputElement;
      if (input.checked) {
        this.selectedRows = this.rows.map(row => this.getRowIdentifier(row.alert, row.hostname));
      } else {
        this.selectedRows = [];
      }
    },

    parseTimestamp(timestampStr: string) {
      try {
        if (!timestampStr) return "";
        if (timestampStr.includes("Z00:00Z")){ timestampStr = timestampStr.replace("Z00:00Z", "Z"); }
        if (timestampStr.endsWith("Z")){ timestampStr = timestampStr.replace("Z", "+00:00"); }
        if (timestampStr.includes(".")){
          const datePart = timestampStr.split(".")[0];
          let fractionPart = timestampStr.split(".")[1];
          fractionPart = fractionPart.replace(/Z$/, ""); // Remove trailing Z if exists

          if (fractionPart.includes("+") || fractionPart.includes("-")){
            let fraction = fractionPart.split(/[+-]/)[0];
            const tz = fractionPart.split(/[+-]/)[1];
            fraction = fraction.substring(0, 6); // Trim to 6 digits
            timestampStr = `${datePart}.${fraction}+${tz}`;
          } else {
            timestampStr = `${datePart}.${fractionPart.substring(0, 6)}`;
          }
        }
        const dateObj = new Date(timestampStr);

        // For UTC TimeZone uncomment this block and comment out the Dynamic block
        // const offsetMinutes = dateObj.getTimezoneOffset();
        // const offsetHours = Math.abs(Math.floor(offsetMinutes / 60));
        // const offsetMins = Math.abs(offsetMinutes % 60);
        // const sign = offsetMinutes > 0 ? "-" : "+";
        // const utcOffset = `UTC${sign}${String(offsetHours).padStart(2, "0")}:${String(offsetMins).padStart(2, "0")}`;
        // const formattedDate = dateObj.toISOString().split("T")[0]; // "YYYY-MM-DD"
        // const formattedTime = dateObj.toTimeString().split(" ")[0]; // "HH:MM:SS"
        // return `${formattedDate} ${formattedTime} ${utcOffset}`;
        // For UTC TimeZone uncomment this block and comment out the Dynamic block

        // For Dynamic TimeZone
        const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        const formattedDate = dateObj.toISOString().split("T")[0]; // "YYYY-MM-DD"
        const formattedTime = dateObj.toTimeString().split(" ")[0]; // "HH:MM:SS"
        return `${formattedDate} ${formattedTime} ${timeZone}`;
        // For Dynamic TimeZone

      } catch (error) {
        console.error("Invalid timestamp:", timestampStr, error);
        return "";
      }
    },

    sortRowsBySeverity() {
      this.rows.sort((a, b) => {
        const severityA = severity_order[a.severity as keyof typeof severity_order] || 5;
        const severityB = severity_order[b.severity as keyof typeof severity_order] || 5;
        return severityA - severityB;
      });
    },

    async fetchAlerts() {
      this.clearRows();
      this.updateShowSpinner(true);
      let alert_groups = [];
      let alertData = false;
      try {
        const proxyUrl = `${this.url}/proxy?url=${this.statusAPI}`;
        const response = await axios.get(proxyUrl);
        if (response.status === 200) {
          alert_groups = response.data.data.groups;
          alert_groups = alert_groups.filter((group: { name: string; }) => group.name === "trinityx" || group.name === "trinityx_hw");
        }
      } catch (error: unknown) {
        if (error instanceof AxiosError) {
          this.noRowsPrometheus = `<strong>[Prometheus Server] :: ${error.message}: CODE:${error.code} URL:${error.config?.url}</strong>`;
        } else if (error instanceof Error) {
          this.noRowsPrometheus = `<strong>[Prometheus Server] :: ${error.message}</strong>`;
        }else {
          this.noRowsPrometheus = `<strong>[Prometheus Server] :: ${error}</strong>`;
        }
        this.noRowsTypePrometheus = 'danger';
      }

      if (this.dataFrom === "" || this.dataFrom === "Alert Manager" || this.noRowsAlertManager !== '') {
        const url = new URL(this.alertURL);
          url.username = '';
          url.password = '';
          const sanitizedUrl = url.href;
      if (this.alertURL.includes("http")) {
        

        try {
          const alert_manager_Url = `${this.url}/proxy?url=${this.alertURL}`;
          const alert_manager = await axios.get(alert_manager_Url, { timeout: 5000 });

          

          if (alert_manager.status === 200) {
            alert_manager.data.forEach((alert: AlertManager) => {
              if (alert.status.state !== "suppressed"){
                let ruleBelongs;
                let alertsBelongs;
                if (alert_groups.length !== 0){
                  const match = (alert_groups as Prometheus[]).flatMap(group => group.rules).find(rule => rule.name === alert.labels.alertname && rule.labels?.category === alert.labels.category);
                  const { alerts, ...cleanRule } = match || {};
                  const matchedAlerts = alerts?.filter(a => a.labels?.hostname === alert.labels.hostname);
                  alertsBelongs =  matchedAlerts ?? [];
                  ruleBelongs = [cleanRule];
                }
                if (String(alert.labels.disabled) === 'false' || alert.labels.disabled === undefined){
                  this.rows.push({
                    alert: alert.labels.alertname,
                    nhc: String(alert.labels.nhc) === 'true',
                    state: alert.status.state,
                    severity: alert.labels.severity as keyof typeof severity_order,
                    eventTime: this.parseTimestamp(alert.startsAt),
                    hostname: alert.labels.hostname,
                    exporter: alert.labels.exporter,
                    job: alert.labels.job,
                    rule: ruleBelongs as AlertRules[] || [],
                    alerts: alertsBelongs as Alerts[] || [],
                  });
                  this.dataFrom = "Alert Manager";
                  this.sortRowsBySeverity();
                }
              }

            });
            this.noRowsAlertManager = '';
            this.noRowsTypeAlertManager = '';
            if (this.rows.length === 0){
              this.noRowsAlertManager = `<strong>[Alert Manager] :: There is no alerts coming from Alert Manager, so falling back to Promethues Data to get the Alerts. \n\t [${sanitizedUrl}].</strong>`;
              this.noRowsTypeAlertManager = 'info';
            } else { alertData = true; }
          } else {
            this.noRowsAlertManager = `<strong>[Alert Manager] :: Error fetching Alerts from [${sanitizedUrl}] Status: ${alert_manager.status}.</strong>`;
            this.noRowsTypeAlertManager = 'warning';
          }
        } catch (error: unknown) {
          if (error instanceof Error) {
            this.noRowsAlertManager = `<strong>[Alert Manager] :: Could not read from Alert Manager: \n\t ${error.message}: ${sanitizedUrl}`;
            this.noRowsAlertManager += `\n\t Please ensure Alert Manager service is running and the port can be reached.`;
            this.noRowsAlertManager += `\n\t Falling back to Prometheus data.</strong>`;
          } else {
            this.noRowsAlertManager = `<strong>[Alert Manager] :: ${error}</strong>`;
          }
          this.noRowsTypeAlertManager = 'danger';
        }
      } else {
        this.noRowsAlertManager = `<strong>[Alert Manager] :: URL is incorrect: ${sanitizedUrl}</strong>`;
        this.noRowsTypeAlertManager = 'danger';
      }
    }
    
      if (alertData === false) {
        if (this.dataFrom === "" || this.dataFrom === "Prometheus" || this.noRowsAlertManager !== '') {
          
        if (alert_groups.length !== 0) {
          alert_groups.forEach((group: Prometheus) => {
            group.rules.forEach((rule) => {
              if (rule.alerts && rule.alerts.length > 0){
                rule.alerts.forEach((alert) => {
                  if (String(alert.labels.disabled) === 'false' || alert.labels.disabled === undefined){
                    const exists = this.rows.some(row => row.alert === rule.name && row.hostname === alert.labels.hostname && row.exporter === alert.labels.exporter && row.job === alert.labels.job);
                    if (!exists) {

                      this.rows.push({
                        alert: rule.name,
                        nhc: String(rule.labels.nhc) === 'true',
                        state: rule.state,
                        severity: rule.labels.severity as keyof typeof severity_order,
                        eventTime: this.parseTimestamp(rule.lastEvaluation),
                        hostname: alert.labels.hostname,
                        exporter: alert.labels.exporter,
                        job: alert.labels.job,
                        rule: Array.isArray(rule) ? rule : [rule],
                        alerts: rule.alerts as Alerts[]
                      });
                      this.dataFrom = "Prometheus";
                      alertData = true;
                      this.sortRowsBySeverity();
                    }
                  }
                });
              }
            });
          });
        } else {
          this.noRowsPrometheus = `<strong>[Prometheus Server] :: Could not read from Prometheus Server: URL: ${this.statusAPI}`;
          this.noRowsPrometheus += `\n\t Please ensure Prometheus Server service is running and the port can be reached.</strong>`;
          this.noRowsTypePrometheus = 'danger';
          this.dataFrom = "";
        }

      }
    }
      this.updateShowSpinner(false);
      await nextTick();
      this.refreshDataTable();
    },

    refreshDataTable() {
      const table = $('#dataTable');
          table.DataTable({
          pageLength: 25,
          columnDefs: [
            { orderable: false, targets: 1 } // 0 = first column (checkbox)
          ]
        });
    },

    startAutoReload() {
      if (this.autoReload && !this.intervalId) {
        this.intervalId = setInterval(this.fetchAlerts, 30000);
      }
    },

    stopAutoReload() {
      if (this.intervalId) {
        clearInterval(this.intervalId);
        this.intervalId = null;
      }
    },

    toggleAutoReload() {
      this.autoReload = !this.autoReload;
      if (this.autoReload) {
        this.startAutoReload();
      } else {
        this.stopAutoReload();
      }
    },

    openStatusModal(row: { alert: string; nhc: boolean; state: string; severity: keyof typeof severity_order; eventTime: string; hostname: string; exporter: string; job: string; rule: AlertRules[]; alerts: Alerts[]; }) {
      console.log("Opening status modal for row:", row);
      this.selectedRow = row;
      this.$nextTick(() => {
        const modalEl = document.getElementById('dynamicStatusModal');
        if (modalEl) {
          const modal = new Modal(modalEl, { backdrop: 'static' });
          modal.show();
        }
      });
    },

    updateShowSpinner(value: boolean) {
      this.$emit("update:showSpinner", value);
    },

    toggleData() {
      if (this.dataFrom === 'Alert Manager') {
        this.dataFrom = 'Prometheus';
      } else if (this.dataFrom === 'Prometheus') {
        this.dataFrom = 'Alert Manager';
      } else {
        this.dataFrom = '';
      }
      this.fetchAlerts();
    },

  },
});

</script>

<style scoped>
/* Fix Table Header */
.table thead th {
  position: sticky;
  top: 0;
  /* z-index: 2; */
  background: white;
}
/* Fix Table Header */
</style>

<template>
  <div v-for="(msg, index) in silenceMessages" :key="index" class="alert alert-primary" role="alert" v-html="msg"></div>
  <AlertsSilence v-if="dataFrom === 'Alert Manager'" :alerts="selectedRows" :silenceAPI="`${url}/proxy_post?url=${silenceAPI}`" modalId="silenceAlerts" @silence-message="handleSilenceMessage" @modal-open="stopAutoReload" @modal-close="startAutoReload" />
  <h4 class="fw-bold py-3 mb-4">
    <div class="d-flex justify-content-between align-items-center">
      <div v-if="dataFrom">
        <span class="text-muted fw-light"> Monitoring / Alerts /</span> {{ dataFrom }}
      </div>
      <div v-else>
        <span class="text-muted fw-light"> Monitoring /</span> Alerts
      </div>
      <div class="d-flex">
        <button v-if="dataFrom === 'Alert Manager'" type="button" class="btn btn-sm btn-info me-2" @click="silentAlerts">Silent Alerts</button>
        <button type="button" :class="['btn', 'btn-sm', ' me-2', autoReload ? 'btn-success' : 'btn-warning']" @click="toggleAutoReload">{{ autoReload ? "Stop Auto Reload" : "Start Auto Reload" }}</button>
        <button type="button" :class="['btn', 'btn-sm', dataFrom === 'Alert Manager' ? 'btn-secondary' : 'btn-primary']" @click="toggleData">{{ dataFrom === 'Alert Manager' ? "Prometheus" : "Alert Manager" }}</button>
    </div>
  </div>
  </h4>
  <div v-if="noRowsAlertManager || dataFrom === 'Alert Manager'" :class="['alert', 'alert-'+noRowsTypeAlertManager, 'alert-dismissible']" role="alert">
    <pre v-if="noRowsAlertManager" v-html="noRowsAlertManager" style="font-size: larger; margin-bottom: 0rem;"></pre>
    <button v-if="noRowsAlertManager" type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  </div>
  <div v-if="noRowsPrometheus && !rows.length" :class="['alert', 'alert-'+noRowsTypePrometheus, 'alert-dismissible']" role="alert">
     <pre v-html="noRowsPrometheus" style="font-size: larger; margin-bottom: 0rem;"></pre>
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  </div>
  <div v-if="rows.length">
    <table id="dataTable" class="table table-bordered table-striped table-hover caption-top">
      <thead>
        <tr>
          <th>#</th>
          <th v-if="dataFrom === 'Alert Manager'">Silent <input type="checkbox" @change="toggleAll($event)" /></th>
          <th>Alert</th>
          <th>State</th>
          <th>Severity</th>
          <th>NHC</th>
          <th>First Occurrence</th>
          <th>Hostname</th>
          <th>Exporter</th>
          <th>Job</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="(row, index) in rows" :key="index">
          <td>{{ index +1 }}</td>
          <td v-if="dataFrom === 'Alert Manager'"><input type="checkbox" :value="getRowIdentifier(row.alert, row.hostname)" v-model="selectedRows" /></td>
          <td>
            <a href="#" @click.prevent="openStatusModal(row)">{{ row.alert }}</a>
          </td>
          <td><span class="badge me-1" :class="{'bg-label-secondary': row.state === 'inactive', 'bg-label-danger': row.state === 'firing', 'bg-label-warning': row.state === 'pending', 'bg-label-success': row.state === 'active', 'bg-label-info': row.state === 'suppressed'}" >{{ row.state }}</span></td>
          <td><span class="badge me-1" :class="{'bg-label-info': row.severity === 'info', 'bg-label-warning': row.severity === 'warning', 'bg-label-danger': row.severity === 'danger', 'bg-label-dark': row.severity === 'critical' }" >{{ row.severity }}</span></td>
          <td><span class="badge me-1" :class="{'bg-label-primary': row.nhc === true, 'bg-label-warning': row.nhc === false || row.nhc === undefined }" >{{ row.nhc === true ? true : false }}</span></td>
          <td>{{ row.eventTime }}</td>
          <td v-html="row.hostname"></td>
          <td>{{ row.exporter }}</td>
          <td>{{ row.job }}</td>
        </tr>
      </tbody>
    </table>

    <StatusAlerts
      v-if="selectedRow"
      :rule="selectedRow.rule"
      :alerts="selectedRow.alerts"
      :first_occurrence="selectedRow.eventTime"
      modalId="dynamicStatusModal"
      @modal-open="stopAutoReload"
      @modal-close="startAutoReload"
    />

  </div>

</template>
