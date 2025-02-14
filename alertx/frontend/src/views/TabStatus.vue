<script lang="ts">
import { defineComponent, nextTick } from "vue";
import axios from 'axios';

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
    labels: {alertname: string, exporter: string, hostname: string, instance: string, job: string, luna_group: string, nhc: boolean, severity: string};
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

// interface AlertManager { // COMMENTED - UNTIL DO NOT GET THE SOLUTION FOR THE ALERT MANAGER PROXY PASS.
//     annotations: {description: string;};
//     endsAt: string;
//     fingerprint: string;
//     receivers: [{name: string;}],
//     startsAt: string;
//     status: {
//         inhibitedBy: [];
//         silencedBy: [];
//         state: string;
//     },
//     updatedAt: string;
//     generatorURL: string;
//     labels: {
//         alertname: string;
//         cluster: string;
//         exporter: string;
//         hostname: string;
//         job: string;
//         luna_group: string;
//         nhc: boolean;
//         severity: string;
//     }
// }; // COMMENTED - UNTIL DO NOT GET THE SOLUTION FOR THE ALERT MANAGER PROXY PASS.

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
      rows: [] as { id: number; rule: string; nhc: boolean; state: string; severity: string; eventTime: string; affected: unknown; }[],
      alerts: [],
      noRows: '',
      showPopup: false,
    };
  },

  async mounted() {
    // let alertData = false; // COMMENTED - UNTIL DO NOT GET THE SOLUTION FOR THE ALERT MANAGER PROXY PASS.
    this.updateShowSpinner(true);
    // if (this.alertURL.includes("http")) {  // COMMENTED - UNTIL DO NOT GET THE SOLUTION FOR THE ALERT MANAGER PROXY PASS.
      // try {
      //   // const alert_manager = await axios.get('/api/api/v2/alerts'); // Development Purpose Only - Remove this line when deploying to production
      //   const alert_manager = await axios.get(this.alertURL);
      //   if (alert_manager.status === 200) {
      //     let alert_rows:number = 0;
      //     alert_manager.data.forEach((alert: AlertManager) => {
      //       alert_rows = alert_rows + 1;
      //       const affected:object = {"hostname":  alert.labels.hostname, "exporter":  alert.labels.exporter, "job":  alert.labels.job};
      //       this.rows.push({"id": alert_rows, "rule": alert.labels.alertname, "nhc": alert.labels.nhc, "state": alert.status.state, "severity": alert.labels.severity, "eventTime": alert.startsAt, "affected": affected});
      //     });
      //     if (this.rows.length === 0){
      //       this.noRows += `ERROR[Alert Manager] ::There is no records coming from ${this.alertURL}.`;
      //     } else { alertData = true; }
      //   } else {
      //     this.noRows += `\nERROR[Alert Manager] :: Error fetching Alerts from ${this.alertURL} Status: ${alert_manager.status}.`;
      //     console.error("Error fetching Alerts:", alert_manager.status, alert_manager.data);
      //   }
      // } catch (error: unknown) {
      //   console.error("Error fetching Alerts:", error);
      //   if (error instanceof Error) {
      //     this.noRows += `\nERROR[Alert Manager] :: ${error.message}: ${error.stack}`;
      //   } else {
      //     this.noRows += `\nERROR[Alert Manager] :: ${error}`;
      //   }
      // }
    // } else {
      // this.noRows += `\nERROR[Alert Manager] :: URL is incorrect: ${this.alertURL}`;
    // }  // COMMENTED - UNTIL DO NOT GET THE SOLUTION FOR THE ALERT MANAGER PROXY PASS.
    // if (alertData === false) {  // COMMENTED - UNTIL DO NOT GET THE SOLUTION FOR THE ALERT MANAGER PROXY PASS.
      try {
        const proxyUrl = `${this.url}/proxy?url=${this.statusAPI}`;
        const response = await axios.get(proxyUrl);
        // const response = await axios.get(this.statusAPI);
        if (response.status === 200) {
          response.data.data.groups.forEach((group: Prometheus) => {
            if (group.name === "trinityx"){
              let count_rows:number = 0;
              group.rules.forEach((rule) => {
                if (rule.alerts && rule.alerts.length > 0){
                  rule.alerts.forEach((alert) => {
                    count_rows = count_rows + 1;
                    const affected:object = {"hostname":  alert.labels.hostname, "exporter":  alert.labels.exporter, "job":  alert.labels.job};
                    this.rows.push({id: count_rows, rule: rule.name, nhc: String(rule.labels.nhc) === 'true', state: rule.state, severity: rule.labels.severity, eventTime: rule.lastEvaluation, affected: affected});
                  });
                } // else {
                  // count_rows = count_rows + 1;
                  // this.rows.push({"id": count_rows, "rule": rule.name, "state": rule.state, "severity": rule.labels.severity, "eventTime": rule.lastEvaluation, "affected": "Nothing"});
                  // }
              });
              if (this.rows.length === 0){
                this.noRows += `\nERROR[Prometheus Server] :: There is only inactive alerts for TrinityX Group.`;
              }
            }
          });
        } else {
          this.noRows += `\nERROR[Prometheus Server] :: Error fetching Alerts from ${this.statusAPI} Status: ${response.status}.`;
          console.error("Error fetching rules:", response.status, response.data);
        }
      } catch (error: unknown) {
        console.error("ERROR[Prometheus Server] :: Error fetching status:", error);
        if (error instanceof Error) {
          // Need  a Pop up to accept that risk
          this.noRows += `\nERROR[Prometheus Server] :: ${error.message}: ${error.stack}`;
        } else {
          this.noRows += `\nERROR[Prometheus Server] :: ${error}`;
        }
      }
    // }  // COMMENTED - UNTIL DO NOT GET THE SOLUTION FOR THE ALERT MANAGER PROXY PASS.
    this.updateShowSpinner(false);
    await nextTick();
    $("#dataTable").DataTable();
  },
  methods: {
    updateShowSpinner(value: boolean) {
      this.$emit("update:showSpinner", value);
    },
  },
});

