import type {
  ControlStatusRow,
  RequestEnvelope,
  StatusField,
  StatusSnapshot,
  StatusToast,
} from './types'
import { pendingStatus } from './utils/statusDisplay'
import { oodAppRoot } from './utils/oodAppRoot'

const STATUS_TYPES = ['power', 'sel', 'chassis'] as const
const ALL_STATUS_FIELDS = ['power', 'sel', 'chassis', 'redfish'] as const
type PollField = (typeof ALL_STATUS_FIELDS)[number]

const BACKGROUND_POLL_MS = 30000
const POLL_INTERVAL_MS = 1000

export function baseUrl(): string {
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

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function normalizeState(v: unknown): string {
  const s = String(v ?? '').trim()
  if (!s) return 'UNKNOWN'
  return s.toUpperCase()
}

function emptyRow(node: string): ControlStatusRow {
  const pending = pendingStatus()
  return { node, power: pending, sel: pending, chassis: pending, redfish: pending, errors: {} }
}

function rowMapFromRows(rows: ControlStatusRow[]): Record<string, ControlStatusRow> {
  const map: Record<string, ControlStatusRow> = {}
  for (const row of rows) {
    map[row.node] = { ...row, errors: { ...row.errors } }
  }
  return map
}

function sortedRows(rowMap: Record<string, ControlStatusRow>): ControlStatusRow[] {
  return Object.values(rowMap).sort((a, b) => a.node.localeCompare(b.node))
}

function makeToast(
  node: string,
  field: StatusField,
  message: string,
  idPrefix = '',
): StatusToast {
  const label = node ? `${node} · ${field}: ${message}` : message
  return {
    id: `${idPrefix}${node}:${field}:${message}`,
    node,
    field,
    message: label,
  }
}

function walkCollectFailures(obj: unknown, out: Map<string, string>): void {
  if (!obj || typeof obj !== 'object') return
  const o = obj as Record<string, unknown>
  if ('failed' in o) addFailedMap(o.failed, out)
  for (const val of Object.values(o)) {
    if (val && typeof val === 'object') walkCollectFailures(val, out)
  }
}

function finalizeNodePowerIfPending(rows: Record<string, ControlStatusRow>, node: string): void {
  if (!rows[node]) return
  if (rows[node].power !== pendingStatus()) return
  rows[node].power = 'ERROR'
}

function addFailedMap(map: unknown, out: Map<string, string>): void {
  if (!map || typeof map !== 'object') return
  for (const [node, msg] of Object.entries(map as Record<string, unknown>)) {
    const message = String(msg ?? '').trim()
    if (message) out.set(node, message)
  }
}

/** Walk entire control tree for per-node failed{ node: message } maps. */
function collectControlFailures(ctl: Record<string, unknown>): Map<string, string> {
  const out = new Map<string, string>()
  walkCollectFailures(ctl, out)
  return out
}

function collectFailuresFromBody(
  body: unknown,
  field: StatusField,
  hostlist?: string[],
  idPrefix = '',
): StatusToast[] {
  if (!body || typeof body !== 'object') return []
  const o = body as Record<string, unknown>
  const ctl = o.control
  const toasts: StatusToast[] = []
  if (ctl && typeof ctl === 'object') {
    toasts.push(...failuresToToasts(collectControlFailures(ctl as Record<string, unknown>), field, hostlist, idPrefix))
  }
  const topMessage = String(o.message ?? '').trim()
  if (topMessage && toasts.length === 0) {
    const node = hostlist?.length === 1 ? (hostlist[0] ?? '') : ''
    toasts.push(makeToast(node, field, topMessage, idPrefix))
  }
  return toasts
}

function failuresToToasts(
  failures: Map<string, string>,
  field: StatusField,
  hostlist?: string[],
  idPrefix = '',
): StatusToast[] {
  const hosts = hostlist ? new Set(hostlist) : null
  const toasts: StatusToast[] = []
  for (const [node, message] of failures) {
    if (hosts && !hosts.has(node)) continue
    toasts.push(makeToast(node, field, message, idPrefix))
  }
  if (toasts.length === 0 && hosts && failures.size > 0) {
    for (const [node, message] of failures) {
      toasts.push(makeToast(node, field, message, idPrefix))
    }
  }
  return toasts
}

function applyResultItem(
  rows: Record<string, ControlStatusRow>,
  item: unknown,
  toasts: StatusToast[],
  options?: { system?: PollField; action?: string; hostlist?: string[]; idPrefix?: string },
): void {
  if (!item || typeof item !== 'object') return
  const o = item as Record<string, unknown>
  const ctl = o.control as Record<string, unknown> | undefined
  if (!ctl) return
  const system =
    options?.system ?? (ALL_STATUS_FIELDS.find((k) => k in ctl) as PollField | undefined)
  if (!system) return

  const idPrefix = options?.idPrefix ?? ''
  const failures = collectControlFailures(ctl)
  for (const [node, message] of failures) {
    if (options?.hostlist && !options.hostlist.includes(node)) continue
    if (!rows[node]) rows[node] = emptyRow(node)
    rows[node][system] = 'ERROR'
    finalizeNodePowerIfPending(rows, node)
    if (system !== 'redfish') {
      rows[node].errors = { ...rows[node].errors, [system]: message }
    }
    toasts.push(makeToast(node, system, message, idPrefix))
  }

  const statusObj = ctl[system] as Record<string, unknown> | undefined
  if (!statusObj || typeof statusObj !== 'object') return
  for (const statusKey of ['off', 'on', 'ok'] as const) {
    const hostMap = statusObj[statusKey]
    if (!hostMap || typeof hostMap !== 'object') continue
    for (const node of Object.keys(hostMap as Record<string, unknown>)) {
      if (options?.hostlist && !options.hostlist.includes(node)) continue
      if (!rows[node]) rows[node] = emptyRow(node)
      rows[node][system] = normalizeState(statusKey)
      if (system !== 'redfish' && rows[node].errors?.[system]) {
        const nextErrors = { ...rows[node].errors }
        delete nextErrors[system]
        rows[node].errors = nextErrors
      }
    }
  }
}

function extractRequestId(data: unknown): string {
  if (!data || typeof data !== 'object') return ''
  const o = data as Record<string, unknown>
  const top = String(o.request_id ?? '').trim()
  if (top) return top
  const ctl = o.control
  if (ctl && typeof ctl === 'object') {
    return String((ctl as Record<string, unknown>).request_id ?? '').trim()
  }
  return ''
}

function pollTimeoutMs(system: string, action: string): number {
  if (system === 'power' && action === 'reset') return 120000
  return BACKGROUND_POLL_MS
}

function hasControlPayload(
  body: unknown,
  system?: string,
  action?: string,
): boolean {
  if (!body || typeof body !== 'object') return false
  const ctl = (body as RequestEnvelope).control
  if (!ctl || typeof ctl !== 'object') return false
  const ctlObj = ctl as Record<string, unknown>
  if (collectControlFailures(ctlObj).size > 0) return true
  const types = system ? [system] : [...ALL_STATUS_FIELDS]
  for (const type of types) {
    const typeObj = ctlObj[type]
    if (!typeObj || typeof typeObj !== 'object') continue
    for (const statusKey of ['off', 'on', 'ok'] as const) {
      const hostMap = (typeObj as Record<string, unknown>)[statusKey]
      if (hostMap && typeof hostMap === 'object' && Object.keys(hostMap).length > 0) {
        return true
      }
    }
  }
  return false
}

async function fetchRequestBody(
  requestId: string,
  options?: { throwOnError?: boolean },
): Promise<{ ok: boolean; status: number; body: unknown }> {
  const res = await fetch(apiPath(`/api/v1/request/${encodeURIComponent(requestId)}`), {
    headers: { Accept: 'application/json' },
  })
  const body = await readJson(res)
  if (!res.ok && options?.throwOnError) {
    throw new Error(`Failed loading request ${requestId} (${res.status})`)
  }
  return { ok: res.ok, status: res.status, body }
}

function isPendingRequestStatus(status: number): boolean {
  return status === 404 || status === 202 || status === 204
}

function parseStatusPayload(data: {
  results?: unknown[]
  request_ids?: Record<string, string>
  nodes?: unknown[]
}): StatusSnapshot {
  const results = Array.isArray(data.results) ? data.results : []
  const ids = data.request_ids || {}
  const nodeNames = Array.isArray(data.nodes)
    ? data.nodes.map((n) => String(n).trim()).filter(Boolean)
    : []

  const rowMap: Record<string, ControlStatusRow> = {}
  for (const node of nodeNames) {
    rowMap[node] = emptyRow(node)
  }

  const toasts: StatusToast[] = []
  for (const item of results) {
    applyResultItem(rowMap, item, toasts)
  }

  return {
    rows: sortedRows(rowMap),
    requestIds: {
      power: String(ids.power || ''),
      sel: String(ids.sel || ''),
      chassis: String(ids.chassis || ''),
    },
    toasts,
  }
}

export function rowsFromNodeList(nodes: string[]): ControlStatusRow[] {
  return nodes.map((n) => emptyRow(n)).sort((a, b) => a.node.localeCompare(b.node))
}

export function mergeRowUpdates(
  existing: ControlStatusRow[],
  updates: ControlStatusRow[],
): ControlStatusRow[] {
  const map = rowMapFromRows(existing)
  for (const row of updates) {
    map[row.node] = { ...row, errors: { ...row.errors } }
  }
  return sortedRows(map)
}

/** Fast node name list only — no per-node Luna status jobs. */
export async function fetchNodeList(): Promise<string[]> {
  const res = await fetch(apiPath('/api/v1/get_nodes'), { headers: { Accept: 'application/json' } })
  if (!res.ok) throw new Error(`Failed loading node list (${res.status})`)
  const data = (await readJson(res)) as { node_list?: unknown[]; options?: unknown[] }
  const raw = Array.isArray(data.node_list)
    ? data.node_list
    : Array.isArray(data.options)
      ? data.options
      : []
  return raw.map((n) => String(n).trim()).filter(Boolean)
}

/** Status for a page subset; does not wait for background polls. */
export async function fetchPageStatusSnapshot(hostlist: string[]): Promise<StatusSnapshot> {
  if (hostlist.length === 0) {
    return { rows: [], requestIds: { power: '', sel: '', chassis: '' }, toasts: [] }
  }
  const res = await fetch(apiPath('/api/v1/status'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ hostlist }),
  })
  if (!res.ok) throw new Error(`Failed loading status (${res.status})`)
  const data = (await readJson(res)) as {
    results?: unknown[]
    request_ids?: Record<string, string>
    nodes?: unknown[]
  }
  return parseStatusPayload(data)
}

