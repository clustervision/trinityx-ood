/**
 * Toolbar icons: resolved at runtime via APP_URL so paths are correct under OOD/Pun.
 */

import { punAppAssetUrl } from './publicAssets'

/** Inventory toolbar icons (lazy-init so window.APP_URL is available) */
export const actionIcons = {
  get clone() { return punAppAssetUrl('icons/icon-clone.png') },
  get osgrab() { return punAppAssetUrl('icons/icon-osgrab.png') },
  get ospush() { return punAppAssetUrl('icons/icon-ospush.png') },
  get delete() { return punAppAssetUrl('icons/icon-delete.png') },
}
