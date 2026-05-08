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
