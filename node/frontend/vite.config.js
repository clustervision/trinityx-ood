import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

/**
 * Local Vite: leave window.APP_URL empty; api.js uses /node-backend prefix in dev.
 * That path is proxied to VITE_NODE_BACKEND (avoids CORS and / vs SPA conflicts).
 */
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const backendTarget = env.VITE_NODE_BACKEND

  console.info('[vite] Node Flask proxy target:', backendTarget || '(not set — set VITE_NODE_BACKEND in .env.development)')

  const proxy = {}
  if (backendTarget) {
    proxy['/node-backend'] = {
      target: backendTarget,
      changeOrigin: true,
      secure: false,
      rewrite: (path) => path.replace(/^\/node-backend/, '') || '/',
    }
  }

  return {
    // Dev: '/' so `public/` and /src assets work on :5174. Production: '/static/' so URLs match
    // Flask static_folder (files served as /static/<name>).
    base: mode === 'production' ? '/static/' : '/',
    plugins: [vue()],
    build: {
      // Same layout as rack: Flask static_folder app/assets (see trinityx-ood/node/app/index.html).
      outDir: '../trinityx-ood/node/app/assets',
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
      port: 5174,
      proxy,
    },
  }
})
