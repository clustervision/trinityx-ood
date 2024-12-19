
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
              <label for="configuration" class="form-label">Configuration File: <span style="text-transform: lowercase; color: #007bff !important">{{ rulesFile }}</span></label> &nbsp;&nbsp;
              <CodeMirrorEditor @update:Content="syncFromCodeMirror" ref="codeMirrorRef" editorHeight="600" :Content="Content" :ContentType="ContentType" @Toast="$emit('toast', $event)" />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Close</button>
          <button type="button" @click.prevent="save_configuration(newContent)" id="save_configuration" class="btn btn-primary">Save changes</button>
        </div>
      </div>
    </div>
  </div>

</template>

<script lang="ts" setup>
import { type PropType } from 'vue';
import CodeMirrorEditor from '@/components/CodeMirrorEditor.vue';
import { ref } from 'vue';
// import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  rulesFile: {
    type: String,
    required: true,
  },
  save_configuration: {
    type: Function,
    required: true,
  },
  Content: {
    type: String,
    required: true,
  },
  ContentType: {
    type: String as PropType<'JSON' | 'YAML'>,
    required: true,
  },
});

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const emit = defineEmits(['toast']);
const newContent = ref(props.Content);

const syncFromCodeMirror = (content: string) => {
  newContent.value = content;
};

</script>
