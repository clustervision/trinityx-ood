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

/**
 * Dev: same-origin `/osimage-backend` -> Vite proxies to `VITE_APP_URL` (no CORS).
 * Prod: `window.APP_URL` from host shell, or `VITE_APP_URL`.
 *
 * Backend: trinityx-ood/osimage Flask JSON API (thin daemon proxy).
 */
import type {
  DaemonEnvelope,
  OsimageConfigContent,
  OsimageInventoryRow,
  OsimageListResult,
  OsimageRecord,
} from './types'

const UNSUBSTITUTED_APP_URL = /^\{\{\s*APP_URL\s*\}\}$/i

const TABLE = 'osimage'

/** Matches legacy Python Helper.prepare_payload / prepare_json EDITOR_KEYS. */
const EDITOR_KEYS = [
  'options',
  'content',
  'comment',
  'prescript',
  'partscript',
  'postscript',
  'grab_filesystems',
  'grab_exclude',
  'kerneloptions',
]

export const baseUrl = () => {
  if (import.meta.env.DEV) return '/osimage-backend'

  let explicit = String(
    (typeof window !== 'undefined' && (window as any).APP_URL) || import.meta.env.VITE_APP_URL || ''
  )
    .trim()
    .replace(/\/$/, '')
  if (UNSUBSTITUTED_APP_URL.test(explicit)) explicit = ''
  if (explicit) {
    try {
      const parsed = new URL(explicit)
      if (typeof window !== 'undefined' && window.location?.origin) {
        // OOD/Proxy environments may inject http APP_URL even when browser uses https.
        // Keep the injected path, but always align origin with the active page.
        return `${window.location.origin}${parsed.pathname}`.replace(/\/$/, '')
      }
    } catch {
      /* ignore and fall through */
    }
    return explicit
  }
  return ''
}

function apiPath(suffix: string) {
  const b = String(baseUrl() || '').replace(/\/+$/, '')
  const s = suffix == null ? '' : String(suffix).trim()
  if (!s) return b
  const path = s.startsWith('/') ? s : `/${s}`
  return `${b}${path}`
}

async function readJsonResponse<T = Record<string, unknown>>(res: Response): Promise<T | { _raw: string }> {
  const text = await res.text()
  if (!text) return {} as T
  try {
    return JSON.parse(text) as T
  } catch {
    return { _raw: text }
  }
}

/**
 * Unwrap Rest().get_data JSON: { status, status_code, content }.
 */
function unwrapGetData<T>(data: unknown, context = 'request'): T {
  if (data == null || typeof data !== 'object') {
    throw new Error(`${context}: invalid response`)
  }
  const envelope = data as DaemonEnvelope<T>
  if (envelope.status === false) {
    const c = envelope.content
    const msg =
      typeof c === 'string'
        ? c
        : c && typeof c === 'object' && c.message != null
          ? String(c.message)
          : 'Daemon request failed'
    throw new Error(String(msg || 'Daemon request failed'))
  }
  if (envelope.status === true) return (envelope.content as T) ?? ({} as T)
  return data as T
}

function tryB64Decode(str: string) {
  const trimmed = String(str || '').trim()
  if (!trimmed) return str
  try {
    const bin = atob(trimmed)
    const bytes = new Uint8Array(bin.length)
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i)
    const decoded = new TextDecoder().decode(bytes)
    const reBytes = new TextEncoder().encode(decoded)
    let reBin = ''
    reBytes.forEach((b) => {
      reBin += String.fromCharCode(b)
    })
    const reEncoded = btoa(reBin).replace(/=+$/, '')
    if (reEncoded === trimmed.replace(/=+$/, '')) return decoded
    return str
  } catch {
    return str
  }
}

/** Decode editor fields for display in forms (mirrors prepare_json for EDITOR_KEYS). */
export function prepareJsonForDisplay<T extends Record<string, unknown>>(obj: T): T {
  if (!obj || typeof obj !== 'object') return obj
  const out = { ...obj } as T
  for (const key of EDITOR_KEYS) {
    const value = out[key]
    if (typeof value === 'string' && value) {
      const dec = tryB64Decode(value)
      if (dec !== value) out[key] = dec as T[Extract<keyof T, string>]
    }
  }
  return out
}

