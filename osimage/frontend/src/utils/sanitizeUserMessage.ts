/**
 * Remove internal REST path segments from strings shown in the UI (errors, pack log, alerts).
 */
export function sanitizeUserMessage(raw: unknown): string {
  if (raw == null) return ''
  let s = String(raw)
  s = s.replace(/\/api\/v1(?:\/[\w.%-]*)*/gi, '')
  s = s.replace(/\s{2,}/g, ' ')
  return s.trim()
}

/** Use for daemon/HTTP messages: strip API paths; if nothing readable remains, generic fallback. */
export function messageForDisplay(raw: unknown): string {
  const trimmed = String(raw ?? '').trim()
  if (!trimmed) return ''
  const t = sanitizeUserMessage(trimmed)
  return t || 'Request failed.'
}
