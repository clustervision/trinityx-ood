import type { ControlStatusRow } from '@/types'
import { isStatusLoading, isStatusOk, statusDotClass, statusLabel, statusTextClass } from './statusDisplay'

/** True when the power status string refers to a reset action/result. */
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
  if (isStatusLoading(value)) return 'tx-status-dot tx-status-bad'
  return statusDotClass(value)
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
