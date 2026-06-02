const UNSUBSTITUTED_APP_URL = /^\{\{\s*APP_URL\s*\}\}$/i

export function appUrlFromRuntime(): string {
  const raw = String((typeof window !== 'undefined' && window.APP_URL) || '').trim()
  if (!raw || UNSUBSTITUTED_APP_URL.test(raw)) return ''
  return raw.replace(/\/+$/, '')
}

export function oodAppRootFromBrowser(): string {
  if (typeof window === 'undefined') return ''
  const path = window.location.pathname.replace(/\/+$/, '') || ''
  return `${window.location.origin}${path}`.replace(/\/$/, '')
}

export function oodAppRoot(): string {
  const fromRuntime = appUrlFromRuntime()
  if (fromRuntime) {
    try {
      const parsed = new URL(fromRuntime)
      const path = parsed.pathname.replace(/\/+$/, '') || ''
      if (path && path !== '/') return `${window.location.origin}${path}`.replace(/\/$/, '')
      return fromRuntime
    } catch {
      return fromRuntime
    }
  }
  return oodAppRootFromBrowser()
}
