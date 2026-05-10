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
