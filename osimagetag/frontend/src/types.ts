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

export interface OsimageTagRecord {
  name?: string
  osimage?: string
  kernelfile?: string
  initrdfile?: string
  imagefile?: string
  path?: string
  nodes?: string
  groups?: string
  [key: string]: unknown
}

export interface OsimageTagConfigContent {
  config?: {
    osimagetag?: Record<string, OsimageTagRecord>
  }
}

/** Daemon list payload for `GET /api/v1/osimage` (read-only picker). */
export interface OsimageNamesConfigContent {
  config?: {
    osimage?: Record<string, unknown>
  }
}

export interface OsimageTagInventoryRow {
  osimage?: string
  name?: string
  kernelfile?: string
  initrdfile?: string
  imagefile?: string
  path?: string
  nodes?: string
  groups?: string
}

export interface OsimageTagListResult {
  tags: OsimageTagInventoryRow[]
  error: string
}
