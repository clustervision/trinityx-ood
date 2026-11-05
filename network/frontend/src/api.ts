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

/**
 * Dev: `/network-backend` → Vite proxy → Flask network app (`trinityx-ood/network`).
 */
import type {
  DaemonEnvelope,
  NetworkConfigContent,
  NetworkFormState,
  NetworkInventoryRow,
  NetworkListResult,
  NetworkRecord,
  ReservedIpRow,
} from './types'
import { messageForDisplay } from './utils'
import { oodAppRoot } from './utils/oodAppRoot'

const TABLE = 'network'

export function baseUrl(): string {
  if (import.meta.env.DEV) return '/network-backend'
  return oodAppRoot()
}

function apiPath(suffix: string): string {
  const b = baseUrl().replace(/\/+$/, '')
  const s = suffix.trim()
  const path = s.startsWith('/') ? s : `/${s}`
  return `${b}${path}`
}

async function readJson<T = Record<string, unknown>>(res: Response): Promise<T | { _raw: string }> {
  const text = await res.text()
  if (!text) return {} as T
  try {
    return JSON.parse(text) as T
  } catch {
    return { _raw: text }
  }
}

function unwrapEnvelope<T>(data: unknown, context = 'request'): T {
  if (data == null || typeof data !== 'object') {
    throw new Error(`${context}: invalid response`)
  }
  const envelope = data as DaemonEnvelope<T>
  if (envelope.status === false) {
    const c = envelope.content
    const msg =
      typeof c === 'string'
        ? c
        : c && typeof c === 'object' && 'message' in c
          ? String((c as { message?: string }).message || '')
          : 'Daemon request failed'
    throw new Error(messageForDisplay(msg || 'Daemon request failed'))
  }
  if (envelope.status === true) return (envelope.content as T) ?? ({} as T)
  return data as T
}

function envelopeMessage(data: unknown): string {
  if (!data || typeof data !== 'object') return ''
  const d = data as DaemonEnvelope
  if (typeof d.message === 'string' && d.message.trim()) return d.message.trim()
  const c = d.content
  if (typeof c === 'string') return c.trim()
  if (c && typeof c === 'object' && 'message' in c) {
    return String((c as { message?: string }).message || '').trim()
  }
  return ''
}

export function buildRequestData(recordName: string, recordPayload: NetworkRecord) {
  return { config: { [TABLE]: { [recordName]: recordPayload } } }
}

function prepareNetworkPayload(name: string, form: NetworkFormState): NetworkRecord {
  const payload: NetworkRecord = {
    name,
    network: form.network.trim(),
    type: form.type.trim(),
    zone: form.zone.trim(),
    dhcp: form.dhcp,
    dhcp_nodes_only: form.dhcp_nodes_only,
    dhcp_nodes_in_pool: form.dhcp_nodes_in_pool,
    non_authoritative: form.non_authoritative,
  }

  const optionalStrings: (keyof NetworkFormState)[] = [
    'dhcp_range_begin',
    'dhcp_range_end',
    'gateway',
    'nameserver_ip',
    'ntp_server',
    'comment',
  ]
  for (const key of optionalStrings) {
    const v = String(form[key] ?? '').trim()
    if (v) (payload as Record<string, unknown>)[key] = v
  }

  const metric = String(form.gateway_metric ?? '').trim()
  if (metric) {
    const n = Number(metric)
    if (!Number.isNaN(n)) payload.gateway_metric = n
  }

  const shared = form.shared.trim().toLowerCase()
  if (shared === 'true') payload.shared = true
  else if (shared === 'false') payload.shared = false

  return payload
}

function inventoryRowsFromConfig(map?: Record<string, NetworkRecord>): NetworkInventoryRow[] {
  const rows: NetworkInventoryRow[] = []
  if (!map || typeof map !== 'object') return rows
  for (const [key, record] of Object.entries(map)) {
    if (!record || typeof record !== 'object') continue
    const name = String(record.name || key)
    rows.push({
      name,
      network: record.network != null ? String(record.network) : '',
      type: record.type != null ? String(record.type) : '',
      zone: record.zone != null ? String(record.zone) : '',
      dhcp: record.dhcp === true || record.dhcp === 'true',
      dhcp_range_begin:
        record.dhcp_range_begin != null ? String(record.dhcp_range_begin) : '',
      dhcp_range_end: record.dhcp_range_end != null ? String(record.dhcp_range_end) : '',
    })
  }
  return rows
}

