import type {
  FetchNodesResponse,
  NodeFormPayload,
  OsPushGrabPayload,
  SubmitResult,
} from '@/types'


const UNSUBSTITUTED_APP_URL = /^\{\{\s*APP_URL\s*\}\}$/i

const API_V1 = '/api/v1'

const NODE_INVENTORY_FIELDS = [
  'name',
  'group',
  'osimage',
  'osimagetag',
  'setupbmc',
  'bmcsetup',
  'status',
  'tpm_present',
  'interfaces',
] as const

const BOND_MODE_OPTIONS = [
  'balance-rr',
  'active-backup',
  'balance-xor',
  'broadcast',
  '802.3ad',
  'balance-tlb',
  'balance-alb',
]

const EDITOR_FIELDS = [
  'options',
  'content',
  'comment',
  'prescript',
  'partscript',
  'postscript',
  'grab_filesystems',
  'grab_exclude',
  'kerneloptions',
] as const

const EDITOR_FIELD_SET = new Set<string>(EDITOR_FIELDS)

function b64EncodeUtf8(value: string): string {
  const bytes = new TextEncoder().encode(value)
  let bin = ''
  bytes.forEach((b) => {
    bin += String.fromCharCode(b)
  })
  return btoa(bin)
}

function b64DecodeUtf8(value: string): string {
  const bin = atob(value)
  const bytes = new Uint8Array(bin.length)
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i)
  return new TextDecoder().decode(bytes)
}

function safeDecodeIfPossible(value: string): string {
  const trimmed = value.trim()
  if (!trimmed) return value
  try {
    const decoded = b64DecodeUtf8(trimmed)
    const reEncoded = b64EncodeUtf8(decoded).replace(/=+$/, '')
    if (reEncoded === trimmed.replace(/=+$/, '')) return decoded
  } catch {
    // not base64, keep value as-is
  }
  return value
}

function transformEditorFieldsDeep(payload: unknown, mode: 'encode' | 'decode'): unknown {
  if (Array.isArray(payload)) return payload.map((item) => transformEditorFieldsDeep(item, mode))
  if (!payload || typeof payload !== 'object') return payload

  const input = payload as Record<string, unknown>
  const out: Record<string, unknown> = {}

  for (const [key, value] of Object.entries(input)) {
    if (EDITOR_FIELD_SET.has(key) && typeof value === 'string') {
      if (mode === 'encode') {
        out[key] = value.length ? b64EncodeUtf8(value) : value
      } else {
        out[key] = safeDecodeIfPossible(value)
      }
    } else {
      out[key] = transformEditorFieldsDeep(value, mode)
    }
  }

  return out
}

