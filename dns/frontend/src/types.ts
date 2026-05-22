export interface DnsEntryRow {
  network: string
  host: string
  ipaddress: string
}

export interface DnsFormState {
  network: string
  host: string
  ipaddress: string
}

export interface DnsListResponse {
  entries: DnsEntryRow[]
}

export interface NetworksResponse {
  networks: string[]
}

export interface ApiEnvelope<T = unknown> {
  status?: boolean
  status_code?: number
  content?: T
  message?: string
}
