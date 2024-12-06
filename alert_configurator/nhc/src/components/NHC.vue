<script setup lang="ts">
defineProps<{
  msg: string
}>()
</script>

<template>
  <div class="layout-wrapper layout-content-navbar">
    <div class="layout-container">
      <div class="content-wrapper">
        <div id="spinner-overlay" class="spinner-overlay">
          <div id="spinner" class="d-flex justify-content-center">
            <div
              class="spinner-border spinner-border-lg text-success"
              style="width: 10rem; height: 10rem"
              role="status"
            >
              <span class="visually-hidden">Saving Configuration...</span>
            </div>
          </div>
        </div>

        <div class="container-xxl flex-grow-1 container-p-y" style="max-width: none">
          <h4 class="fw-bold py-3 mb-4">
            <span class="text-muted fw-light"> Monitoring /</span> Alert Configurator
          </h4>
          <!-- Bordered Table -->
          <div class="card">
            <h5 class="card-header">Rules</h5>
            <div class="card-body">
              <div class="table-responsive text-nowrap">
                <div id="modal-container"></div>
                <div id="editor-container"></div>

                <table
                  class="table table-bordered table-striped table-hover table-responsive"
                  id="alert-table"
                >
                  <thead>
                    <tr>
                      <th scope="col">#</th>
                      <th scope="col">Group</th>
                      <th scope="col">Rule</th>
                      <th scope="col">Enable</th>
                      <th scope="col">NHC</th>
                      <th scope="col">Priority</th>
                      <th scope="col">Actions</th>
                    </tr>
                  </thead>
                  <tbody></tbody>
                </table>
              </div>
            </div>
          </div>
          <!--/ Bordered Table -->
        </div>
        <!-- / Content -->
        <hr class="my-5" />
        <footer class="content-footer footer bg-footer-theme">
          <div
            class="container-xxl d-flex flex-wrap justify-content-between py-2 flex-md-row flex-column"
          >
            <div class="mb-2 mb-md-0">
              © 2023, made with ❤️ by
              <a href="https://clustervision.com/" target="_blank" class="footer-link fw-bolder"
                >ClusterVision</a
              >
            </div>
            <div>
              <a href="/license_info" class="footer-link me-4" target="_blank">License</a>
              <a
                href="https://github.com/clustervision/trinityX"
                target="_blank"
                class="footer-link me-4"
                >Documentation</a
              >
              <a href="https://support.clustervision.com/" target="_blank" class="footer-link me-4"
                >Support</a
              >
            </div>
          </div>
        </footer>
        <div class="content-backdrop fade"></div>
      </div>
    </div>
    <div class="layout-overlay layout-menu-toggle"></div>
  </div>
</template>
