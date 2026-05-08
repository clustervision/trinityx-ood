/**
 * Public static files (served from project `public/`), with correct Vite `BASE_URL` prefix.
 * Navbar logo only — toolbar icons live in `src/assets/img/` (see assetImg.ts).
 */

export function publicAssetUrl(relativePath: string): string {
  const base = import.meta.env.BASE_URL || '/'
  const r = String(relativePath || '').replace(/^\//, '')
  return `${base}${r}`
}