/** Load all nodes from /api/v1/status; does not wait for background polls. */
export async function fetchControlStatusSnapshot(): Promise<StatusSnapshot> {
  const res = await fetch(apiPath('/api/v1/status'), { headers: { Accept: 'application/json' } })
  if (!res.ok) throw new Error(`Failed loading status (${res.status})`)
  const data = (await readJson(res)) as {
    results?: unknown[]
    request_ids?: Record<string, string>
    nodes?: unknown[]
  }
  return parseStatusPayload(data)
}

/** @deprecated Use fetchControlStatusSnapshot + startBackgroundStatusPoll */
export async function fetchControlStatus(): Promise<StatusSnapshot> {
  return fetchControlStatusSnapshot()
}

function clearPendingField(
  rowMap: Record<string, ControlStatusRow>,
  field: PollField,
): void {
  const pending = pendingStatus()
  for (const row of Object.values(rowMap)) {
    if (row[field] === pending) row[field] = 'UNKNOWN'
    if (field === 'power') continue
    if (row.power === pending) row.power = 'UNKNOWN'
  }
}

async function pollOneRequest(
  requestId: string,
  field: PollField,
  rowMap: Record<string, ControlStatusRow>,
  timeoutMs: number,
  signal: AbortSignal,
  onUpdate: (rows: ControlStatusRow[], toasts: StatusToast[]) => void,
  options?: { action?: string; hostlist?: string[] },
): Promise<void> {
  if (!requestId || signal.aborted) return
  const start = Date.now()
  while (!signal.aborted && Date.now() - start < timeoutMs) {
    const { ok, status, body } = await fetchRequestBody(requestId)
    if (ok && hasControlPayload(body, field, options?.action)) {
      const idPrefix = `${requestId}:`
      const toasts: StatusToast[] = []
      applyResultItem(rowMap, body, toasts, {
        system: field,
        action: options?.action,
        hostlist: options?.hostlist,
        idPrefix,
      })
      if (toasts.length === 0) {
        toasts.push(...collectFailuresFromBody(body, field, options?.hostlist, idPrefix))
      }
      onUpdate(sortedRows(rowMap), toasts)
      return
    }
    if (!ok && !isPendingRequestStatus(status)) {
      clearPendingField(rowMap, field)
      const message = String((body as RequestEnvelope)?.message ?? `Request failed (${status})`).trim()
      const toasts: StatusToast[] = []
      if (message) {
        toasts.push({
          id: `poll:${requestId}:${message}`,
          node: '',
          field,
          message,
        })
      }
      onUpdate(sortedRows(rowMap), toasts)
      return
    }
    await sleep(POLL_INTERVAL_MS)
  }
  if (!signal.aborted) {
    clearPendingField(rowMap, field)
    onUpdate(sortedRows(rowMap), [])
  }
}

