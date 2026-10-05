
<template>
  <button type="button" @click.prevent="switchMode('JSON')" class="btn btn-primary btn-sm" v-if="editorHeight !== '300'">JSON View</button>&nbsp;
  <button type="button" @click.prevent="switchMode('YAML')" class="btn btn-warning btn-sm" v-if="editorHeight !== '300'">YAML View</button>
  <div ref="editorContainer" class="editor-container"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, type PropType } from 'vue';
import { basicSetup } from 'codemirror';
import { EditorState } from '@codemirror/state';
import { EditorView } from '@codemirror/view';
import { json } from '@codemirror/lang-json';
import { yaml } from '@codemirror/lang-yaml';
import { oneDark } from '@codemirror/theme-one-dark';
import jsyaml from 'js-yaml';

const props = defineProps({
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
      type: String,
      required: true,
    },

  });


const emit = defineEmits(['update:Content', 'toast']);

const editorContainer = ref(null);
let editor: EditorView | null = null;
const fixedHeightTheme = EditorView.theme({
  '&': { height: props.editorHeight + 'px' },
  '.cm-scroller': { overflow: 'auto' },
});

const createEditorState = (Content: string, ContentType: string) => {
  const langExtension = ContentType === 'JSON' ? json() : yaml();
  return EditorState.create({
    doc: Content,
    extensions: [
      basicSetup,
      langExtension,
      oneDark,
      fixedHeightTheme,
      EditorView.updateListener.of((update) => {
        if (update.docChanged) {
          emit('update:Content', editor?.state.doc.toString());
        }
      }),
    ],
  });
};

const switchMode = (mode: string) => {
  updateEditorLanguage(mode);
};

const getContentType = (content: string): 'JSON' | 'YAML' | null => {
  const shouldLog = false;
  try {
    JSON.parse(content);
    return 'JSON';
  } catch (e: unknown) {
    if (shouldLog) { console.log('Not a valid JSON', e); }
    try {
      jsyaml.load(content);
      return 'YAML';
    } catch (err: unknown) {
      console.log('Not a valid content', err);
      return null;
    }
  }
};

const updateEditorLanguage = (contentType: string) => {
  let newContent: string = '';;
  if (editor) {
    if (contentType === 'JSON') {
      const docContentType = getContentType(editor.state.doc.toString());
      if (docContentType === 'JSON') {
        newContent = editor.state.doc.toString();
        if(props.editorHeight !== '300'){
          emit('toast', {message: `Error: Already in ${docContentType} Mode, no conversion needed`, toastClass: 'bg-warning'});
        }
        return;
      } else {
        try {
          newContent = JSON.stringify(jsyaml.load(editor.state.doc.toString()), null, 2);
        } catch (err: unknown) {
          if (err instanceof Error) {
            emit('toast', {message: err.message, toastClass: 'bg-danger'});
          } else {
            console.error('An unknown error occurred', err);
            emit('toast', {message: 'An unknown error occurred', toastClass: 'bg-danger'});
          }
          return;
        }
      }
    } else if (contentType === 'YAML') {
      const docContentType = getContentType(editor.state.doc.toString());
      if (docContentType === 'YAML') {
        newContent = editor.state.doc.toString();
        if(props.editorHeight !== '300'){
          emit('toast', {message: `Error: Already in ${docContentType} Mode, no conversion needed`, toastClass: 'bg-warning'});
          return;
        }

      } else {
        try {
          newContent = jsyaml.dump(JSON.parse(editor.state.doc.toString()));
        } catch (err: unknown) {
          if (err instanceof Error) {
            emit('toast', {message: err.message, toastClass: 'bg-danger'});
          } else {
            console.error('An unknown error occurred', err);
            emit('toast', {message: 'An unknown error occurred', toastClass: 'bg-danger'});
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
    updateEditorLanguage(newContentType);
  }
);

</script>
