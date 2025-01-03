
<template>
  <div class="row">

    <div class="col-md">
      <small class="text-light fw-medium">Basic Accordion</small>
      <div class="accordion mt-4" id="accordionExample">
        <div class="card accordion-item">
          <h2 class="accordion-header" id="headingOne">
            <button type="button" class="accordion-button" data-bs-toggle="collapse" data-bs-target="#accordionOne" aria-expanded="true" aria-controls="accordionOne">
              Active (In Progress)
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
              History
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

<script lang="ts" setup>



</script>
