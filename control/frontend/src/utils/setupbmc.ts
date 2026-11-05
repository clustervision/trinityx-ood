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

/** Match node app: empty / inherit → default true; only explicit false disables BMC/SEL. */
export function isSetupBmcEnabled(value: unknown): boolean {
  if (value === false) return false
  if (typeof value === 'string' && ['false', 'no', '0'].includes(value.trim().toLowerCase())) {
    return false
  }
  return true
}

export function filterSelHostlist(
  hostlist: string[],
  setupbmcByNode: Record<string, boolean | undefined>,
): { enabled: string[]; skipped: string[] } {
  const enabled: string[] = []
  const skipped: string[] = []
  for (const node of hostlist) {
    const key = Object.keys(setupbmcByNode).find((k) => k.toLowerCase() === node.toLowerCase())
    const enabledFlag = key != null ? setupbmcByNode[key] : undefined
    if (enabledFlag === false) skipped.push(node)
    else enabled.push(node)
  }
  return { enabled, skipped }
}
