
<template>
  <button type="button" @click="switchMode('JSON')" class="btn btn-primary btn-sm">JSON View</button>&nbsp;
  <button type="button" @click="switchMode('YAML')" class="btn btn-warning btn-sm">YAML View</button>
  <div ref="editorContainer" class="editor-container"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, type PropType, type SetupContext, defineExpose } from 'vue';
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

  // const emits = defineEmits(['update:Content', 'Toast']);
  const emit = defineEmits(['update:Content', 'Toast']);
//   const attrs = useAttrs(); // Equivalent to context.attrs
// const slots = useSlots();
  // const context: SetupContext;
 // setup(props: { Content: string; ContentType: string; editorHeight: string; }, context: SetupContext) {
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
      console.log(`Mode>>>>>>>>> ${mode} Mode`);
      updateEditorLanguage(mode);
    };

    const getContentType = (content: string): 'JSON' | 'YAML' | null => {
      try {
        JSON.parse(content);
        return 'JSON';
      } catch (e: unknown) {
        console.log('Not a valid JSON', e);
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
      defineExpose({newContent });
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


    // return { editorContainer, switchMode, };

 // },





</script>






<!-- <script lang="ts">
import { ref, onMounted, watch, type PropType, type SetupContext, defineExpose } from 'vue';
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
      type: String,
      required: true,
    },
  },

  emits: ['update:Content', 'Toast'],

  setup(props: { Content: string; ContentType: string; editorHeight: string; }, context: SetupContext) {
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
              context.emit('update:Content', editor?.state.doc.toString());
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
      } catch (e: unknown) {
        console.log('Not a valid JSON', e);
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
      console.warn('updateEditorLanguage contentType >>>>>>>>>>>', contentType);
      if (editor) {
        if (contentType === 'JSON') {
          const docContentType = getContentType(editor.state.doc.toString());
          console.warn('doccontentType >>>>>>>>>>>', docContentType);
          if (docContentType === 'JSON') {
            newContent = editor.state.doc.toString();
            context.emit('Toast', {message: `Error: Already in ${docContentType} Mode, no conversion needed`, toastClass: 'bg-warning'});
            return;
          } else {
            try {
              newContent = JSON.stringify(jsyaml.load(editor.state.doc.toString()), null, 2);
            } catch (err: unknown) {
              if (err instanceof Error) {
                console.error('Failed to parse YAML to JSON', err);
                context.emit('Toast', {message: err.message, toastClass: 'bg-danger'});
              } else {
                console.error('An unknown error occurred', err);
                context.emit('Toast', {message: 'An unknown error occurred', toastClass: 'bg-danger'});
              }
              return;
            }
          }
        } else if (contentType === 'YAML') {
          const docContentType = getContentType(editor.state.doc.toString());
          console.warn('doccontentType >>>>>>>>>>>', docContentType);
          if (docContentType === 'YAML') {
            newContent = editor.state.doc.toString();
            context.emit('Toast', {message: `Error: Already in ${docContentType} Mode, no conversion needed`, toastClass: 'bg-warning'});
            return;
          } else {
            try {
              newContent = jsyaml.dump(JSON.parse(editor.state.doc.toString()));
            } catch (err: unknown) {
              if (err instanceof Error) {
                console.error('Failed to parse JSON to YAML', err);
                context.emit('Toast', {message: err.message, toastClass: 'bg-danger'});
              } else {
                console.error('An unknown error occurred', err);
                context.emit('Toast', {message: 'An unknown error occurred', toastClass: 'bg-danger'});
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
    defineExpose({editorContainer, });
  },



};

</script> -->

