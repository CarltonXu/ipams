import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import type { MonitorData, SystemStats, ResourceHistory, ProcessInfo } from '../types/monitor'
import { API_CONFIG } from '../config/api'

export const useMonitorStore = defineStore('monitor', () => {
  // 状态
  const systemStats = ref<SystemStats>({
    cpu_usage: 0,
    memory_usage: 0,
    disk_usage: 0,
    process_count: 0
  })

  const resourceHistory = ref<ResourceHistory>({
    timestamps: [],
    cpu: [],
    memory: [],
    disk: [],
    network_sent: [],
    network_recv: [],
    disk_read: [],
    disk_write: []
  })

  const processes = ref<ProcessInfo[]>([])
  const timeRange = ref<'1h' | '6h' | '24h'>('1h')
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const cpuUsage = computed(() => systemStats.value.cpu_usage)
  const memoryUsage = computed(() => systemStats.value.memory_usage)
  const diskUsage = computed(() => systemStats.value.disk_usage)
  const processCount = computed(() => systemStats.value.process_count)

  const resourceChartData = computed(() => ({
    timestamps: resourceHistory.value.timestamps,
    cpu: resourceHistory.value.cpu,
    memory: resourceHistory.value.memory,
    disk: resourceHistory.value.disk
  }))

  const networkChartData = computed(() => ({
    timestamps: resourceHistory.value.timestamps,
    sent: resourceHistory.value.network_sent,
    recv: resourceHistory.value.network_recv
  }))

  const diskChartData = computed(() => ({
    timestamps: resourceHistory.value.timestamps,
    read: resourceHistory.value.disk_read,
    write: resourceHistory.value.disk_write
  }))

  // 方法
  const fetchMonitorData = async (range: string) => {
    loading.value = true
    error.value = null
    try {
      const response = await axios.get(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.MONITOR.LIST}`, {
        params: {
          time_range: range
        }
      })
      if (response.data.code === 200) {
        const { data } = response.data
        systemStats.value = data.stats
        resourceHistory.value = data.resources.resource_history
        processes.value = data.processes
      } else {
        error.value = response.data.message || '获取监控数据失败'
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取监控数据失败'
    } finally {
      loading.value = false
    }
  }

  const setTimeRange = (range: '1h' | '6h' | '24h') => {
    timeRange.value = range
    fetchMonitorData(range)
  }

  const searchProcesses = (keyword: string) => {
    if (!keyword) return processes.value
    const search = keyword.toLowerCase()
    return processes.value.filter(p => 
      p.name.toLowerCase().includes(search) || 
      p.pid.toString().includes(search)
    )
  }

  // 初始化
  const init = () => {
    fetchMonitorData(timeRange.value)
    // 设置定时刷新
    const timer = setInterval(() => fetchMonitorData(timeRange.value), 10000)
    return () => clearInterval(timer)
  }

  return {
    // 状态
    systemStats,
    resourceHistory,
    processes,
    timeRange,
    loading,
    error,

    // 计算属性
    cpuUsage,
    memoryUsage,
    diskUsage,
    processCount,
    resourceChartData,
    networkChartData,
    diskChartData,

    // 方法
    fetchMonitorData,
    setTimeRange,
    searchProcesses,
    init
  }
})
