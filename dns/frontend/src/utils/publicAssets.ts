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

import { oodAppRoot } from './oodAppRoot'

function upgradeScheme(url: string): string {
  if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
    return url.replace(/^http:\/\//i, 'https://')
  }
  return url
}

export function publicAssetUrl(relativePath: string): string {
  const base = import.meta.env.BASE_URL || '/'
  const r = String(relativePath || '').replace(/^\//, '')
  return `${base}${r}`
}

export function punAppAssetUrl(relativePath: string): string {
  const r = String(relativePath || '').replace(/^\//, '')
  if (import.meta.env.DEV) {
    return `/dns-backend/app/assets/${r}`
  }
  const root = oodAppRoot()
  if (root) {
    return upgradeScheme(`${root.replace(/\/+$/, '')}/app/assets/${r}`)
  }
  if (typeof window !== 'undefined') {
    const path = window.location.pathname.replace(/\/+$/, '')
    return `${path}/app/assets/${r}`
  }
  return `/app/assets/${r}`
}

export function appUrlFromRuntime(): string {
  const raw = String(window.APP_URL || '').trim()
  if (!raw || /^\{\{\s*APP_URL\s*\}\}$/i.test(raw)) return ''
  return raw.replace(/\/$/, '')
}
