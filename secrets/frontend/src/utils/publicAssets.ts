import { oodAppRoot } from './oodAppRoot'

export function punAppAssetUrl(relativePath: string): string {
  const r = String(relativePath || '').replace(/^\//, '')
  if (import.meta.env.DEV) return `/secret-backend/app/assets/${r}`
  const root = oodAppRoot()
  if (root) return `${root.replace(/\/+$/, '')}/app/assets/${r}`
  return `/app/assets/${r}`
}
