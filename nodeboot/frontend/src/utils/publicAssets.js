/**
 * Public static files (served from project `public/`), with correct Vite `BASE_URL` prefix.
 *
 * In OOD, Flask exposes the bundle under `/app/assets`; `window.APP_URL` is the Pun app root.
 */

function upgradeScheme(url) {
  if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
    return url.replace(/^http:\/\//i, 'https://')
  }
  return url
}

export function publicAssetUrl(relativePath) {
  const base = import.meta.env.BASE_URL || '/'
  const clean = String(relativePath || '').replace(/^\//, '')
  return `${base}${clean}`
}

/** Assets served by Flask as `…/app/assets/<path>`. */
export function punAppAssetUrl(relativePath) {
  const clean = String(relativePath || '').replace(/^\//, '')
  const appUrl = (typeof window !== 'undefined' ? window.APP_URL : '')?.trim()
  if (appUrl) {
    return upgradeScheme(`${appUrl.replace(/\/+$/, '')}/app/assets/${clean}`)
  }
  return publicAssetUrl(clean)
}
