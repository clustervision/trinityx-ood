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

import type {
  InventoryIpv4Record,
  NodeFormInterface,
  SuggestIpResult,
  SuggestNextFreeIpParams,
} from '@/types'

const IPV4_RE =
  /^(?:(?:25[0-5]|2[0-4]\d|[01]?\d{1,2})\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d{1,2})$/

export function parseIpv4String(s: unknown): number | null {
  if (s == null) return null
  const t = String(s).trim().split(/\s+/)[0]!
  if (!IPV4_RE.test(t)) return null
  const parts = t.split('.').map(Number)
  return ((parts[0]! << 24) | (parts[1]! << 16) | (parts[2]! << 8) | parts[3]!) >>> 0
}

export function formatIpv4(n: number | null | undefined): string {
  if (n == null || !Number.isFinite(n)) return ''
  const x = n >>> 0
  return [x >>> 24, (x >>> 16) & 0xff, (x >>> 8) & 0xff, x & 0xff].join('.')
}

function network24Base(ipNum: number): number {
  return (ipNum >>> 0) & 0xffffff00
}

function collectSubnetBase(
  networkName: string,
  formInterfaces: Pick<NodeFormInterface, 'ipaddress' | 'network'>[],
  inventoryRecords: InventoryIpv4Record[],
  excludeNodeName: string,
): number | null {
  const net = String(networkName || '').trim()
  if (!net) return null
  for (const r of inventoryRecords) {
    if (excludeNodeName && r.nodeName === excludeNodeName) continue
    if (String(r.network || '').trim() === net && r.ipNum != null) {
      return network24Base(r.ipNum)
    }
  }
  for (const iface of formInterfaces) {
    if (String(iface.network || '').trim() !== net) continue
    const ipNum = parseIpv4String(iface.ipaddress)
    if (ipNum != null) return network24Base(ipNum)
  }
  return null
}

function buildUsedSet(
  inventoryRecords: InventoryIpv4Record[],
  excludeNodeName: string,
  formInterfaces: Pick<NodeFormInterface, 'ipaddress' | 'network'>[],
): Set<number> {
  const used = new Set<number>()
  for (const r of inventoryRecords) {
    if (excludeNodeName && r.nodeName === excludeNodeName) continue
    if (r.ipNum != null) used.add(r.ipNum)
  }
  for (const iface of formInterfaces) {
    const ipNum = parseIpv4String(iface.ipaddress)
    if (ipNum != null) used.add(ipNum)
  }
  return used
}

/**
 * Picks the lowest free host IPv4 in the /24 inferred from existing assignments on the same network.
 */
export function suggestNextFreeIpv424({
  networkName,
  formInterfaces,
  inventoryRecords,
  excludeNodeName,
}: SuggestNextFreeIpParams): SuggestIpResult {
  const net = String(networkName || '').trim()
  if (!net) return { ok: false, reason: 'network' }

  const base = collectSubnetBase(net, formInterfaces, inventoryRecords, excludeNodeName || '')
  if (base == null) return { ok: false, reason: 'subnet' }

  const used = buildUsedSet(inventoryRecords, excludeNodeName || '', formInterfaces)

  for (let host = 1; host <= 254; host++) {
    const cand = (base >>> 0) + host
    if (!used.has(cand)) return { ok: true, ip: formatIpv4(cand) }
  }
  return { ok: false, reason: 'full' }
}