function alignApiBaseToPage(abs: string): string {
  const s = String(abs).trim()
  if (!s || typeof window === 'undefined') return s
  try {
    const u = new URL(s)
    if (window.location.protocol === 'https:' && u.protocol === 'http:') {
      u.protocol = 'https:'
    }
    return `${u.origin}${u.pathname}`.replace(/\/+$/, '')
  } catch {
    if (window.location.protocol === 'https:') {
      return s.replace(/^http:\/\//i, 'https://')
    }
    return s
  }
}

export const baseUrl = (): string => {
  let explicit = String(
    (typeof window !== 'undefined' && window.APP_URL) || import.meta.env.VITE_APP_URL || '',
  )
    .trim()
    .replace(/\/$/, '')
  if (UNSUBSTITUTED_APP_URL.test(explicit)) explicit = ''

  if (!explicit) {
    if (import.meta.env.DEV) return '/node-backend'
    if (typeof window !== 'undefined') {
      const path = window.location.pathname.replace(/\/+$/, '')
      return `${window.location.origin}${path}`.replace(/\/$/, '')
    }
    return ''
  }

  if (/^https?:\/\//i.test(explicit)) {
    return alignApiBaseToPage(explicit)
  }

  return explicit
}

/** App root (no trailing slash) + /api/v1 */
function apiV1Base(): string {
  const b = baseUrl()
  if (!b) return API_V1.startsWith('/') ? API_V1 : `/${API_V1}`
  return `${b}${API_V1}`
}

async function fetchText(url: string, init?: RequestInit): Promise<{ res: Response; text: string }> {
  const res = await fetch(url, {
    ...init,
    headers: { Accept: 'application/json', ...init?.headers },
  })
  const text = await res.text()
  return { res, text }
}

function parseJsonMaybe(text: string): Record<string, unknown> {
  if (!text) return {}
  try {
    const v = JSON.parse(text) as unknown
    return v && typeof v === 'object' ? (v as Record<string, unknown>) : {}
  } catch {
    return { message: text }
  }
}

/** Flask node service: { status, status_code, content } */
function unwrapFlaskRest(raw: Record<string, unknown>): {
  ok: boolean
  statusCode: number
  content: unknown
} {
  if ('status_code' in raw && 'content' in raw) {
    const sc = Number(raw.status_code) || 500
    const ok = raw.status === true && sc >= 200 && sc < 300
    return { ok, statusCode: sc, content: raw.content }
  }
  return { ok: true, statusCode: 200, content: raw }
}

function daemonConfig(payload: unknown): Record<string, unknown> | null {
  if (!payload || typeof payload !== 'object') return null
  const p = payload as Record<string, unknown>
  if (typeof p.config === 'object' && p.config !== null) {
    return p.config as Record<string, unknown>
  }
  return null
}

function messageFromUnknown(v: unknown): string | undefined {
  if (!v || typeof v !== 'object') return undefined
  const m = (v as Record<string, unknown>).message
  return m != null ? String(m) : undefined
}

function tableKeysFromDaemon(content: unknown, table: string): string[] {
  const cfg = daemonConfig(content)
  if (!cfg) return []
  const t = cfg[table]
  if (!t || typeof t !== 'object') return []
  return Object.keys(t as Record<string, unknown>).sort((a, b) =>
    a.localeCompare(b, undefined, { sensitivity: 'base' }),
  )
}

async function fetchTableDaemon(table: string): Promise<{ ok: boolean; content: unknown; status: number }> {
  const url = `${apiV1Base()}/table/${encodeURIComponent(table)}`
  const { res, text } = await fetchText(url)
  const raw = parseJsonMaybe(text)
  const u = unwrapFlaskRest(raw)
  return {
    ok: res.ok && u.ok,
    content: u.content,
    status: res.status,
  }
}

async function assembleOptionPayload(): Promise<NodeFormPayload> {
  const tables = ['group', 'switch', 'bmcsetup', 'osimage', 'network', 'cloud'] as const
  const results = await Promise.all(tables.map((t) => fetchTableDaemon(t)))
  const opts = Object.fromEntries(tables.map((t, i) => [t, results[i]])) as Record<
    (typeof tables)[number],
    { ok: boolean; content: unknown; status: number }
  >
  const groupKeys = tableKeysFromDaemon(opts.group.content, 'group')
  const switchKeys = tableKeysFromDaemon(opts.switch.content, 'switch')
  const bmcKeys = tableKeysFromDaemon(opts.bmcsetup.content, 'bmcsetup')
  const osimageKeys = tableKeysFromDaemon(opts.osimage.content, 'osimage')
  const netKeys = tableKeysFromDaemon(opts.network.content, 'network')
  const cloudKeys = tableKeysFromDaemon(opts.cloud.content, 'cloud')

  return {
    groups: groupKeys,
    groupname_list: groupKeys,
    switches: switchKeys,
    switchname_list: switchKeys,
    bmcsetupname_list: bmcKeys,
    osimage: osimageKeys,
    network: netKeys,
    cloud_list: cloudKeys,
    cloud_name_list: cloudKeys,
    bond_modes: BOND_MODE_OPTIONS,
    hints: {},
  }
}

async function fetchNodeDaemonRecord(canonicalName: string): Promise<Record<string, unknown>> {
  const url = `${apiV1Base()}/node/${encodeURIComponent(canonicalName)}`
  const { res, text } = await fetchText(url)
  if (!res.ok) {
    throw new Error(`Failed to load node: HTTP ${res.status}`)
  }
  const raw = parseJsonMaybe(text)
  const u = unwrapFlaskRest(raw)
  if (!u.ok) {
    throw new Error(messageFromUnknown(u.content) || 'Daemon returned error for node')
  }

  const inner = u.content
  const cfg = daemonConfig(inner)
  if (cfg?.node && typeof cfg.node === 'object') {
    const nm = (cfg.node as Record<string, unknown>)[canonicalName]
    if (nm && typeof nm === 'object') return transformEditorFieldsDeep(nm, 'decode') as Record<string, unknown>
    const keys = Object.keys(cfg.node as Record<string, unknown>)
    if (keys.length === 1) {
      const one = (cfg.node as Record<string, unknown>)[keys[0]!]
      if (one && typeof one === 'object') return transformEditorFieldsDeep(one, 'decode') as Record<string, unknown>
    }
  }
  if (inner && typeof inner === 'object') {
    return transformEditorFieldsDeep(inner, 'decode') as Record<string, unknown>
  }
  return {}
}

export async function fetchNodes(): Promise<FetchNodesResponse> {
  const url = `${apiV1Base()}/node`
  const { res, text } = await fetchText(url)
  const raw = parseJsonMaybe(text)
  const u = unwrapFlaskRest(raw)

  if (!res.ok || !u.ok) {
    const msg =
      messageFromUnknown(u.content) ||
      `Failed to load nodes: HTTP ${res.status}${u.statusCode ? ` (${u.statusCode})` : ''}`.trim()
    throw new Error(String(msg))
  }

  const cfg = daemonConfig(u.content)
  if (!cfg?.node || typeof cfg.node !== 'object') {
    return { fields: [...NODE_INVENTORY_FIELDS], nodes: [] }
  }
  const nodeMap = cfg.node as Record<string, Record<string, unknown>>
  const nodes = Object.entries(nodeMap).map(([k, rec]) => ({
    ...(rec || {}),
    name: rec?.name ?? k,
  }))

  return { fields: [...NODE_INVENTORY_FIELDS], nodes }
}

export async function fetchNodeDetail(name: string): Promise<Record<string, unknown>> {
  return fetchNodeDaemonRecord(name)
}

export async function deleteNode(name: string): Promise<{ status: string; message?: string }> {
  const url = `${apiV1Base()}/delete/${encodeURIComponent(name)}`
  const { res, text } = await fetchText(url, { method: 'DELETE' })
  const raw = parseJsonMaybe(text)
  const u = unwrapFlaskRest(raw)
  const data =
    typeof u.content === 'object' && u.content !== null ? (u.content as Record<string, unknown>) : {}
  if (!res.ok || !u.ok) {
    throw new Error(String(data.message || `Delete failed (${res.status})`))
  }
  return {
    status: 'success',
    message: messageFromUnknown(data),
  }
}

export async function fetchNodeAddData(): Promise<NodeFormPayload> {
  return assembleOptionPayload()
}

export async function fetchNodeEditData(name: string): Promise<NodeFormPayload> {
  const [base, record] = await Promise.all([assembleOptionPayload(), fetchNodeDaemonRecord(name)])
  const data =
    Object.keys(record).length === 0
      ? {}
      : { ...record, name: record.name ?? name }

  return { ...base, data }
}

export async function fetchNodeCloneData(sourceName: string): Promise<NodeFormPayload> {
  const base = await fetchNodeEditData(sourceName)
  if (!base.data || String(base.data.name ?? '') === '') {
    return base
  }
  return {
    ...base,
    data: {
      ...(base.data as Record<string, unknown>),
      name: base.data?.name ?? sourceName,
      newnodename: '',
    },
  }
}

export async function fetchNodeOspushData(name: string): Promise<OsPushGrabPayload> {
  const keys = await (async (): Promise<string[]> => {
    const r = await fetchTableDaemon('osimage')
    return tableKeysFromDaemon(r.content, 'osimage')
  })()
  let sel = ''
  try {
    const rec = await fetchNodeDaemonRecord(name)
    const o = rec.osimage
    sel = o != null ? String(o) : ''
  } catch {
    /* keep default */
  }
  return {
    osimage_list: { options: keys, selected: sel },
    data: { osimage: sel },
  }
}

export async function fetchNodeOsgrabData(name: string): Promise<OsPushGrabPayload> {
  return fetchNodeOspushData(name)
}

async function postSubmitResult(url: string, body: unknown): Promise<SubmitResult> {
  const encodedBody = transformEditorFieldsDeep(body, 'encode')
  const { res, text } = await fetchText(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(encodedBody ?? {}),
  })
  let data = parseJsonMaybe(text)

  if (
    typeof data === 'object' &&
    data !== null &&
    'status_code' in data &&
    'content' in data &&
    typeof (data as Record<string, unknown>).content === 'object'
  ) {
    const u = unwrapFlaskRest(data as Record<string, unknown>)
    const c = u.content
    data =
      c && typeof c === 'object' ? (c as Record<string, unknown>) : {}
  }

  const statusStr = typeof data.status === 'string' ? String(data.status) : ''
  const ok = res.ok && !(statusStr && /^(error|fail|invalid)/i.test(statusStr))

  return {
    ok: ok || statusStr === 'success',
    status: res.status,
    data,
  }
}

