/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_AMAP_KEY: string
  readonly VITE_AMAP_SECURITY_JS_CODE?: string
  readonly VITE_AMAP_SERVICE_HOST?: string
  readonly VITE_API_BASE_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}