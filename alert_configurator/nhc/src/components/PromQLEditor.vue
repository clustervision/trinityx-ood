<!-- <template>
   <div :id="editorId" class="promql-container">
      <div class="promql"></div>
   </div>
 </template>

 <script setup lang="ts">
 import { onMounted } from 'vue';
 import {PromQLExtension} from '@prometheus-io/codemirror-promql';
 import {basicSetup} from 'codemirror';
 import {EditorState} from '@codemirror/state';
 import {EditorView} from '@codemirror/view';

 const props = defineProps({
  promQLurl: {
    type: String,
    required: true,
  },
  editorId: {
    type: String,
    required: true,
  },
  editorRule: {
    type: String,
    required: true,
  },
});

onMounted(() => {
  try {
    const parentElement = document.getElementById(props.editorId);
    if (!parentElement) {
      console.error("Element with ID 'editor-container' not found.");
      return;
    }

    const promQL = new PromQLExtension();
    promQL.setComplete({ maxMetricsMetadata: 10000, remote: { httpErrorHandler: (error: string) => console.error(error), httpMethod: 'GET', url: props.promQLurl } });

    new EditorView({
      state: EditorState.create({
        doc: props.editorRule,
        extensions: [basicSetup, promQL.asExtension()],
      }),
      parent: parentElement,
    });
  } catch (error) {
    console.error("Error initializing the editor:", error);
  }
});

</script>


<style>
.promql {
  position: relative !important;
  z-index: 1055 !important;
}
</style> -->
<template>
  <div :id="editorId" class="promql-container">
    <div class="promql"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, defineProps, defineEmits } from 'vue';
import { PromQLExtension } from '@prometheus-io/codemirror-promql';
import { basicSetup } from 'codemirror';
import { EditorState } from '@codemirror/state';
import { EditorView } from '@codemirror/view';

// Define props
const props = defineProps({
  promQLurl: {
    type: String,
    required: true,
  },
  editorId: {
    type: String,
    required: true,
  },
  editorRule: {
    type: String,
    required: true,
  },
});

// Define emits
const emit = defineEmits(['update:editorRule']);

// Reactive reference for the editor instance
const editorInstance = ref<EditorView | null>(null);

// Initialize the PromQL editor
onMounted(() => {
  try {
    const parentElement = document.getElementById(props.editorId);
    if (!parentElement) {
      console.error(`Element with ID '${props.editorId}' not found.`);
      return;
    }

    const promQL = new PromQLExtension();
    promQL.setComplete({
      maxMetricsMetadata: 10000,
      remote: {
        httpErrorHandler: (error: string) => console.error(error),
        httpMethod: 'GET',
        url: props.promQLurl,
      },
    });

    // Initialize the CodeMirror editor
    editorInstance.value = new EditorView({
      state: EditorState.create({
        doc: props.editorRule,
        extensions: [
          basicSetup,
          promQL.asExtension(),
          EditorView.updateListener.of((update) => {
            if (update.docChanged) {
              // Emit the updated content to the parent
              emit('update:editorRule', editorInstance.value?.state.doc.toString() || '');
            }
          }),
        ],
      }),
      parent: parentElement,
    });
  } catch (error) {
    console.error('Error initializing the editor:', error);
  }
});

// Watch for changes in the editorRule prop and update the editor content
watch(
  () => props.editorRule,
  (newRule) => {
    if (editorInstance.value && editorInstance.value.state.doc.toString() !== newRule) {
      editorInstance.value.dispatch({
        changes: {
          from: 0,
          to: editorInstance.value.state.doc.length,
          insert: newRule,
        },
      });
    }
  }
);
</script>

<style>
.promql {
  position: relative !important;
  z-index: 1055 !important;
}
</style>
