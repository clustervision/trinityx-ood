import type { SelLogEntry } from '@/types'

const STATUS_PLACEHOLDERS = new Set(['', 'sel list', 'ok', 'none', 'unknown', 'pending'])
const SUCCESS_FALLBACK = 'SEL list completed successfully.'
const MISSING_FALLBACK = 'No SEL log data was returned.'

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function formatStringValue(value: unknown): string {
  if (value == null) return ''
  if (typeof value === 'string') return value.trim()
  if (typeof value === 'number' || typeof value === 'boolean') return String(value)
  return ''
}

function isLogContent(text: string): boolean {
  const normalized = text.trim().toLowerCase()
  return Boolean(normalized) && !STATUS_PLACEHOLDERS.has(normalized)
}

function walkFailedMaps(obj: unknown, out: Map<string, string>): void {
  if (!obj || typeof obj !== 'object') return
  const record = obj as Record<string, unknown>
  if ('failed' in record) {
    const failed = record.failed
    if (failed && typeof failed === 'object') {
      for (const [node, message] of Object.entries(failed as Record<string, unknown>)) {
        const text = formatStringValue(message)
        if (text) out.set(node.trim(), text)
      }
    }
  }
  for (const value of Object.values(record)) {
    if (value && typeof value === 'object') walkFailedMaps(value, out)
  }
}

function collectFailures(body: unknown): Map<string, string> {
  const failures = new Map<string, string>()
  if (body && typeof body === 'object') {
    walkFailedMaps(body, failures)
  }
  return failures
}

function topMessage(body: unknown): string {
  if (!body || typeof body !== 'object') return ''
  return formatStringValue((body as Record<string, unknown>).message)
}

function splitMessageByNodes(message: string, hostlist: string[]): Map<string, string> {
  const result = new Map<string, string>()
  const normalized = message.trim()
  if (!normalized) return result

  const positions: { node: string; index: number }[] = []
  for (const node of hostlist) {
    const patterns = [
      new RegExp(`(?:^|\\n)\\s*${escapeRegExp(node)}\\s*[:\\-]`, 'im'),
      new RegExp(`(?:^|\\n)\\s*\\[${escapeRegExp(node)}\\]`, 'im'),
      new RegExp(`(?:^|\\n)${escapeRegExp(node)}\\b`, 'im'),
    ]
    for (const re of patterns) {
      const match = re.exec(normalized)
      if (match && match.index !== undefined) {
        positions.push({ node, index: match.index })
        break
      }
    }
  }

  if (positions.length === 0) return result

  positions.sort((a, b) => a.index - b.index)
  for (let i = 0; i < positions.length; i += 1) {
    const current = positions[i]
    if (!current) continue
    const nextIndex = positions[i + 1]?.index ?? normalized.length
    let chunk = normalized.slice(current.index, nextIndex).trim()
    chunk = chunk.replace(new RegExp(`^${escapeRegExp(current.node)}\\s*[:\\-\\]]?\\s*`, 'i'), '').trim()
    if (chunk) result.set(current.node, chunk)
  }

  return result
}

/** Read per-node SEL list output from control.sel host maps (strings only, never JSON blobs). */
function collectSelNodeOutput(control: unknown, node: string): string {
  if (!control || typeof control !== 'object') return ''
  const sel = (control as Record<string, unknown>).sel
  if (!sel || typeof sel !== 'object') return ''

  for (const actionVal of Object.values(sel as Record<string, unknown>)) {
    if (!actionVal || typeof actionVal !== 'object' || Array.isArray(actionVal)) continue
    const block = actionVal as Record<string, unknown>

    for (const statusKey of ['ok', 'off', 'on', 'list'] as const) {
      const hostMap = block[statusKey]
      if (!hostMap || typeof hostMap !== 'object' || Array.isArray(hostMap)) continue
      if (!(node in (hostMap as Record<string, unknown>))) continue
      const text = formatStringValue((hostMap as Record<string, unknown>)[node])
      if (text) return text
    }

    if (node in block) {
      const text = formatStringValue(block[node])
      if (text) return text
    }
  }

  return ''
}

