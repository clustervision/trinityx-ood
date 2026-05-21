export const SWITCH_NAME_MAX_LENGTH = 200

/** Visible characters in table / compact UI before appending "...". */
export const SWITCH_NAME_DISPLAY_MAX = 50

/** Full name for tooltips (hover note). */
export function switchNameTitle(name: string | null | undefined): string {
  return String(name ?? '')
}

/** Truncate long names for display (full name still in title / storage). */
export function formatSWITCHNameDisplay(
  name: string | null | undefined,
  maxVisible = SWITCH_NAME_DISPLAY_MAX,
): string {
  const s = String(name ?? '')
  if (s.length <= maxVisible) return s
  return `${s.slice(0, maxVisible - 3)}...`
}
