/** Max characters for an OS image name (Luna / UI). */
export const OSIMAGE_NAME_MAX_LENGTH = 200

/** Visible characters in table / compact UI before appending "...". */
export const OSIMAGE_NAME_DISPLAY_MAX = 25

/** Full name for tooltips (hover). */
export function osimageNameTitle(name: string | null | undefined): string {
  return String(name ?? '')
}

/** Truncate long OS image names for display (full name still in title / value). */
export function formatOsimageNameDisplay(
  name: string | null | undefined,
  maxVisible = OSIMAGE_NAME_DISPLAY_MAX,
): string {
  const s = String(name ?? '')
  if (s.length <= maxVisible) return s
  return `${s.slice(0, maxVisible - 3)}...`
}
