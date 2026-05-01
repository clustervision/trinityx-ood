/**
 * Flask embed: window.APP_URL / VITE_APP_URL. Dev without those: /node-backend (proxied) so SPA / stays separate from ?format=json.
 * Literal Jinja placeholders (never substituted by Vite) must not become path segments → /%7B%7B%20APP_URL%20%7D%7D/...
 */
const UNSUBSTITUTED_APP_URL = /^\{\{\s*APP_URL\s*\}\}$/i

export const baseUrl = () => {
  let explicit = String(
    (typeof window !== 'undefined' && window.APP_URL) || import.meta.env.VITE_APP_URL || ''
  )
    .trim()
    .replace(/\/$/, '')
  if (UNSUBSTITUTED_APP_URL.test(explicit)) explicit = ''
  if (explicit) return explicit
  if (import.meta.env.DEV) return '/node-backend'
  return ''
}

export async function fetchNodes() {
  const b = baseUrl()
  const root = b ? `${b}/` : '/'
  const res = await fetch(`${root}?format=json`, {
    headers: { Accept: 'application/json' },
  })
  let data = {}
  try {
    data = await res.json()
  } catch {
    /* ignore */
  }
  if (!res.ok) {
    const msg =
      (data && (data.error || data.message)) ||
      `Failed to load nodes: HTTP ${res.status} ${res.statusText || ''}`.trim()
    throw new Error(msg)
  }
  return data
}

export async function fetchNodeDetail(name) {
  const res = await fetch(`${baseUrl()}/show/${encodeURIComponent(name)}`, {
    headers: { Accept: 'application/json' },
  })
  return res.json()
}

export async function deleteNode(name) {
  const res = await fetch(`${baseUrl()}/delete/${encodeURIComponent(name)}?format=json`, {
    headers: { Accept: 'application/json' },
  })
  let data = {}
  try {
    data = await res.json()
  } catch {
    /* ignore */
  }
  if (!res.ok || data.status !== 'success') {
    throw new Error(data.message || `Delete failed (${res.status})`)
  }
  return data
}

export async function fetchNodeAddData() {
  const res = await fetch(`${baseUrl()}/add?format=json`, {
    headers: { Accept: 'application/json' },
  })
  if (!res.ok) throw new Error(`Failed to load add form: ${res.status}`)
  return res.json()
}

export async function fetchNodeEditData(name) {
  const res = await fetch(`${baseUrl()}/edit/${encodeURIComponent(name)}?format=json`, {
    headers: { Accept: 'application/json' },
  })
  if (!res.ok) throw new Error(`Failed to load edit data: ${res.status}`)
  return res.json()
}

export async function fetchNodeCloneData(name) {
  const res = await fetch(`${baseUrl()}/clone/${encodeURIComponent(name)}?format=json`, {
    headers: { Accept: 'application/json' },
  })
  if (!res.ok) throw new Error(`Failed to load clone data: ${res.status}`)
  return res.json()
}

export async function fetchNodeOspushData(name) {
  const res = await fetch(`${baseUrl()}/ospush/${encodeURIComponent(name)}?format=json`, {
    headers: { Accept: 'application/json' },
  })
  if (!res.ok) throw new Error(`Failed to load OS push data: ${res.status}`)
  return res.json()
}

export async function fetchNodeOsgrabData(name) {
  const res = await fetch(`${baseUrl()}/osgrab/${encodeURIComponent(name)}?format=json`, {
    headers: { Accept: 'application/json' },
  })
  if (!res.ok) throw new Error(`Failed to load OS grab data: ${res.status}`)
  return res.json()
}

export async function submitNodeForm(action, formData) {
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
  } catch {
    /* empty */
  }
  return { ok: res.ok, status: res.status, data }
}
