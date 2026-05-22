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

/** Assets served by Flask as `…/pun/sys/<app>/app/assets/<path>`. */
export function punAppAssetUrl(relativePath: string): string {
  const r = String(relativePath || '').replace(/^\//, '')
  if (import.meta.env.DEV) {
    return `/network-backend/app/assets/${r}`
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
