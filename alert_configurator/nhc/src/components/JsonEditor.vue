<template>
    <div ref="editorContainer" class="editor-container"></div>
  </template>
  
  <script>
  import { ref, onMounted, watch } from 'vue';
  import { basicSetup } from 'codemirror';
  import { EditorState } from '@codemirror/state';
  import { EditorView } from '@codemirror/view';
  import { json } from '@codemirror/lang-json';
  import { yaml } from '@codemirror/lang-yaml';
  import { oneDark } from '@codemirror/theme-one-dark';
  import jsyaml from 'js-yaml'; // Ensure you have this installed
  
  export default {
    props: {
      Content: {
        type: String,
        required: true,
      },
      ContentType: {
        type: String,
        required: true,
        validator: (value) => ['JSON', 'YAML'].includes(value),
      },
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
    height: 400px;
    overflow: auto;
  }
  </style>
  