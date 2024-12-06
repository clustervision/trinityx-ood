<!-- <script setup lang="ts">
import NHC from '@/components/NHC.vue'
</script> -->

<template>
  <!-- <div>
    <b-input-group class="expression-input">
      <b-input-group-prepend>
        <b-input-group-text>
          <font-awesome-icon :icon="loading ? faSpinner : faSearch" :spin="loading" />
        </b-input-group-text>
      </b-input-group-prepend>
      <div ref="containerRef" class="cm-expression-input"></div>
      <b-input-group-append>
        <b-button
          class="btn-light border"
          title="Open metrics explorer"
          @click="showMetricsExplorer = true"
        >
          <font-awesome-icon :icon="faGlobeEurope" />
        </b-button>
      </b-input-group-append>
      <b-input-group-append>
        <b-button class="execute-btn" variant="primary" @click="executeQuery"> Execute </b-button>
      </b-input-group-append>
    </b-input-group>

    <NHC
      :show="showMetricsExplorer"
      @updateShow="showMetricsExplorer = $event"
      :metrics="metricNames"
      :insertAtCursor="insertAtCursor"
    />
  </div> -->
</template>
<!--
<script lang="ts">
import { ref, onMounted, watch } from 'vue'
import {
  EditorView,
  highlightSpecialChars,
  keymap,
  ViewUpdate,
  placeholder,
} from '@codemirror/view'
import { EditorState, Prec, Compartment } from '@codemirror/state'
import { indentOnInput, syntaxTree } from '@codemirror/language'
import { history, historyKeymap } from '@codemirror/history'
import { defaultKeymap, insertNewlineAndIndent } from '@codemirror/commands'
import { bracketMatching } from '@codemirror/matchbrackets'
import { closeBrackets, closeBracketsKeymap } from '@codemirror/closebrackets'
import { searchKeymap, highlightSelectionMatches } from '@codemirror/search'
import { commentKeymap } from '@codemirror/comment'
import { lintKeymap } from '@codemirror/lint'
import { PromQLExtension } from '@prometheus-io/codemirror-promql'
import {
  autocompletion,
  completionKeymap,
  CompletionContext,
  CompletionResult,
} from '@codemirror/autocomplete'
import { theme, promqlHighlighter } from './CMTheme'
import NHC from '../components/NHC.vue'
import { faSearch, faSpinner, faGlobeEurope } from '@fortawesome/free-solid-svg-icons'

const promqlExtension = new PromQLExtension()
const dynamicConfigCompartment = new Compartment()

export default {
  components: { NHC },

  props: {
    value: String,
    onExpressionChange: Function,
    queryHistory: Array,
    metricNames: Array,
    executeQuery: Function,
    loading: Boolean,
    enableAutocomplete: Boolean,
    enableHighlighting: Boolean,
    enableLinter: Boolean,
  },

  setup(props : any) {
    const containerRef = ref(null)
    const viewRef = ref(null)
    const showMetricsExplorer = ref(false)

    const initializeEditor = () => {
      promqlExtension.activateCompletion(props.enableAutocomplete)
      promqlExtension.activateLinter(props.enableLinter)
      promqlExtension.setComplete({
        completeStrategy: new HistoryCompleteStrategy(
          newCompleteStrategy({ remote: { url: "https://vmware-controller1.cluster:9090" } }),
          // newCompleteStrategy({ remote: { url: props.pathPrefix } }),
          props.queryHistory,
        ),
      })

      const dynamicConfig = [
        props.enableHighlighting ? promqlHighlighter : [],
        promqlExtension.asExtension(),
      ]

      if (!viewRef.value) {
        const startState = EditorState.create({
          doc: props.value,
          extensions: [
            theme,
            highlightSpecialChars(),
            history(),
            EditorState.allowMultipleSelections.of(true),
            indentOnInput(),
            bracketMatching(),
            closeBrackets(),
            autocompletion(),
            highlightSelectionMatches(),
            EditorView.lineWrapping,
            keymap.of([
              ...closeBracketsKeymap,
              ...defaultKeymap,
              ...searchKeymap,
              ...historyKeymap,
              ...commentKeymap,
              ...completionKeymap,
              ...lintKeymap,
            ]),
            placeholder('Expression (press Shift+Enter for newlines)'),
            dynamicConfigCompartment.of(dynamicConfig),
            keymap.of([
              {
                key: 'Escape',
                run: (v) => {
                  v.contentDOM.blur()
                  return false
                },
              },
            ]),
            Prec.override(
              keymap.of([
                {
                  key: 'Enter',
                  run: (v) => {
                    props.executeQuery()
                    return true
                  },
                },
                {
                  key: 'Shift-Enter',
                  run: insertNewlineAndIndent,
                },
              ]),
            ),
            EditorView.updateListener.of((update) => {
              props.onExpressionChange(update.state.doc.toString())
            }),
          ],
        })

        viewRef.value = new EditorView({
          state: startState,
          parent: containerRef.value,
        })

        viewRef.value.focus()
      } else {
        viewRef.value.dispatch(
          viewRef.value.state.update({
            effects: dynamicConfigCompartment.reconfigure(dynamicConfig),
          }),
        )
      }
    }

    const insertAtCursor = (value) => {
      const view = viewRef.value
      if (!view) return
      const { from, to } = view.state.selection.ranges[0]
      view.dispatch(
        view.state.update({
          changes: { from, to, insert: value },
        }),
      )
    }

    onMounted(() => {
      initializeEditor()
    })

    watch(
      [
        () => props.enableAutocomplete,
        () => props.enableHighlighting,
        () => props.enableLinter,
        () => props.queryHistory,
      ],
      initializeEditor,
    )

    return {
      containerRef,
      showMetricsExplorer,
      insertAtCursor,
      faSearch,
      faSpinner,
      faGlobeEurope,
    }
  },
}
</script>

<style>
.cm-expression-input {
  width: 100%;
  height: 100%;
}
</style> -->
