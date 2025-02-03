import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import vueDevTools from 'vite-plugin-vue-devtools'
// const username = 'admin';
// const password = 'drqPne9GaN5r9QGUzrRQ'; // For local Home Setup
// const password = 'z80ea5dbbce33DZ2z420'; // ### For Local Lab Setup
// https://vite.dev/config/
export default defineConfig({
  // server: {
  //   proxy: {
  //     '/api': {
  //       target: 'https://vmware-controller1.cluster:9093',
  //       changeOrigin: true,
  //       secure: false,
  //       rewrite: (path) => path.replace(/^\/api/, ''),
  //       headers: {
  //         'Authorization': 'Basic ' + btoa(`${username}:${password}`)
  //       }
  //     },
  //   },
  // },
  plugins: [
    vue({
      template: {
        compilerOptions: {
          isCustomElement: (tag) => tag === 'box-icon',
        },
      },
    }),
    vueJsx(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  build: {
    // Disable hash in filenames
    rollupOptions: {
      output: {
        entryFileNames: 'index.js',  // Fixed name for JS file
        chunkFileNames: 'index.js',  // Fixed name for chunk files
        assetFileNames: (assetInfo) => {
          if (assetInfo.name) {
            if (/\.(png|jpe?g|gif|svg)$/.test(assetInfo.name)) {
              return 'logo.png';  // Fixed name for image files
            }
            if (/\.css$/.test(assetInfo.name)) {
              return 'index.css';  // Fixed name for CSS files
            }
          }
          return '[name].[ext]';  // Default for other assets
        },
      },
    },
  },
})
