import type { DaemonEnvelope, SecretEntity, SecretFormState, SecretRecord } from './types'
import { oodAppRoot } from './utils/oodAppRoot'

export function baseUrl(): string {
  if (import.meta.env.DEV) return '/secret-backend'
  return oodAppRoot()
}

function apiPath(suffix: string): string {
  const b = baseUrl().replace(/\/+$/, '')
  return `${b}${suffix.startsWith('/') ? suffix : `/${suffix}`}`
}

function decodeBase64(s: string): string {
  try {
    return atob(s || '')
  } catch {
    return s || ''
  }
}

function encodeBase64(s: string): string {
  return btoa(unescape(encodeURIComponent(s || '')))
}

async function readJson<T = unknown>(res: Response): Promise<T> {
  const text = await res.text()
  return (text ? JSON.parse(text) : {}) as T
}

function messageFromEnvelope(data: unknown): string {
  if (!data || typeof data !== 'object') return 'Request failed.'
  const env = data as DaemonEnvelope
  if (typeof env.message === 'string' && env.message.trim()) return env.message.trim()
  if (typeof env.content === 'string' && env.content.trim()) return env.content.trim()
  if (env.content && typeof env.content === 'object' && 'message' in env.content) {
    return String((env.content as { message?: string }).message || 'Request failed.')
  }
  return 'Request failed.'
}

function flattenSecrets(content: unknown): SecretRecord[] {
  const rows: SecretRecord[] = []
  const cfg = (content as { config?: { secrets?: Record<string, unknown> } })?.config?.secrets || {}
  for (const entity of ['group', 'node'] as const) {
    const owners = cfg[entity] as Record<string, unknown> | undefined
    if (!owners || typeof owners !== 'object') continue
    for (const [ownerName, secretList] of Object.entries(owners)) {
      if (!Array.isArray(secretList)) continue
      for (const item of secretList) {
        const obj = item as Record<string, unknown>
        rows.push({
          entity,
          owner: ownerName,
          name: String(obj.name || ''),
          path: String(obj.path || ''),
          content: decodeBase64(String(obj.content || '')),
        })
      }
    }
  }
  return rows
}

export async function fetchSecrets(): Promise<{ rows: SecretRecord[]; error: string }> {
  try {
    const res = await fetch(apiPath('/api/v1/secrets'), { headers: { Accept: 'application/json' } })
    const data = await readJson<DaemonEnvelope>(res)
    if (data.status === false) return { rows: [], error: messageFromEnvelope(data) }
    return { rows: flattenSecrets(data.content), error: '' }
  } catch (e) {
    return { rows: [], error: e instanceof Error ? e.message : 'Failed to load secrets.' }
  }
}

async function jsonRequest(method: string, path: string, body?: unknown): Promise<void> {
  const res = await fetch(apiPath(path), {
    method,
    headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    body: body == null ? undefined : JSON.stringify(body),
  })
  const data = await readJson<DaemonEnvelope>(res)
  if (data.status !== true) throw new Error(messageFromEnvelope(data))
}

function toPayload(form: SecretFormState) {
  return {
    entity: form.entity,
    owner: form.owner.trim(),
    secret: form.name.trim().toLowerCase(),
    path: form.path.trim(),
    content: encodeBase64(form.content),
  }
}

export async function addSecret(form: SecretFormState): Promise<void> {
  await jsonRequest('POST', '/api/v1/add', toPayload(form))
}

export async function updateSecret(original: SecretRecord, form: SecretFormState): Promise<void> {
  await jsonRequest('PUT', '/api/v1/update', {
    original: { entity: original.entity, owner: original.owner, secret: original.name },
    updated: toPayload(form),
  })
}

export async function cloneSecret(original: SecretRecord, form: SecretFormState): Promise<void> {
  await jsonRequest('POST', '/api/v1/clone', {
    original: { entity: original.entity, owner: original.owner, secret: original.name },
    clone: toPayload(form),
  })
}

export async function deleteSecret(entity: SecretEntity, owner: string, secret: string): Promise<void> {
  const path = `/api/v1/delete/${encodeURIComponent(entity)}/${encodeURIComponent(owner)}/${encodeURIComponent(secret)}`
  await jsonRequest('DELETE', path)
}
