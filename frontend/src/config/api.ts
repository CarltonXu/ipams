// API 配置
export const API_CONFIG = {
  // API 基础路径
  BASE_URL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  
  // API 版本
  VERSION: 'v1',
  API_PREFIX: 'api',
  
  // 完整的基础 URL
  get BASE_API_URL() {
    return this.BASE_URL
  },
  
  // 各模块的 API 路径
  ENDPOINTS: {
    AUTH: {
      LOGIN: '/auth/login',
      REGISTER: '/auth/register',
      LOGOUT: '/auth/logout',
      REFRESH: '/auth/refresh',
      CAPTCHA: '/auth/captcha'
    },
    USER: {
      LIST: '/user',
      LIST_BY_FILTER: '/user',
      ME: '/user/me',
      CREATE: '/user',
      BATCH_DELETE: '/user/batch-delete',
      AVATAR: '/user/avatar',
      PROFILE: '/user/profile',
      CHANGE_PASSWORD: '/user/change-password',
      LIST_IPS: '/user/check-ips',
      LIST_BY_ID: (id: string) => `/user/${id}`,
      UPDATE: (id: string) => `/user/${id}`,
      DELETE: (id: string) => `/user/${id}`,
      UPDATE_STATUS: (id: string) => `/user/${id}/status`,
    },
    DASHBOARD: {
      LIST: '/dashboard',
    },
    IP: {
      LIST: '/ip',
      CLAIM: (id: string) => `/ip/${id}/claim`,
      RELEASE: (id: string) => `/ip/${id}/release`,
      UPDATE: (id: string) => `/ip/${id}`
    },
    TASK: {
      LIST: '/task',
      SUBMIT: '/task',
      JOBS: (id: string) => `/task/${id}`,
      PROGRESS: (id: string) => `/task/${id}/progress`,
      JOB_CANCEL: (id: string) => `/task/${id}/cancel`,
      JOB_RESULTS: (id: string) => `/task/${id}/results`, 
    },
    POLICY: {
      LIST: '/policy',
      CREATE: '/policy',
      UPDATE: (id: string) => `/policy/${id}`,
      DELETE: (id: string) => `/policy/${id}`,
      JOBS: (id: string) => `/policy/${id}/jobs`,
      SCHEDULER_JOBS: '/policy/scheduler/jobs',
      UPDATE_STATUS: (id: string) => `/policy/${id}/status`,
    },
    NOTIFICATION: {
      CONFIG: '/notification/config',
      HISTORY: '/notification/history',
      MARK_READ: (id: string) => `/notification/${id}/read`,
      MARK_ALL_READ: '/notification/read-all',
      DELETE: (id: string) => `/notification/${id}`,
      CLEAR_ALL: '/notification/clear-all',
      TEST: '/notification/test',
      UNREAD_COUNT: '/notification/unread-count'
    },
    MONITOR: {
      LIST: '/monitor'
    }
  }
} 