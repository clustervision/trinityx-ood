import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

/**
 * Dev: base `/` so `/nodeboot-backend` proxy paths stay at the dev root.
 * Prod: set VITE_PUBLIC_BASE to the Flask static URL under Pun, e.g.
 *       /pun/sys/trinity_nodeboot/app/assets/
 */
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const backendTarget = env.VITE_NODEBOOT_BACKEND

  const rawBase =
    mode === 'production' ? (env.VITE_PUBLIC_BASE || './').trim() : '/'
  const base =
    !rawBase || rawBase === '/'
      ? '/'
      : rawBase === './'
        ? './'
        : rawBase.endsWith('/')
          ? rawBase
          : `${rawBase}/`

  const proxy = {}
  if (backendTarget) {
    proxy['/nodeboot-backend'] = {
      target: backendTarget,
      changeOrigin: true,
      secure: false,
      rewrite: (path) => path.replace(/^\/nodeboot-backend/, '') || '/',
    }
  }

  return {
    base,
    plugins: [vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    build: {
      assetsInlineLimit: 0,
      emptyOutDir: true,
      rollupOptions: {
        output: {
          entryFileNames: 'index.js',
          chunkFileNames: '[name].js',
          assetFileNames: (info) => {
            if (info.names.some((name) => name.endsWith('.css'))) return 'index.css'
            return '[name][extname]'
          },
        },
      },
    },
    server: {
      port: 5173,
      proxy,
    },
  }
})
