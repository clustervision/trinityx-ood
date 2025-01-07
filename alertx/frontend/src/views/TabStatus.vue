<script setup lang="ts"></script>
<template>
  <div class="row">

    <div class="col-md">
      <small class="text-light fw-medium">Basic Accordion</small>
      <div class="accordion mt-4" id="accordionExample">
        <div class="card accordion-item">
          <h2 class="accordion-header" id="headingOne">
            <button type="button" class="accordion-button" data-bs-toggle="collapse" data-bs-target="#accordionOne" aria-expanded="true" aria-controls="accordionOne">
              Active (In Progress)<span style="color: red; font-weight: bold;"> FAKE DATA; Need a API to show Data</span>
            </button>
          </h2>

          <div id="accordionOne" class="accordion-collapse collapse show" data-bs-parent="#accordionExample" style="">
            <div class="accordion-body">


              <div class="table table-bordered table-striped table-hover table-responsive text-nowrap">
                <table class="table table-bordered">
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>Date</th>
                      <th>Severity</th>
                      <th>Rule</th>
                      <th>Affected</th>
                    </tr>
                  </thead>
                  <tbody>
                  <tr v-for="(rule, ruleIndex) in rules" :key="ruleIndex" style="background-color: aquamarine;">
                    <td>{{ ruleIndex }}</td>
                    <td>{{ rule.name }}</td>
                    <td>{{ rule.state }}</td>
                    <td>{{ rule.labels.severity }}</td>
                    <td>{{ rule.lastEvaluation }}</td>
                    <!-- {{ ruleIndex }}
                    {{ rule }} -->
                    <tr v-for="(alert, alertIndex) in rule.alerts" :key="alertIndex" style="background-color:antiquewhite;">
                      <!-- {{ alertIndex }}
                      {{ alert }} -->

                    <td>{{ alertIndex }}</td>
                    <td>{{ alert.labels.alertname }}</td>
                    <td>{{ alert.labels.exporter }}</td>
                    <td>{{ alert.labels.hostname }}</td>
                    <td>{{ alert.labels.instance }}</td>
                    <td>{{ alert.labels.severity }}</td>
                    <td>{{ alert.labels.nhc }}</td>

                    </tr>
                    </tr>
                    
                  </tbody>
                  <!-- <tbody>
                    <tr>
                      <td>1</td>
                      <td>03/01/2015 10:41:56</td>
                      <td><span class="badge bg-label-primary me-1">Active</span></td>
                      <td>Exporter</td>
                      <td>Nothing</td>
                    </tr>
                    <tr>
                      <td>2</td>
                      <td>03/01/2015 10:41:56</td>
                      <td><span class="badge bg-label-success me-1">Completed</span></td>
                      <td>Exporter</td>
                      <td>Nothing</td>
                    </tr>
                    <tr>
                      <td>3</td>
                      <td>03/01/2015 10:41:56</td>
                      <td><span class="badge bg-label-info me-1">Scheduled</span></td>
                      <td>Exporter</td>
                      <td>Nothing</td>
                    </tr>
                    <tr>
                      <td>4</td>
                      <td>03/01/2015 10:41:56</td>
                      <td><span class="badge bg-label-warning me-1">Pending</span></td>
                      <td>Exporter</td>
                      <td>Nothing</td>
                    </tr>
                    <tr>
                      <td>5</td>
                      <td>03/01/2015 10:41:56</td>
                      <td><span class="badge bg-label-primary me-1">Active</span></td>
                      <td>Exporter</td>
                      <td>Nothing</td>
                    </tr> -->
                  <!-- </tbody> -->
                </table>
              </div>


            </div>
          </div>
        </div>
        <div class="card accordion-item">
          <h2 class="accordion-header" id="headingTwo">
            <button type="button" class="accordion-button collapsed" data-bs-toggle="collapse" data-bs-target="#accordionTwo" aria-expanded="false" aria-controls="accordionTwo">
              History<span style="color: red; font-weight: bold;"> FAKE DATA; Need a API to show Data</span>
            </button>
          </h2>
          <div id="accordionTwo" class="accordion-collapse collapse" aria-labelledby="headingTwo" data-bs-parent="#accordionExample" style="">
            <div class="accordion-body">


              <div class="table table-bordered table-striped table-hover table-responsive text-nowrap">
                <table class="table table-bordered">
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>Date</th>
                      <th>Severity</th>
                      <th>Rule</th>
                      <th>Affected</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>1</td>
                      <td>03/01/2015 10:41:56</td>
                      <td><span class="badge bg-label-primary me-1">Active</span></td>
                      <td>Exporter</td>
                      <td>Nothing</td>
                    </tr>
                    <tr>
                      <td>2</td>
                      <td>03/01/2015 10:41:56</td>
                      <td><span class="badge bg-label-success me-1">Completed</span></td>
                      <td>Exporter</td>
                      <td>Nothing</td>
                    </tr>
                    <tr>
                      <td>3</td>
                      <td>03/01/2015 10:41:56</td>
                      <td><span class="badge bg-label-info me-1">Scheduled</span></td>
                      <td>Exporter</td>
                      <td>Nothing</td>
                    </tr>
                    <tr>
                      <td>4</td>
                      <td>03/01/2015 10:41:56</td>
                      <td><span class="badge bg-label-warning me-1">Pending</span></td>
                      <td>Exporter</td>
                      <td>Nothing</td>
                    </tr>
                    <tr>
                      <td>5</td>
                      <td>03/01/2015 10:41:56</td>
                      <td><span class="badge bg-label-primary me-1">Active</span></td>
                      <td>Exporter</td>
                      <td>Nothing</td>
                    </tr>
                  </tbody>
                </table>
              </div>



            </div>
          </div>
        </div>
        <!-- <div class="card accordion-item">
          <h2 class="accordion-header" id="headingThree">
            <button type="button" class="accordion-button collapsed" data-bs-toggle="collapse" data-bs-target="#accordionThree" aria-expanded="false" aria-controls="accordionThree">
              Accordion Item 3
            </button>
          </h2>
          <div id="accordionThree" class="accordion-collapse collapse" aria-labelledby="headingThree" data-bs-parent="#accordionExample" style="">
            <div class="accordion-body">
              Oat cake toffee chocolate bar jujubes. Marshmallow brownie lemon drops cheesecake. Bonbon gingerbread
              marshmallow sweet jelly beans muffin. Sweet roll bear claw candy canes oat cake dragée caramels. Ice cream
              wafer danish cookie caramels muffin.
            </div>
          </div>
        </div> -->
      </div>
    </div>

  </div>

