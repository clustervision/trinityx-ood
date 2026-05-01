/**
 * Dev: always call same-origin `/osimage-backend` → Vite proxies to `VITE_APP_URL` (no CORS).
 * Prod: `window.APP_URL` from Flask in index.html, or build-time `VITE_APP_URL`.
 * Literal Jinja `{{ APP_URL }}` must be ignored so it is not used as a path.
 */
const UNSUBSTITUTED_APP_URL = /^\{\{\s*APP_URL\s*\}\}$/i

export const baseUrl = () => {
  if (import.meta.env.DEV) return '/osimage-backend'

  let explicit = String(
    (typeof window !== 'undefined' && window.APP_URL) || import.meta.env.VITE_APP_URL || ''
  )
    .trim()
    .replace(/\/$/, '')
  if (UNSUBSTITUTED_APP_URL.test(explicit)) explicit = ''
  if (explicit) return explicit
  return ''
}

export async function fetchOsimages() {
  const b = baseUrl()
  const root = b ? `${b}/` : '/'
  let res
  try {
    res = await fetch(root, {
      headers: { Accept: 'application/json' },
    })
  } catch (e) {
    const msg = e.message || 'Network error'
    if (import.meta.env.DEV) {
      throw new Error(
        `${msg} — Is \`npm run dev\` running and VITE_APP_URL set in .env.development?`
      )
    }
    throw e
  }
  let data = {}
  try {
    data = await res.json()
  } catch { /* ignore */ }
  if (!res.ok) {
    const msg =
      (data && (data.error || data.message)) ||
      `Failed to load OS images: HTTP ${res.status} ${res.statusText || ''}`.trim()
    throw new Error(msg)
  }
  return data
}

export async function fetchOsimageDetail(name) {
  const res = await fetch(`${baseUrl()}/show/${encodeURIComponent(name)}`, {
    headers: { Accept: 'application/json' },
  })
  return res.json()
}

export async function fetchOsimageEditData(name) {
  const res = await fetch(`${baseUrl()}/edit/${encodeURIComponent(name)}`, {
    headers: { Accept: 'application/json' },
  })
  if (!res.ok) throw new Error(`Failed to load edit data: ${res.status}`)
  return res.json()
}

export async function fetchOsimageCloneData(name) {
  const res = await fetch(`${baseUrl()}/clone/${encodeURIComponent(name)}`, {
    headers: { Accept: 'application/json' },
  })
  if (!res.ok) throw new Error(`Failed to load clone data: ${res.status}`)
  return res.json()
}

export async function deleteOsimage(name) {
  const res = await fetch(`${baseUrl()}/delete/${encodeURIComponent(name)}`, {
    headers: { Accept: 'application/json' },
  })
  let data = {}
  try {
    data = await res.json()
  } catch { /* ignore */ }
  if (!res.ok || data.status !== 'success') {
    throw new Error(data.message || `Delete failed (${res.status})`)
  }
  return data
}

export async function submitOsimageForm(action, formData) {
  const root = baseUrl()
  const url = `${root}${action.startsWith('/') ? action : `/${action}`}`
  const res = await fetch(url, {
    method: 'POST',
    body: formData,
    headers: {
      Accept: 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
    },
  })
  const text = await res.text()
  let data = {}
  try {
    data = JSON.parse(text)
  } catch { /* empty */ }
  return { ok: res.ok, status: res.status, data }
}

export async function packOsimage(name) {
  const res = await fetch(
    `${baseUrl()}/get_request/osimage/${encodeURIComponent(name)}/_pack`,
    { headers: { Accept: 'application/json' } }
  )
  let data = {}
  try {
    data = await res.json()
  } catch { /* ignore */ }
  return { ok: res.ok, status: res.status, data }
}

export async function checkPackStatus(requestId) {
  const res = await fetch(
    `${baseUrl()}/check_status/config/status/${encodeURIComponent(requestId)}`,
    { headers: { Accept: 'application/json' } }
  )
  let data = {}
  try {
    data = await res.json()
  } catch { /* ignore */ }
  return { ok: res.ok, status: res.status, data }
}
