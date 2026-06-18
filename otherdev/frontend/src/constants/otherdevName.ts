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

export const OTHER_DEV_NAME_MAX_LENGTH = 200
export const OTHER_DEV_NAME_PATTERN = /^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$/

export type OtherDevNameValidation =
  | { ok: true; name: string }
  | { ok: false; message: string }

export function normalizeOtherDevName(raw: unknown): string {
  return String(raw ?? '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9.-]/g, '')
}

export function validateOtherdevNameInput(raw: unknown): OtherDevNameValidation {
  const trimmed = String(raw ?? '').trim()
  if (!trimmed) {
    return { ok: false, message: 'Other device name is required.' }
  }
  if (trimmed.length > OTHER_DEV_NAME_MAX_LENGTH) {
    return {
      ok: false,
      message: `Other device name must be at most ${OTHER_DEV_NAME_MAX_LENGTH} characters.`,
    }
  }
  if (/[<>&"']/.test(trimmed) || /<\/?[a-z][\s\S]*?>/i.test(trimmed)) {
    return {
      ok: false,
      message: 'Other device name cannot contain HTML tags or characters such as <, >, &, ", \'.',
    }
  }
  const lower = trimmed.toLowerCase()
  const normalized = normalizeOtherDevName(trimmed)
  if (normalized !== lower) {
    return {
      ok: false,
      message: 'Other device name may only contain letters, numbers, dots, and hyphens (no spaces).',
    }
  }
  if (!OTHER_DEV_NAME_PATTERN.test(normalized)) {
    return {
      ok: false,
      message:
        'Other device name must start and end with a letter or number; only a-z, 0-9, dot, and hyphen are allowed.',
    }
  }
  return { ok: true, name: normalized }
}

/** Visible characters in table / compact UI before appending "...". */
export const OTHER_DEV_NAME_DISPLAY_MAX = 50

/** Full name for tooltips (hover note). */
export function otherdevNameTitle(name: string | null | undefined): string {
  return String(name ?? '')
}

/** Truncate long names for display (full name still in title / storage). */
export function formatOtherDevNameDisplay(
  name: string | null | undefined,
  maxVisible = OTHER_DEV_NAME_DISPLAY_MAX,
): string {
  const s = String(name ?? '')
  if (s.length <= maxVisible) return s
  return `${s.slice(0, maxVisible - 3)}...`
}