function preparePayload(raw: Record<string, any>) {
  const payload: Record<string, any> = {}
  for (const [k, v] of Object.entries(raw)) {
    if (v === undefined || v === null) continue
    if (typeof v === 'string' && v.trim() === '') continue
    payload[k] = v
  }
  for (const key of EDITOR_KEYS) {
    if (typeof payload[key] === 'string' && payload[key].length > 0) {
      const s = payload[key].replace(/\r\n/g, '\n')
      const binary = new TextEncoder().encode(s)
      let bin = ''
      binary.forEach((b) => {
        bin += String.fromCharCode(b)
      })
      payload[key] = btoa(bin)
    }
  }
  return payload
}

function buildRequestData(recordName: string, recordPayload: Record<string, any>) {
  return { config: { [TABLE]: { [recordName]: recordPayload } } }
}

/** Build inventory rows like legacy `filter_data_json` + list fields for the table. */
function inventoryRowsFromConfig(osimageMap?: Record<string, OsimageRecord>): OsimageInventoryRow[] {
  const images: OsimageInventoryRow[] = []
  if (!osimageMap || typeof osimageMap !== 'object') return images
  for (const [, record] of Object.entries(osimageMap)) {
    if (!record || typeof record !== 'object') continue
    let displayName = record.name
    if (record._override && typeof displayName === 'string') displayName = `${displayName} *`
    images.push({
      name: displayName,
      kernelversion: record.kernelversion,
      kerneldetails: record.kerneldetails,
      distribution: record.distribution,
      osrelease: record.osrelease,
      path: record.path,
      initrdfile: record.initrdfile,
      kernelfile: record.kernelfile,
      imagefile: record.imagefile,
    })
  }
  return images
}

export async function fetchOsimages(): Promise<OsimageListResult> {
  let res: Response
  try {
    res = await fetch(apiPath('/api/v1/osimage'), { headers: { Accept: 'application/json' } })
    let data: DaemonEnvelope<OsimageConfigContent> | Record<string, unknown> = {}
    try {
      data = await res.json()
    } catch {
      /* ignore */
    }
    if (!res.ok) {
      const msg =
        (data && (data.error || data.message)) ||
        `Failed to load OS images: HTTP ${res.status} ${res.statusText || ''}`.trim()
      throw new Error(String(msg || `Failed to load OS images: HTTP ${res.status}`))
    }
    const content = unwrapGetData<OsimageConfigContent>(data, 'list osimage')
    const osMap = content?.config?.[TABLE]
    const images = inventoryRowsFromConfig(osMap || {})
    return { images, error: '', chroot_base_url: '' }
  } catch (e: any) {
    const msg = String(e?.message || 'Network error')
    if (import.meta.env.DEV) {
      throw new Error(
        `${msg} - Is the Flask backend running and VITE_APP_URL set in .env.development?`
      )
    }
    throw new Error(msg)
  }
}

export async function fetchOsimageDetail(name: string) {
  const res = await fetch(apiPath(`/api/v1/osimage/${encodeURIComponent(name)}`), {
    headers: { Accept: 'application/json' },
  })
  const data = await readJsonResponse<DaemonEnvelope<OsimageConfigContent>>(res)
  if (!res.ok) {
    const errRaw = data.message || data.error || `HTTP ${res.status}`
    return { osimage: {}, error: String(errRaw || `HTTP ${res.status}`) }
  }
  try {
    const content = unwrapGetData<OsimageConfigContent>(data, 'detail')
    const rec = content?.config?.[TABLE]?.[name]
    if (!rec) return { osimage: {}, error: `${name} not found` }
    const osimage = prepareJsonForDisplay({ ...rec })
    return { osimage, error: '' }
  } catch (e: any) {
    return {
      osimage: {},
      error: String(e?.message || 'Failed to parse record'),
    }
  }
}

export async function fetchOsimageEditData(name: string) {
  const res = await fetch(apiPath(`/api/v1/osimage/${encodeURIComponent(name)}`), {
    headers: { Accept: 'application/json' },
  })
  if (!res.ok) throw new Error(`Failed to load edit data: ${res.status}`)
  const data = await readJsonResponse<DaemonEnvelope<OsimageConfigContent>>(res)
  try {
    const content = unwrapGetData<OsimageConfigContent>(data, 'edit')
    const rec = content?.config?.[TABLE]?.[name]
    if (!rec) return { data: {}, error: `${name} not found` }
    const d = prepareJsonForDisplay({ ...rec })
    return { data: d, error: '' }
  } catch (e: any) {
    return { data: {}, error: String(e?.message || 'Failed to load record') }
  }
}

export async function fetchOsimageCloneData(name: string) {
  return fetchOsimageEditData(name)
}

