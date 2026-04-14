import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

/**
 * Remote VM + local Vite:
 * - Keep window.APP_URL empty in index.html so the browser calls /api/... on :5173.
 * - Vite forwards those paths to VITE_GROUP_BACKEND (see .env.development).
 * - Node accepts self-signed TLS (secure: false); the browser never talks to :7755 directly.
 */
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const backendTarget =
    env.VITE_GROUP_BACKEND || 'http://127.0.0.1:7755'

  // Vite treats proxy keys starting with ^ as RegExp (must be strings, not RegExp objects).
  const groupApi =
    '^/(api|show|get_list|add|edit|delete|clone|remove|rename|member|ospush|check_status|license)(/|$|\\?)'

  console.info('[vite] Group API proxy target:', backendTarget)

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
        [groupApi]: {
          target: backendTarget,
          changeOrigin: true,
          secure: false,
        },
      },
    },
  }
})