/** True when Luna finished the SEL list job and returned per-node or message content. */
export function isSelListResponseReady(body: unknown, hostlist: string[]): boolean {
  if (!body || typeof body !== 'object') return false

  if (topMessage(body)) return true

  const failures = collectFailures(body)
  if (hostlist.some((node) => failures.has(node))) return true

  const control = (body as Record<string, unknown>).control
  if (hostlist.some((node) => Boolean(collectSelNodeOutput(control, node).trim()))) return true

  return false
}

function combinedEntry(hostlist: string[], text: string, error = false): SelLogEntry[] {
  if (hostlist.length === 1) {
    const node = hostlist[0]
    return node ? [{ node, text, error }] : []
  }
  return [{ node: `${hostlist.length} nodes`, nodes: hostlist, text, error }]
}

function resolveNodeEntry(
  body: unknown,
  node: string,
  hostlist: string[],
  failures: Map<string, string>,
  message: string,
  split: Map<string, string>,
): SelLogEntry {
  if (failures.has(node)) {
    return { node, text: failures.get(node)!, error: true }
  }

  const control = body && typeof body === 'object' ? (body as Record<string, unknown>).control : undefined
  const selOut = collectSelNodeOutput(control, node)
  if (isLogContent(selOut)) {
    return { node, text: selOut }
  }
  if (selOut) {
    return { node, text: selOut }
  }

  if (split.has(node)) {
    return { node, text: split.get(node)! }
  }

  if (message && hostlist.length === 1) {
    return { node, text: message }
  }

  return { node, text: '', error: false }
}

/** Pull SEL list text — always one entry per hostlist node, never merge failures into one blob. */
export function extractSelListResults(body: unknown, hostlist: string[]): SelLogEntry[] {
  if (hostlist.length === 0) return []

  const failures = collectFailures(body)
  const message = topMessage(body)
  const split = message ? splitMessageByNodes(message, hostlist) : new Map<string, string>()

  const results = hostlist.map((node) => resolveNodeEntry(body, node, hostlist, failures, message, split))
  const missing = results.filter((entry) => !entry.text.trim())
  const anyFailure = hostlist.some((node) => failures.has(node))

  if (message && missing.length === hostlist.length && split.size === 0) {
    return combinedEntry(hostlist, message)
  }

  if (message && missing.length > 0 && split.size > 0) {
    return results.map((entry) =>
      entry.text.trim() ? entry : { ...entry, text: split.get(entry.node) ?? message, error: false },
    )
  }

  return results.map((entry) => {
    if (entry.text.trim()) return entry
    if (anyFailure) {
      return { ...entry, text: MISSING_FALLBACK, error: true }
    }
    return { ...entry, text: SUCCESS_FALLBACK, error: false }
  })
}

export function formatSelLogText(entries: SelLogEntry[]): string {
  return entries
    .map((entry) => {
      const header = entry.nodes?.length
        ? `${entry.node}\n${entry.nodes.join(', ')}`
        : entry.node
      return `${header}\nSystem Event Log\n${entry.text.trim() || MISSING_FALLBACK}`
    })
    .join('\n\n────────────────────────────────────────\n\n')
}

export function orderSelLogEntries(entries: SelLogEntry[], hostlist: string[]): SelLogEntry[] {
  const byNode = new Map(entries.map((entry) => [entry.node, entry]))
  const ordered = hostlist
    .map((node) => byNode.get(node))
    .filter((entry): entry is SelLogEntry => Boolean(entry))
  const combined = entries.find((entry) => entry.nodes && entry.nodes.length > 1)
  if (combined) return [combined]
  return ordered.length > 0 ? ordered : entries
}

export function selLogModalTitle(
  entries: SelLogEntry[],
  loading: boolean,
  nodeCount?: number,
): string {
  if (loading) return 'SEL System Event Log'
  const count = nodeCount ?? entries.length
  if (count === 1) {
    const only = entries[0]
    return only ? `SEL System Event Log — ${only.node}` : 'SEL System Event Log'
  }
  if (entries.length === 1 && entries[0]?.nodes && entries[0].nodes.length > 1) {
    return `SEL System Event Logs — ${entries[0].nodes.length} nodes`
  }
  return `SEL System Event Logs — ${count} nodes`
}
