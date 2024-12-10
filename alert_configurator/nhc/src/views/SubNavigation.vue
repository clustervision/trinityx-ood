
<template>
  <div class="row sub-navbar">
      <div class="col col-2">Manage Node Health Checks</div>
      <div class="col col-1">
        <button type="button" class="btn btn-primary btn-sm" id="add_rule" data-bs-toggle="modal" data-bs-target="#rule_modal_">Add Alert Rule</button>
      </div>
      <div class="col col-1">
        <button type="button" class="btn btn-warning btn-sm" id="edit_configuration" data-bs-toggle="modal" data-bs-target="#edit_config">Edit Configuration</button>
      </div>
      <div class="col col-8"></div>
    </div>


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

</template>

<script lang="ts">

export default {
  name: "SubNavigation",
}

</script>
