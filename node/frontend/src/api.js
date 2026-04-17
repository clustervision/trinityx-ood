/** Same-origin base for Flask node app: explicit APP_URL, or dev proxy prefix, or '' (prod relative). */
export function backendBasePath() {
  const url = (typeof window !== 'undefined' && window.APP_URL) || ''
  if (url) return url.replace(/\/$/, '')
  if (import.meta.env.DEV) return '/node-backend'
  return ''
}

const baseUrl = () => backendBasePath()

export async function fetchNodes() {
  const root = baseUrl() ? `${baseUrl()}/` : '/'
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
