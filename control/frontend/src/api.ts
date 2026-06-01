import type { BulkStatusResult, ControlStatusRow, RequestEnvelope } from './types'

function oodAppRoot(): string {
  const explicit = String(window.APP_URL || import.meta.env.VITE_APP_URL || '').trim().replace(/\/$/, '')
  if (explicit && !/^\{\{/.test(explicit)) return explicit
  return `${window.location.origin}${window.location.pathname}`.replace(/\/$/, '')
}

function baseUrl(): string {
  if (import.meta.env.DEV) return '/control-backend'
  return oodAppRoot()
}

function apiPath(path: string): string {
  return `${baseUrl().replace(/\/+$/, '')}${path.startsWith('/') ? path : `/${path}`}`
}

async function readJson(res: Response): Promise<unknown> {
  const text = await res.text()
  if (!text) return {}
  try {
    return JSON.parse(text)
  } catch {
    return { message: text }
  }
}

function normalizeState(v: unknown): string {
  const s = String(v ?? '').trim()
  if (!s) return 'UNKNOWN'
  return s.toUpperCase()
}

function mapRows(results: unknown[]): ControlStatusRow[] {
  const rows: Record<string, ControlStatusRow> = {}
  for (const item of results) {
    if (!item || typeof item !== 'object') continue
    const o = item as Record<string, unknown>
    const ctl = o.control as Record<string, unknown> | undefined
    if (!ctl) continue
    const type = ['power', 'sel', 'chassis'].find((k) => k in ctl)
    if (!type) continue
    const failed = (ctl.failed as Record<string, unknown>) || {}
    for (const [node, msg] of Object.entries(failed)) {
      if (!rows[node]) rows[node] = { node, power: 'UNKNOWN', sel: 'UNKNOWN', chassis: 'UNKNOWN' }
      rows[node][type as 'power' | 'sel' | 'chassis'] = normalizeState(msg)
    }
    const statusObj = ctl[type] as Record<string, unknown> | undefined
    if (!statusObj) continue
    for (const [statusKey, hostMap] of Object.entries(statusObj)) {
      if (!hostMap || typeof hostMap !== 'object') continue
      for (const node of Object.keys(hostMap as Record<string, unknown>)) {
        if (!rows[node]) rows[node] = { node, power: 'UNKNOWN', sel: 'UNKNOWN', chassis: 'UNKNOWN' }
        rows[node][type as 'power' | 'sel' | 'chassis'] = normalizeState(statusKey)
      }
    }
  }
  return Object.values(rows).sort((a, b) => a.node.localeCompare(b.node))
}

export async function fetchControlStatus(): Promise<BulkStatusResult> {
  const res = await fetch(apiPath('/api/v1/status'), { headers: { Accept: 'application/json' } })
  if (!res.ok) throw new Error(`Failed loading status (${res.status})`)
  const data = (await readJson(res)) as { results?: unknown[]; request_ids?: Record<string, string> }
  const results = Array.isArray(data.results) ? data.results : []
  const ids = data.request_ids || {}
  return {
    rows: mapRows(results),
    requestIds: {
      power: String(ids.power || ''),
      sel: String(ids.sel || ''),
      chassis: String(ids.chassis || ''),
    },
  }
}

export async function triggerAction(system: string, action: string, hostlist: string[]): Promise<string> {
  const res = await fetch(apiPath(`/api/v1/action/${encodeURIComponent(system)}/${encodeURIComponent(action)}`), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ hostlist }),
  })
  const data = (await readJson(res)) as RequestEnvelope
  if (!res.ok) throw new Error(String(data.message || `Action failed (${res.status})`))
  return String(data.request_id || '')
}

export async function checkRequest(requestId: string): Promise<boolean> {
  const res = await fetch(apiPath(`/api/v1/request/${encodeURIComponent(requestId)}`), {
    headers: { Accept: 'application/json' },
  })
  const data = (await readJson(res)) as RequestEnvelope
  return Boolean(data.message || (data.control && Object.keys(data.control).length > 0))
}

export async function pollRequestDone(requestId: string, timeoutMs = 30000): Promise<void> {
  const start = Date.now()
  while (Date.now() - start < timeoutMs) {
    if (await checkRequest(requestId)) return
    await new Promise((r) => setTimeout(r, 1000))
  }
  throw new Error('Request timed out.')
}
