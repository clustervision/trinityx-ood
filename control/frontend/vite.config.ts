import { copyFileSync, mkdirSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

const projectRoot = fileURLToPath(new URL('.', import.meta.url))

/** Ensure `public/img/logo.png` is in dist for Flask `app/assets/img/`. */
function copyLogoPlugin() {
  return {
    name: 'copy-logo',
    closeBundle() {
      const src = join(projectRoot, 'public/img/logo.png')
      const outDir = join(projectRoot, 'dist/img')
      mkdirSync(outDir, { recursive: true })
      copyFileSync(src, join(outDir, 'logo.png'))
    },
  }
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const backendTarget = (env.VITE_APP_URL || env.VITE_CONTROL_BACKEND || '').trim()
  const rawBasePath = (env.VITE_BASE_PATH || '').trim()
  const normalizedBasePath = rawBasePath ? `/${rawBasePath.replace(/^\/+|\/+$/g, '')}/` : './'

  const proxy: Record<string, object> = {}
  if (backendTarget && mode === 'development') {
    proxy['/control-backend'] = {
      target: backendTarget,
      changeOrigin: true,
      secure: false,
      rewrite: (path: string) => path.replace(/^\/control-backend/, '') || '/',
    }
  }

  return {
    base: mode === 'production' ? normalizedBasePath : '/',
    plugins: [vue(), copyLogoPlugin()],
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
          assetFileNames: (info: { name?: string }) => {
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
