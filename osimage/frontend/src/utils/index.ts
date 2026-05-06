export function publicAssetUrl(relativePath: string) {
  const base = import.meta.env.BASE_URL || '/'
  const r = String(relativePath || '').replace(/^\//, '')
  return `${base}${r}`
}

const UNSUBSTITUTED_APP_URL = /^\{\{\s*APP_URL\s*\}\}$/i

/**
 * Runtime app URL source of truth:
 * 1) index.html injected window.APP_URL (preferred)
 * 2) VITE_APP_URL from .env
 */
export function appUrlFromRuntime() {
  const fromWindow =
    typeof window !== 'undefined' && (window as any).APP_URL != null
      ? String((window as any).APP_URL).trim()
      : ''
  if (fromWindow && !UNSUBSTITUTED_APP_URL.test(fromWindow)) return fromWindow
  const fromEnv = String(import.meta.env.VITE_APP_URL || '').trim()
  return fromEnv && !UNSUBSTITUTED_APP_URL.test(fromEnv) ? fromEnv : ''
}

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

/**
 * Dev: Flask may sit on :7755 while OOD Shell lives on another origin (e.g. :8080).
 * Set VITE_OOD_SHELL_ORIGIN to rewrite lchroot links to the real OnDemand base URL.
 */
export function oodShellOrigin() {
  return String(import.meta.env.VITE_OOD_SHELL_ORIGIN || '').trim().replace(/\/$/, '')
}

function inferredOodShellOrigin() {
  const appUrl = appUrlFromRuntime()
  if (!appUrl) return ''
  try {
    const u = new URL(appUrl)
    return `https://${u.hostname}:8080`
  } catch {
    return ''
  }
}

function preferredShellOrigin() {
  return oodShellOrigin() || inferredOodShellOrigin()
}

function inferredShellHost() {
  const appUrl = appUrlFromRuntime()
  if (appUrl) {
    try {
      return new URL(appUrl).hostname
    } catch {
      /* ignore */
    }
  }
  if (typeof window !== 'undefined' && window.location?.hostname) {
    return window.location.hostname
  }
  return ''
}

/**
 * Replace scheme/host/port of an absolute URL; keep path, query, hash.
 */
export function rewriteUrlOrigin(url: string, newOrigin: string) {
  if (!url || !newOrigin) return url || ''
  const origin = newOrigin.replace(/\/$/, '')
  try {
    const abs = new URL(url)
    const o = new URL(origin.includes('://') ? origin : `http://${origin}`)
    abs.protocol = o.protocol
    abs.hostname = o.hostname
    abs.port = o.port
    return abs.toString()
  } catch {
    return url
  }
}

export function resolveChrootBaseUrl(inventoryPayload: any) {
  const manual = String(import.meta.env.VITE_OOD_CHROOT_BASE || '').trim().replace(/\/$/, '')
  let raw = manual || String(inventoryPayload.chroot_base_url || '').trim()
  if (!raw) {
    const origin = preferredShellOrigin()
    const host = inferredShellHost()
    if (origin && host) raw = `${origin}/pun/sys/shell/ssh/${host}`
  }
  if (!raw) return ''
  const shellO = preferredShellOrigin()
  if (shellO) raw = rewriteUrlOrigin(raw, shellO).replace(/\/$/, '')
  return raw
}

export function rewriteIfShellOrigin(url: string) {
  const o = preferredShellOrigin()
  return o && url ? rewriteUrlOrigin(url, o) : url
}
