/**
 * Public static files (served from project `public/`), with correct Vite `BASE_URL` prefix.
 *
 * In OOD, Flask exposes the bundle under `/app/assets`; `window.APP_URL` is the Pun app root,
 * never `https://host/static/…` at the Apache docroot — so prefer APP_URL when present.
 */

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

/** Assets served by Flask as `…/app/assets/<path>`. */
export function punAppAssetUrl(relativePath: string): string {
  const r = String(relativePath || '').replace(/^\//, '')
  const appUrl = (
    typeof window !== 'undefined'
      ? (window as Window & { APP_URL?: string }).APP_URL
      : ''
  )?.trim()
  if (appUrl) {
    return upgradeScheme(`${appUrl.replace(/\/+$/, '')}/app/assets/${r}`)
  }
  return publicAssetUrl(r)
}
