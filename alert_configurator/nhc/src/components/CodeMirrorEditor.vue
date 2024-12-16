<script setup lang="ts"></script>

<template>
  <button type="button" @click="switchMode('JSON')" class="btn btn-primary btn-sm">JSON View</button>
  <button type="button" @click="switchMode('YAML')" class="btn btn-warning btn-sm">YAML View</button>
  <div ref="editorContainer" class="editor-container"></div>
</template>

<script lang="ts">
import { ref, onMounted, watch, type PropType } from 'vue';
import { basicSetup } from 'codemirror';
import { EditorState } from '@codemirror/state';
import { EditorView } from '@codemirror/view';
import { json } from '@codemirror/lang-json';
import { yaml } from '@codemirror/lang-yaml';
import { oneDark } from '@codemirror/theme-one-dark';
import jsyaml from 'js-yaml';

export default {
  props: {
    Content: {
      type: String,
      required: true,
    },
    ContentType: {
      type: String as PropType<'JSON' | 'YAML'>,
      required: true,
      validator: (value: string) => ['JSON', 'YAML'].includes(value),
    },
    // onShowErrorToast: {
    //   type: Function as PropType<(message: string) => void>,
    //   required: true,
    // },
  },

  data() {
    return {
      currentContent: this.Content,
      currentContentType: this.ContentType,
    };
  },
  methods: {
    switchMode(mode: string) {
      console.log(`Mode>>>>>>>>> ${mode} Mode`);
      console.log(`Mode>>>>>>>>> ${this.currentContentType} Mode`);
      if (this.currentContentType !== mode) {
        this.currentContentType = mode;
        console.log(`Switched to ${mode} Mode`);
        this.convertContent(mode);
      } else {
        console.log(`Already in ${mode} Mode, no conversion needed`);
        this.$emit('showErrorToast', `Error: Already in ${mode} Mode, no conversion needed`);
      }
    },
    convertContent(mode: string) {
      if (mode === 'JSON') {
        console.log('Converting to JSON...');
      } else if (mode === 'YAML') {
        console.log('Converting to YAML...');
      }
    }
  },



  emits: ['update:Content', 'showErrorToast'],
  setup(props, { emit }) {
    const editorContainer = ref(null);
    let editor = null;

    const createEditorState = (content, contentType) => {
      const langExtension = contentType === 'JSON' ? json() : yaml();
      return EditorState.create({
        doc: content,
        extensions: [
          basicSetup,
          langExtension,
          oneDark,
          EditorView.updateListener.of((update) => {
            if (update.docChanged) {
              emit('update:Content', editor.state.doc.toString());
            }
          }),
        ],
      });
    };

    const updateEditorLanguage = (contentType) => {
      let newContent;
      if (contentType === 'JSON') {
        try {
          newContent = JSON.stringify(jsyaml.load(editor.state.doc.toString()), null, 2);
        } catch (err) {
          console.error('Failed to parse YAML to JSON', err);
          emit('showErrorToast', err.message);
          return;
        }
      } else if (contentType === 'YAML') {
        try {
          newContent = jsyaml.dump(JSON.parse(editor.state.doc.toString()));
        } catch (err) {
          console.error('Failed to parse JSON to YAML', err);
          emit('showErrorToast', err.message);
          return;
        }
      }

      editor.setState(createEditorState(newContent, contentType));
    };

    onMounted(() => {
      editor = new EditorView({
        state: createEditorState(props.Content, props.ContentType),
        parent: editorContainer.value,
      });
    });

    watch(
      () => props.Content,
      (newValue) => {
        if (newValue !== editor.state.doc.toString()) {
          editor.dispatch({
            changes: {
              from: 0,
              to: editor.state.doc.length,
              insert: newValue,
            },
          });
        }
      }
    );

    watch(
      () => props.ContentType,
      (newContentType) => {
        updateEditorLanguage(newContentType);
      }
    );

    return { editorContainer, };
  },
};
</script>

<style>
.editor-container {
  border: 1px solid #ccc;
  height: 600px;
  overflow: auto;
}
</style>
