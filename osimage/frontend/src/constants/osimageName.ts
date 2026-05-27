/** Max characters for an OS image name (Luna / UI). */
export const OSIMAGE_NAME_MAX_LENGTH = 200
export const OSIMAGE_NAME_PATTERN = /^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$/

export type OsimageNameValidation =
  | { ok: true; name: string }
  | { ok: false; message: string }

export function normalizeOsimageName(raw: unknown): string {
  return String(raw ?? '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9.-]/g, '')
}

export function validateOsimageNameInput(raw: unknown): OsimageNameValidation {
  const trimmed = String(raw ?? '').trim()
  if (!trimmed) {
    return { ok: false, message: 'OS image is required.' }
  }
  if (trimmed.length > OSIMAGE_NAME_MAX_LENGTH) {
    return {
      ok: false,
      message: `OS image name must be at most ${OSIMAGE_NAME_MAX_LENGTH} characters.`,
    }
  }
  if (/[<>&"']/.test(trimmed) || /<\/?[a-z][\s\S]*?>/i.test(trimmed)) {
    return {
      ok: false,
      message: 'OS image name cannot contain HTML tags or characters such as <, >, &, ", \'.',
    }
  }
  const lower = trimmed.toLowerCase()
  const normalized = normalizeOsimageName(trimmed)
  if (normalized !== lower) {
    return {
      ok: false,
      message: 'OS image name may only contain letters, numbers, dots, and hyphens (no spaces).',
    }
  }
  if (!OSIMAGE_NAME_PATTERN.test(normalized)) {
    return {
      ok: false,
      message:
        'OS image name must start and end with a letter or number; only a-z, 0-9, dot, and hyphen are allowed.',
    }
  }
  return { ok: true, name: normalized }
}

/** Visible characters in table / compact UI before appending "...". */
export const OSIMAGE_NAME_DISPLAY_MAX = 25

/** Full name for tooltips (hover). */
export function osimageNameTitle(name: string | null | undefined): string {
  return String(name ?? '')
}

/** Truncate long OS image names for display (full name still in title / value). */
export function formatOsimageNameDisplay(
  name: string | null | undefined,
  maxVisible = OSIMAGE_NAME_DISPLAY_MAX,
): string {
  const s = String(name ?? '')
  if (s.length <= maxVisible) return s
  return `${s.slice(0, maxVisible - 3)}...`
}
