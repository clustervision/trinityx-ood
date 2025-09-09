
import { createApp, h, Transition } from 'vue'

import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'


import $ from "jquery";
import "datatables.net-dt/css/dataTables.dataTables.min.css";
import "datatables.net";
window.$ = window.jQuery = $;



const app = createApp(App)

Object.defineProperty(app.config.globalProperties, '$createElement', {
  get() {
    return h
  }
})
app.component('transition', Transition)

app.use(createPinia())
app.use(router)

app.mount('#app')

