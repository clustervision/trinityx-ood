import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import type { AssetInfo } from 'rollup'

/**
 * Dev: base `/` so `/node-backend` proxy paths stay at the dev root.
 * Prod: set VITE_PUBLIC_BASE to the Flask static URL under Pun, e.g.
 *       /pun/sys/trinity_node/app/assets/  (must include `app` — matches Flask static_url_path).
 * If unset, defaults to `./` so CSS url() paths stay relative to index.css and work under any mount
 * without baking in wrong paths like /static/ or /pun/.../assets/ (missing app/).
 */
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const backendTarget = env.VITE_NODE_BACKEND

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

  console.info('[vite] base:', base)
  console.info(
    '[vite] Node Flask proxy target:',
    backendTarget || '(not set — set VITE_NODE_BACKEND in .env.development)'
  )

  const proxy: Record<string, object> = {}
  if (backendTarget) {
    proxy['/node-backend'] = {
      target: backendTarget,
      changeOrigin: true,
      secure: false,
      rewrite: (path: string) => path.replace(/^\/node-backend/, '') || '/',
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
          assetFileNames: (info: AssetInfo) => {
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
