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

/* ------------------------------------------------------------------ */
/*  Node inventory (table)                                            */
/* ------------------------------------------------------------------ */

export interface NodeInventoryInterface {
  interface?: string
  macaddress?: string
  ipaddress?: string
  ipaddress_ipv6?: string
  dhcp?: boolean | string
  network?: string
}

export interface NodeRow {
  name?: string
  group?: string
  osimage?: string
  osimagetag?: string
  setupbmc?: boolean | string
  bmcsetup?: string
  status?: string
  tpm_present?: boolean | string
  interfaces?: NodeInventoryInterface[]
  [key: string]: unknown
}

export interface FetchNodesResponse {
  fields?: string[]
  nodes?: NodeRow[]
  error?: string
}

/* ------------------------------------------------------------------ */
/*  Form interface row (Add / Edit / Clone)                           */
/* ------------------------------------------------------------------ */

export interface NodeFormInterface {
  interface: string
  network: string
  ipaddress: string
  mtu: string | number
  dhcp: string
  bond_mode: string
  bond_slaves: string
  vlanid: string | number
  options: string
  vlan_parent: string
  macaddress: string
}

/* ------------------------------------------------------------------ */
/*  Form data (reactive model in NodeFormFields)                      */
/* ------------------------------------------------------------------ */

export interface NodeFormData {
  name: string
  newnodename: string
  groupname: string
  osimage: string
  netboot: string
  setupbmc: string
  bmcsetupname: string
  switchname: string
  switchport: string
  vendor: string
  scripts: string
  roles: string
  domain: string
  unmanaged_bmc_users: string
  asset_tag: string
  cloud_name: string
  kerneloptions: string
  prescript: string
  partscript: string
  postscript: string
  osimagetag: string
  provision_interface: string
  provision_fallback: string
  provision_method: string
  tpm_uuid: string
  tpm_pubkey: string
  tpm_sha256: string
  service: boolean
  comment: string
  interfaces: NodeFormInterface[]
  [key: string]: unknown
}

/* ------------------------------------------------------------------ */
/*  API payload for add / edit / clone forms                          */
/* ------------------------------------------------------------------ */

export interface OptionListPayload {
  options?: string[]
  selected?: string
  [key: string]: unknown
}

export interface NodeFormPayload {
  data?: Partial<NodeFormData> & { [key: string]: unknown }
  group_list?: string[] | OptionListPayload
  groups?: string[]
  groupname_list?: string[]
  /** group name → that group's osimage (for inherit option label). */
  group_osimage_map?: Record<string, string>
  switch_list?: string[] | OptionListPayload
  switchname_list?: string[]
  switches?: string[]
  bmcsetup_list?: string[] | OptionListPayload
  bmcsetupname_list?: string[]
  osimage_list?: string[] | OptionListPayload
  osimage?: string[]
  cloudname_list?: string[]
  cloud_name_list?: string[]
  cloud_list?: string[]
  network_list?: string[] | OptionListPayload
  network?: string[]
  bond_modes?: string[]
  bond_mode_list?: OptionListPayload
  hints?: Record<string, string>
  form_hints?: Record<string, string>
  [key: string]: unknown
}

/* ------------------------------------------------------------------ */
/*  OS push / grab payloads                                           */
/* ------------------------------------------------------------------ */

export interface OsPushGrabPayload {
  osimage_list?: string[] | OptionListPayload
  osimage?: string[]
  data?: { osimage?: string; [key: string]: unknown }
  [key: string]: unknown
}

/* ------------------------------------------------------------------ */
/*  Submit result                                                     */
/* ------------------------------------------------------------------ */

export interface SubmitResult {
  ok: boolean
  status: number
  data: {
    status?: string
    message?: string
    error?: string
    [key: string]: unknown
  }
}

/* ------------------------------------------------------------------ */
/*  IPv4 suggestion utilities                                         */
/* ------------------------------------------------------------------ */

export interface InventoryIpv4Record {
  nodeName: string
  network: string
  ipNum: number
}

export type SuggestIpSuccess = { ok: true; ip: string }
export type SuggestIpFailure = { ok: false; reason: 'network' | 'subnet' | 'full' }
export type SuggestIpResult = SuggestIpSuccess | SuggestIpFailure

export interface SuggestNextFreeIpParams {
  networkName: string
  formInterfaces: Pick<NodeFormInterface, 'ipaddress' | 'network'>[]
  inventoryRecords: InventoryIpv4Record[]
  excludeNodeName?: string
}

/* ------------------------------------------------------------------ */
/*  Column descriptor (inventory table)                               */
/* ------------------------------------------------------------------ */

export interface ColumnDef {
  field: string
  label: string
}
