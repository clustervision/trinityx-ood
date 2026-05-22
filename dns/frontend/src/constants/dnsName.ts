export const DNS_NAME_MAX_LENGTH = 200
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
): DnsLabelValidation {
  const trimmed = String(raw ?? '').trim()
  if (!trimmed) {
    return required
      ? { ok: false, message: `${fieldLabel} is required.` }
      : { ok: true, value: '' }
  }
  if (trimmed.length > DNS_NAME_MAX_LENGTH) {
    return {
      ok: false,
      message: `${fieldLabel} must be at most ${DNS_NAME_MAX_LENGTH} characters.`,
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
