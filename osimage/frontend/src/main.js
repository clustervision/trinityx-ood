/**
 * Prod only: if build injects empty APP_URL, optional VITE_APP_URL can supply base
 * (usually Flask sets window.APP_URL in index.html).
 * Dev: do not set window.APP_URL from env — api.js uses /osimage-backend + Vite proxy.
 */
import { createApp } from 'vue'
import App from './App.vue'
import './assets/styles.css'

createApp(App).mount('#app')
