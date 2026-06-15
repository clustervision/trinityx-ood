import type { NodeFormInterface } from '@/types'

function interfaceNames(list: NodeFormInterface[] | undefined): string[] {
  return (list ?? [])
    .map((row) => String(row.interface ?? '').trim())
    .filter(Boolean)
}

/** Interface names present when the form was opened but removed before Save. */
export function removedInterfaceNames(
  initialSnapshot: string,
  currentInterfaces: NodeFormInterface[],
): string[] {
  let initial: { interfaces?: NodeFormInterface[] }
  try {
    initial = JSON.parse(initialSnapshot) as { interfaces?: NodeFormInterface[] }
  } catch {
    return []
  }

  const initialSet = new Set(interfaceNames(initial.interfaces))
  const currentSet = new Set(interfaceNames(currentInterfaces))
  return [...initialSet].filter((name) => !currentSet.has(name))
}