/** Add node → POST /api/v1/add with { config: { node: { name: record } } } */
export async function submitNodeAdd(nodeName: string, record: Record<string, unknown>): Promise<SubmitResult> {
  const name = nodeName.trim()
  const body = { config: { node: { [name]: { ...record, name } } } }
  return postSubmitResult(`${apiV1Base()}/add`, body)
}

/** Update node fields → POST /api/v1/update/<name> (JSON record) */
export async function submitNodeUpdate(nodeName: string, record: Record<string, unknown>): Promise<SubmitResult> {
  return postSubmitResult(`${apiV1Base()}/update/${encodeURIComponent(nodeName)}`, record)
}

/**
 * Rename-like POST handled by Luna through /api/v1/rename — same envelope as add with newnodename in record.
 */
export async function submitNodeRename(
  oldName: string,
  record: Record<string, unknown>,
  newName: string,
): Promise<SubmitResult> {
  const body = {
    config: {
      node: {
        [oldName]: { ...record, newnodename: newName },
      },
    },
  }
  return postSubmitResult(`${apiV1Base()}/rename`, body)
}

/** Clone → POST /api/v1/clone ({ config.node[newName]: record }); daemon URL uses new name path. */
export async function submitNodeClone(newName: string, record: Record<string, unknown>): Promise<SubmitResult> {
  const nn = String(newName).trim()
  const { newnodename: _drop, ...rest } = record
  void _drop
  const body = { config: { node: { [nn]: { ...rest, name: nn } } } }
  return postSubmitResult(`${apiV1Base()}/clone`, body)
}

export async function submitOspush(nodeName: string, fields: Record<string, unknown>): Promise<SubmitResult> {
  return postSubmitResult(`${apiV1Base()}/ospush/${encodeURIComponent(nodeName)}`, fields)
}

export async function submitOsgrab(nodeName: string, fields: Record<string, unknown>): Promise<SubmitResult> {
  return postSubmitResult(`${apiV1Base()}/osgrab/${encodeURIComponent(nodeName)}`, fields)
}
