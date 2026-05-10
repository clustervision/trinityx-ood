export interface NetworkInterface {
  interface: string
  network: string
  mtu?: string
  vlanid?: string
  vlan_parent?: string
  bond_mode?: string
  bond_slaves?: string
  options?: string
  dhcp?: boolean | string | number
}
