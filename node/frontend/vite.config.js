import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

/**
 * Local Vite: leave window.APP_URL empty so requests go to the dev server.
 * GET /?format=json and legacy Flask paths are proxied to VITE_NODE_BACKEND.
 */
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const backendTarget =
    env.VITE_NODE_BACKEND || 'http://127.0.0.1:7755'

  console.info('[vite] Node Flask proxy target:', backendTarget)

  /** @returns {string|false} false = proxy to backend; else path for Vite to serve */
  function devApiBypass(req) {
    const raw = req.url || '/'
    if (
      raw.startsWith('/src/') ||
      raw.startsWith('/@') ||
      raw.startsWith('/node_modules/') ||
      raw.startsWith('/@fs/')
    ) {
      return raw
    }
    if (
      raw.match(
        /^\/(show|get_list|add|edit|delete|clone|remove|rename|nextip_network|osgrab|ospush|check_status|license)(\/|$|\?)/
      )
    ) {
      return false
    }
    try {
      const parsed = new URL(raw, 'http://vite.local')
      if (parsed.pathname === '/' && parsed.searchParams.get('format') === 'json') {
        return false
      }
    } catch {
      /* ignore */
    }
    const accept = req.headers?.accept || ''
    if (accept.includes('application/json')) {
      try {
        const parsed = new URL(raw, 'http://vite.local')
        if (parsed.pathname === '/') return false
      } catch {
        /* ignore */
      }
    }
    return '/index.html'
  }

  return {
    plugins: [vue()],
    build: {
      outDir: '../static/spa',
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
      proxy: {
        '^/': {
          target: backendTarget,
          changeOrigin: true,
          secure: false,
          bypass: devApiBypass,
        },
      },
    },
  }
})
