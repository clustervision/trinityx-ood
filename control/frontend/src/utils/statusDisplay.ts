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
