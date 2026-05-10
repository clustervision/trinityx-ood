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
