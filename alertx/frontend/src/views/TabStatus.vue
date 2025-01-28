<script setup lang="ts"></script>
<template>
  <h4 class="fw-bold py-3 mb-4">
    <span class="text-muted fw-light"> Monitoring /</span> Alerts
  </h4>
  <div v-if="rows.length" class="table table-bordered table-striped table-hover table-responsive text-nowrap">
    <table class="table table-bordered table-striped table-hover caption-top">
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
      <tbody v-for="row in rows" :key="row.id">
        <tr>
          <td>{{ row.id }}</td>
          <td>{{ row.rule }}</td>
          <td><span class="badge me-1" :class="{ 'bg-label-primary': row.state === 'inactive', 'bg-label-danger': row.state === 'firing' , 'bg-label-warning': row.state === 'pending' }" >{{ row.state }}</span></td>
          <td><span class="badge me-1" :class="{ 'bg-label-info': row.severity === 'info', 'bg-label-warning': row.severity === 'warning', 'bg-label-danger': row.severity === 'danger', 'bg-label-dark': row.severity === 'critical' }" >{{ row.severity }}</span></td>
          <td><span class="badge me-1" :class="{ 'bg-label-primary': row.nhc === 'yes', 'bg-label-warning': row.nhc === 'no' }" >{{ row.nhc }}</span></td>
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
    <div v-else-if="noRows" class="alert alert-danger" role="alert">{{ noRows }}</div>

</template>

<script  lang="ts">
import axios from 'axios';

interface StatusAlert {
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
    nhc: string,
  };
  alerts: Array<{
    activeAt: string;
    annotations: {description: string};
    labels: {alertname: string, exporter: string, hostname: string, instance: string, job: string, luna_group: string, nhc: string, severity: string};
    state: string;
    value: string;
  }>;
};


export default {
  props: {
    statusAPI: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      rows: [] as { id: number; rule: string; nhc: string; state: string; severity: string; eventTime: string; affected: unknown; }[],
      rules: [] as StatusAlert[],
      alerts: [],
      noRows: '',
    };
  },
  async mounted() {
    console.log(`Status API :: ${this.statusAPI}`)
    try {
      this.updateShowSpinner(true);
      const response = await axios.get(this.statusAPI);
      if (response.status === 200) {
        this.rules = response.data.data.groups[0].rules;
        let count_rows:number = 0;
        this.rules.forEach((rule) => {
          if (rule.alerts && rule.alerts.length > 0){
            rule.alerts.forEach((alert) => {
              count_rows = count_rows + 1;
              const affected:object = {"hostname":  alert.labels.hostname, "exporter":  alert.labels.exporter, "job":  alert.labels.job};
              this.rows.push({"id": count_rows, "rule": rule.name, "nhc": rule.labels.nhc, "state": rule.state, "severity": rule.labels.severity, "eventTime": rule.lastEvaluation, "affected": affected});
            });
          } //else {
            //count_rows = count_rows + 1;
            //this.rows.push({"id": count_rows, "rule": rule.name, "state": rule.state, "severity": rule.labels.severity, "eventTime": rule.lastEvaluation, "affected": "Nothing"});
          //}
        });

      } else {
        console.error("Error fetching rules:", response.status, response.data);
      }

    } catch (error: unknown) {
      console.error("Error fetching status:", error);
      if (error instanceof Error) {
        this.noRows = `${error.message}: ${error.stack}`;
      } else {
        this.noRows = `${error}`;
      }
    }
    this.updateShowSpinner(false);
  },
  methods: {
    updateShowSpinner(value: boolean) {
      this.$emit("update:showSpinner", value);
    },
  },
};


</script>
