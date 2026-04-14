import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  build: {
    outDir: '../app/assets',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        entryFileNames: 'index.js',
        chunkFileNames: '[name].js',
        assetFileNames: (info) => {
          if (info.name && info.name.endsWith('.css')) return 'index.css'
          return '[name][extname]'
        },
      },
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:7755',
      '/show': 'http://localhost:7755',
      '/get_list': 'http://localhost:7755',
      '/add': 'http://localhost:7755',
      '/edit': 'http://localhost:7755',
      '/delete': 'http://localhost:7755',
      '/clone': 'http://localhost:7755',
      '/remove': 'http://localhost:7755',
      '/rename': 'http://localhost:7755',
      '/member': 'http://localhost:7755',
      '/ospush': 'http://localhost:7755',
      '/check_status': 'http://localhost:7755',
      '/license': 'http://localhost:7755',
    },
  },
})
