import type { NetworkFormState } from './types'

export function emptyNetworkForm(): NetworkFormState {
  return {
    network: '',
    type: '',
    zone: '',
    dhcp: false,
    dhcp_range_begin: '',
    dhcp_range_end: '',
    gateway: '',
    nameserver_ip: '',
    ntp_server: '',
    gateway_metric: '',
    shared: '',
    dhcp_nodes_only: true,
    dhcp_nodes_in_pool: false,
    non_authoritative: false,
    comment: '',
  }
}
