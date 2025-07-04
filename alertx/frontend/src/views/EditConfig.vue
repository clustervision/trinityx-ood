
<template>
  <button type="button" class="btn btn-sm btn-info me-2" data-bs-toggle="modal" :data-bs-target="`#wizard_modal_${props.configType}`"><strong>Rule Wizard</strong></button>
  <button type="button" class="btn btn-primary btn-sm me-2" id="add_rule" data-bs-toggle="modal" :data-bs-target="`#rule_modal_${props.configType}_0`">Add Alert Rule</button>
  <button type="button" class="btn btn-warning btn-sm" id="edit_configuration" data-bs-toggle="modal" :data-bs-target="`#edit_${props.configType}_config`">Edit Configuration</button>

  <div class="modal fade" :id="`edit_${props.configType}_config`" tabindex="-1">
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
          <button type="button" @click.prevent="save_configuration(props.configType, newContent, `edit_${props.configType}_config`)" class="btn btn-primary">Save changes</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { type PropType } from 'vue';
import CodeMirrorEditor from '@/components/CodeMirrorEditor.vue';
import { ref } from 'vue';

const props = defineProps({
  configType: {
    type: String,
    required: true,
  },
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
