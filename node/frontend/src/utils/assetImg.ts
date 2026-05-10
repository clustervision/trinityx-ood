/**
 * Toolbar icons: resolved at runtime via APP_URL so paths are correct under OOD/Pun.
 */

import { punAppAssetUrl } from './publicAssets'

/** Inventory toolbar icons (lazy-init so window.APP_URL is available) */
export const actionIcons = {
  get clone() { return punAppAssetUrl('icon-clone.png') },
  get osgrab() { return punAppAssetUrl('icon-osgrab.png') },
  get ospush() { return punAppAssetUrl('icon-ospush.png') },
  get delete() { return punAppAssetUrl('icon-delete.png') },
}
