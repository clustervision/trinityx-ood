import { oodAppRoot } from './oodAppRoot'

function upgradeScheme(url: string): string {
  if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
    return url.replace(/^http:\/\//i, 'https://')
  }
  return url
}

export function publicAssetUrl(relativePath: string): string {
  const base = import.meta.env.BASE_URL || '/'
  const r = String(relativePath || '').replace(/^\//, '')
  return `${base}${r}`
}

export function punAppAssetUrl(relativePath: string): string {
  const r = String(relativePath || '').replace(/^\//, '')
  if (import.meta.env.DEV) {
    return `/dns-backend/app/assets/${r}`
  }
  const root = oodAppRoot()
  if (root) {
    return upgradeScheme(`${root.replace(/\/+$/, '')}/app/assets/${r}`)
  }
  if (typeof window !== 'undefined') {
    const path = window.location.pathname.replace(/\/+$/, '')
    return `${path}/app/assets/${r}`
  }
  return `/app/assets/${r}`
}

export function appUrlFromRuntime(): string {
  const raw = String(window.APP_URL || '').trim()
  if (!raw || /^\{\{\s*APP_URL\s*\}\}$/i.test(raw)) return ''
  return raw.replace(/\/$/, '')
}