</script>

<template>
  <h4 class="fw-bold py-3 mb-4">
    <span class="text-muted fw-light"> Monitoring /</span> Alerts
  </h4>
  <div v-if="noRows" class="alert alert-danger alert-dismissible" role="alert">
    <pre>{{ noRows }}</pre>
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  </div>
  <div v-if="rows.length" class="table table-bordered table-striped table-hover table-responsive text-nowrap">
    <table id="dataTable" class="table table-bordered table-striped table-hover caption-top">
      <thead>
        <tr>
          <th>#</th>
          <th>Rule</th>
          <th>State</th>
          <th>Severity</th>
          <th>NHC</th>
          <th>Event Time</th>
          <th>Affected</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in rows" :key="row.id">
          <td>{{ row.id }}</td>
          <td>{{ row.rule }}</td>
          <td><span class="badge me-1" :class="{'bg-label-secondary': row.state === 'inactive', 'bg-label-danger': row.state === 'firing', 'bg-label-warning': row.state === 'pending', 'bg-label-success': row.state === 'active', 'bg-label-info': row.state === 'suppressed'}" >{{ row.state === 'active' ? 'firing' : row.state }}</span></td>
          <td><span class="badge me-1" :class="{'bg-label-info': row.severity === 'info', 'bg-label-warning': row.severity === 'warning', 'bg-label-danger': row.severity === 'danger', 'bg-label-dark': row.severity === 'critical' }" >{{ row.severity }}</span></td>
          <td><span class="badge me-1" :class="{'bg-label-primary': row.nhc === true, 'bg-label-warning': row.nhc === false || row.nhc === undefined }" >{{ row.nhc === true ? true : false }}</span></td>
          <td>{{ row.eventTime }}</td>
          <td>
            <strong v-if="typeof row.affected === 'string'"><span class="badge bg-label-secondary me-1">{{ row.affected }}</span></strong>
            <template v-else-if="typeof row.affected === 'object' && row.affected !== null">
              <span v-for="(value, key, index) in row.affected" :key="index">
                <strong><span class="badge bg-label-primary me-1">{{ key }}: </span></strong> "{{ value }}"<span v-if="index < Object.keys(row.affected).length - 1">, </span>
              </span>
            </template>
          </td>
        </tr>
      </tbody>
    </table>
  </div>

</template>
