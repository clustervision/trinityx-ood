import './assets/css/main-ui.css'
import './assets/css/rack.css'
import './assets/fonts/boxicons.css'
import './assets/css/core.css'
import './assets/css/theme-default.css'
import Toast from "vue-toastification"
import {POSITION} from "vue-toastification"
import type { PluginOptions } from "vue-toastification";
import "vue-toastification/dist/index.css";
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import type { Plugin } from 'vue';

const options: PluginOptions = {
    position: POSITION.TOP_RIGHT, 
    timeout: 4000,  
};
const app = createApp(App)

app.use(createPinia())
app.use((Toast as unknown) as Plugin, options);
app.mount('#app')
