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

export function appUrlFromRuntime(): string {
  const fromWindow =
    typeof window !== 'undefined' && window.APP_URL != null ? String(window.APP_URL).trim() : ''
  if (fromWindow && !UNSUBSTITUTED_APP_URL.test(fromWindow)) return fromWindow
  const fromEnv = String(import.meta.env.VITE_APP_URL || '').trim()
  return fromEnv && !UNSUBSTITUTED_APP_URL.test(fromEnv) ? fromEnv : ''
}

export function sanitizeUserMessage(raw: unknown): string {
  if (raw == null) return ''
  let s = String(raw)
  s = s.replace(/\/api\/v1(?:\/[\w.%-]*)*/gi, '')
  s = s.replace(/\s{2,}/g, ' ')
  return s.trim()
}

export function messageForDisplay(raw: unknown): string {
  const trimmed = String(raw ?? '').trim()
  if (!trimmed) return ''
  const t = sanitizeUserMessage(trimmed)
  return t || 'Request failed.'
}
