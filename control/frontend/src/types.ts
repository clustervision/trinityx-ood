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

export type StatusField = 'power' | 'sel' | 'chassis' | 'redfish'

export interface ControlStatusRow {
  node: string
  power: string
  sel: string
  chassis: string
  redfish: string
  /** false → skip SEL status/actions (from Luna node.setupbmc). Default true. */
  setupbmc?: boolean
  errors?: Partial<Record<Exclude<StatusField, 'redfish'>, string>>
}

export interface ControlNodeInfo {
  name: string
  setupbmc: boolean
}

export interface StatusToast {
  id: string
  node: string
  field: StatusField
  message: string
  /** When many failures are collapsed into one toast. */
  details?: string[]
}

export interface RequestEnvelope {
  control?: Record<string, unknown>
  request_id?: string
  message?: string
}

export interface StatusSnapshot {
  rows: ControlStatusRow[]
  requestIds: {
    power: string
    sel: string
    chassis: string
  }
  toasts: StatusToast[]
}

export interface BulkStatusResult extends StatusSnapshot {}

export interface SelLogEntry {
  node: string
  text: string
  error?: boolean
  /** When Luna returns one combined log for many nodes. */
  nodes?: string[]
}
