/** Max stored length for node / OS image names (forms). */
export const NAME_MAX_LENGTH = 200

/** Visible characters in table / compact UI before appending "...". */
export const NAME_DISPLAY_MAX = 25

/** Full name for tooltips (hover). */
export function displayNameTitle(name: string | null | undefined): string {
  return String(name ?? '')
}

/** Truncate long names for table display (full name still in title / value). */
export function formatDisplayName(
  name: string | null | undefined,
  maxVisible = NAME_DISPLAY_MAX,
): string {
  const s = String(name ?? '')
  if (s.length <= maxVisible) return s
  return `${s.slice(0, maxVisible - 3)}...`
}
