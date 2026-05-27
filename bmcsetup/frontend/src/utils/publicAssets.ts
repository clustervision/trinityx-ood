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
