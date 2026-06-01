export interface ControlStatusRow {
  node: string
  power: string
  sel: string
  chassis: string
}

export interface RequestEnvelope {
  control?: Record<string, unknown>
  request_id?: string
  message?: string
}

export interface BulkStatusResult {
  rows: ControlStatusRow[]
  requestIds: {
    power: string
    sel: string
    chassis: string
  }
}
