export type SecretEntity = 'group' | 'node'

export interface SecretRecord {
  entity: SecretEntity
  owner: string
  name: string
  path: string
  content: string
}

export interface SecretFormState {
  entity: SecretEntity
  owner: string
  name: string
  path: string
  content: string
}

export interface DaemonEnvelope<T = unknown> {
  status?: boolean
  status_code?: number
  content?: T
  message?: string
}
