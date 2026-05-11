import axios from 'axios'
const app_url = window.APP_URL || import.meta.env.VITE_APP_URL;

const EDITOR_FIELDS = [
  'options',
  'content',
  'comment',
  'prescript',
  'partscript',
  'postscript',
  'grab_filesystems',
  'grab_exclude',
  'kerneloptions',
] as const
const EDITOR_FIELD_SET = new Set<string>(EDITOR_FIELDS)

function b64EncodeUtf8(value: string): string {
  const bytes = new TextEncoder().encode(value)
  let bin = ''
  bytes.forEach((b) => {
    bin += String.fromCharCode(b)
  })
  return btoa(bin)
}

function b64DecodeUtf8(value: string): string {
  const bin = atob(value)
  const bytes = new Uint8Array(bin.length)
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i)
  return new TextDecoder().decode(bytes)
}

function safeDecodeIfPossible(value: string): string {
  const trimmed = value.trim()
  if (!trimmed) return value
  try {
    const decoded = b64DecodeUtf8(trimmed)
    const reEncoded = b64EncodeUtf8(decoded).replace(/=+$/, '')
    if (reEncoded === trimmed.replace(/=+$/, '')) return decoded
  } catch {
    // keep original value
  }
  return value
}

function transformEditorFieldsDeep(payload: unknown, mode: 'encode' | 'decode'): unknown {
  if (Array.isArray(payload)) return payload.map((item) => transformEditorFieldsDeep(item, mode))
  if (!payload || typeof payload !== 'object') return payload

  const input = payload as Record<string, unknown>
  const out: Record<string, unknown> = {}
  for (const [key, value] of Object.entries(input)) {
    if (EDITOR_FIELD_SET.has(key) && typeof value === 'string') {
      if (mode === 'encode') {
        out[key] = value.length ? b64EncodeUtf8(value) : value
      } else {
        out[key] = safeDecodeIfPossible(value)
      }
    } else {
      out[key] = transformEditorFieldsDeep(value, mode)
    }
  }
  return out
}

function encodeFormDataEditorFields(fd: FormData): FormData {
  const next = new FormData()
  for (const [key, value] of fd.entries()) {
    if (EDITOR_FIELD_SET.has(key) && typeof value === 'string' && value.length > 0) {
      next.append(key, b64EncodeUtf8(value))
    } else {
      next.append(key, value)
    }
  }
  return next
}

export const apiClient = axios.create({
  baseURL: String(app_url).replace(/\/$/, ''),
  headers: {
    Accept: 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
  },
})

apiClient.interceptors.request.use((config) => {
  const data = config.data
  if (!data) return config

  if (data instanceof FormData) {
    config.data = encodeFormDataEditorFields(data)
    return config
  }

  if (typeof data === 'object') {
    config.data = transformEditorFieldsDeep(data, 'encode')
  }

  return config
})

apiClient.interceptors.response.use(
  (response) => {
    if (response?.data && typeof response.data === 'object') {
      response.data = transformEditorFieldsDeep(response.data, 'decode')
    }
    return response
  },
  (error) => {
    const message =
      error?.response?.data?.message ||
      error?.response?.data?.error ||
      error.message

    return Promise.reject(new Error(message))
  }
)
