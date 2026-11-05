const UNSUBSTITUTED_APP_URL = /^\{\{\s*APP_URL\s*\}\}$/i

export function oodAppRootFromBrowser(): string {
  if (typeof window === 'undefined') return ''
  const path = window.location.pathname.replace(/\/+$/, '') || ''
  return `${window.location.origin}${path}`.replace(/\/$/, '')
}

export function oodAppRoot(): string {
  let explicit = String(
    (typeof window !== 'undefined' && window.APP_URL) || import.meta.env.VITE_APP_URL || '',
  )
    .trim()
    .replace(/\/$/, '')

  if (UNSUBSTITUTED_APP_URL.test(explicit)) explicit = ''

  if (explicit) {
    try {
      const parsed = new URL(explicit)
      const path = parsed.pathname.replace(/\/+$/, '') || ''
      if (path && path !== '/') {
        if (typeof window !== 'undefined' && window.location?.origin) {
          return `${window.location.origin}${path}`.replace(/\/$/, '')
        }
        return explicit.replace(/\/$/, '')
      }
    } catch {
      if (!/^https?:\/\//i.test(explicit)) return explicit.replace(/\/$/, '')
    }
  }

  return oodAppRootFromBrowser()
}