/**
 * Poll power/sel/chassis in the background and push row + toast updates.
 * Returns a stop function (call before starting a new poll generation).
 */
export function startBackgroundStatusPoll(
  initialRows: ControlStatusRow[],
  requestIds: StatusSnapshot['requestIds'],
  onUpdate: (rows: ControlStatusRow[], toasts: StatusToast[]) => void,
  options?: { timeoutMs?: number; onPowerPollComplete?: () => void; hostlist?: string[] },
): () => void {
  const ac = new AbortController()
  const rowMap = rowMapFromRows(initialRows)
  const timeoutMs = options?.timeoutMs ?? BACKGROUND_POLL_MS

  const notify = (rows: ControlStatusRow[], toasts: StatusToast[]) => {
    if (!ac.signal.aborted) onUpdate(rows, toasts)
  }

  for (const type of STATUS_TYPES) {
    const requestId = requestIds[type]
    if (!requestId) continue
    void pollOneRequest(requestId, type, rowMap, timeoutMs, ac.signal, (rows, toasts) => {
      notify(rows, toasts)
      if (type === 'power') options?.onPowerPollComplete?.()
    }, { hostlist: options?.hostlist })
  }

  if (!requestIds.power) options?.onPowerPollComplete?.()

  return () => ac.abort()
}

