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
  status?: boolean
  status_code?: number
  content?: T | string | DaemonErrorContent
  message?: string
  error?: string
}

export interface NetworkRecord {
  name?: string
  network?: string
  network_ipv6?: string | null
  type?: string
  zone?: string
  comment?: string | null
  dhcp?: boolean
  dhcp_nodes_in_pool?: boolean
  dhcp_nodes_only?: boolean
  dhcp_range_begin?: string
  dhcp_range_end?: string
  dhcp_range_begin_ipv6?: string | null
  dhcp_range_end_ipv6?: string | null
  gateway?: string
  gateway_ipv6?: string | null
  gateway_metric?: number | string | null
  nameserver_ip?: string | null
  nameserver_ip_ipv6?: string | null
  ntp_server?: string | null
  subnet_ipv6?: string | null
  non_authoritative?: boolean | null
  shared?: boolean | null
  newnetname?: string
  [key: string]: unknown
}

export interface NetworkConfigContent {
  config?: {
    network?: Record<string, NetworkRecord>
  }
}

export interface NetworkInventoryRow {
  name: string
  network?: string
  type?: string
  zone?: string
  dhcp?: boolean
  dhcp_range_begin?: string
  dhcp_range_end?: string
}

export interface NetworkListResult {
  networks: NetworkInventoryRow[]
  error: string
}

export interface NetworkFormState {
  network: string
  type: string
  zone: string
  dhcp: boolean
  dhcp_range_begin: string
  dhcp_range_end: string
  gateway: string
  nameserver_ip: string
  ntp_server: string
  gateway_metric: string
  shared: string
  dhcp_nodes_only: boolean
  dhcp_nodes_in_pool: boolean
  non_authoritative: boolean
  comment: string
}

export interface ReservedIpRow {
  ip: string
  deviceName: string
}
