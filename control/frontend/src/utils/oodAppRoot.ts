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

const UNSUBSTITUTED_APP_URL = /^\{\{\s*APP_URL\s*\}\}$/i

/** OOD Pun app root, e.g. https://host:8080/pun/sys/trinity_control */
export function oodAppRootFromBrowser(): string {
  if (typeof window === 'undefined') return ''
  const path = window.location.pathname.replace(/\/+$/, '') || ''
  return `${window.location.origin}${path}`.replace(/\/$/, '')
}

export function oodAppRoot(): string {
  let explicit = String(
    (typeof window !== 'undefined' && window.APP_URL) || import.meta.env.VITE_APP_URL || '',
  )
    .trim()
    .replace(/\/$/, '')
  if (UNSUBSTITUTED_APP_URL.test(explicit)) explicit = ''
  if (explicit) {
    try {
      const parsed = new URL(explicit)
      const path = parsed.pathname.replace(/\/+$/, '') || ''
      if (path && path !== '/') {
        if (typeof window !== 'undefined' && window.location?.origin) {
          return `${window.location.origin}${path}`.replace(/\/$/, '')
        }
        return explicit.replace(/\/$/, '')
      }
    } catch {
      if (!/^https?:\/\//i.test(explicit)) {
        return explicit.replace(/\/$/, '')
      }
    }
  }
  return oodAppRootFromBrowser()
}

export function appUrlFromRuntime(): string {
  const raw = String(
    (typeof window !== 'undefined' && window.APP_URL) || import.meta.env.VITE_APP_URL || '',
  ).trim()
  if (!raw || UNSUBSTITUTED_APP_URL.test(raw)) return ''
  return raw.replace(/\/$/, '')
}
