/** Max characters for an OS image tag name (Luna / UI). */
export const TAG_NAME_MAX_LENGTH = 200

/** Visible characters in table / compact UI before appending "...". */
export const TAG_NAME_DISPLAY_MAX = 25

/** Luna: lowercase a-z, 0-9, dot, hyphen. */
export const TAG_NAME_PATTERN = /^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$/

export type TagNameValidation =
  | { ok: true; name: string }
  | { ok: false; message: string }

export function normalizeTagName(raw: unknown): string {
  return String(raw ?? '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9.-]/g, '')
}

/** Reject HTML / invalid characters before add. */
export function validateTagNameInput(raw: unknown): TagNameValidation {
  const trimmed = String(raw ?? '').trim()
  if (!trimmed) {
    return { ok: false, message: 'Tag name is required.' }
  }
  if (trimmed.length > TAG_NAME_MAX_LENGTH) {
    return {
      ok: false,
      message: `Tag name must be at most ${TAG_NAME_MAX_LENGTH} characters.`,
    }
  }
  if (/[<>&"']/.test(trimmed) || /<\/?[a-z][\s\S]*?>/i.test(trimmed)) {
    return {
      ok: false,
      message: 'Tag name cannot contain HTML tags or characters such as <, >, &, ", \'.',
    }
  }
  const lower = trimmed.toLowerCase()
  const normalized = normalizeTagName(trimmed)
  if (normalized !== lower) {
    return {
      ok: false,
      message: 'Tag name may only contain letters, numbers, dots, and hyphens (no spaces).',
    }
  }
  if (!TAG_NAME_PATTERN.test(normalized)) {
    return {
      ok: false,
      message:
        'Tag name must start and end with a letter or number; only a-z, 0-9, dot, and hyphen are allowed.',
    }
  }
  return { ok: true, name: normalized }
}

export function tagNameTitle(name: string | null | undefined): string {
  return String(name ?? '')
}

export function formatTagNameDisplay(
  name: string | null | undefined,
  maxVisible = TAG_NAME_DISPLAY_MAX,
): string {
  const s = String(name ?? '')
  if (s.length <= maxVisible) return s
  return `${s.slice(0, maxVisible - 3)}...`
}
