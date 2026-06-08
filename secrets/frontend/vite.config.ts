import { copyFileSync, mkdirSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

const projectRoot = fileURLToPath(new URL('.', import.meta.url))

/** Copy static assets from `public/` into dist for Flask `app/assets/`. */
function copyPublicAssetsPlugin() {
  return {
    name: 'copy-public-assets',
    closeBundle() {
      const logoSrc = join(projectRoot, 'public/img/logo.png')
      const logoOut = join(projectRoot, 'dist/img')
      mkdirSync(logoOut, { recursive: true })
      copyFileSync(logoSrc, join(logoOut, 'logo.png'))

      for (const icon of ['icon-clone.png', 'icon-delete.png', 'icon-edit.png']) {
        copyFileSync(join(projectRoot, 'public', icon), join(projectRoot, 'dist', icon))
      }
    },
  }
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const backendTarget = (env.VITE_APP_URL || env.VITE_SECRET_BACKEND || '').trim()
  const rawBasePath = (env.VITE_BASE_PATH || '').trim()
  const normalizedBasePath = rawBasePath
    ? `/${rawBasePath.replace(/^\/+|\/+$/g, '')}/`
    : './'

  if (mode === 'development') {
    console.info(
      '[vite] Proxy /secret-backend →',
      backendTarget || '(set VITE_APP_URL in .env.development, e.g. http://ctrl:7755)'
    )
  }

  const proxy: Record<string, object> = {}
  if (backendTarget && mode === 'development') {
    proxy['/secret-backend'] = {
      target: backendTarget,
      changeOrigin: true,
      secure: false,
      rewrite: (path: string) => path.replace(/^\/secret-backend/, '') || '/',
    }
  }

  return {
    base: mode === 'production' ? normalizedBasePath : '/',
    plugins: [vue(), copyPublicAssetsPlugin()],
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
            if (info.name && info.name.endsWith('.css')) return 'index.css'
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
