/// <reference types="vite/client" />

interface ImportMetaEnv {
  // Proxy API 配置
  readonly VITE_API_BASE_URL: string
  
  // 应用信息
  readonly VITE_APP_TITLE: string
  readonly VITE_APP_DESCRIPTION: string

  // 文件上传配置
  readonly VITE_UPLOAD_BASE_URL: string
  readonly VITE_MAX_UPLOAD_SIZE: string
  readonly VITE_ALLOWED_FILE_TYPES: string
  
  // 服务器配置
  readonly VITE_SERVER_PORT: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
} 