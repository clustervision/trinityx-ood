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
    // host: '0.0.0.0',      // Allows access from outside the VM
    // watch: {
    //   usePolling: true    // Fixes the "Shared Folder" update issue
    // },
    proxy: {
      '/api': {
        target: 'https://yixin3-dev-ctrl001.taurusgroup.one:7755', // Note: HTTPS
        changeOrigin: true,
        secure: false, // CRITICAL: Allows connection to self-signed HTTPS
      },
      '/manage': {
        target: 'https://yixin3-dev-ctrl001.taurusgroup.one:7755',
        changeOrigin: true,
        secure: false,
      },
      '/update': {
        target: 'https://yixin3-dev-ctrl001.taurusgroup.one:7755',
        changeOrigin: true,
        secure: false,
      }
    }
  }
    }
)
