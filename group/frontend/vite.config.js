import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

/**
 * When Flask runs on a VM (not localhost), create group/frontend/.env.development:
 *   VITE_GROUP_BACKEND=https://yixin3-dev-ctrl001:7755
 * Leave window.APP_URL empty in index.html so /api/* goes through this proxy.
 */
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const backendTarget =
    env.VITE_GROUP_BACKEND || 'http://127.0.0.1:7755'

  const groupBackend =
    /^\/(api|show|get_list|add|edit|delete|clone|remove|rename|member|ospush|check_status|license)(\/|$|\?)/

  return {
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
        [groupBackend]: {
          target: backendTarget,
          changeOrigin: true,
          secure: false,
        },
      },
    },
  }
})
