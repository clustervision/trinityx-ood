const UNSUBSTITUTED_APP_URL = /^\{\{\s*APP_URL\s*\}\}$/i

function normalizeAppUrl(url) {
  const trimmed = String(url).trim()
  if (!trimmed || typeof window === 'undefined') return trimmed
  try {
    const parsed = new URL(trimmed)
    if (window.location.protocol === 'https:' && parsed.protocol === 'http:') {
      parsed.protocol = 'https:'
    }
    return `${parsed.origin}${parsed.pathname}`.replace(/\/+$/, '')
  } catch {
    return window.location.protocol === 'https:'
      ? trimmed.replace(/^http:\/\//i, 'https://')
      : trimmed
  }
}

export function getAppUrl() {
  if (import.meta.env.DEV && import.meta.env.VITE_NODEBOOT_BACKEND) {
    return '/nodeboot-backend'
  }

  let url = String(typeof window !== 'undefined' ? window.APP_URL : '').trim().replace(/\/$/, '')
  if (UNSUBSTITUTED_APP_URL.test(url)) url = ''
  if (!url) {
    if (typeof window !== 'undefined') {
      const path = window.location.pathname.replace(/\/+$/, '')
      return `${window.location.origin}${path}`.replace(/\/$/, '')
    }
    return ''
  }
  return /^https?:\/\//i.test(url) ? normalizeAppUrl(url) : url
}

export async function fetchStatus() {
  const response = await fetch(`${getAppUrl()}/api/status`, { cache: 'no-store' })
  return response.json()
}

export async function fetchConsole(nodeName) {
  const response = await fetch(`${getAppUrl()}/api/console/${encodeURIComponent(nodeName)}`, {
    cache: 'no-store',
  })
  return response.json()
}
