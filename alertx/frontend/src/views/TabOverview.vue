<script setup lang="ts">
import OverviewAlerts from '@/components/OverviewAlerts.vue';
</script>
<script lang="ts">
import { defineComponent, nextTick } from "vue";
import axios, { AxiosError } from 'axios';
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
  alerts: SpecificAlerts[];
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

interface SpecificAlerts {
  activeAt: string;
  annotations: {description: string};
  labels: {
    alertname: string,
    category: string;
    class: string;
    description: string;
    disabled: boolean;
    exporter: string;
    hostname: string;
    instance: string;
    job: string;
    luna_group: string;
    nhc: boolean;
    severity: string;
    path: string;
    product: string;
    serial: string;
    vendor: string;
  };
  state: string;
  value: string;
};


interface Overview {
  state: boolean;
  hostname: string;
  genericRules: boolean | null;
  services: boolean | null;
  hardware: boolean | null;
  other: boolean | null;
  ipmi: boolean | null;
  genericAlerts: SpecificAlerts[];
  servicesAlerts: SpecificAlerts[];
  hardwareAlerts: SpecificAlerts[];
  otherAlerts: SpecificAlerts[];
  allAlerts: SpecificAlerts[];
};

interface NodeList {
  metric: {hostname: string};
  value: [string, string];
};

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
    nodeListAPI: {
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
      overview: [] as Overview[],
      alerts: [],
      icons: "default",
      noRowsPrometheus: '',
      noRowsTypePrometheus: '',
      showPopup: false,
      intervalId: null as number | null,
      autoReload: true,
    };
  },

  // watch: {
  //   async isActive(newValue) {
  //     if (newValue) {
  //       await this.fetchOverview();
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
      await this.fetchOverview();
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
        this.fetchOverview();
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
      await this.fetchOverview();
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
    async fetchOverview() {
      this.overview = [];
      this.updateShowSpinner(true);
      try {
        const nodeList = `${this.url}/proxy?url=${this.nodeListAPI}`;
        const nodeResponse = await axios.get(nodeList);
        if (nodeResponse.status === 200) {
          nodeResponse.data.data.result.forEach((node: NodeList) => {
            const hostname = node.metric.hostname;
            if (hostname !== undefined) {
              this.overview.push({state: true, hostname: hostname, genericRules: null, services: null, hardware: null, other: null, ipmi: null, genericAlerts:[], servicesAlerts:[], hardwareAlerts:[], otherAlerts:[], allAlerts:[]});
            }
          });
        } else {
          this.noRowsPrometheus = `<strong>[Prometheus Server] :: Error fetching Nodes from ${this.nodeListAPI} Status: ${nodeResponse.status}.</strong>`;
          console.error("Error fetching nodes:", nodeResponse.status, nodeResponse.data);
        }
      } catch (error: unknown) {
        if (error instanceof AxiosError) {
          this.noRowsPrometheus = `<strong>[Prometheus Server] :: Could not read from Prometheus Server: URL: ${this.statusAPI}`;
          this.noRowsPrometheus += `\n\t Please ensure Prometheus Server service is running and the port can be reached.</strong>`;
          this.noRowsTypePrometheus = 'danger';
        } else if (error instanceof Error) {
          this.noRowsPrometheus = `<strong>[Prometheus Server] :: ${error.message}</strong>`;
        }else {
          this.noRowsPrometheus = `<strong>[Prometheus Server] :: ${error}</strong>`;
        }
        this.noRowsTypePrometheus = 'danger';
      }
      if (!this.noRowsPrometheus){
        try {
          const proxyUrl = `${this.url}/proxy?url=${this.statusAPI}`;
          const response = await axios.get(proxyUrl);
          if (response.status === 200) {

            response.data.data.groups.forEach((group: Prometheus) => {
              if (group.name === "trinityx" || group.name === "trinityx_hw") {
                group.rules.forEach((rule) => {
                  if (rule.alerts && rule.alerts.length > 0) {
                    rule.alerts.forEach((alert : SpecificAlerts) => {
                      const hostname = alert.labels.hostname;
                      const state = true;
                      let genericRules: boolean | null = null;
                      let services: boolean | null = null;
                      let hardware: boolean | null = null;
                      let other: boolean | null = null;

                      const genericAlerts: SpecificAlerts[] = [];
                      const servicesAlerts: SpecificAlerts[] = [];
                      const hardwareAlerts: SpecificAlerts[] = [];
                      const otherAlerts: SpecificAlerts[] = [];

                      const nhc: boolean = String(rule.labels.nhc) === "true";

                      if (hostname !== undefined) {
                        if (rule.state === "firing" && (String(alert.labels.disabled) === 'false' || alert.labels.disabled === undefined)){
                          if (alert.labels.category === "generic") {
                            if (nhc === true){ genericRules = true; } else { genericRules = false; }
                            genericAlerts.push(alert);
                          }
                          if (alert.labels.category === "service") {
                            if (nhc === true){ services = true; } else { services = false; }
                            servicesAlerts.push(alert);
                          }
                          if (alert.labels.category === "hardware") {
                            if (nhc === true){ hardware = true; } else { hardware = false; }
                            hardwareAlerts.push(alert);
                          }
                          if ((alert.labels.category !== "generic" && alert.labels.category !== "service" && alert.labels.category !== "hardware") || (alert.labels.category === undefined)) {
                            if (nhc === true){ other = true; } else { other = false; }
                            otherAlerts.push(alert);
                          }


                          const hostEntry = this.overview.find(item => item.hostname === hostname);
                          if (hostEntry) {
                            if (genericRules === true || (genericRules === false && hostEntry.genericRules !== true)){
                              hostEntry.genericRules = genericRules;
                              hostEntry.genericAlerts.push(...genericAlerts);
                            } 
                            if (services === true || (services === false && hostEntry.services !== true)){
                              hostEntry.services = services;
                              hostEntry.servicesAlerts.push(...servicesAlerts);
                            }
                            if (hardware === true || (hardware === false && hostEntry.hardware !== true)){
                              hostEntry.hardware = hardware;
                              hostEntry.hardwareAlerts.push(...hardwareAlerts);
                            }
                            if (other === true || (other === false && hostEntry.other !== true)){
                              hostEntry.other = other;
                              hostEntry.otherAlerts.push(...otherAlerts);
                            }
                            if (alert.labels.alertname === "ServerDown") {
                              hostEntry.state = false;
                            }
                            hostEntry.allAlerts.push(...genericAlerts, ...servicesAlerts, ...hardwareAlerts, ...otherAlerts);
                          }
                        }
                      }
                    });
                  }
                });
                if (this.overview.length === 0) {
                  this.noRowsPrometheus = `<strong>[Prometheus Server] :: There is only inactive alerts for TrinityX Group.</strong>`;
                }
              }
            });

          } else {
            this.noRowsPrometheus = `<strong>[Prometheus Server] :: Error fetching Alerts from ${this.statusAPI} Status: ${response.status}.</strong>`;
            console.error("Error fetching rules:", response.status, response.data);
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
    }
      this.updateShowSpinner(false);
      await nextTick();
      this.refreshDataTable();
    },

    refreshDataTable() {
      const table = $('#dataTableOverview');
      nextTick(() => {
          table.DataTable({
          order: [[1, 'asc']],
          columnDefs: [{ targets: 2, type: "string" }],
          pageLength: 25
        });
      });
      tippy('[data-tippy-content]');
    },

    updateShowSpinner(value: boolean) {
      this.$emit("update:showSpinner", value);
    },

    startAutoReload() {
      if (this.autoReload && !this.intervalId) {
        this.intervalId = setInterval(this.fetchOverview, 30000);
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

  computed: {
  overviewCompact() {
    const chunkSize = 10;
    const chunks = [];
    for (let i = 0; i < this.overview.length; i += chunkSize) {
      chunks.push(this.overview.slice(i, i + chunkSize));
    }
    return chunks;
  },

  overviewSuperCompact() {
    const chunkSize = 25;
    const chunks = [];
    for (let i = 0; i < this.overview.length; i += chunkSize) {
      chunks.push(this.overview.slice(i, i + chunkSize));
    }
    return chunks;
  },

  showContainerClass() {
    return this.overview.length > 0 && this.overview.length <= 101;
  }
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
  <h4 class="fw-bold py-3 mb-4">
    <div class="d-flex justify-content-between align-items-center">
      <div><span class="text-muted fw-light"> Monitoring /</span> Overview</div>
      <div class="d-flex">
        <div class="btn-group btn-group-sm me-2" role="group" aria-label="Basic radio toggle button group">
          <input type="radio" class="btn-check" name="glyphs" id="glyphs" autocomplete="off" value="default" v-model="icons">
          <label class="btn btn-outline-primary" for="glyphs">Glyphs</label>
          <input type="radio" class="btn-check" name="glyphs" id="no_glyphs" autocomplete="off" value="blank" v-model="icons">
          <label class="btn btn-outline-primary" for="no_glyphs">No Glyphs</label>
        </div>
        <button type="button" :class="['btn', 'btn-sm', autoReload ? 'btn-success' : 'btn-warning']"  @click="toggleAutoReload">{{ autoReload ? "Stop Auto Reload" : "Start Auto Reload" }}</button>
    </div>
  </div>
  </h4>

  <div v-if="noRowsPrometheus && !overview.length" :class="['alert', 'alert-'+noRowsTypePrometheus, 'alert-dismissible']" role="alert">
     <pre v-html="noRowsPrometheus" style="font-size: larger; margin-bottom: 0rem;"></pre>
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  </div>
  <div :class="showContainerClass ? 'container-xxl flex-grow-1 container-p-y' : ''">
    <div class="card">
      <div class="alert alert-info alert-dismissible" role="alert">
        <div class="row">
          <div class="col col-1"><box-icon :name="icons === 'default' ? 'check-circle' : 'circle'" type="solid" color="#198754"></box-icon></div>
          <div class="col col-9"><i><strong>OK</strong></i></div>
        </div>
        <div class="row">
          <div class="col col-1"><box-icon :name="icons === 'default' ? 'info-circle' : 'circle'" type="solid" color="#FFC107"></box-icon></div>
          <div class="col col-9"><i>When Firing and NHC is <strong>Disabled</strong>.</i></div>
        </div>
        <div class="row">
          <div class="col col-1"><box-icon :name="icons === 'default' ? 'error-circle' : 'circle'" type="solid" color="#DC3545"></box-icon></div>
          <div class="col col-9"><i>When Firing and NHC is <strong>Enabled</strong>.</i></div>
        </div>
        <div class="row">
          <div class="col col-1"><box-icon :name="icons === 'default' ? 'x-circle' : 'circle'" type="solid" color="#000000"></box-icon></div>
          <div class="col col-9"><i>When Host is <strong>Down</strong>.</i></div>
        </div>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      </div>

      <div v-if="overview.length && overview.length > 0 && overview.length <= 101">
        <table id="dataTableOverview" class="table table-bordered table-striped table-hover caption-top">
          <thead>
            <tr>
              <th>#</th>
              <th>Node(s)</th>
              <th>Generic Rules</th>
              <th>Services</th>
              <th>Node H/W</th>
              <th>Other Rules</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in overview" :key="row.hostname">
              <td>{{ index +1 }}</td>
              <td :class="{'text-danger': !row.state}" :data-tippy-content="!row.state ? `Node ${row.hostname} is Down.` : `Node ${row.hostname} is UP.`">{{ row.hostname }}</td>
              <td>
                <template v-if="row.state === false">
                  <box-icon v-if="row.genericRules === null" :name="icons === 'default' ? 'x-circle' : 'circle'" type="solid" color="#000000" :data-tippy-content="`Node ${row.hostname} is Down.`"></box-icon>
                  <box-icon v-else-if="row.genericRules === false" :name="icons === 'default' ? 'x-circle' : 'circle'" type="solid" color="#000000" :data-tippy-content="`Node ${row.hostname} is Down.`"></box-icon>
                  <box-icon v-else-if="row.genericRules === true" :name="icons === 'default' ? 'x-circle' : 'circle'" type="solid" color="#000000" :data-tippy-content="`Node ${row.hostname} is Down.`"></box-icon>
                </template>
                <template v-else>
                  <OverviewAlerts :alerts="row.genericAlerts || []" :hostname="row.hostname" ruleType="Generic Rules" :modalId="`${row.hostname}_Generic`" @modal-open="stopAutoReload" @modal-close="startAutoReload" />
                  <box-icon v-if="row.genericRules === null" :name="icons === 'default' ? 'check-circle' : 'circle'" type="solid" color="#198754" :data-tippy-content="`Node  Rules are OK.`"></box-icon>
                  <box-icon v-else-if="row.genericRules === false" data-bs-toggle="modal" :data-bs-target="`#${row.hostname}_Generic`" :name="icons === 'default' ? 'info-circle' : 'circle'" type="solid" color="#FFC107" :data-tippy-content="`Node ${row.hostname} Rules NHC is Disabled.`"></box-icon>
                  <box-icon v-else-if="row.genericRules === true" data-bs-toggle="modal" :data-bs-target="`#${row.hostname}_Generic`" :name="icons === 'default' ? 'error-circle' : 'circle'" type="solid" color="#DC3545" :data-tippy-content="`Node ${row.hostname} Rules NHC is Enabled.`"></box-icon>
                </template>
              </td>
              <td>
                <template v-if="row.state === false">
                  <box-icon v-if="row.services === null" :name="icons === 'default' ? 'x-circle' : 'circle'" type="solid" color="#000000" :data-tippy-content="`Node ${row.hostname} is Down.`"></box-icon>
                  <box-icon v-else-if="row.services === false" :name="icons === 'default' ? 'x-circle' : 'circle'" type="solid" color="#000000" :data-tippy-content="`Node ${row.hostname} is Down.`"></box-icon>
                  <box-icon v-else-if="row.services === true" :name="icons === 'default' ? 'x-circle' : 'circle'" type="solid" color="#000000" :data-tippy-content="`Node ${row.hostname} is Down.`"></box-icon>
                </template>
                <template v-else>
                  <OverviewAlerts :alerts="row.servicesAlerts || []" :hostname="row.hostname" ruleType="Service Rules" :modalId="`${row.hostname}_Service`" @modal-open="stopAutoReload" @modal-close="startAutoReload" />
                  <box-icon v-if="row.services === null" :name="icons === 'default' ? 'check-circle' : 'circle'" type="solid" color="#198754" :data-tippy-content="`Node ${row.hostname} Services are OK.`"></box-icon>
                  <box-icon v-else-if="row.services === false" data-bs-toggle="modal" :data-bs-target="`#${row.hostname}_Service`" :name="icons === 'default' ? 'info-circle' : 'circle'" type="solid" color="#FFC107" :data-tippy-content="`Node ${row.hostname} Services NHC is Disabled.`"></box-icon>
                  <box-icon v-else-if="row.services === true" data-bs-toggle="modal" :data-bs-target="`#${row.hostname}_Service`" :name="icons === 'default' ? 'error-circle' : 'circle'" type="solid" color="#DC3545" :data-tippy-content="`Node ${row.hostname} Services NHC is Enabled.`"></box-icon>
                </template>
              </td>
              <td>
                <template v-if="row.state === false">
                  <box-icon v-if="row.hardware === null" :name="icons === 'default' ? 'x-circle' : 'circle'" type="solid" color="#000000" :data-tippy-content="`Node ${row.hostname} is Down.`"></box-icon>
                  <box-icon v-else-if="row.hardware === false" :name="icons === 'default' ? 'x-circle' : 'circle'" type="solid" color="#000000" :data-tippy-content="`Node ${row.hostname} is Down.`"></box-icon>
                  <box-icon v-else-if="row.hardware === true" :name="icons === 'default' ? 'x-circle' : 'circle'" type="solid" color="#000000" :data-tippy-content="`Node ${row.hostname} is Down.`"></box-icon>
                </template>
                <template v-else>
                  <OverviewAlerts :alerts="row.hardwareAlerts || []" :hostname="row.hostname" ruleType="Hardware Rules" :modalId="`${row.hostname}_Hardware`" @modal-open="stopAutoReload" @modal-close="startAutoReload" />
                  <box-icon v-if="row.hardware === null" :name="icons === 'default' ? 'check-circle' : 'circle'" type="solid" color="#198754" :data-tippy-content="`Node ${row.hostname} Hardware are OK.`"></box-icon>
                  <box-icon v-else-if="row.hardware === false" data-bs-toggle="modal" :data-bs-target="`#${row.hostname}_Hardware`" :name="icons === 'default' ? 'info-circle' : 'circle'" type="solid" color="#FFC107" :data-tippy-content="`Node ${row.hostname} Hardware NHC is Disabled.`"></box-icon>
                  <box-icon v-else-if="row.hardware === true" data-bs-toggle="modal" :data-bs-target="`#${row.hostname}_Hardware`" :name="icons === 'default' ? 'error-circle' : 'circle'" type="solid" color="#DC3545" :data-tippy-content="`Node ${row.hostname} Hardware NHC is Enabled.`"></box-icon>
                </template>
              </td>
              <td>
                <template v-if="row.state === false">
                  <box-icon v-if="row.other === null" :name="icons === 'default' ? 'x-circle' : 'circle'" type="solid" color="#000000" :data-tippy-content="`Node ${row.hostname} is Down.`"></box-icon>
                  <box-icon v-else-if="row.other === false" :name="icons === 'default' ? 'x-circle' : 'circle'" type="solid" color="#000000" :data-tippy-content="`Node ${row.hostname} is Down.`"></box-icon>
                  <box-icon v-else-if="row.other === true" :name="icons === 'default' ? 'x-circle' : 'circle'" type="solid" color="#000000" :data-tippy-content="`Node ${row.hostname} is Down.`"></box-icon>
                </template>
                <template v-else>
                  <OverviewAlerts :alerts="row.otherAlerts || []" :hostname="row.hostname" ruleType="Other Rules" :modalId="`${row.hostname}_Other`" @modal-open="stopAutoReload" @modal-close="startAutoReload" />
                  <box-icon v-if="row.other === null" :name="icons === 'default' ? 'check-circle' : 'circle'" type="solid" color="#198754" :data-tippy-content="`Node ${row.hostname} Other are OK.`"></box-icon>
                  <box-icon v-else-if="row.other === false" data-bs-toggle="modal" :data-bs-target="`#${row.hostname}_Other`" :name="icons === 'default' ? 'info-circle' : 'circle'" type="solid" color="#FFC107" :data-tippy-content="`Node ${row.hostname} Other NHC is Disabled.`"></box-icon>
                  <box-icon v-else-if="row.other === true" data-bs-toggle="modal" :data-bs-target="`#${row.hostname}_Other`" :name="icons === 'default' ? 'error-circle' : 'circle'" type="solid" color="#DC3545" :data-tippy-content="`Node ${row.hostname} Other NHC is Enabled.`"></box-icon>
                </template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="overview.length && overview.length > 101 && overview.length <= 251">
        <table class="table table-bordered table-striped table-hover caption-top">
          <tbody>
            <tr v-for="(chunk, rowIndex) in overviewCompact" :key="rowIndex">
              <td v-for="(row) in chunk" :key="row.hostname">
                <span :class="{'text-danger': !row.state}" class="me-2" :data-tippy-content="!row.state ? `Node ${row.hostname} is Down.` : `Node ${row.hostname} is UP.`">{{ row.hostname }}</span>
                <span class="d-inline-flex gap-1 align-items-center">
                  <template v-if="row.state === false">
                    <box-icon v-if="row.genericRules === null" :name="icons === 'default' ? 'x-circle' : 'circle'" type="solid" color="#000000" :data-tippy-content="`Node ${row.hostname} is Down.`"></box-icon>
                    <box-icon v-else-if="row.genericRules === false" :name="icons === 'default' ? 'x-circle' : 'circle'" type="solid" color="#000000" :data-tippy-content="`Node ${row.hostname} is Down.`"></box-icon>
                    <box-icon v-else-if="row.genericRules === true" :name="icons === 'default' ? 'x-circle' : 'circle'" type="solid" color="#000000" :data-tippy-content="`Node ${row.hostname} is Down.`"></box-icon>
                  </template>
                  <template v-else>
                    <box-icon v-if="row.genericRules === null" :name="icons === 'default' ? 'check-circle' : 'circle'" type="solid" color="#198754" :data-tippy-content="`Node  Rules are OK.`"></box-icon>
                    <box-icon v-else-if="row.genericRules === false" data-bs-toggle="modal" :data-bs-target="`#${row.hostname}_Generic`" :name="icons === 'default' ? 'info-circle' : 'circle'" type="solid" color="#FFC107" :data-tippy-content="`Node ${row.hostname} Rules NHC is Disabled.`"></box-icon>
                    <box-icon v-else-if="row.genericRules === true" data-bs-toggle="modal" :data-bs-target="`#${row.hostname}_Generic`" :name="icons === 'default' ? 'error-circle' : 'circle'" type="solid" color="#DC3545" :data-tippy-content="`Node ${row.hostname} Rules NHC is Enabled.`"></box-icon>
                    <OverviewAlerts :alerts="row.genericAlerts || []" :hostname="row.hostname" ruleType="Generic Rules" :modalId="`${row.hostname}_Generic`" @modal-open="stopAutoReload" @modal-close="startAutoReload" />
                  </template>

                  <template v-if="row.state === false">
                    <box-icon v-if="row.services === null" :name="icons === 'default' ? 'x-circle' : 'circle'" type="solid" color="#000000" :data-tippy-content="`Node ${row.hostname} is Down.`"></box-icon>
                    <box-icon v-else-if="row.services === false" :name="icons === 'default' ? 'x-circle' : 'circle'" type="solid" color="#000000" :data-tippy-content="`Node ${row.hostname} is Down.`"></box-icon>
                    <box-icon v-else-if="row.services === true" :name="icons === 'default' ? 'x-circle' : 'circle'" type="solid" color="#000000" :data-tippy-content="`Node ${row.hostname} is Down.`"></box-icon>
                  </template>
                  <template v-else>
                    <box-icon v-if="row.services === null" :name="icons === 'default' ? 'check-circle' : 'circle'" type="solid" color="#198754" :data-tippy-content="`Node ${row.hostname} Services are OK.`"></box-icon>
                    <box-icon v-else-if="row.services === false" data-bs-toggle="modal" :data-bs-target="`#${row.hostname}_Service`" :name="icons === 'default' ? 'info-circle' : 'circle'" type="solid" color="#FFC107" :data-tippy-content="`Node ${row.hostname} Services NHC is Disabled.`"></box-icon>
                    <box-icon v-else-if="row.services === true" data-bs-toggle="modal" :data-bs-target="`#${row.hostname}_Service`" :name="icons === 'default' ? 'error-circle' : 'circle'" type="solid" color="#DC3545" :data-tippy-content="`Node ${row.hostname} Services NHC is Enabled.`"></box-icon>
                    <OverviewAlerts :alerts="row.servicesAlerts || []" :hostname="row.hostname" ruleType="Service Rules" :modalId="`${row.hostname}_Service`" @modal-open="stopAutoReload" @modal-close="startAutoReload" />
                  </template>

                  <template v-if="row.state === false">
                    <box-icon v-if="row.hardware === null" :name="icons === 'default' ? 'x-circle' : 'circle'" type="solid" color="#000000" :data-tippy-content="`Node ${row.hostname} is Down.`"></box-icon>
                    <box-icon v-else-if="row.hardware === false" :name="icons === 'default' ? 'x-circle' : 'circle'" type="solid" color="#000000" :data-tippy-content="`Node ${row.hostname} is Down.`"></box-icon>
                    <box-icon v-else-if="row.hardware === true" :name="icons === 'default' ? 'x-circle' : 'circle'" type="solid" color="#000000" :data-tippy-content="`Node ${row.hostname} is Down.`"></box-icon>
                  </template>
                  <template v-else>
                    <box-icon v-if="row.hardware === null" :name="icons === 'default' ? 'check-circle' : 'circle'" type="solid" color="#198754" :data-tippy-content="`Node ${row.hostname} Hardware are OK.`"></box-icon>
                    <box-icon v-else-if="row.hardware === false" data-bs-toggle="modal" :data-bs-target="`#${row.hostname}_Hardware`" :name="icons === 'default' ? 'info-circle' : 'circle'" type="solid" color="#FFC107" :data-tippy-content="`Node ${row.hostname} Hardware NHC is Disabled.`"></box-icon>
                    <box-icon v-else-if="row.hardware === true" data-bs-toggle="modal" :data-bs-target="`#${row.hostname}_Hardware`" :name="icons === 'default' ? 'error-circle' : 'circle'" type="solid" color="#DC3545" :data-tippy-content="`Node ${row.hostname} Hardware NHC is Enabled.`"></box-icon>
                    <OverviewAlerts :alerts="row.hardwareAlerts || []" :hostname="row.hostname" ruleType="Hardware Rules" :modalId="`${row.hostname}_Hardware`" @modal-open="stopAutoReload" @modal-close="startAutoReload" />
                  </template>

                  <template v-if="row.state === false">
                    <box-icon v-if="row.other === null" :name="icons === 'default' ? 'x-circle' : 'circle'" type="solid" color="#000000" :data-tippy-content="`Node ${row.hostname} is Down.`"></box-icon>
                    <box-icon v-else-if="row.other === false" :name="icons === 'default' ? 'x-circle' : 'circle'" type="solid" color="#000000" :data-tippy-content="`Node ${row.hostname} is Down.`"></box-icon>
                    <box-icon v-else-if="row.other === true" :name="icons === 'default' ? 'x-circle' : 'circle'" type="solid" color="#000000" :data-tippy-content="`Node ${row.hostname} is Down.`"></box-icon>
                  </template>
                  <template v-else>
                    <box-icon v-if="row.other === null" :name="icons === 'default' ? 'check-circle' : 'circle'" type="solid" color="#198754" :data-tippy-content="`Node ${row.hostname} Other are OK.`"></box-icon>
                    <box-icon v-else-if="row.other === false" data-bs-toggle="modal" :data-bs-target="`#${row.hostname}_Other`" :name="icons === 'default' ? 'info-circle' : 'circle'" type="solid" color="#FFC107" :data-tippy-content="`Node ${row.hostname} Other NHC is Disabled.`"></box-icon>
                    <box-icon v-else-if="row.other === true" data-bs-toggle="modal" :data-bs-target="`#${row.hostname}_Other`" :name="icons === 'default' ? 'error-circle' : 'circle'" type="solid" color="#DC3545" :data-tippy-content="`Node ${row.hostname} Other NHC is Enabled.`"></box-icon>
                    <OverviewAlerts :alerts="row.otherAlerts || []" :hostname="row.hostname" ruleType="Other Rules" :modalId="`${row.hostname}_Other`" @modal-open="stopAutoReload" @modal-close="startAutoReload" />
                  </template>
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>


      <div v-if="overview.length && overview.length > 251">
        <table class="table table-bordered table-striped table-hover caption-top">
          <tbody>
            <tr v-for="(chunk, rowIndex) in overviewSuperCompact" :key="rowIndex">
              <td v-for="(row) in chunk" :key="row.hostname">
                <span class="d-inline-flex gap-1 align-items-center">
                  <template v-if="row.state === false">
                    <box-icon :name="icons === 'default' ? 'x-circle' : 'circle'" type="solid" color="#000000" :data-tippy-content="`Node ${row.hostname} is Down.`"></box-icon>
                  </template>
                  <template v-else>
                    <box-icon v-if="[row.genericRules, row.services, row.hardware, row.other].some(val => val === true)" data-bs-toggle="modal" :data-bs-target="`#${row.hostname}_All`" :name="icons === 'default' ? 'error-circle' : 'circle'" type="solid" color="#DC3545" :data-tippy-content="`Node ${row.hostname} Rules NHC is Enabled.`"></box-icon>
                    <box-icon v-else-if="[row.genericRules, row.services, row.hardware, row.other].some(val => val === false)" data-bs-toggle="modal" :data-bs-target="`#${row.hostname}_All`" :name="icons === 'default' ? 'info-circle' : 'circle'" type="solid" color="#FFC107" :data-tippy-content="`Node ${row.hostname} Rules NHC is Disabled.`"></box-icon>
                    <box-icon v-else-if="[row.genericRules, row.services, row.hardware, row.other].some(val => val === null)" data-bs-toggle="modal" :data-bs-target="`#${row.hostname}_All`" :name="icons === 'default' ? 'check-circle' : 'circle'" type="solid" color="#198754" :data-tippy-content="`Node  Rules are OK.`"></box-icon>
                    <OverviewAlerts :alerts="row.allAlerts || []" :hostname="row.hostname" ruleType="All Rules" :modalId="`${row.hostname}_All`" @modal-open="stopAutoReload" @modal-close="startAutoReload" />
                  </template>
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>


  </div>
</div>


</template>
