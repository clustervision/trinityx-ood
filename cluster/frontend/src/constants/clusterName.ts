export const CLUSTER_NAME_MAX_LENGTH = 200
export const CLUSTER_NAME_PATTERN = /^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$/

export type ClusterNameValidation =
  | { ok: true; name: string }
  | { ok: false; message: string }

export function normalizeClusterName(raw: unknown): string {
  return String(raw ?? '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9.-]/g, '')
}

export function validateClusterNameInput(raw: unknown): ClusterNameValidation {
  const trimmed = String(raw ?? '').trim()
  if (!trimmed) {
    return { ok: false, message: 'Cluster name is required.' }
  }
  if (trimmed.length > CLUSTER_NAME_MAX_LENGTH) {
    return {
      ok: false,
      message: `Cluster name must be at most ${CLUSTER_NAME_MAX_LENGTH} characters.`,
    }
  }
  if (/[<>&"']/.test(trimmed) || /<\/?[a-z][\s\S]*?>/i.test(trimmed)) {
    return {
      ok: false,
      message: 'Cluster name cannot contain HTML tags or characters such as <, >, &, ", \'.',
    }
  }
  const lower = trimmed.toLowerCase()
  const normalized = normalizeClusterName(trimmed)
  if (normalized !== lower) {
    return {
      ok: false,
      message: 'Cluster name may only contain letters, numbers, dots, and hyphens (no spaces).',
    }
  }
  if (!CLUSTER_NAME_PATTERN.test(normalized)) {
    return {
      ok: false,
      message:
        'Cluster name must start and end with a letter or number; only a-z, 0-9, dot, and hyphen are allowed.',
    }
  }
  return { ok: true, name: normalized }
}
