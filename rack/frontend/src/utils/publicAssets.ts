/**
 * Rack Flask serves the Vite build from `app/assets` at `/static/` on the **current document origin**
 * (OOD pun URL or direct :7755). Do not use `APP_URL` for static images — it often points at a
 * different host/port than the page the user is viewing.
 */

function upgradeScheme(url: string): string {
  if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
    return url.replace(/^http:\/\//i, 'https://')
  }
  return url
}

export function publicAssetUrl(relativePath: string): string {
  const base = import.meta.env.BASE_URL || './'
  const r = String(relativePath || '').replace(/^\//, '')
  return `${base}${r}`
}

function rackDocumentBase(): string {
  const href = typeof window !== 'undefined' ? window.location.href : ''
  const pageUrl = href.split('#')[0]?.split('?')[0] ?? ''
  return pageUrl.endsWith('/') ? pageUrl : `${pageUrl}/`
}

/** Static file under Flask `/app/assets/<path>` (same origin as the SPA page). */
export function rackStaticUrl(relativePath: string): string {
  const r = String(relativePath || '').replace(/^\//, '')
  if (import.meta.env.DEV) {
    return publicAssetUrl(r)
  }
  if (typeof window !== 'undefined' && window.location?.href) {
    return upgradeScheme(new URL(`app/assets/${r}`, rackDocumentBase()).href)
  }
  return publicAssetUrl(r)
}
