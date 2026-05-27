/** Max characters for a BMC setup name (Luna / UI). */
export const BMC_NAME_MAX_LENGTH = 200

/** Visible characters in table / compact UI before appending "...". */
export const BMC_NAME_DISPLAY_MAX = 50

/** Luna: lowercase a-z, 0-9, dot, hyphen. */
export const BMC_NAME_PATTERN = /^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$/

export type BmcNameValidation =
  | { ok: true; name: string }
  | { ok: false; message: string }

export function normalizeBmcName(raw: unknown): string {
  return String(raw ?? '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9.-]/g, '')
}

export function validateBmcNameInput(raw: unknown): BmcNameValidation {
  const trimmed = String(raw ?? '').trim()
  if (!trimmed) {
    return { ok: false, message: 'Name is required.' }
  }
  if (trimmed.length > BMC_NAME_MAX_LENGTH) {
    return {
      ok: false,
      message: `BMC setup name must be at most ${BMC_NAME_MAX_LENGTH} characters.`,
    }
  }
  if (/[<>&"']/.test(trimmed) || /<\/?[a-z][\s\S]*?>/i.test(trimmed)) {
    return {
      ok: false,
      message: 'BMC setup name cannot contain HTML tags or characters such as <, >, &, ", \'.',
    }
  }
  const lower = trimmed.toLowerCase()
  const normalized = normalizeBmcName(trimmed)
  if (normalized !== lower) {
    return {
      ok: false,
      message: 'BMC setup name may only contain letters, numbers, dots, and hyphens (no spaces).',
    }
  }
  if (!BMC_NAME_PATTERN.test(normalized)) {
    return {
      ok: false,
      message:
        'BMC setup name must start and end with a letter or number; only a-z, 0-9, dot, and hyphen are allowed.',
    }
  }
  return { ok: true, name: normalized }
}

/** Full name for tooltips (hover note). */
export function bmcNameTitle(name: string | null | undefined): string {
  return String(name ?? '')
}

/** Truncate long names for display (full name still in title / storage). */
export function formatBMCNameDisplay(
  name: string | null | undefined,
  maxVisible = BMC_NAME_DISPLAY_MAX,
): string {
  const s = String(name ?? '')
  if (s.length <= maxVisible) return s
  return `${s.slice(0, maxVisible - 3)}...`
}
