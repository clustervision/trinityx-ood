/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_APP_URL: string
  readonly VITE_NODE_BACKEND: string
  readonly VITE_PUBLIC_BASE: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
