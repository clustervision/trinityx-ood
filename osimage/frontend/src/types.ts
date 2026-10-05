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

export interface DaemonErrorContent {
  message?: string
}

export interface DaemonEnvelope<T = unknown> {
  status?: boolean | string
  status_code?: number
  content?: T | string | DaemonErrorContent
  message?: string
  error?: string
}

export interface OsimageRecord {
  name?: string
  _override?: boolean
  kernelversion?: string
  kerneldetails?: string
  distribution?: string
  osrelease?: string
  path?: string
  initrdfile?: string
  kernelfile?: string
  imagefile?: string
  [key: string]: unknown
}

export interface OsimageConfigContent {
  config?: {
    osimage?: Record<string, OsimageRecord>
  }
}

export interface OsimageInventoryRow {
  name?: string
  kernelversion?: string
  kerneldetails?: string
  distribution?: string
  osrelease?: string
  path?: string
  initrdfile?: string
  kernelfile?: string
  imagefile?: string
}

export interface OsimageListResult {
  images: OsimageInventoryRow[]
  error: string
  chroot_base_url: string
}

export interface OsimageFormBase {
  kernelversion: string
  distribution: string
  osrelease: string
  path: string
  grab_filesystems: string
  grab_exclude: string
  kerneloptions: string
  kernelmodules: string
  kernelfile: string
  initrdfile: string
  imagefile: string
  comment: string
}

export interface AddOsimageForm extends OsimageFormBase {
  name: string
}

export interface EditOsimageForm extends OsimageFormBase {
  tag: string
  bare: boolean
}

export interface CloneOsimageForm extends OsimageFormBase {
  newosimage: string
  bare: boolean
}

export type PackStatusPayload =
  | string
  | {
      message?: string
      status?: string | boolean
      state?: string
      phase?: string
      content?: unknown
      log?: string
      logs?: string[] | string
      stdout?: string
      stderr?: string
      details?: unknown
      result?: unknown
      error?: string
      done?: boolean
      finished?: boolean
      complete?: boolean
      completed?: boolean
      [key: string]: unknown
    }
