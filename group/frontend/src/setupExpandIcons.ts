/**
 * Set background-image CSS vars at runtime so paths resolve correctly under OOD/Pun.
 */
import { punAppAssetUrl } from './utils/publicAssets'

const asCssUrl = (href: string): string =>
  `url("${href.replace(/\\/g, '/')}")`

document.documentElement.style.setProperty(
  '--tx-icon-edit',
  asCssUrl(punAppAssetUrl('icons/icon-edit.png')),
)
document.documentElement.style.setProperty(
  '--tx-icon-edit-orange',
  asCssUrl(punAppAssetUrl('icons/icon-edit-orange.png')),
)
