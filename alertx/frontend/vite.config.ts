import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
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
  base: './',
  // base: '/pun/sys/trinity_alertx/assets/',
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  build: {
    // assetsDir: 'app/assets',
    // assetsDir: 'assets',
    // Disable hash in filenames
    rollupOptions: {
      output: {
        entryFileNames: 'index.js',  // Fixed name for JS file
        chunkFileNames: 'index.js',  // Fixed name for chunk files
        assetFileNames: (assetInfo) => {
          if (assetInfo.name) {
            // if (/\.(png|jpe?g|gif|svg)$/.test(assetInfo.name)) {
            //   return 'logo.png';  // Fixed name for image files
            // }
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
