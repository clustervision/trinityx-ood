/*
 * This code is part of the TrinityX software suite
 * Copyright (C) 2026  ClusterVision Solutions b.v.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>
 *
 * @author      Yixin Zhang
 * @copyright   Copyright 2026, Luna2 Project[OOD]
 * @license     GPL
 * @version     2.0
 * @maintainer  Yixin Zhang
 * @email       yixin.zhang@clustervision.com
 * @status      Development
 */

import { copyFileSync, mkdirSync, readdirSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

const projectRoot = fileURLToPath(new URL('.', import.meta.url))

/** Copy static assets from `public/` into `dist/` for Flask `app/assets/`. */
function copyStaticAssetsPlugin() {
  return {
    name: 'copy-static-assets',
    closeBundle() {
      const logoSrc = join(projectRoot, 'public/img/logo.png')
      const logoOut = join(projectRoot, 'dist/img')
      mkdirSync(logoOut, { recursive: true })
      copyFileSync(logoSrc, join(logoOut, 'logo.png'))

      const iconsSrc = join(projectRoot, 'public/icons')
      const iconsOut = join(projectRoot, 'dist/icons')
      mkdirSync(iconsOut, { recursive: true })
      for (const name of readdirSync(iconsSrc)) {
        if (!name.endsWith('.png')) continue
        copyFileSync(join(iconsSrc, name), join(iconsOut, name))
      }
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
    plugins: [vue(), copyStaticAssetsPlugin()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    build: {
      // Inline small power icons into index.js so OOD deploy only needs JS + CSS.
      assetsInlineLimit: 8192,
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
