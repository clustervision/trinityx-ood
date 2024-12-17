<script setup lang="ts">
import CodeMirrorEditor from '@/components/CodeMirrorEditor.vue';
</script>
<template>

  <div class="row sub-navbar">
      <div class="col col-2">Manage Node Health Checks</div>
      <div class="col col-1">
        <button type="button" class="btn btn-primary btn-sm" id="add_rule" data-bs-toggle="modal" data-bs-target="#add_rule_rule_modal">Add Alert Rule</button>
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
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="row">
              <div class="col mb-12">
                <!-- <label for="configuration" class="form-label">Configuration File: <span style="text-transform: lowercase; color: #007bff !important">file path</span></label> -->
                <!-- <button type="button" @click="switchMode('JSON')" class="btn btn-primary btn-sm">JSON View</button>
                <button type="button" @click="switchMode('YAML')" class="btn btn-warning btn-sm">YAML View</button> :ContentType="currentContentType"-->
                <div>
                  <CodeMirrorEditor :editorHeight="600"  :Content="Content" :ContentType="ContentType" @Toast="$emit('Toast', $event)" />
                </div>

              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Close</button>
            <button type="button" @click.prevent="save_configuration()" id="save_configuration" class="btn btn-primary">Save changes</button>
          </div>
        </div>
      </div>
    </div>

</template>

<script lang="ts">

export default {
  name: "SubNavigation",
  props: {
    save_configuration: {
      type: Function,
      required: true,
    },
    Content: {
      type: String,
      required: true,
    },
    ContentType: {
      type: String,
      required: true,
    },
  },
  emits: ['Toast'],
};
</script>
