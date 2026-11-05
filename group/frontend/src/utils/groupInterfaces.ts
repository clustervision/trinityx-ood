/*
 * This code is part of the TrinityX software suite
 * Copyright (C) 2026  ClusterVision Solutions b.v.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>
 *
 * @author      Yixin Zhang
 * @copyright   Copyright 2026, Luna2 Project[OOD]
 * @license     GPL
 * @version     2.0
 * @maintainer  Yixin Zhang
 * @email       yixin.zhang@clustervision.com
 * @status      Development
 */

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