export async function fetchNetworks(): Promise<NetworkListResult> {
  try {
    const res = await fetch(apiPath('/api/v1/networks'), {
      headers: { Accept: 'application/json' },
    })
    const data = await readJson<DaemonEnvelope<NetworkConfigContent>>(res)
    if (!res.ok) {
      throw new Error(envelopeMessage(data) || `Failed to load networks: HTTP ${res.status}`)
    }
    const content = unwrapEnvelope<NetworkConfigContent>(data, 'list networks')
    const networks = inventoryRowsFromConfig(content?.config?.network)
    return { networks, error: '' }
  } catch (e) {
    const msg = e instanceof Error ? e.message : 'Network error'
    if (import.meta.env.DEV) {
      return {
        networks: [],
        error: `${msg} — Is the Flask backend running and VITE_APP_URL set?`,
      }
    }
    return { networks: [], error: msg }
  }
}

export async function fetchNetworkRecord(name: string): Promise<{ record: NetworkRecord; error: string }> {
  try {
    const res = await fetch(apiPath('/api/v1/networks'), {
      headers: { Accept: 'application/json' },
    })
    const data = await readJson<DaemonEnvelope<NetworkConfigContent>>(res)
    const content = unwrapEnvelope<NetworkConfigContent>(data, 'network detail')
    const rec = content?.config?.network?.[name]
    if (!rec) return { record: {}, error: `${name} not found` }
    return { record: { ...rec, name: rec.name || name }, error: '' }
  } catch (e) {
    return { record: {}, error: e instanceof Error ? e.message : 'Failed to load network' }
  }
}

export function recordToFormState(rec: NetworkRecord): NetworkFormState {
  let shared = ''
  if (rec.shared === true) shared = 'true'
  else if (rec.shared === false) shared = 'false'

  return {
    network: rec.network != null ? String(rec.network) : '',
    type: rec.type != null ? String(rec.type) : '',
    zone: rec.zone != null ? String(rec.zone) : '',
    dhcp: rec.dhcp === true || rec.dhcp === 'true',
    dhcp_range_begin: rec.dhcp_range_begin != null ? String(rec.dhcp_range_begin) : '',
    dhcp_range_end: rec.dhcp_range_end != null ? String(rec.dhcp_range_end) : '',
    gateway: rec.gateway != null ? String(rec.gateway) : '',
    nameserver_ip: rec.nameserver_ip != null ? String(rec.nameserver_ip) : '',
    ntp_server: rec.ntp_server != null ? String(rec.ntp_server) : '',
    gateway_metric:
      rec.gateway_metric != null && rec.gateway_metric !== '' ? String(rec.gateway_metric) : '',
    shared,
    dhcp_nodes_only: rec.dhcp_nodes_only === true || rec.dhcp_nodes_only === 'true',
    dhcp_nodes_in_pool: rec.dhcp_nodes_in_pool === true || rec.dhcp_nodes_in_pool === 'true',
    non_authoritative: rec.non_authoritative === true || rec.non_authoritative === 'true',
    comment: rec.comment != null ? String(rec.comment) : '',
  }
}

async function jsonRequest(method: string, path: string, body?: unknown) {
  const res = await fetch(apiPath(path), {
    method,
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
    },
    body: body != null ? JSON.stringify(body) : undefined,
  })
  const data = await readJson(res)
  const ok =
    (data as DaemonEnvelope).status === true ||
    res.status === 204 ||
    res.status === 201
  return { ok, status: res.status, data, message: envelopeMessage(data) }
}

export async function createNetwork(name: string, form: NetworkFormState) {
  const request_data = buildRequestData(name, prepareNetworkPayload(name, form))
  const result = await jsonRequest('POST', '/api/v1/add', request_data)
  if (!result.ok) {
    throw new Error(result.message || `Add failed (${result.status})`)
  }
  return result
}

export async function updateNetwork(name: string, form: NetworkFormState) {
  const request_data = buildRequestData(name, prepareNetworkPayload(name, form))
  const result = await jsonRequest('PUT', '/api/v1/update', request_data)
  if (!result.ok) {
    throw new Error(result.message || `Update failed (${result.status})`)
  }
  return result
}

export async function renameNetwork(oldName: string, newName: string) {
  const request_data = buildRequestData(oldName, { newnetname: newName })
  const result = await jsonRequest('PATCH', '/api/v1/rename', request_data)
  if (!result.ok) {
    throw new Error(result.message || `Rename failed (${result.status})`)
  }
  return result
}

