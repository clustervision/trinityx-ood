import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  // https://yixin3-dev-ctrl001.taurusgroup.one:7755//get_temperature
  server: {
    port: 3003,
    proxy: {
      '/api': {
        target: 'https://yixin3-dev-ctrl001.taurusgroup.one:7755',
        changeOrigin: true,
        secure: false,
      },
      '/manage': {
        target: 'https://yixin3-dev-ctrl001.taurusgroup.one:7755',
        changeOrigin: true,
        secure: false,
      },
      '/edit': {
        target: 'https://yixin3-dev-ctrl001.taurusgroup.one:7755',
        changeOrigin: true,
        secure: false,
      },
      '/delete': {
        target: 'https://yixin3-dev-ctrl001.taurusgroup.one:7755',
        changeOrigin: true,
        secure: false,
      }
    }
  }
    }
)
