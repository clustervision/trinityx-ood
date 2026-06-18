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

export const DNS_NAME_MAX_LENGTH = 200
export const DNS_HOST_MAX_LENGTH = 63
export const DNS_NAME_DISPLAY_MAX = 25

/** Host / network label: letters, digits, dot, hyphen, underscore; no spaces. */
export const DNS_LABEL_PATTERN = /^[a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?$/

export type DnsLabelValidation =
  | { ok: true; value: string }
  | { ok: false; message: string }

export function validateDnsLabel(
  raw: unknown,
  fieldLabel: string,
  required = true,
  maxLength = DNS_NAME_MAX_LENGTH,
): DnsLabelValidation {
  const trimmed = String(raw ?? '').trim()
  if (!trimmed) {
    return required
      ? { ok: false, message: `${fieldLabel} is required.` }
      : { ok: true, value: '' }
  }
  if (trimmed.length > maxLength) {
    return {
      ok: false,
      message: `${fieldLabel} must be at most ${maxLength} characters.`,
    }
  }
  if (/\s/.test(trimmed)) {
    return { ok: false, message: `${fieldLabel} cannot contain spaces.` }
  }
  if (/[<>&"']/.test(trimmed)) {
    return {
      ok: false,
      message: `${fieldLabel} cannot contain characters such as <, >, &, ", '.`,
    }
  }
  if (!DNS_LABEL_PATTERN.test(trimmed)) {
    return {
      ok: false,
      message: `${fieldLabel} must start and end with a letter or number.`,
    }
  }
  return { ok: true, value: trimmed }
}

export function formatDnsLabelDisplay(
  value: string | null | undefined,
  maxVisible = DNS_NAME_DISPLAY_MAX,
): string {
  const s = String(value ?? '')
  if (s.length <= maxVisible) return s
  return `${s.slice(0, maxVisible - 3)}...`
}

export function dnsLabelTitle(value: string | null | undefined): string {
  return String(value ?? '')
}
