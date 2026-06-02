import { oodAppRoot } from './oodAppRoot'

function upgradeScheme(url: string): string {
  if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
    return url.replace(/^http:\/\//i, 'https://')
  }
  return url
}

/** Assets served by Flask as `…/app/assets/<path>`. */
export function punAppAssetUrl(relativePath: string): string {
  const r = String(relativePath || '').replace(/^\//, '')
  if (import.meta.env.DEV) {
    return `/control-backend/app/assets/${r}`
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
