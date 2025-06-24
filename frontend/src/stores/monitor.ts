import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'
import { API_CONFIG } from '../config/api'

interface SystemStats {
  cpu_usage: number
  memory_usage: number
  process_count: number
  cpu_count: number
  disk_usage: number
  memory_total: number
  memory_used: number
  memory_free: number
  load_avg_1min: number
  load_avg_5min: number
  load_avg_15min: number
}

interface CpuTrend {
  timestamps: string[]
  cpu: number[]
}

interface MemoryTrend {
  timestamps: string[]
  memory: number[]
}

interface DiskTrend {
  timestamps: string[]
  disk_read: number[]
  disk_write: number[]
  disk_iops: number[]
}

interface NetworkTrend {
  timestamps: string[]
  network_sent: number[]
  network_recv: number[]
}

interface Process {
  pid: number
  name: string
  cpu_percent: number
  memory_percent: number
  memory_rss: number
  memory_vms: number
  status: string
  num_threads: number
  create_time: string
}

interface NetworkInterface {
  name: string
  bytes_sent: number
  bytes_recv: number
  packets_sent: number
  packets_recv: number
  errin: number
  errout: number
  dropin: number
  dropout: number
  is_up: boolean
  speed: number
  mtu: number
}

interface DiskPartition {
  device: string
  mountpoint: string
  total: number
  used: number
  free: number
  usage: number
  read_bytes: number
  write_bytes: number
  read_count: number
  write_count: number
  read_time: number
  write_time: number
  is_removable: boolean
  fstype: string
}

export const useMonitorStore = defineStore('monitor', () => {
  const systemStats = ref<SystemStats>({
    cpu_usage: 0,
    memory_usage: 0,
    disk_usage: 0,
    process_count: 0,
    cpu_count: 0,
    memory_total: 0,
    memory_used: 0,
    memory_free: 0,
    load_avg_1min: 0,
    load_avg_5min: 0,
    load_avg_15min: 0
  })

  const cpuTrend = ref<CpuTrend>({ timestamps: [], cpu: [] })
  const memoryTrend = ref<MemoryTrend>({ timestamps: [], memory: [] })
  const diskTrend = ref<DiskTrend>({ timestamps: [], disk_read: [], disk_write: [], disk_iops: [] })
  const networkTrend = ref<NetworkTrend>({ timestamps: [], network_sent: [], network_recv: [] })

  const processes = ref<Process[]>([])
  const timeRange = ref<'1h' | '6h' | '24h'>('1h')
  const loading = ref(false)
  const error = ref<string | null>(null)
  const networkInfo = ref<{ interfaces: NetworkInterface[] }>({ interfaces: [] })
  const diskInfo = ref<{ partitions: DiskPartition[] }>({ partitions: [] })

  let pollInterval: number | null = null

  const fetchMonitorData = async () => {
    try {
      loading.value = true
      error.value = null
      const response = await axios.get(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.MONITOR.LIST}`, {
        params: { time_range: timeRange.value }
      })
      if (response.data.code === 200) {
        const data = response.data.data
        cpuTrend.value = data.cpu_trend
        memoryTrend.value = data.memory_trend
        diskTrend.value = data.disk_trend
        networkTrend.value = data.network_trend
        systemStats.value = data.stats
        diskInfo.value = data.disk
        networkInfo.value = data.network
        processes.value = data.processes
      } else {
        error.value = response.data.message || '获取监控数据失败'
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : '获取监控数据失败'
    } finally {
      loading.value = false
    }
  }

  const setTimeRange = (range: '1h' | '6h' | '24h') => {
    timeRange.value = range
    fetchMonitorData()
  }

  const init = () => {
    fetchMonitorData()
    pollInterval = window.setInterval(fetchMonitorData, 5000)
    return () => {
      if (pollInterval) {
        clearInterval(pollInterval)
      }
    }
  }

  return {
    systemStats,
    cpuTrend,
    memoryTrend,
    diskTrend,
    networkTrend,
    processes,
    timeRange,
    loading,
    error,
    networkInfo,
    diskInfo,
    setTimeRange,
    init
  }
})
