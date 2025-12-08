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
  server: {
    proxy: {
      '/api': {
        target: 'https://yixin3-dev-ctrl001:8080',
        changeOrigin: true,
        secure: false,
      },
      '/update': {
        target: 'https://yixin3-dev-ctrl001:8080',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
