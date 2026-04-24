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

export async function fetchNodeRenameData(record) {
  const res = await fetch(`${baseUrl()}/rename/${encodeURIComponent(record)}?format=json`, {
    headers: { Accept: 'application/json' },
  })
  if (!res.ok) {
    let err = {}
    try {
      err = await res.json()
    } catch {
      /* ignore */
    }
    throw new Error(err.error || err.message || `Failed to load rename form: ${res.status}`)
  }
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
