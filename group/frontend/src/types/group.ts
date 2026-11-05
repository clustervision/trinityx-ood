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

export interface Group {
  name: string
  newgroupname?: string

  roles?: string | null
  netboot?: string
  osimage?: string
  scripts?: string | null

  setupbmc?: string
  bmcsetupname?: string

  domain?: string
  unmanaged_bmc_users?: string | null

  kerneloptions?: string
  prescript?: string
  partscript?: string
  postscript?: string

  osimagetag?: string

  provision_interface?: string
  provision_fallback?: string
  provision_method?: string

  bootmenu?: string

  comment?: string | null

  interfaces?: NetworkInterface[]
}
