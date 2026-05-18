/** Resolve icon URL for dev (Vite public/) vs deployed Luna app assets. */
export function iconUrl(fileName: string): string {
  if (import.meta.env.DEV) {
    return `/icons/${fileName}`
  }
  const appUrl = String(
    window.APP_URL || import.meta.env.VITE_APP_URL || '',
  ).replace(/\/$/, '')
  return `${appUrl}/app/assets/icons/${fileName}`
}

export function applyIconCssVars(): void {
  const root = document.documentElement
  root.style.setProperty(
    '--tx-icon-edit',
    `url("${iconUrl('icon-edit.png')}")`,
  )
  root.style.setProperty(
    '--tx-icon-edit-orange',
    `url("${iconUrl('icon-edit-orange.png')}")`,
  )
  root.style.setProperty(
    '--tx-icon-rename',
    `url("${iconUrl('icon-rename.png')}")`,
  )
}
