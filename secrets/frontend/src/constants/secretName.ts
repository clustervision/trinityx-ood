/** Max characters for a secret name (Luna / UI). */
export const SECRET_NAME_MAX_LENGTH = 200
export const SECRET_NAME_PATTERN = /^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$/

export type SecretNameValidation =
  | { ok: true; name: string }
  | { ok: false; message: string }

export function normalizeSecretName(raw: unknown): string {
  return String(raw ?? '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9.-]/g, '')
}

export function validateSecretNameInput(raw: unknown): SecretNameValidation {
  const trimmed = String(raw ?? '').trim()
  if (!trimmed) {
    return { ok: false, message: 'Secret name is required.' }
  }
  if (trimmed.length > SECRET_NAME_MAX_LENGTH) {
    return {
      ok: false,
      message: `Secret name must be at most ${SECRET_NAME_MAX_LENGTH} characters.`,
    }
  }
  if (/[<>&"']/.test(trimmed) || /<\/?[a-z][\s\S]*?>/i.test(trimmed)) {
    return {
      ok: false,
      message: 'Secret name cannot contain HTML tags or characters such as <, >, &, ", \'.',
    }
  }
  const lower = trimmed.toLowerCase()
  const normalized = normalizeSecretName(trimmed)
  if (normalized !== lower) {
    return {
      ok: false,
      message: 'Secret name may only contain letters, numbers, dots, and hyphens (no spaces).',
    }
  }
  if (!SECRET_NAME_PATTERN.test(normalized)) {
    return {
      ok: false,
      message:
        'Secret name must start and end with a letter or number; only a-z, 0-9, dot, and hyphen are allowed.',
    }
  }
  return { ok: true, name: normalized }
}

/** Visible characters in table / compact UI before appending "...". */
export const SECRET_NAME_DISPLAY_MAX = 25

export function secretNameTitle(name: string | null | undefined): string {
  return String(name ?? '')
}

export function formatSecretNameDisplay(
  name: string | null | undefined,
  maxVisible = SECRET_NAME_DISPLAY_MAX,
): string {
  const s = String(name ?? '')
  if (s.length <= maxVisible) return s
  return `${s.slice(0, maxVisible - 3)}...`
}
