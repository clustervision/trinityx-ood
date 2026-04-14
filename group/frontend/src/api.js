const baseUrl = () => {
  const url = window.APP_URL || ''
  return url.replace(/\/$/, '')
}

export async function fetchGroups() {
  const res = await fetch(`${baseUrl()}/api/groups`, {
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
      `Failed to load groups: HTTP ${res.status} ${res.statusText || ''}`.trim()
    throw new Error(msg)
  }
  return data
}

export async function deleteGroup(name) {
  const res = await fetch(`${baseUrl()}/delete/${encodeURIComponent(name)}`, {
    headers: { Accept: 'application/json' },
  })
  const data = await res.json()
  if (!res.ok || data.status !== 'success') {
    throw new Error(data.message || 'Delete failed')
  }
  return data
}

export async function fetchEditData(name) {
  const res = await fetch(`${baseUrl()}/edit/${encodeURIComponent(name)}?format=json`, {
    headers: { Accept: 'application/json' },
  })
  if (!res.ok) throw new Error(`Failed to load edit data: ${res.status}`)
  return res.json()
}

export async function fetchAddData() {
  const res = await fetch(`${baseUrl()}/add?format=json`, {
    headers: { Accept: 'application/json' },
  })
  if (!res.ok) throw new Error(`Failed to load add data: ${res.status}`)
  return res.json()
}

export async function fetchCloneData(name) {
  const res = await fetch(`${baseUrl()}/clone/${encodeURIComponent(name)}?format=json`, {
    headers: { Accept: 'application/json' },
  })
  if (!res.ok) throw new Error(`Failed to load clone data: ${res.status}`)
  return res.json()
}

export async function fetchOspushData(name) {
  const res = await fetch(`${baseUrl()}/ospush/${encodeURIComponent(name)}?format=json`, {
    headers: { Accept: 'application/json' },
  })
  if (!res.ok) throw new Error(`Failed to load push data: ${res.status}`)
  return res.json()
}

export async function removeInterface(record, iface) {
  const res = await fetch(`${baseUrl()}/remove/${encodeURIComponent(record)}/${encodeURIComponent(iface)}`, {
    headers: { Accept: 'application/json' },
  })
  const data = await res.json()
  if (!res.ok || data.status !== 'success') {
    throw new Error(data.message || 'Remove interface failed')
  }
  return data
}

export async function checkStatus(requestId) {
  const res = await fetch(`${baseUrl()}/check_status/config/status/${encodeURIComponent(requestId)}`, {
    headers: { Accept: 'application/json' },
  })
  return res.json()
}

export async function submitForm(action, formData) {
  const res = await fetch(`${baseUrl()}${action}`, {
    method: 'POST',
    body: formData,
    headers: {
      Accept: 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
    },
  })
  const text = await res.text()
  let data = {}
  try { data = JSON.parse(text) } catch { /* empty */ }
  return { ok: res.ok, status: res.status, data }
}
