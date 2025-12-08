import './assets/css/main-ui.css'
import './assets/css/rack.css'
// 1. CORE STYLES (Order matters!)
import './assets/fonts/boxicons.css' // You need the icons
import './assets/css/core.css'       // Bootstrap & Layout wrappers
import './assets/css/theme-default.css' // Colors & Sidebar theme

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
