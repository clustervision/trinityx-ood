import './assets/styles.css'

import { applyIconCssVars } from '@/utils/icons'
import { createApp } from 'vue'

applyIconCssVars()
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
