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
 * Live IPv4 field formatting: keeps '.' separators visible while typing.
 * Supports explicit dots (192.168.) or digit-only input (192168 → 192.168).
 */
export function formatIpv4Typing(input: string): string {
  const raw = String(input ?? '')
  const trailingDot = /[.\s]$/.test(raw) || raw.endsWith('.')
  const normalized = raw.replace(/[^0-9.]/g, '')

  if (!normalized) {
    return trailingDot ? '' : ''
  }

  if (normalized.includes('.')) {
    const parts = normalized.split('.').slice(0, 4)
    const octets = parts.map((part) => clampOctetDigits(part.replace(/\D/g, '').slice(0, 3)))
    while (octets.length > 1 && octets[octets.length - 1] === '' && !trailingDot) {
      octets.pop()
    }
    if (octets.length === 0) return ''
    return octets.join('.')
  }

  const digits = normalized.replace(/\D/g, '').slice(0, 12)
  if (!digits) return ''

  const octets: string[] = []
  for (let i = 0; i < digits.length && octets.length < 4; ) {
    const rest = digits.length - i
    const take = rest <= 3 ? rest : 3
    octets.push(clampOctetDigits(digits.slice(i, i + take)))
    i += take
  }
  return octets.join('.')
}

function clampOctetDigits(digits: string): string {
  if (!digits) return ''
  const n = Math.min(parseInt(digits, 10), 255)
  return String(n)
}

/** Value sent to API: trimmed dotted IPv4 or raw string if incomplete. */
export function ipv4ForSubmit(display: string): string {
  return formatIpv4Typing(display).trim()
}
