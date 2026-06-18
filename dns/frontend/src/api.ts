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

import type { ApiEnvelope, DnsEntryRow, DnsFormState, DnsListResponse, NetworksResponse } from './types'
import { oodAppRoot } from './utils/oodAppRoot'

const TABLE = 'dns'

export function baseUrl(): string {
  if (import.meta.env.DEV) return '/dns-backend'
  return oodAppRoot()
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
  if (!res.ok) {
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
