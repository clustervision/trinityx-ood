<script lang="ts">

import { defineComponent, nextTick } from "vue";
import axios from 'axios';
import BoxIcon from 'boxicons';
import tippy from 'tippy.js';
import 'tippy.js/dist/tippy.css';

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
    disabled: boolean,
    category: string,
  };
  alerts: Array<{
    activeAt: string;
    annotations: {description: string};
    labels: {alertname: string, category: string; disabled: boolean; exporter: string, hostname: string, instance: string, job: string, luna_group: string, nhc: boolean, severity: string};
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


interface Overview {
  hostname: string;
  genericRules: boolean | null;
  services: boolean | null;
  hardware: boolean | null;
  other: boolean | null;
  ipmi: boolean | null;
};


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
  components: {
    BoxIcon,
  },
  data() {
    return {
      overview: [] as { hostname: string; genericRules: boolean | null; services: boolean | null; hardware: boolean | null; other: boolean | null; ipmi: boolean | null; }[],
      alerts: [],
      noRows: '',
      showPopup: false,
    };
  },

  async mounted() {
    this.updateShowSpinner(true);
      try {
        const proxyUrl = `${this.url}/proxy?url=${this.statusAPI}`;
        const response = await axios.get(proxyUrl);
        if (response.status === 200) {
          response.data.data.groups.forEach((group: Prometheus) => {
            if (group.name === "trinityx") {
              const uniqueOverviewMap = new Map<string, Overview>();
              group.rules.forEach((rule) => {
                if (rule.alerts && rule.alerts.length > 0) {
                  rule.alerts.forEach((alert) => {
                    const hostname = alert.labels.hostname;
                    let genericRules: boolean | null = null;
                    let services: boolean | null = null;
                    let hardware: boolean | null = null;
                    let other: boolean | null = null;
                    const nhc: boolean = String(rule.labels.nhc) === "true";



                    if (hostname !== undefined) {

                      if (alert.state === "firing" && String(alert.labels.disabled) === 'false'){
                        if (alert.labels.category === "generic") {
                          // genericRules = nhc ? true : (genericRules ?? false);
                          // console.log(genericRules);
                          if (nhc === true){ genericRules = true; } else { genericRules = false; }
                          console.log(`hostname ${hostname} NHC ${nhc} RULE: ${genericRules}`);
                        }
                        if (alert.labels.category === "service") {
                          // services = nhc ? true : (services ?? false);
                          if (nhc === true){ services = true; } else { services = false; }
                        }
                        if (alert.labels.category === "hardware") {
                          // hardware = nhc ? true : (hardware ?? false);
                          if (nhc === true){ hardware = true; } else { hardware = false; }
                        }

                        if ((alert.labels.category !== "generic" && alert.labels.category !== "service" && alert.labels.category !== "hardware") || (alert.labels.category === undefined)) {
                          // other = nhc ? true : (other ?? false);
                          if (nhc === true){ other = true; } else { other = false; }
                        }
                      }
                    // console.log(` RULE: ${genericRules} ==========+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++===`);
                      if (uniqueOverviewMap.has(hostname)) {
                        // const existing = uniqueOverviewMap.get(hostname)!;
                        // existing.genericRules = existing.genericRules && genericRules;
                        // existing.services = existing.services && services;
                        // existing.hardware = existing.hardware && hardware;

                        // existing.genericRules = existing.genericRules === true ? true : genericRules;
                        // existing.services = existing.services === true ? true : services;
                        // existing.hardware = existing.hardware === true ? true : hardware;

                        // existing.genericRules = existing.genericRules && genericRules;
                        // existing.services = existing.services && services;
                        // existing.hardware = existing.hardware && hardware;
                        // existing.other = existing.other && other;

                      } else {
                        // console.log(` RULE: ${genericRules} ==========+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++===`);
                        uniqueOverviewMap.set(hostname, {
                          hostname: hostname,
                          genericRules: genericRules,
                          services: services,
                          hardware: hardware,
                          other: other,
                          ipmi: null,
                        });
                      }
                    }
                  });
                  if (this.overview.length === 0) {
                    this.overview = Array.from(uniqueOverviewMap.values());
                    }
                  // this.overview = Array.from(uniqueOverviewMap.values());
                } // else {
                // count_rows = count_rows + 1;
                // this.rows.push({"id": count_rows, "rule": rule.name, "state": rule.state, "severity": rule.labels.severity, "eventTime": rule.lastEvaluation, "affected": "Nothing"});
                // }

              });

              console.log(this.overview);
              if (this.overview.length === 0) {
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
          this.noRows += `\nERROR[Prometheus Server] :: ${error.message}: ${error.stack}`;
        } else {
          this.noRows += `\nERROR[Prometheus Server] :: ${error}`;
        }
      }
    this.updateShowSpinner(false);
    await nextTick();
    $("#dataTableOverview").DataTable();
    tippy('[data-tippy-content]');
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
    <span class="text-muted fw-light"> Monitoring /</span> Overview
  </h4>
  <div v-if="noRows" class="alert alert-danger alert-dismissible" role="alert">
    <pre>{{ noRows }}</pre>
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  </div>
  <div class="container-xxl flex-grow-1 container-p-y">
    <div class="card">
  <div class="alert alert-info alert-dismissible" role="alert">
    <div class="row">
      <div class="col col-1"><box-icon name="circle" type="solid" color="#198754"></box-icon></div>
      <div class="col col-1"><i><strong>OK</strong></i></div>
    </div>
    <div class="row">
      <div class="col col-1"><box-icon name="circle" type="solid" color="#FFC107"></box-icon></div>
      <div class="col col-11"><i>When Firing and NHC is <strong>Disabled</strong>.</i></div>
    </div>
    <div class="row">
      <div class="col col-1"><box-icon name="circle" type="solid" color="#DC3545"></box-icon></div>
      <div class="col col-11"><i>When Firing and NHC is <strong>Enabled</strong>.</i></div>
    </div>
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  </div>
  <div v-if="overview.length">


    <table id="dataTableOverview" class="table table-bordered table-striped table-hover caption-top">
      <thead>
        <tr>
          <th>#</th>
          <th>Node(s)</th>
          <th>Generic Rules</th>
          <th>Services</th>
          <th>Node H/W</th>
          <th>Other Rules</th>
          <!-- <th style="color:#FFC107">IPMI Status (beta)<box-icon style="width: 10px;height: 10px;" name='star' type='solid' flip='horizontal' color='#FFC107' data-tippy-content="This is in BETA"></box-icon></th> -->
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, index) in overview" :key="row.hostname">
          <td>{{ index +1 }}</td>
          <td>{{ row.hostname }}</td>
          <td>
            <box-icon v-if="row.genericRules === null" name="circle" type="solid" color="#198754" :data-tippy-content="`Node ${row.hostname} Rules are OK.`"></box-icon>
            <box-icon v-else-if="row.genericRules === false" name="circle" type="solid" color="#FFC107" :data-tippy-content="`Node ${row.hostname} Rules NHC is Disabled.`"></box-icon>
            <box-icon v-else-if="row.genericRules === true" name="circle" type="solid" color="#DC3545" :data-tippy-content="`Node ${row.hostname} Rules NHC is Enabled.`"></box-icon>
          </td>
          <td>
            <box-icon v-if="row.services === null" name="circle" type="solid" color="#198754" :data-tippy-content="`Node ${row.hostname} Services are OK.`"></box-icon>
            <box-icon v-else-if="row.services === false" name="circle" type="solid" color="#FFC107" :data-tippy-content="`Node ${row.hostname} Services NHC is Disabled.`"></box-icon>
            <box-icon v-else-if="row.services === true" name="circle" type="solid" color="#DC3545" :data-tippy-content="`Node ${row.hostname} Services NHC is Enabled.`"></box-icon>
          </td>
          <td>
            <box-icon v-if="row.hardware === null" name="circle" type="solid" color="#198754" :data-tippy-content="`Node ${row.hostname} Hardware are OK.`"></box-icon>
            <box-icon v-else-if="row.hardware === false" name="circle" type="solid" color="#FFC107" :data-tippy-content="`Node ${row.hostname} Hardware NHC is Disabled.`"></box-icon>
            <box-icon v-else-if="row.hardware === true" name="circle" type="solid" color="#DC3545" :data-tippy-content="`Node ${row.hostname} Hardware NHC is Enabled.`"></box-icon>
          </td>
          <td>
            <box-icon v-if="row.other === null" name="circle" type="solid" color="#198754" :data-tippy-content="`Node ${row.hostname} Other are OK.`"></box-icon>
            <box-icon v-else-if="row.other === false" name="circle" type="solid" color="#FFC107" :data-tippy-content="`Node ${row.hostname} Other NHC is Disabled.`"></box-icon>
            <box-icon v-else-if="row.other === true" name="circle" type="solid" color="#DC3545" :data-tippy-content="`Node ${row.hostname} Other NHC is Enabled.`"></box-icon>
          </td>
          <!-- <td>
            <box-icon v-if="row.ipmi === true" name="circle" type="solid" color="#198754" data-tippy-content="This is in BETA"></box-icon>
            <box-icon v-else-if="row.ipmi === false" name="circle" type="solid" color="#DC3545" data-tippy-content="This is in BETA"></box-icon>
            <box-icon v-else name="circle" type="solid" color="#FFC107" data-tippy-content="This is in BETA"></box-icon>
          </td> -->
        </tr>
      </tbody>
    </table>
  </div>

  </div>
</div>


</template>
