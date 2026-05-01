import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  /** One variable: same as VITE_APP_URL (legacy alias still works). */
  const backendTarget = (env.VITE_APP_URL || env.VITE_OSIMAGE_BACKEND || '').trim()

  if (mode === 'development') {
    console.info(
      '[vite] Proxy /osimage-backend →',
      backendTarget || '(set VITE_APP_URL in .env.development, e.g. http://ctrl:7755)'
    )
  }

  const proxy = {}
  if (backendTarget && mode === 'development') {
    proxy['/osimage-backend'] = {
      target: backendTarget,
      changeOrigin: true,
      secure: false,
      rewrite: (path) => path.replace(/^\/osimage-backend/, '') || '/',
    }
  }

  return {
    base: mode === 'production' ? '/static/' : '/',
    plugins: [vue()],
    build: {
      assetsInlineLimit: 0,
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
      port: 5175,
      proxy,
    },
  }
})
