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

import type { ControlStatusRow } from '@/types'
import {
  isNodeControllable,
  isStatusLoading,
  isStatusOk,
  statusLabel,
  statusTextClass,
} from './statusDisplay'

export type PowerToggleVisual = 'on' | 'off' | 'loading' | 'unknown'

export function isResetPowerStatus(value: string): boolean {
  return String(value ?? '').toUpperCase().includes('RESET')
}

export function isPowerStatusOk(value: string): boolean {
  return isStatusOk(value)
}

export function isPowerLoading(value: string): boolean {
  return isStatusLoading(value)
}

export function powerStatusLabel(value: string): string {
  if (isStatusLoading(value)) return ''
  if (isStatusOk(value) && !String(value).toUpperCase().includes('OFF')) return 'ON'
  return statusLabel(value)
}

export function powerStatusTextClass(value: string): string {
  if (isStatusLoading(value)) return 'tx-status-text tx-status-loading-text'
  return statusTextClass(value)
}

export function powerStatusDotClass(value: string): string {
  if (isStatusLoading(value)) return 'tx-status-dot tx-status-dot--power tx-status-loading-dot'
  if (isPowerOn(value)) return 'tx-status-dot tx-status-dot--power tx-status-ok'
  const v = String(value ?? '').trim().toUpperCase()
  if (v.includes('OFF')) return 'tx-status-dot tx-status-dot--power tx-status-bad'
  if (!isNodeControllable({ power: value })) return 'tx-status-dot tx-status-dot--power tx-status-muted'
  return 'tx-status-dot tx-status-dot--power tx-status-bad'
}

export function isPowerOn(value: string): boolean {
  if (isStatusLoading(value)) return false
  const v = String(value ?? '').trim().toUpperCase()
  if (!v || v === 'UNKNOWN' || v === 'ERROR') return false
  if (v.includes('OFF')) return false
  return isStatusOk(value)
}

export function powerToggleVisualState(power: string, loading = false): PowerToggleVisual {
  if (loading || isStatusLoading(power)) return 'loading'
  if (!isNodeControllable({ power })) return 'unknown'
  return isPowerOn(power) ? 'on' : 'off'
}

/** Next power action when the user clicks the toggle (on ↔ off; unknown → on). */
export function powerToggleAction(power: string, loading = false): 'on' | 'off' | null {
  const visual = powerToggleVisualState(power, loading)
  if (visual === 'on') return 'off'
  if (visual === 'off' || visual === 'unknown') return 'on'
  return null
}

export function bulkPowerToggleAction(
  hostlist: string[],
  rows: ControlStatusRow[],
  loadingNodes: Record<string, boolean> = {},
): 'on' | 'off' | null {
  if (hostlist.length === 0) return null
  for (const node of hostlist) {
    if (loadingNodes[node]) return null
  }
  const anyNotOn = hostlist.some((node) => {
    const row = rows.find((r) => r.node === node)
    return !row || !isPowerOn(row.power)
  })
  return anyNotOn ? 'on' : 'off'
}

export function bulkPowerToggleVisualState(
  hostlist: string[],
  rows: ControlStatusRow[],
  loadingNodes: Record<string, boolean> = {},
): PowerToggleVisual {
  if (hostlist.length === 0) return 'unknown'
  if (hostlist.some((node) => loadingNodes[node])) return 'loading'
  const powers = hostlist.map((node) => rows.find((r) => r.node === node)?.power ?? '')
  if (powers.every((power) => isPowerOn(power))) return 'on'
  if (powers.some((power) => !isNodeControllable({ power }))) return 'unknown'
  return 'off'
}

/** Build a notification message from reset power statuses for the given nodes. */
export function resetPowerNotification(
  rows: ControlStatusRow[],
  hostlist: string[],
): string | null {
  const hosts = new Set(hostlist)
  const parts: string[] = []
  for (const row of rows) {
    if (!hosts.has(row.node)) continue
    const power = String(row.power ?? '').trim()
    if (!power || !isResetPowerStatus(power)) continue
    parts.push(power)
  }
  if (parts.length === 0) return null
  const unique = [...new Set(parts)]
  if (unique.length === 1) return unique[0] ?? null
  return unique.join('; ')
}