export async function deleteNetwork(name: string) {
  const res = await fetch(apiPath(`/api/v1/delete/${encodeURIComponent(name)}`), {
    method: 'DELETE',
    headers: { Accept: 'application/json' },
  })
  const data = await readJson(res)
  const ok = (data as DaemonEnvelope).status === true || res.status === 204
  if (!ok) {
    throw new Error(envelopeMessage(data) || `Delete failed (${res.status})`)
  }
  return { message: envelopeMessage(data) || `${name} deleted.` }
}

export async function fetchNextIp(networkName: string): Promise<string> {
  const res = await fetch(apiPath(`/api/v1/nextip/${encodeURIComponent(networkName)}`), {
    headers: { Accept: 'application/json' },
  })
  const data = await readJson<DaemonEnvelope<NetworkConfigContent>>(res)
  const content = unwrapEnvelope<NetworkConfigContent>(data, 'next ip')
  const net = content?.config?.network?.[networkName]
  const next = net && typeof net === 'object' ? (net as { nextip?: string }).nextip : ''
  return next ? String(next) : ''
}

export function formatIpCheckMessage(ip: string, content: unknown): string {
  if (typeof content === 'string' && content.trim()) {
    return messageForDisplay(content)
  }

  const root =
    content && typeof content === 'object' ? (content as Record<string, unknown>) : null
  const config =
    root?.config && typeof root.config === 'object'
      ? (root.config as Record<string, unknown>)
      : root
  const network =
    config?.network && typeof config.network === 'object'
      ? (config.network as Record<string, unknown>)
      : null

  if (network) {
    const entry = network[ip]
    if (entry && typeof entry === 'object' && 'status' in entry) {
      const status = String((entry as { status?: string }).status || '').trim().toLowerCase()
      if (status === 'free') return `IP address ${ip} is not occupied.`
      if (status === 'taken') return `IP address ${ip} is occupied.`
      if (status) return `${ip}: ${status}.`
    }
  }

  const fallback = envelopeMessage(content)
  return fallback ? messageForDisplay(fallback) : 'Could not determine IP status.'
}

export async function fetchIpInfo(networkName: string, ip: string): Promise<string> {
  const res = await fetch(apiPath(`/api/v1/ipinfo/${encodeURIComponent(networkName)}/${encodeURIComponent(ip)}`), {
    headers: { Accept: 'application/json' },
  })
  const data = await readJson(res)
  if ((data as DaemonEnvelope).status === false) {
    throw new Error(envelopeMessage(data) || 'Could not load IP information')
  }
  try {
    return formatIpCheckMessage(ip, unwrapEnvelope(data, 'ip info'))
  } catch {
    return formatIpCheckMessage(ip, data)
  }
}

function parseReservedMembers(raw: unknown): ReservedIpRow[] {
  const rows: ReservedIpRow[] = []
  if (raw == null) return rows

  if (Array.isArray(raw)) {
    for (const item of raw) {
      if (typeof item === 'string') {
        rows.push({ ip: item, deviceName: '' })
      } else if (item && typeof item === 'object') {
        const o = item as Record<string, unknown>
        const ip = String(o.ipaddress ?? o.ip ?? o.address ?? Object.keys(o)[0] ?? '')
        const deviceName = String(
          o.devicename ?? o.device_name ?? o.hostname ?? o.name ?? Object.values(o)[0] ?? '',
        )
        if (ip) rows.push({ ip, deviceName })
      }
    }
    return rows
  }

  if (typeof raw === 'object') {
    for (const [k, v] of Object.entries(raw as Record<string, unknown>)) {
      if (typeof v === 'string') rows.push({ ip: k, deviceName: v })
      else if (v && typeof v === 'object') {
        const o = v as Record<string, unknown>
        rows.push({
          ip: String(o.ipaddress ?? o.ip ?? k),
          deviceName: String(o.devicename ?? o.device_name ?? o.hostname ?? ''),
        })
      } else rows.push({ ip: k, deviceName: '' })
    }
  }
  return rows
}

export async function fetchReservedIps(networkName: string): Promise<ReservedIpRow[]> {
  const res = await fetch(apiPath(`/api/v1/reserve/${encodeURIComponent(networkName)}`), {
    headers: { Accept: 'application/json' },
  })
  const data = await readJson<DaemonEnvelope<NetworkConfigContent>>(res)
  const content = unwrapEnvelope<NetworkConfigContent>(data, 'reserved ips')
  const net = content?.config?.network?.[networkName]
  const member =
    net && typeof net === 'object' ? (net as { member?: unknown }).member : undefined
  return parseReservedMembers(member)
}

export const DEFAULT_NETWORK_TYPES = ['ethernet', 'infiniband']
export const DEFAULT_NETWORK_ZONES = ['internal', 'management', 'storage']
