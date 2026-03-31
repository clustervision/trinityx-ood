import '@fontsource/geist/400.css'
import '@fontsource/geist/500.css'
import './assets/css/main-ui.css'
import './assets/css/rack.css'
import './assets/fonts/boxicons.css'
import './assets/css/core.css'
import './assets/css/theme-default.css'
import axios from 'axios';
import { handle401Disconnect } from '@/utils/connectionStatus';
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
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      handle401Disconnect();
    }
    return Promise.reject(error);
  }
);

const app = createApp(App)

app.use(createPinia())
app.use((Toast as unknown) as Plugin, options);
app.mount('#app')
