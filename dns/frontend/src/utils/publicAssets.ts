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
  const appUrl = window.APP_URL?.trim()
  if (appUrl && !/^\{\{\s*APP_URL\s*\}\}$/i.test(appUrl)) {
    return upgradeScheme(`${appUrl.replace(/\/+$/, '')}/app/assets/${r}`)
  }
  return publicAssetUrl(r)
}

export function appUrlFromRuntime(): string {
  const raw = String(window.APP_URL || '').trim()
  if (!raw || /^\{\{\s*APP_URL\s*\}\}$/i.test(raw)) return ''
  return raw.replace(/\/$/, '')
}
