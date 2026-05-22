const UNSUBSTITUTED_APP_URL = /^\{\{\s*APP_URL\s*\}\}$/i

export function appUrlFromRuntime(): string {
  const fromWindow =
    typeof window !== 'undefined' && window.APP_URL != null ? String(window.APP_URL).trim() : ''
  if (fromWindow && !UNSUBSTITUTED_APP_URL.test(fromWindow)) return fromWindow
  const fromEnv = String(import.meta.env.VITE_APP_URL || '').trim()
  return fromEnv && !UNSUBSTITUTED_APP_URL.test(fromEnv) ? fromEnv : ''
}

export function sanitizeUserMessage(raw: unknown): string {
  if (raw == null) return ''
  let s = String(raw)
  s = s.replace(/\/api\/v1(?:\/[\w.%-]*)*/gi, '')
  s = s.replace(/\s{2,}/g, ' ')
  return s.trim()
}

export function messageForDisplay(raw: unknown): string {
  const trimmed = String(raw ?? '').trim()
  if (!trimmed) return ''
  const t = sanitizeUserMessage(trimmed)
  return t || 'Request failed.'
}
