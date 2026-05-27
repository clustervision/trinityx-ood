export const SWITCH_NAME_MAX_LENGTH = 200
export const SWITCH_NAME_PATTERN = /^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$/

export type SwitchNameValidation =
  | { ok: true; name: string }
  | { ok: false; message: string }

export function normalizeSwitchName(raw: unknown): string {
  return String(raw ?? '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9.-]/g, '')
}

export function validateSwitchNameInput(raw: unknown): SwitchNameValidation {
  const trimmed = String(raw ?? '').trim()
  if (!trimmed) {
    return { ok: false, message: 'Switch name is required.' }
  }
  if (trimmed.length > SWITCH_NAME_MAX_LENGTH) {
    return {
      ok: false,
      message: `Switch name must be at most ${SWITCH_NAME_MAX_LENGTH} characters.`,
    }
  }
  if (/[<>&"']/.test(trimmed) || /<\/?[a-z][\s\S]*?>/i.test(trimmed)) {
    return {
      ok: false,
      message: 'Switch name cannot contain HTML tags or characters such as <, >, &, ", \'.',
    }
  }
  const lower = trimmed.toLowerCase()
  const normalized = normalizeSwitchName(trimmed)
  if (normalized !== lower) {
    return {
      ok: false,
      message: 'Switch name may only contain letters, numbers, dots, and hyphens (no spaces).',
    }
  }
  if (!SWITCH_NAME_PATTERN.test(normalized)) {
    return {
      ok: false,
      message:
        'Switch name must start and end with a letter or number; only a-z, 0-9, dot, and hyphen are allowed.',
    }
  }
  return { ok: true, name: normalized }
}

/** Visible characters in table / compact UI before appending "...". */
export const SWITCH_NAME_DISPLAY_MAX = 50

/** Full name for tooltips (hover note). */
export function switchNameTitle(name: string | null | undefined): string {
  return String(name ?? '')
}

/** Truncate long names for display (full name still in title / storage). */
export function formatSWITCHNameDisplay(
  name: string | null | undefined,
  maxVisible = SWITCH_NAME_DISPLAY_MAX,
): string {
  const s = String(name ?? '')
  if (s.length <= maxVisible) return s
  return `${s.slice(0, maxVisible - 3)}...`
}
