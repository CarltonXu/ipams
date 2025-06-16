export interface SystemStats {
  cpu_usage: number
  memory_usage: number
  disk_usage: number
  process_count: number
}

export interface ResourceHistory {
  timestamps: string[]
  cpu: number[]
  memory: number[]
  disk: number[]
  network_sent: number[]
  network_recv: number[]
  disk_read: number[]
  disk_write: number[]
}

export interface ProcessInfo {
  pid: number
  name: string
  cpu_percent: number
  memory_percent: number
  status: string
  num_threads: number
}

export interface MonitorData {
  stats: SystemStats
  resources: {
    resource_history: ResourceHistory
  }
  processes: ProcessInfo[]
}

export interface MonitorResponse {
  code: number
  message?: string
  data: MonitorData
} 