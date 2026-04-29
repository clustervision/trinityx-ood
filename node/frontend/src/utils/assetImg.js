/**
 * Bundled images under src/assets/img/ (same pattern as rack-app deviceImageUrls).
 */

export function assetImgUrl(file) {
  return new URL(`../assets/img/${file}`, import.meta.url).href
}

/** Inventory toolbar icons */
export const actionIcons = {
  clone: assetImgUrl('icon-clone.png'),
  osgrab: assetImgUrl('icon-osgrab.png'),
  ospush: assetImgUrl('icon-ospush.png'),
  delete: assetImgUrl('icon-delete.png'),
}
