// import './assets/main.css'

import { createApp, ref, onMounted, watch } from 'vue'

// import {
//   EditorView,
//   highlightSpecialChars,
//   keymap,
//   ViewUpdate,
//   placeholder,
// } from '@codemirror/view'
// import { EditorState, Prec, Compartment } from '@codemirror/state'
// import { indentOnInput, syntaxTree } from '@codemirror/language'
// import { history, historyKeymap } from '@codemirror/history'
// import { defaultKeymap, insertNewlineAndIndent } from '@codemirror/commands'
// import { bracketMatching } from '@codemirror/matchbrackets'
// import { closeBrackets, closeBracketsKeymap } from '@codemirror/closebrackets'
// import { searchKeymap, highlightSelectionMatches } from '@codemirror/search'
// import { commentKeymap } from '@codemirror/comment'
// import { lintKeymap } from '@codemirror/lint'
// import { PromQLExtension } from '@prometheus-io/codemirror-promql'
// import {
//   autocompletion,
//   completionKeymap,
//   CompletionContext,
//   // CompletionResult,
// } from '@codemirror/autocomplete'
// import { theme, promqlHighlighter } from './views/CMTheme'
// import NHC from './components/NHC.vue'
// import { faSearch, faSpinner, faGlobeEurope } from '@fortawesome/free-solid-svg-icons'



import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')

