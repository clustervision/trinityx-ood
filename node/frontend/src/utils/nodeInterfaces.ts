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

import type { NodeFormInterface } from '@/types'

function interfaceNames(list: NodeFormInterface[] | undefined): string[] {
  return (list ?? [])
    .map((row) => String(row.interface ?? '').trim())
    .filter(Boolean)
}

function ifaceDhcpString(v: unknown): string {
  if (v === true || v === 1 || v === '1') return 'true'
  if (v === false || v === 0 || v === '0') return 'false'
  const s = String(v ?? '').trim().toLowerCase()
  if (s === 'true' || s === 'yes' || s === 'on') return 'true'
  return 'false'
}

function mapInterfaceRow(name: string, row: Record<string, unknown>): NodeFormInterface {
  const key = String(name ?? '').trim()
  return {
    // Object keys from Luna are the authoritative delete/API names (e.g. BOOTIF, BMC).
    interface: key || String(row.interface ?? '').trim(),
    network: String(row.network ?? '').trim(),
    ipaddress: row.ipaddress != null ? String(row.ipaddress) : '',
    mtu: (row.mtu as string | number) ?? '',
    dhcp: ifaceDhcpString(row.dhcp),
    bond_mode: String(row.bond_mode ?? '').trim(),
    bond_slaves: String(row.bond_slaves ?? '').trim(),
    vlanid: (row.vlanid as string | number) ?? '',
    options: String(row.options ?? '').trim(),
    vlan_parent: String(row.vlan_parent ?? '').trim(),
    macaddress: row.macaddress != null ? String(row.macaddress) : '',
  }
}

/** Luna may return interfaces as an array or as an object keyed by interface name. */
export function normalizeNodeInterfaces(raw: unknown): NodeFormInterface[] {
  if (Array.isArray(raw)) {
    return raw
      .filter((item) => item && typeof item === 'object')
      .map((item) => mapInterfaceRow(String((item as Record<string, unknown>).interface ?? ''), item as Record<string, unknown>))
      .filter((row) => row.interface)
  }
  if (raw && typeof raw === 'object') {
    return Object.entries(raw as Record<string, unknown>)
      .map(([name, item]) => {
        const row = item && typeof item === 'object' ? (item as Record<string, unknown>) : {}
        return mapInterfaceRow(name, row)
      })
      .filter((row) => row.interface)
  }
  return []
}

/** Interface names present when the form was opened but removed before Save. */
export function removedInterfaceNames(
  initialSnapshot: string,
  currentInterfaces: NodeFormInterface[],
): string[] {
  let initial: { interfaces?: NodeFormInterface[] }
  try {
    initial = JSON.parse(initialSnapshot) as { interfaces?: NodeFormInterface[] }
  } catch {
    return []
  }

  const initialSet = new Set(interfaceNames(initial.interfaces))
  const currentSet = new Set(interfaceNames(currentInterfaces))
  return [...initialSet].filter((name) => !currentSet.has(name))
}
