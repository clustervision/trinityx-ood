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
