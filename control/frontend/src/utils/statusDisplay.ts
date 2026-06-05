const PENDING = 'PENDING'

/** True when the status should show a green dot (ON / OK / reset). */
export function isStatusOk(value: string): boolean {
  const v = String(value ?? '').trim().toUpperCase()
  if (!v || v === PENDING || v === 'UNKNOWN' || v === 'ERROR') return false
  if (v.includes('RESET')) return true
  if (v.includes('OFF')) return false
  return v.includes('ON') || v === 'OK'
}

export function statusLabel(value: string): string {
  const v = String(value ?? '').trim().toUpperCase()
  if (!v || v === PENDING) return ''
  if (isStatusOk(value)) {
    if (v.includes('OFF')) return 'OFF'
    return 'ON'
  }
  if (v === 'ERROR' || v === 'UNKNOWN') return ''
  return String(value ?? '').trim()
}

export function statusDotClass(value: string): string {
  if (isStatusOk(value)) return 'tx-status-dot tx-status-ok'
  const v = String(value ?? '').trim().toUpperCase()
  if (v.includes('OFF')) return 'tx-status-dot tx-status-warn'
  return 'tx-status-dot tx-status-bad'
}

export function statusTextClass(value: string): string {
  if (isStatusOk(value)) return 'tx-status-text tx-status-ok-text'
  const v = String(value ?? '').trim().toUpperCase()
  if (v.includes('OFF')) return 'tx-status-text tx-status-warn-text'
  return 'tx-status-text tx-status-bad-text'
}

export function pendingStatus(): string {
  return PENDING
}

export function isStatusLoading(value: string): boolean {
  return String(value ?? '').trim().toUpperCase() === PENDING
}

/** Node can receive BMC actions when power status is known and not failed. */
export function isNodeControllable(row: { power: string }): boolean {
  const p = String(row.power ?? '').trim().toUpperCase()
  if (!p || p === PENDING || p === 'UNKNOWN' || p === 'ERROR') return false
  return true
}
