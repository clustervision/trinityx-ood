<script setup lang="ts">

import './assets/fonts/boxicons.css';
import './assets/css/core.css';
import './assets/css/theme-default.css';
import './assets/css/codemirror.min.css';
import './assets/css/material-darker.min.css';
import './assets/css/app.css';
import './assets/js/jquery.js';
import './assets/js/bootstrap.js';
import './assets/js/main.js';
import './assets/js/codemirror.min.js';
import './assets/js/javascript.min.js';
import './assets/js/yaml.min.js';
import './assets/js/js-yaml.min.js';
import './assets/js/app.js';

import TopNavigation from '@/views/TopNavigation.vue';
import SubNavigation from '@/views/SubNavigation.vue';
import HomeView from '@/views/HomeView.vue';
import FooterBar from '@/views/FooterBar.vue';
</script>


<template>

  <header>
    <TopNavigation />
    <SubNavigation />
  </header>


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
                <HomeView>
                  <div class="promql"></div>
                  <textarea class="promql"></textarea>
                </HomeView>

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
        <FooterBar />
        <div class="content-backdrop fade"></div>
      </div>
    </div>
    <div class="layout-overlay layout-menu-toggle"></div>
  </div>








  <div v-if="showSuccessToast" class="bs-toast toast toast-placement-ex m-2 fade bg-success top-0 end-0 show" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="2000">
    <div class="toast-header">
      <i class="bx bx-bell me-2"></i>
      <div class="me-auto fw-medium">Configuration</div>
      <small>0 seconds ago</small>
      <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>
    <div class="toast-body">Configuration Saved successfully.</div>
  </div>

  <div v-if="showfailedToast" class="bs-toast toast toast-placement-ex m-2 fade bg-danger top-0 end-0 show" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="2000">
    <div class="toast-header">
      <i class="bx bx-bell me-2"></i>
      <div class="me-auto fw-medium">Configuration</div>
      <small>0 seconds ago</small>
      <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>
    <div class="toast-body"></div>
  </div>

  <div v-if="showwarningToast" class="bs-toast toast toast-placement-ex m-2 fade bg-warning top-0 end-0 show" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="2000">
    <div class="toast-header">
      <i class="bx bx-bell me-2"></i>
      <div class="me-auto fw-medium">Configuration</div>
      <small>0 seconds ago</small>
      <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>
    <div class="toast-body"></div>
  </div>




</template>


<script lang="ts">
export default {
  data() {
    let url = window.location.href;
    url = url.replace('#', '');
    return {
      configuration: null,
      activeButton: 1,
      previousButton: null,
      classMap: {
        critical: 'btn-dark',
        danger: 'btn-danger',
        warning: 'btn-warning',
        info: 'btn-info',
      },
      url_real: url,
      url: 'http://vmware-controller1.cluster:7755',
      showSuccessToast: false,
      showfailedToast: false,
      showwarningToast: false,
    };
  },
  methods: {
    showSuccessToast() {
      this.showSuccessToast = true;
      setTimeout(() => {
        this.showSuccessToast = false;
      }, 2000);
    },

    showfailedToast() {
      this.showfailedToast = true;
      setTimeout(() => {
        this.showfailedToast = false;
      }, 2000);
    },

    showwarningToast() {
      this.showwarningToast = true;
      setTimeout(() => {
        this.showwarningToast = false;
      }, 2000);
    },
    // ... methods to show other toasts
  },
};
</script>
