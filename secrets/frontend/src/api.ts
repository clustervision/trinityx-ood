/*
 * This code is part of the TrinityX software suite
 * Copyright (C) 2026  ClusterVision Solutions b.v.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>
 *
 * @author      Yixin Zhang
 * @copyright   Copyright 2026, Luna2 Project[OOD]
 * @license     GPL
 * @version     2.0
 * @maintainer  Yixin Zhang
 * @email       yixin.zhang@clustervision.com
 * @status      Development
 */

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
  if (!text.trim()) return {} as T
  try {
    return JSON.parse(text) as T
  } catch {
    const snippet = text.trim().slice(0, 80).replace(/\s+/g, ' ')
    const isHtml = /^</.test(text.trim())
    throw new Error(
      isHtml
        ? `Server returned HTML instead of JSON (HTTP ${res.status}). Redeploy the Secrets backend if group/node lists fail to load.`
        : `Invalid JSON from server (HTTP ${res.status}): ${snippet}`,
    )
  }
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

function namesFromDaemonConfig(content: unknown, table: 'group' | 'node'): string[] {
  const cfg = (content as { config?: Record<string, unknown> })?.config
  const entries = cfg?.[table]
  if (!entries || typeof entries !== 'object' || Array.isArray(entries)) return []
  return Object.keys(entries as Record<string, unknown>).sort()
}

async function fetchNameList(path: string, table: 'group' | 'node'): Promise<string[]> {
  const res = await fetch(apiPath(path), { headers: { Accept: 'application/json' } })
  const data = await readJson<DaemonEnvelope<{ names?: string[] }>>(res)
  if (data.status === false) throw new Error(messageFromEnvelope(data))
  const names = data.content?.names
  if (Array.isArray(names)) return names
  const fromConfig = namesFromDaemonConfig(data.content ?? data, table)
  if (fromConfig.length) return fromConfig
  return []
}

export async function fetchGroupNames(): Promise<string[]> {
  return fetchNameList('/api/v1/groups', 'group')
}

export async function fetchNodeNames(): Promise<string[]> {
  return fetchNameList('/api/v1/nodes', 'node')
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
