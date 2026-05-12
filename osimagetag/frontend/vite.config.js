import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const backendTarget = (env.VITE_APP_URL || '').trim()
  const rawBasePath = (env.VITE_BASE_PATH || '').trim()
  const normalizedBasePath = rawBasePath
    ? `/${rawBasePath.replace(/^\/+|\/+$/g, '')}/`
    : './'

  if (mode === 'development') {
    console.info(
      '[vite] Proxy /osimagetag-backend →',
      backendTarget || '(set VITE_APP_URL in .env.development, e.g. http://ctrl:7755)'
    )
  }

  const proxy = {}
  if (backendTarget && mode === 'development') {
    proxy['/osimagetag-backend'] = {
      target: backendTarget,
      changeOrigin: true,
      secure: false,
      rewrite: (path) => path.replace(/^\/osimagetag-backend/, '') || '/',
    }
  }

  return {
    base: mode === 'production' ? normalizedBasePath : '/',
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
      port: 5176,
      proxy,
    },
  }
})
