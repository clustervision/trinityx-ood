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



// import HomeView from './views/HomeView.vue';





</script>


<template>

  <!-- <div class="wrapper">
    <NHC trix_config="/trinity/local/etc/prometheus_server/rules/trix.rules" />
    <HomeView />
  </div> -->


  <header>
    <nav class="navbar shadow-sm navbar-light">
      <ol class="breadcrumb bg-transparent d-flex align-items-center">
        <a href="/" aria-current="page" role="menuitem">
          <img src="@/assets/img/logo.png" class="img-logo" />
        </a>
        <li class="breadcrumb-item"><a class="align-middle" href="/">Home</a></li>
        <li class="breadcrumb-item"><a class="align-middle" href="/">Alert Configurator</a></li>
      </ol>
    </nav>

    <div class="row sub-navbar">
      <div class="col col-2">Manage Node Health Checks</div>
      <div class="col col-1">
        <button
          type="button"
          class="btn btn-primary btn-sm"
          id="add_rule"
          data-bs-toggle="modal"
          data-bs-target="#rule_modal_"
        >
          Add Alert Rule
        </button>
      </div>
      <div class="col col-1">
        <button
          type="button"
          class="btn btn-warning btn-sm"
          id="edit_configuration"
          data-bs-toggle="modal"
          data-bs-target="#edit_config"
        >
          Edit Configuration
        </button>
      </div>
      <div class="col col-8"></div>
    </div>

    <!-- Edit Configuration Modal -->
    <div class="modal fade" id="edit_config" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-xl" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="exampleModalLabel4">Edit Configuration</h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <div class="row">
              <div class="col mb-12">
                <label for="configuration" class="form-label"
                  >Configuration File:
                  <span style="text-transform: lowercase; color: #007bff !important"
                    >file path</span
                  ></label
                >
                <button type="button" id="jsonModeBtn" class="btn btn-primary btn-sm">
                  Switch to JSON Mode
                </button>
                <button type="button" id="yamlModeBtn" class="btn btn-warning btn-sm">
                  Switch to YAML Mode
                </button>
                <div id="jsonEditor" style="height: 600px; border: 1px solid #ddd"></div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">
              Close
            </button>
            <button type="button" id="save_configuration" class="btn btn-primary">
              Save changes
            </button>
          </div>
        </div>
      </div>
    </div>
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