function extractActionFailures(
  data: unknown,
  hostlist: string[],
  system: string,
  actionPrefix: string,
): StatusToast[] {
  const field = (ALL_STATUS_FIELDS.find((f) => f === system) ?? 'power') as StatusField
  return collectFailuresFromBody(data, field, hostlist, `${actionPrefix}:`)
}

export async function triggerAction(
  system: string,
  action: string,
  hostlist: string[],
): Promise<{ requestId: string; immediateToasts: StatusToast[] }> {
  const res = await fetch(apiPath(`/api/v1/action/${encodeURIComponent(system)}/${encodeURIComponent(action)}`), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ hostlist }),
  })
  const data = (await readJson(res)) as RequestEnvelope
  if (!res.ok) throw new Error(String(data.message || `Action failed (${res.status})`))
  const requestId = extractRequestId(data)
  const immediateToasts = extractActionFailures(
    data,
    hostlist,
    system,
    requestId || `${system}/${action}/${Date.now()}`,
  )
  return { requestId, immediateToasts }
}

export function pollActionInBackground(
  requestId: string,
  initialRows: ControlStatusRow[],
  hostlist: string[],
  onUpdate: (rows: ControlStatusRow[], toasts: StatusToast[]) => void,
  system: string,
  action: string,
): () => void {
  const ac = new AbortController()
  const rowMap = rowMapFromRows(initialRows)
  const timeoutMs = pollTimeoutMs(system, action)
  const pending = pendingStatus()
  const field = ALL_STATUS_FIELDS.find((f) => f === system)
  if (field) {
    for (const node of hostlist) {
      if (rowMap[node]) rowMap[node][field] = pending
    }
    onUpdate(sortedRows(rowMap), [])
  }

  const pollField = (field ?? 'power') as PollField
  void pollOneRequest(requestId, pollField, rowMap, timeoutMs, ac.signal, (rows, toasts) => {
    if (!ac.signal.aborted) onUpdate(rows, toasts)
  }, { action, hostlist })

  return () => ac.abort()
}

export function actionPollTimeoutMs(system: string, action: string): number {
  return pollTimeoutMs(system, action)
}
