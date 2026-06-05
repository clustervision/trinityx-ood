export type StatusField = 'power' | 'sel' | 'chassis' | 'redfish'

export interface ControlStatusRow {
  node: string
  power: string
  sel: string
  chassis: string
  redfish: string
  errors?: Partial<Record<Exclude<StatusField, 'redfish'>, string>>
}

export interface StatusToast {
  id: string
  node: string
  field: StatusField
  message: string
}

export interface RequestEnvelope {
  control?: Record<string, unknown>
  request_id?: string
  message?: string
}

export interface StatusSnapshot {
  rows: ControlStatusRow[]
  requestIds: {
    power: string
    sel: string
    chassis: string
  }
  toasts: StatusToast[]
}

export interface BulkStatusResult extends StatusSnapshot {}

export interface SelLogEntry {
  node: string
  text: string
  error?: boolean
  /** When Luna returns one combined log for many nodes. */
  nodes?: string[]
}
