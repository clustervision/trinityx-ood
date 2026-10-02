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
 */

export interface Controller {
  hostname: string
  ipaddress: string
  luna_config: string
  serverport: number
  status: string | null
  vendor: string | null
}

/** Known cluster scalar / primary-controller fields — not extra HA controller entries. */
export const CLUSTER_STATIC_KEYS = new Set([
  'name', 'user', 'domain_search', 'nameserver_ip', 'forwardserver_ip',
  'ntp_server', 'technical_contacts', 'provision_method', 'provision_fallback',
  'debug', 'security', 'packing_bootpause', 'createnode_ondemand',
  'createnode_macashost', 'nextnode_discover', 'controller',
])

export function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

/** Extra HA controller objects keyed by arbitrary names (e.g. availability-one). */
export function isHaController(value: unknown): value is Controller {
  if (!isObject(value)) return false
  return (
    'hostname' in value &&
    'ipaddress' in value &&
    'serverport' in value &&
    'luna_config' in value
  )
}

export function collectHaControllers(cluster: Record<string, unknown>): Controller[] {
  return Object.entries(cluster)
    .filter(([key, value]) => !CLUSTER_STATIC_KEYS.has(key) && isHaController(value))
    .map(([, value]) => value)
}

export type HaControllerEntry = { key: string; controller: Controller }

export function collectHaControllerEntries(cluster: Record<string, unknown>): HaControllerEntry[] {
  return Object.entries(cluster)
    .filter(([key, value]) => !CLUSTER_STATIC_KEYS.has(key) && isHaController(value))
    .map(([key, value]) => ({ key, controller: value }))
}

export function collectHaControllerMap(cluster: Record<string, unknown>): Record<string, Controller> {
  const map: Record<string, Controller> = {}
  for (const [key, value] of Object.entries(cluster)) {
    if (!CLUSTER_STATIC_KEYS.has(key) && isHaController(value)) {
      map[key] = { ...value }
    }
  }
  return map
}
