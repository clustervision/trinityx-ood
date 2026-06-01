import type { ControlStatusRow } from '@/types'

/** True when the power status string refers to a reset action/result. */
export function isResetPowerStatus(value: string): boolean {
  return String(value ?? '').toUpperCase().includes('RESET')
}

/** True when the power status should show a green dot (ON / OK / reset). */
export function isPowerStatusOk(value: string): boolean {
  const v = String(value ?? '').toUpperCase()
  if (isResetPowerStatus(v)) return true
  if (v.includes('OFF')) return false
  return v.includes('ON') || v.includes('OK')
}

/** Table label: green-dot states show "ON"; others show the raw status. */
export function powerStatusLabel(value: string): string {
  if (isPowerStatusOk(value)) return 'ON'
  const s = String(value ?? '').trim()
  return s || 'UNKNOWN'
}

export function powerStatusTextClass(value: string): string {
  if (isPowerStatusOk(value)) return 'tx-status-text tx-status-ok-text'
  const v = String(value ?? '').toUpperCase()
  if (v.includes('OFF')) return 'tx-status-text tx-status-warn-text'
  return 'tx-status-text tx-status-bad-text'
}

export function powerStatusDotClass(value: string): string {
  if (isPowerStatusOk(value)) return 'tx-status-dot tx-status-ok'
  const v = String(value ?? '').toUpperCase()
  if (v.includes('OFF')) return 'tx-status-dot tx-status-warn'
  return 'tx-status-dot tx-status-bad'
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
  if (unique.length === 1) return unique[0]
  return unique.join('; ')
}
