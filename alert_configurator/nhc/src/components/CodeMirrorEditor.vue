
<template>
  <!-- <button type="button" :id="`button_html_${row.id}`" @click="rule_modal_html(row.id, 1);" class="btn btn-secondary btn-sm" v-if="editorHeight === 300">HTML View</button> -->
  <button type="button" @click="switchMode('JSON')" class="btn btn-primary btn-sm" v-if="editorHeight !== 300">JSON View</button>
  <button type="button" @click="switchMode('YAML')" class="btn btn-warning btn-sm" v-if="editorHeight !== 300">YAML View</button>
  <div ref="editorContainer" class="editor-container" :style="{ height: editorHeight + 'px' }"></div>
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
    editorHeight: {
      type: Number,
      required: true
    },
  },

  emits: ['update:Content', 'Toast'],

  setup(props: { Content: string; ContentType: string; }, { emit }: any) {
    const editorContainer = ref(null);
    let editor: EditorView | null = null;
    const createEditorState = (Content: string, ContentType: string) => {
      const langExtension = ContentType === 'JSON' ? json() : yaml();
      return EditorState.create({
        doc: Content,
        extensions: [
          basicSetup,
          langExtension,
          oneDark,
          EditorView.updateListener.of((update) => {
            if (update.docChanged) {
              emit('update:Content', editor?.state.doc.toString());
            }
          }),
        ],
      });
    };

    const switchMode = (mode: string) => {
      console.log(`Mode>>>>>>>>> ${mode} Mode`);
      updateEditorLanguage(mode);
    };

    const getContentType = (content: string): 'JSON' | 'YAML' | null => {
      try {
        JSON.parse(content);
        return 'JSON';
      } catch (e) {
        try {
          jsyaml.load(content);
          return 'YAML';
        } catch (err) {
          return null;
        }
      }
    };

    const updateEditorLanguage = (contentType: string) => {
      let newContent: string;
      console.warn('updateEditorLanguage contentType >>>>>>>>>>>', contentType);
      if (editor) {
        if (contentType === 'JSON') {
          const docContentType = getContentType(editor.state.doc.toString());
          console.warn('doccontentType >>>>>>>>>>>', docContentType);
          if (docContentType === 'JSON') {
            newContent = editor.state.doc.toString();
            emit('Toast', {message: `Error: Already in ${docContentType} Mode, no conversion needed`, toastClass: 'bg-warning'});
            return;
          } else {
            try {
              newContent = JSON.stringify(jsyaml.load(editor.state.doc.toString()), null, 2);
            } catch (err: unknown) {
              if (err instanceof Error) {
                console.error('Failed to parse YAML to JSON', err);
                emit('Toast', {message: err.message, toastClass: 'bg-danger'});
              } else {
                console.error('An unknown error occurred', err);
                emit('Toast', {message: 'An unknown error occurred', toastClass: 'bg-danger'});
              }
              return;
            }
          }
        } else if (contentType === 'YAML') {
          const docContentType = getContentType(editor.state.doc.toString());
          console.warn('doccontentType >>>>>>>>>>>', docContentType);
          if (docContentType === 'YAML') {
            newContent = editor.state.doc.toString();
            emit('Toast', {message: `Error: Already in ${docContentType} Mode, no conversion needed`, toastClass: 'bg-warning'});
            return;
          } else {
            try {
              newContent = jsyaml.dump(JSON.parse(editor.state.doc.toString()));
            } catch (err: unknown) {
              if (err instanceof Error) {
                console.error('Failed to parse JSON to YAML', err);
                emit('Toast', {message: err.message, toastClass: 'bg-danger'});
              } else {
                console.error('An unknown error occurred', err);
                emit('Toast', {message: 'An unknown error occurred', toastClass: 'bg-danger'});
              }
              return;
            }
          }
        }
      }
      editor?.setState(createEditorState(newContent, contentType));
    };

    onMounted(() => {
      if (editorContainer.value) {
        editor = new EditorView({
          state: createEditorState(props.Content, props.ContentType),
          parent: editorContainer.value,
        });
      }
    });

    watch(
      () => props.Content,
      (newValue) => {
        console.error('newValue', newValue);
        if (newValue !== editor?.state.doc.toString()) {
          editor?.dispatch({
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
      [() => props.ContentType],
      ([newContentType]) => {
        console.error('newContentType', newContentType);
        updateEditorLanguage(newContentType);
      }
    );

    return { editorContainer, switchMode, };
  },
};
</script>

<style>
.editor-container {
  border: 1px solid #ccc;
  /* height: 600px; */
  overflow: auto;
}
</style>
