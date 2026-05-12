/**
 * Dev: same-origin `/osimagetag-backend` -> Vite proxies to `VITE_APP_URL` (no CORS).
 * Prod: `window.APP_URL` from host shell, or `VITE_APP_URL`.
 *
 * Backend: trinityx-ood/osimagetag Flask JSON API (thin daemon proxy).
 */
import type {
  DaemonEnvelope,
  OsimageNamesConfigContent,
  OsimageTagConfigContent,
  OsimageTagInventoryRow,
  OsimageTagListResult,
} from './types'

const UNSUBSTITUTED_APP_URL = /^\{\{\s*APP_URL\s*\}\}$/i

const TABLE = 'osimagetag'

export const baseUrl = () => {
  if (import.meta.env.DEV) return '/osimagetag-backend'

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
        return `${window.location.origin}${parsed.pathname}`.replace(/\/$/, '')
      }
    } catch {
      /* ignore and fall through */
    }
    return explicit
  }
  return ''
}

/**
 * Absolute URL for files under Flask `static_folder` (`/app/assets/...`).
 * Do not use Vite `public/` + `import.meta.env.BASE_URL` alone: with an OOD app URL
 * like `/pun/sys/trinity_osimagetag` (no trailing slash), `./icons/...` resolves to
 * `/pun/sys/icons/...` and 404s. This matches `url_for('static', filename=...)`.
 */
export function appStaticAssetUrl(pathUnderAssets: string): string {
  const rel = String(pathUnderAssets || '').replace(/^\/+/, '')
  const tail = rel ? `/app/assets/${rel}` : '/app/assets'
  if (import.meta.env.DEV) {
    return `/osimagetag-backend${tail}`
  }
  const b = String(baseUrl() || '').replace(/\/+$/, '')
  if (b) return `${b}${tail}`
  if (typeof window !== 'undefined' && window.location) {
    const path = window.location.pathname.endsWith('/')
      ? window.location.pathname
      : `${window.location.pathname}/`
    return `${window.location.origin}${path}app/assets/${rel}`
  }
  return `/app/assets/${rel}`
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

function inventoryRowsFromConfig(tagMap?: Record<string, OsimageTagInventoryRow>): OsimageTagInventoryRow[] {
  const tags: OsimageTagInventoryRow[] = []
  if (!tagMap || typeof tagMap !== 'object') return tags
  for (const [, record] of Object.entries(tagMap)) {
    if (!record || typeof record !== 'object') continue
    tags.push({
      osimage: record.osimage,
      name: record.name,
      kernelfile: record.kernelfile,
      initrdfile: record.initrdfile,
      imagefile: record.imagefile,
      path: record.path,
      nodes: record.nodes,
      groups: record.groups,
    })
  }
  return tags
}

export async function fetchOsimageNames(): Promise<{ names: string[]; error: string }> {
  let res: Response
  try {
    res = await fetch(apiPath('/api/v1/osimage'), { headers: { Accept: 'application/json' } })
    let data: DaemonEnvelope<OsimageNamesConfigContent> | Record<string, unknown> = {}
    try {
      data = (await res.json()) as DaemonEnvelope<OsimageNamesConfigContent>
    } catch {
      /* ignore */
    }
    if (!res.ok) {
      const msg =
        (data && ((data as any).error || (data as any).message)) ||
        `Failed to load OS images: HTTP ${res.status} ${res.statusText || ''}`.trim()
      return { names: [], error: String(msg || `Failed to load OS images: HTTP ${res.status}`) }
    }
    const content = unwrapGetData<OsimageNamesConfigContent>(data, 'list osimage')
    const map = content?.config?.osimage
    const names: string[] = []
    if (map && typeof map === 'object') {
      for (const key of Object.keys(map)) {
        if (key) names.push(key)
      }
    }
    names.sort((a, b) => a.localeCompare(b, undefined, { sensitivity: 'base' }))
    return { names, error: '' }
  } catch (e: any) {
    const msg = String(e?.message || 'Network error')
    return { names: [], error: msg }
  }
}

export async function fetchOsimageTags(): Promise<OsimageTagListResult> {
  let res: Response
  try {
    res = await fetch(apiPath('/api/v1/osimagetag'), { headers: { Accept: 'application/json' } })
    let data: DaemonEnvelope<OsimageTagConfigContent> | Record<string, unknown> = {}
    try {
      data = await res.json()
    } catch {
      /* ignore */
    }
    if (!res.ok) {
      const msg =
        (data && (data.error || data.message)) ||
        `Failed to load OS image tags: HTTP ${res.status} ${res.statusText || ''}`.trim()
      throw new Error(String(msg || `Failed to load OS image tags: HTTP ${res.status}`))
    }
    const content = unwrapGetData<OsimageTagConfigContent>(data, 'list osimagetag')
    const tagMap = content?.config?.[TABLE]
    const tags = inventoryRowsFromConfig(tagMap || {})
    return { tags, error: '' }
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

export async function fetchOsimageTagDetail(name: string) {
  const res = await fetch(apiPath(`/api/v1/osimagetag/${encodeURIComponent(name)}`), {
    headers: { Accept: 'application/json' },
  })
  const data = await readJsonResponse<DaemonEnvelope<OsimageTagConfigContent>>(res)
  if (!res.ok) {
    const errRaw = data.message || data.error || `HTTP ${res.status}`
    return { tag: {} as Record<string, unknown>, error: String(errRaw || `HTTP ${res.status}`) }
  }
  try {
    const content = unwrapGetData<OsimageTagConfigContent>(data, 'detail')
    const rec = content?.config?.[TABLE]?.[name]
    if (!rec) return { tag: {} as Record<string, unknown>, error: `${name} not found` }
    return { tag: { ...rec }, error: '' }
  } catch (e: any) {
    return {
      tag: {} as Record<string, unknown>,
      error: String(e?.message || 'Failed to parse record'),
    }
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

export async function deleteOsimageTag(osimage: string, tag: string) {
  const res = await fetch(
    apiPath(`/api/v1/delete/osimage/${encodeURIComponent(osimage)}/osimagetag/${encodeURIComponent(tag)}`),
    {
      method: 'DELETE',
      headers: { Accept: 'application/json' },
    }
  )
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
    message: rawSuccessMsg || `Tag ${tag} deleted from ${osimage}.`,
  }
}

export async function addTagToOsimage(osimage: string, tag: string) {
  const request_data = { config: { osimage: { [osimage]: { tag } } } }
  return postJson(apiPath(`/api/v1/osimage/${encodeURIComponent(osimage)}/tag`), { request_data })
}
