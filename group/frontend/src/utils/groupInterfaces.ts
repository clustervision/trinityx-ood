import type { NetworkInterface } from '@/types/network'

function interfaceNames(list: NetworkInterface[] | undefined): string[] {
  return (list ?? [])
    .map((row) => String(row.interface ?? '').trim())
    .filter(Boolean)
}

/** Interface names present when the form was opened but removed before Save. */
export function removedInterfaceNames(
  initialSnapshot: string,
  currentInterfaces: NetworkInterface[],
): string[] {
  let initial: { interfaces?: NetworkInterface[] }
  try {
    initial = JSON.parse(initialSnapshot) as { interfaces?: NetworkInterface[] }
  } catch {
    return []
  }

  const initialSet = new Set(interfaceNames(initial.interfaces))
  const currentSet = new Set(interfaceNames(currentInterfaces))
  return [...initialSet].filter((name) => !currentSet.has(name))
}
