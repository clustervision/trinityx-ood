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

export const GROUP_NAME_MAX_LENGTH = 200
export const GROUP_NAME_PATTERN = /^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$/

export type GroupNameValidation =
  | { ok: true; name: string }
  | { ok: false; message: string }

export function normalizeGroupName(raw: unknown): string {
  return String(raw ?? '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9.-]/g, '')
}

export function validateGroupNameInput(raw: unknown): GroupNameValidation {
  const trimmed = String(raw ?? '').trim()
  if (!trimmed) {
    return { ok: false, message: 'Group name is required.' }
  }
  if (trimmed.length > GROUP_NAME_MAX_LENGTH) {
    return {
      ok: false,
      message: `Group name must be at most ${GROUP_NAME_MAX_LENGTH} characters.`,
    }
  }
  if (/[<>&"']/.test(trimmed) || /<\/?[a-z][\s\S]*?>/i.test(trimmed)) {
    return {
      ok: false,
      message: 'Group name cannot contain HTML tags or characters such as <, >, &, ", \'.',
    }
  }
  const lower = trimmed.toLowerCase()
  const normalized = normalizeGroupName(trimmed)
  if (normalized !== lower) {
    return {
      ok: false,
      message: 'Group name may only contain letters, numbers, dots, and hyphens (no spaces).',
    }
  }
  if (!GROUP_NAME_PATTERN.test(normalized)) {
    return {
      ok: false,
      message:
        'Group name must start and end with a letter or number; only a-z, 0-9, dot, and hyphen are allowed.',
    }
  }
  return { ok: true, name: normalized }
}

/** Visible characters in table / compact UI before appending "...". */
export const GROUP_NAME_DISPLAY_MAX = 50

/** Full name for tooltips (hover note). */
export function groupNameTitle(name: string | null | undefined): string {
  return String(name ?? '')
}

/** Truncate long names for display (full name still in title / storage). */
export function formatGroupNameDisplay(
  name: string | null | undefined,
  maxVisible = GROUP_NAME_DISPLAY_MAX,
): string {
  const s = String(name ?? '')
  if (s.length <= maxVisible) return s
  return `${s.slice(0, maxVisible - 3)}...`
}