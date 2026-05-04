/**
 * Dev: Flask may sit on :7755 while OOD Shell lives on another origin (e.g. :8080).
 * Set VITE_OOD_SHELL_ORIGIN to rewrite lchroot links to the real OnDemand base URL.
 */

export function oodShellOrigin() {
  return String(import.meta.env.VITE_OOD_SHELL_ORIGIN || '').trim().replace(/\/$/, '')
}

/**
 * Replace scheme/host/port of an absolute URL; keep path, query, hash.
 */
export function rewriteUrlOrigin(url, newOrigin) {
  if (!url || !newOrigin) return url || ''
  const origin = newOrigin.replace(/\/$/, '')
  try {
    const abs = new URL(url)
    const o = new URL(origin.includes('://') ? origin : `http://${origin}`)
    abs.protocol = o.protocol
    abs.hostname = o.hostname
    abs.port = o.port
    return abs.toString()
  } catch {
    return url
  }
}

export function resolveChrootBaseUrl(inventoryPayload) {
  const manual = String(import.meta.env.VITE_OOD_CHROOT_BASE || '').trim().replace(/\/$/, '')
  let raw = manual || String(inventoryPayload.chroot_base_url || '').trim()
  if (!raw) return ''
  const shellO = oodShellOrigin()
  if (shellO) raw = rewriteUrlOrigin(raw, shellO).replace(/\/$/, '')
  return raw
}

export function rewriteIfShellOrigin(url) {
  const o = oodShellOrigin()
  return o && url ? rewriteUrlOrigin(url, o) : url
}