</template>

<script  lang="ts">
// import { ref, onMounted, reactive, toRaw } from 'vue';
import axios from 'axios';


export default {
  props: {
    statusAPI: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      rules: [], // To store the fetched rules
      alerts: [], // Placeholder for alerts, if needed
    };
  },
  async mounted() {
    try {
      const response = await axios.get(this.statusAPI);
      if (response.status === 200) {
        this.rules = response.data.data.groups[0].rules;
      } else {
        console.error("Error fetching rules:", response.status, response.data);
      }
    } catch (error) {
      console.error("Error fetching status:", error);
    }
  },
};

// interface StatusRow {
//   lastEvaluation: string;
//   name: string;
//   labels: {
//     severity: string;
//   };

//   annotations: {
//     description: string;
//   };
//   expr: string;
//   for: string;

// }

// const props = defineProps({
//   statusAPI: {
//     type: String,
//     required: true,
//   },

// });


// async function fetchStatus() {
//   const response = await axios.get(props.statusAPI);
//   if(response.status === 200){
//     return response.data.groups[0].rules;
//   } else {
//     return {"status": response.status, "message": response.data};
//   }
// }


// async function showStatus(){
//   let statusLog:Array = [];

//   const logs = await fetchStatus();
//   // console.log(logs.data.groups[0].rules);
//   // console.log(logs.data.groups[0].rules[0]);
//   // console.log(logs.data.groups[0].rules[0].alerts);
//   // console.log(logs.data.groups[0].rules[0].state);
//   // console.log(logs.data.groups[0].rules[0].name);
//   // console.log(logs.data.groups[0].rules[0].lastEvaluation);
//   // console.log(logs.data.groups[0].rules[0].labels.severity);

//   for (let index = 0; index < logs.data.groups[0].rules.length; index++) {
//     // console.log(index);
//     // console.log(logs.data.groups[0].rules[index]);
//     console.log("==============================");
//     console.log(logs.data.groups[0].rules[index].name);
//     console.log(logs.data.groups[0].rules[index].labels.severity);
//     console.log(logs.data.groups[0].rules[index].state);
//     console.log(logs.data.groups[0].rules[index].lastEvaluation);
//     // statusLog.push(logs.data.groups[0].rules[index].alerts[indexNested])
//     console.log("==============================");

//     for (let indexNested = 0; indexNested < logs.data.groups[0].rules[index].alerts.length; indexNested++) {
//     // console.log(indexNested);
//     console.log("++++++++++++++++++++++++++++++++++");
//     console.log(logs.data.groups[0].rules[index].alerts[indexNested].labels.alertname);
//     console.log(logs.data.groups[0].rules[index].alerts[indexNested].labels.hostname);
//     console.log(logs.data.groups[0].rules[index].alerts[indexNested].state);
//     console.log(logs.data.groups[0].rules[index].alerts[indexNested].activeAt);
//     statusLog.push(logs.data.groups[0].rules[index].alerts[indexNested]);
//     console.log("++++++++++++++++++++++++++++++++++");
//     }
//   }
//   return statusLog;
// }
// showStatus();
// const getStatus:Array = showStatus();
// console.log(getStatus);
// console.log(getStatus[0]);
</script>
