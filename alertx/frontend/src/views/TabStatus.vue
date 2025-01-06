
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

<script setup lang="ts">
// import { ref, onMounted, reactive, toRaw } from 'vue';
import axios from 'axios';


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

const props = defineProps({
  statusAPI: {
    type: String,
    required: true,
  },

});


async function fetchStatus() {
  const response = await axios.get(props.statusAPI);
  // this.configuration =  reactive(response.data);
  // this.configuration = { ...this.configuration };
  // this.Content = JSON.stringify({ ...this.configuration }, null, 2);
  // return this.configuration;
  console.log(response.status);
  console.log(response.data);
  if(response.status === 200){
    return response.data;
  } else {
    return {"status": response.status, "message": response.data};
  }

}

let statusLog:Array = [];

async function showStatus(){
  const logs = await fetchStatus();
  // console.log(logs.data.groups[0].rules);
  // console.log(logs.data.groups[0].rules[0]);
  // console.log(logs.data.groups[0].rules[0].alerts);
  // console.log(logs.data.groups[0].rules[0].state);
  // console.log(logs.data.groups[0].rules[0].name);
  // console.log(logs.data.groups[0].rules[0].lastEvaluation);
  // console.log(logs.data.groups[0].rules[0].labels.severity);

  for (let index = 0; index < logs.data.groups[0].rules.length; index++) {
    // console.log(index);
    // console.log(logs.data.groups[0].rules[index]);
    for (let indexNested = 0; indexNested < logs.data.groups[0].rules[index].alerts.length; indexNested++) {
    // console.log(indexNested);
    // console.log(logs.data.groups[0].rules[index].alerts[indexNested].labels.alertname);
    // console.log(logs.data.groups[0].rules[index].alerts[indexNested].labels.hostname);
    // console.log(logs.data.groups[0].rules[index].alerts[indexNested].state);
    // console.log(logs.data.groups[0].rules[index].alerts[indexNested].activeAt);
    statusLog.push(logs.data.groups[0].rules[index].alerts[indexNested])
    }
  }
}
const getStatus = showStatus();
console.log(getStatus);
</script>
