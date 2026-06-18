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

/** Max characters for a network name (Luna / UI). */
export const NETWORK_NAME_MAX_LENGTH = 200

/** Visible characters in table / compact UI before appending "...". */
export const NETWORK_NAME_DISPLAY_MAX = 25

/** Luna-style identifier: lowercase a-z, 0-9, dot, hyphen. */
export const NETWORK_NAME_PATTERN = /^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$/

export type NetworkNameValidation =
  | { ok: true; name: string }
  | { ok: false; message: string }

export function normalizeNetworkName(raw: unknown): string {
  return String(raw ?? '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9.-]/g, '')
}

export function validateNetworkNameInput(raw: unknown): NetworkNameValidation {
  const trimmed = String(raw ?? '').trim()
  if (!trimmed) {
    return { ok: false, message: 'Network name is required.' }
  }
  if (trimmed.length > NETWORK_NAME_MAX_LENGTH) {
    return {
      ok: false,
      message: `Network name must be at most ${NETWORK_NAME_MAX_LENGTH} characters.`,
    }
  }
  if (/[<>&"']/.test(trimmed) || /<\/?[a-z][\s\S]*?>/i.test(trimmed)) {
    return {
      ok: false,
      message: 'Network name cannot contain HTML tags or characters such as <, >, &, ", \'.',
    }
  }
  const lower = trimmed.toLowerCase()
  const normalized = normalizeNetworkName(trimmed)
  if (normalized !== lower) {
    return {
      ok: false,
      message: 'Network name may only contain letters, numbers, dots, and hyphens (no spaces).',
    }
  }
  if (!NETWORK_NAME_PATTERN.test(normalized)) {
    return {
      ok: false,
      message:
        'Network name must start and end with a letter or number; only a-z, 0-9, dot, and hyphen are allowed.',
    }
  }
  return { ok: true, name: normalized }
}

export function networkNameTitle(name: string | null | undefined): string {
  return String(name ?? '')
}

export function formatNetworkNameDisplay(
  name: string | null | undefined,
  maxVisible = NETWORK_NAME_DISPLAY_MAX,
): string {
  const s = String(name ?? '')
  if (s.length <= maxVisible) return s
  return `${s.slice(0, maxVisible - 3)}...`
}

/** Device names in reserved-IP table (same display rules, slightly looser charset). */
export const DEVICE_NAME_MAX_LENGTH = 200
export const DEVICE_NAME_DISPLAY_MAX = 25
const DEVICE_NAME_PATTERN = /^[a-zA-Z0-9._-]+$/

export function validateDeviceNameInput(raw: unknown): NetworkNameValidation {
  const trimmed = String(raw ?? '').trim()
  if (!trimmed) {
    return { ok: true, name: '' }
  }
  if (trimmed.length > DEVICE_NAME_MAX_LENGTH) {
    return {
      ok: false,
      message: `Device name must be at most ${DEVICE_NAME_MAX_LENGTH} characters.`,
    }
  }
  if (/[<>&"']/.test(trimmed)) {
    return { ok: false, message: 'Device name cannot contain special characters such as <, >, &, ", \'.' }
  }
  if (!DEVICE_NAME_PATTERN.test(trimmed)) {
    return {
      ok: false,
      message: 'Device name may only contain letters, numbers, dots, hyphens, and underscores.',
    }
  }
  return { ok: true, name: trimmed }
}

export function formatDeviceNameDisplay(
  name: string | null | undefined,
  maxVisible = DEVICE_NAME_DISPLAY_MAX,
): string {
  return formatNetworkNameDisplay(name, maxVisible)
}

export function deviceNameTitle(name: string | null | undefined): string {
  return String(name ?? '')
}
