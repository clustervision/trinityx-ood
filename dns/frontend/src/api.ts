import type { ApiEnvelope, DnsEntryRow, DnsFormState, DnsListResponse, NetworksResponse } from './types'

const TABLE = 'dns'

export function baseUrl(): string {
  if (import.meta.env.DEV) return '/dns-backend'

  let explicit = String(
    (typeof window !== 'undefined' && window.APP_URL) || import.meta.env.VITE_APP_URL || '',
  )
    .trim()
    .replace(/\/$/, '')
  if (/^\{\{\s*APP_URL\s*\}\}$/i.test(explicit)) explicit = ''
  if (explicit) {
    try {
      const parsed = new URL(explicit)
      if (typeof window !== 'undefined' && window.location?.origin) {
        return `${window.location.origin}${parsed.pathname}`.replace(/\/$/, '')
      }
    } catch {
      /* fall through */
    }
    return explicit
  }
  return ''
}

function apiPath(suffix: string): string {
  const b = baseUrl().replace(/\/+$/, '')
  const s = suffix.startsWith('/') ? suffix : `/${suffix}`
  return `${b}${s}`
}

async function readJson<T>(res: Response): Promise<T> {
  const text = await res.text()
  if (!text) return {} as T
  try {
    return JSON.parse(text) as T
  } catch {
    throw new Error(text.slice(0, 500) || `HTTP ${res.status}`)
  }
}

function apiError(res: Response, data: unknown): string {
  if (data && typeof data === 'object') {
    const d = data as Record<string, unknown>
    if (typeof d.message === 'string') return d.message
    const content = d.content
    if (content && typeof content === 'object' && typeof (content as Record<string, unknown>).message === 'string') {
      return String((content as Record<string, unknown>).message)
    }
  }
  return `Request failed (${res.status})`
}

export async function fetchDnsEntries(): Promise<DnsEntryRow[]> {
  const res = await fetch(apiPath('/api/v1/dns_entries'), {
    headers: { Accept: 'application/json' },
  })
  const data = await readJson<DnsListResponse | ApiEnvelope<DnsListResponse>>(res)
  if (!res.ok) throw new Error(apiError(res, data))

  if (Array.isArray((data as DnsListResponse).entries)) {
    return (data as DnsListResponse).entries
  }
  const content = (data as ApiEnvelope<DnsListResponse>).content
  if (content && Array.isArray(content.entries)) return content.entries
  return []
}

export async function fetchNetworks(): Promise<string[]> {
  const res = await fetch(apiPath('/api/v1/networks'), {
    headers: { Accept: 'application/json' },
  })
  const data = await readJson<NetworksResponse | ApiEnvelope<NetworksResponse>>(res)
  if (!res.ok) throw new Error(apiError(res, data))

  if (Array.isArray((data as NetworksResponse).networks)) {
    return (data as NetworksResponse).networks
  }
  const content = (data as ApiEnvelope<NetworksResponse>).content
  if (content && Array.isArray(content.networks)) return content.networks
  return []
}

export async function saveDnsEntry(
  form: DnsFormState,
  original?: { network: string; host: string } | null,
): Promise<void> {
  if (
    original &&
    (original.network !== form.network || original.host !== form.host)
  ) {
    await deleteDnsEntry(original.network, original.host)
  }

  const res = await fetch(apiPath(`/api/v1/dns/${encodeURIComponent(form.network)}`), {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      host: form.host,
      ipaddress: form.ipaddress,
    }),
  })
  const data = await readJson<ApiEnvelope>(res)
  if (!res.ok && res.status !== 201) {
    throw new Error(apiError(res, data))
  }
}

export async function deleteDnsEntry(network: string, host: string): Promise<void> {
  const res = await fetch(
    apiPath(`/api/v1/dns/${encodeURIComponent(network)}/${encodeURIComponent(host)}`),
    { method: 'DELETE', headers: { Accept: 'application/json' } },
  )
  const data = await readJson<ApiEnvelope>(res)
  if (!res.ok && res.status !== 204) {
    throw new Error(apiError(res, data))
  }
}