export async function deleteOsimage(name: string) {
  const res = await fetch(apiPath(`/api/v1/delete/${encodeURIComponent(name)}`), {
    method: 'DELETE',
    headers: { Accept: 'application/json' },
  })
  let data: any = {}
  if (res.status !== 204) {
    try {
      data = await res.json()
    } catch {
      /* ignore */
    }
  }
  if (!res.ok) {
    throw new Error(String(data.message || data.error || `Delete failed (${res.status})`))
  }
  const rawSuccessMsg = typeof data.message === 'string' ? data.message.trim() : ''
  return {
    status: 'success',
    message: rawSuccessMsg || `${name} deleted.`,
  }
}

async function postJson(url: string, body: Record<string, any>) {
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
    },
    body: JSON.stringify(body),
  })
  const data: any = await readJsonResponse(res)
  const ok = res.ok && (res.status === 204 || res.status === 201 || res.status === 200)
  const merged = {
    ...data,
    status:
      data.status ||
      (res.status === 204 || res.status === 201 || (res.ok && res.status === 200)
        ? 'success'
        : undefined),
  }
  for (const key of ['message', 'error'] as const) {
    if (typeof merged[key] === 'string') merged[key] = merged[key].trim()
  }
  return { ok, status: res.status, data: merged }
}

/**
 * Legacy: (action, FormData) from modals. Maps to /api/v1 JSON.
 * action: '/add' | '/edit/<name>' | '/rename/<name>' | '/clone/<name>'
 */
export async function submitOsimageForm(action: string, formData: FormData) {
  const o: Record<string, any> = {}
  for (const [k, v] of formData.entries()) {
    o[k] = v
  }

  if (action === '/add' || action.startsWith('/add')) {
    const name = String(o.name || '').trim()
    if (!name) return { ok: false, status: 400, data: { message: 'Name is required' } }
    const inner = { ...o }
    delete inner.name
    inner.name = name
    if (inner.bare === 'on') inner.bare = true
    else delete inner.bare
    const payload = preparePayload(inner)
    const request_data = buildRequestData(name, payload)
    return postJson(apiPath('/api/v1/add'), { name, request_data })
  }

  if (action.startsWith('/edit/')) {
    const recordName = decodeURIComponent(action.replace(/^\/edit\//, ''))
    const inner = { ...o }
    const currentName = String(inner.name || recordName).trim()
    delete inner.name
    inner.name = currentName
    if (inner.bare === 'on') inner.bare = true
    else delete inner.bare
    const payload = preparePayload(inner)
    const request_data = buildRequestData(currentName, payload)
    return postJson(apiPath('/api/v1/edit'), { name: currentName, request_data })
  }

  if (action.startsWith('/rename/')) {
    const oldName = String(o.name || '').trim()
    const newN = String(o.newname || '').trim()
    if (!oldName || !newN) {
      return { ok: false, status: 400, data: { message: 'Name and new name required' } }
    }
    const payload = preparePayload({ name: oldName, newosimage: newN })
    const request_data = buildRequestData(oldName, payload)
    return postJson(apiPath('/api/v1/rename'), { name: oldName, request_data })
  }

  if (action.startsWith('/clone/')) {
    const sourceName = decodeURIComponent(action.replace(/^\/clone\//, ''))
    const inner = { ...o }
    const src = String(inner.name || sourceName).trim()
    delete inner.name
    inner.name = src
    if (inner.bare === 'on') inner.bare = true
    else delete inner.bare
    const payload = preparePayload(inner)
    const request_data = buildRequestData(src, payload)
    return postJson(apiPath('/api/v1/clone'), { source_name: src, request_data })
  }

  return { ok: false, status: 400, data: { message: `Unknown action: ${action}` } }
}

export async function packOsimage(name: string) {
  const res = await fetch(
    apiPath(`/api/v1/request/osimage/${encodeURIComponent(name)}/_pack`),
    { headers: { Accept: 'application/json' } }
  )
  const data = await readJsonResponse(res)
  return { ok: res.ok, status: res.status, data }
}

export async function checkPackStatus(requestId: string) {
  const rid = encodeURIComponent(requestId)
  /** Same origin as other calls: `/api/v1/check_status/...` on the osimage Flask app (daemon proxy). */
  const url = apiPath(`/api/v1/check_status/config/status/${rid}`)
  const res = await fetch(url, {
    headers: { Accept: 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
  })
  const data = await readJsonResponse(res)
  return { ok: res.ok, status: res.status, data }
}
