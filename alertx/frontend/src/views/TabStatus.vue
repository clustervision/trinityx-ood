<script setup lang="ts">
import StatusAlerts from '@/components/StatusAlerts.vue';
</script>

<script lang="ts">
import { defineComponent, nextTick } from "vue";
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
    nhc: boolean,
  };
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

interface AlertManager { // COMMENTED - UNTIL DO NOT GET THE SOLUTION FOR THE ALERT MANAGER PROXY PASS.
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
        cluster: string;
        exporter: string;
        hostname: string;
        job: string;
        luna_group: string;
        nhc: boolean;
        severity: string;
    }
}; // COMMENTED - UNTIL DO NOT GET THE SOLUTION FOR THE ALERT MANAGER PROXY PASS.

const severity_order = { 'critical': 1, 'danger': 2, 'warning': 3, 'info': 4, 'none': 5 };

export default defineComponent({
  props: {
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
  },

  data() {
    return {
      rows: [] as {rule: string; nhc: boolean; state: string; severity: keyof typeof severity_order; eventTime: string; hostname: string; exporter: string; job: string; alerts: Alerts[]; }[],
      alerts: [],
      noRows: '',
      noRowsType: false,
      showPopup: false,
      intervalId: null as number | null,
      autoReload: true,
    };
  },

  async mounted() {
    await this.fetchAlerts();
    this.intervalId = setInterval(this.fetchAlerts, 30000);
  },

  beforeUnmount() {
    if (this.intervalId) {
      clearInterval(this.intervalId); // Clear polling interval when component unmounts
    }
  },

  methods: {

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

    hostnameParser(hostname: string | Array<string> | null) {
      let cleanHostname = "";
      if (Array.isArray(hostname)) {
        cleanHostname = hostname.join("<br />");
      } else if (typeof hostname === "string") {
        if (hostname.includes(",") || hostname.includes(";")) {
          hostname = hostname.replace(/\[|\]|\s/g, ""); // Remove brackets and spaces
          cleanHostname = hostname.split(",").join("<br>");
        } else {
          cleanHostname = hostname;
        }
      } else {
        cleanHostname = "";
      }

      return cleanHostname;
    },

    sortRowsBySeverity() {
      this.rows.sort((a, b) => {
        const severityA = severity_order[a.severity as keyof typeof severity_order] || 5;
        const severityB = severity_order[b.severity as keyof typeof severity_order] || 5;
        return severityA - severityB;
      });
    },


    async fetchAlerts() {
      let alert_groups:number = 0;

      try {
          const proxyUrl = `${this.url}/proxy?url=${this.statusAPI}`;
          const response = await axios.get(proxyUrl);
          if (response.status === 200) {
            alert_groups = response.data.data.groups;
          }
        } catch (error: unknown) {
          if (error instanceof AxiosError) {
            this.noRows += `\nERROR[Prometheus Server] :: ${error.message}: CODE:${error.code} URL:${error.config?.url}`;
          } else if (error instanceof Error) {
            this.noRows += `\nERROR[Prometheus Server] :: ${error.message}`;
          }else {
            this.noRows += `\nERROR[Prometheus Server] :: ${error}`;
          }
        }



      //let alertData = false; // COMMENTED - UNTIL DO NOT GET THE SOLUTION FOR THE ALERT MANAGER PROXY PASS.
      this.rows = [];
      this.noRows = '';
      if (this.alertURL.includes("http")) {  // COMMENTED - UNTIL DO NOT GET THE SOLUTION FOR THE ALERT MANAGER PROXY PASS.
        try {
          const alert_manager_Url = `${this.url}/proxy?url=${this.alertURL}`;
          const alert_manager = await axios.get(alert_manager_Url);

          if (alert_manager.status === 200) {
            let alert_rows:number = 0;
            alert_manager.data.forEach((alert: AlertManager) => {
              if (alert.status.state !== "suppressed"){
                alert_rows = alert_rows + 1;
                let ruleBelongs = {};
                let alertsBelongs = [];
                if (alert_groups.length !== 0){
                  const match = alert_groups.flatMap(group => group.rules).find(rule => rule.name === alert.labels.alertname && rule.labels?.category === alert.labels.category);
                  const { alerts, ...cleanRule } = match || {};
                  const matchedAlerts = alerts?.filter(a => a.labels?.hostname === alert.labels.hostname);
                  alertsBelongs =  matchedAlerts || [];
                  ruleBelongs = cleanRule;
                }

                this.rows.push({
                  id: alert_rows,
                  alert: alert.labels.alertname,
                  nhc: alert.labels.nhc,
                  state: alert.status.state,
                  severity: alert.labels.severity,
                  eventTime: this.parseTimestamp(alert.startsAt),
                  hostname: alert.labels.hostname,
                  exporter: alert.labels.exporter,
                  job: alert.labels.job,
                  rule: ruleBelongs,
                  alerts: alertsBelongs
                });

                this.sortRowsBySeverity();
              }

            });
            if (this.rows.length === 0){
              this.noRows += `ERROR[Alert Manager] ::There is no records coming from ${this.alertURL}.`;
            } //else { alertData = true; }
          } else {
            this.noRows += `\nERROR[Alert Manager] :: Error fetching Alerts from ${this.alertURL} Status: ${alert_manager.status}.`;
            console.error("Error fetching Alerts:", alert_manager.status, alert_manager.data);
          }
        } catch (error: unknown) {
          // console.error("Error fetching Alerts:", error);
          console.error(error);
          if (error instanceof Error) {
            this.noRows += `\nERROR[Alert Manager] :: ${error.message}: ${error.stack}`;
          } else {
            this.noRows += `\nERROR[Alert Manager] :: ${error}`;
          }
        }
      } else {
        this.noRows += `\nERROR[Alert Manager] :: URL is incorrect: ${this.alertURL}`;
      } // COMMENTED - UNTIL DO NOT GET THE SOLUTION FOR THE ALERT MANAGER PROXY PASS.
      //if (alertData === false) {  // COMMENTED - UNTIL DO NOT GET THE SOLUTION FOR THE ALERT MANAGER PROXY PASS.
        // try {
        //   const proxyUrl = `${this.url}/proxy?url=${this.statusAPI}`;
        //   const response = await axios.get(proxyUrl);
        //   // const response = await axios.get(this.statusAPI);
        //   if (response.status === 200) {
        //     response.data.data.groups.forEach((group: Prometheus) => {
        //       if (group.name === "trinityx" || group.name === "trinityx_hw"){
        //         group.rules.forEach((rule) => {
        //           if (rule.alerts && rule.alerts.length > 0){
        //             rule.alerts.forEach((alert) => {
        //               if (String(alert.labels.disabled) === 'false' || alert.labels.disabled === undefined){
        //                 const exists = this.rows.some(row => row.rule === rule.name && row.hostname === alert.labels.hostname && row.exporter === alert.labels.exporter && row.job === alert.labels.job);
        //                 if (!exists) {
        //                   this.rows.push({
        //                     rule: rule.name,
        //                     nhc: String(rule.labels.nhc) === 'true',
        //                     state: rule.state,
        //                     severity: rule.labels.severity as keyof typeof severity_order,
        //                     eventTime: this.parseTimestamp(rule.lastEvaluation),
        //                     hostname: this.hostnameParser(alert.labels.hostname),
        //                     exporter: alert.labels.exporter,
        //                     job: alert.labels.job,
        //                     alerts: rule.alerts as Alerts[]});
        //                 }
        //               }
        //             });
        //           }
        //         });
        //       }
        //     });
        //   } else {
        //     this.noRows += `\nERROR[Prometheus Server] :: Error fetching Alerts from ${this.statusAPI} Status: ${response.status}.`;
        //     console.error("Error fetching rules:", response.status, response.data);
        //   }
        //   if (this.rows.length === 0){
        //     this.noRows += `SUCCESS[Prometheus Server] :: There is no firing alerts for TrinityX Group.`;
        //     this.noRowsType = true;
        //   } else {
        //     this.sortRowsBySeverity();
        //   }
        // } catch (error: unknown) {
        //   if (error instanceof AxiosError) {
        //     this.noRows += `\nERROR[Prometheus Server] :: ${error.message}: CODE:${error.code} URL:${error.config?.url}`;
        //   } else if (error instanceof Error) {
        //     this.noRows += `\nERROR[Prometheus Server] :: ${error.message}`;
        //   }else {
        //     this.noRows += `\nERROR[Prometheus Server] :: ${error}`;
        //   }
        // }
      //}  // COMMENTED - UNTIL DO NOT GET THE SOLUTION FOR THE ALERT MANAGER PROXY PASS.
      await nextTick();
      this.refreshDataTable();
    },

    refreshDataTable() {
      const table = $('#dataTable');
      // nextTick(() => {
          table.DataTable({
          pageLength: 25
        });
      // });
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

  },
});

</script>

<template>
  <h4 class="fw-bold py-3 mb-4">
    <span class="text-muted fw-light"> Monitoring /</span> Alerts
    <button style="float: right;" type="button"  :class="['btn', 'btn-sm', autoReload ? 'btn-success' : 'btn-warning']" @click="toggleAutoReload">{{ autoReload ? "Stop Auto Reload" : "Start Auto Reload" }}</button>
  </h4>
  <div v-if="noRows" :class="['alert', noRowsType ? 'alert-success' : 'alert-danger', 'alert-dismissible']" role="alert">
    <pre style="font-weight: bold; font-size: larger;">{{ noRows }}</pre>
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  </div>
  <div v-if="rows.length" class="table table-bordered table-striped table-hover table-responsive text-nowrap">
    <table id="dataTable" class="table table-bordered table-striped table-hover caption-top">
      <thead>
        <tr>
          <th>#</th>
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
          <td>
            <StatusAlerts :rule="row.rule || []" :alerts="row.alerts || []" :modalId="`Status_${index +1}`" @html="(hostname, resolve) => resolve(hostnameParser(hostname))" @modal-open="stopAutoReload" @modal-close="startAutoReload" />
            <!-- <StatusAlerts :alerts="row.alerts || []" :ruleName="row.rule" :modalId="`Status_${index +1}`" @html="(hostname, resolve) => resolve(hostnameParser(hostname))" @modal-open="stopAutoReload" @modal-close="startAutoReload" /> -->
            <a href="#" data-bs-toggle="modal" :data-bs-target="`#Status_${index +1}`">{{ row.alert }}</a>
          </td>
          <td><span class="badge me-1" :class="{'bg-label-secondary': row.state === 'inactive', 'bg-label-danger': row.state === 'firing', 'bg-label-warning': row.state === 'pending', 'bg-label-success': row.state === 'active', 'bg-label-info': row.state === 'suppressed'}" >{{ row.state }}</span></td>
          <!-- <td><span class="badge me-1" :class="{'bg-label-secondary': row.state === 'inactive', 'bg-label-danger': row.state === 'firing', 'bg-label-warning': row.state === 'pending', 'bg-label-success': row.state === 'active', 'bg-label-info': row.state === 'suppressed'}" >{{ row.state === 'active' ? 'firing' : row.state }}</span></td> -->
          <td><span class="badge me-1" :class="{'bg-label-info': row.severity === 'info', 'bg-label-warning': row.severity === 'warning', 'bg-label-danger': row.severity === 'danger', 'bg-label-dark': row.severity === 'critical' }" >{{ row.severity }}</span></td>
          <td><span class="badge me-1" :class="{'bg-label-primary': row.nhc === true, 'bg-label-warning': row.nhc === false || row.nhc === undefined }" >{{ row.nhc === true ? true : false }}</span></td>
          <td>{{ row.eventTime }}</td>
          <td v-html="row.hostname"></td>
          <td>{{ row.exporter }}</td>
          <td>{{ row.job }}</td>
        </tr>
      </tbody>
    </table>
  </div>

</template>
