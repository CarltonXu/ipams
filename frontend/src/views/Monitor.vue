<template>
  <div class="monitor-container">
    <!-- 系统概览卡片 -->
    <el-row :gutter="20" class="mb-4">
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>CPU 使用率</span>
              <el-tooltip content="CPU核心数: {{ systemStats.cpu_count }}" placement="top">
                <el-icon><InfoFilled /></el-icon>
              </el-tooltip>
            </div>
          </template>
          <div class="metric-value">
            <span class="value">{{ systemStats.cpu_usage }}%</span>
            <div class="sub-metrics">
              <div>1分钟负载: {{ systemStats.load_avg_1min.toFixed(2) }}</div>
              <div>5分钟负载: {{ systemStats.load_avg_5min.toFixed(2) }}</div>
              <div>15分钟负载: {{ systemStats.load_avg_15min.toFixed(2) }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>内存使用率</span>
            </div>
          </template>
          <div class="metric-value">
            <span class="value">{{ systemStats.memory_usage }}%</span>
            <div class="sub-metrics">
              <div>总内存: {{ formatBytes(systemStats.memory_total) }}</div>
              <div>已用内存: {{ formatBytes(systemStats.memory_used) }}</div>
              <div>空闲内存: {{ formatBytes(systemStats.memory_free) }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>磁盘使用率</span>
            </div>
          </template>
          <div class="metric-value">
            <span class="value">{{ systemStats.disk_usage }}%</span>
            <div class="sub-metrics">
              <div v-for="partition in diskInfo.partitions" :key="partition.device">
                {{ partition.mountpoint }}: {{ partition.usage }}%
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>进程数</span>
            </div>
          </template>
          <div class="metric-value">
            <span class="value">{{ systemStats.process_count }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 资源使用趋势图 -->
    <el-row :gutter="20" class="mb-4">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>资源使用趋势</span>
              <el-radio-group v-model="timeRange" size="small" @change="handleTimeRangeChange">
                <el-radio-button label="1h">1小时</el-radio-button>
                <el-radio-button label="6h">6小时</el-radio-button>
                <el-radio-button label="24h">24小时</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-container">
            <v-chart class="chart" :option="resourceChartOption" autoresize />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 网络和磁盘监控 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>网络流量</span>
              <el-select v-model="selectedInterface" size="small" style="width: 150px">
                <el-option
                  v-for="iface in networkInfo.interfaces"
                  :key="iface.name"
                  :label="iface.name"
                  :value="iface.name"
                />
              </el-select>
            </div>
          </template>
          <div class="chart-container">
            <v-chart class="chart" :option="networkChartOption" autoresize />
          </div>
          <div class="network-stats" v-if="selectedInterface">
            <div class="stat-item">
              <span>发送速率:</span>
              <span>{{ formatNetworkSpeed(currentNetworkStats?.bytes_sent ?? 0) }}</span>
            </div>
            <div class="stat-item">
              <span>接收速率:</span>
              <span>{{ formatNetworkSpeed(currentNetworkStats?.bytes_recv ?? 0) }}</span>
            </div>
            <div class="stat-item">
              <span>错误数:</span>
              <span>{{ (currentNetworkStats?.errin ?? 0) + (currentNetworkStats?.errout ?? 0) }}</span>
            </div>
            <div class="stat-item">
              <span>丢包数:</span>
              <span>{{ (currentNetworkStats?.dropin ?? 0) + (currentNetworkStats?.dropout ?? 0) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>磁盘IO</span>
              <el-select v-model="selectedDisk" size="small" style="width: 150px">
                <el-option
                  v-for="disk in diskInfo.partitions"
                  :key="disk.device"
                  :label="disk.mountpoint"
                  :value="disk.device"
                />
              </el-select>
            </div>
          </template>
          <div class="chart-container">
            <v-chart class="chart" :option="diskChartOption" autoresize />
          </div>
          <div class="disk-stats" v-if="selectedDisk">
            <div class="stat-item">
              <span>读取速率:</span>
              <span>{{ formatDiskSpeed(currentDiskStats?.read_bytes ?? 0) }}</span>
            </div>
            <div class="stat-item">
              <span>写入速率:</span>
              <span>{{ formatDiskSpeed(currentDiskStats?.write_bytes ?? 0) }}</span>
            </div>
            <div class="stat-item">
              <span>IOPS:</span>
              <span>{{ (currentDiskStats?.read_count ?? 0) + (currentDiskStats?.write_count ?? 0) }}/s</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 进程列表 -->
    <el-row :gutter="20" class="mt-4">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>进程列表</span>
              <el-input
                v-model="processSearch"
                placeholder="搜索进程"
                style="width: 200px"
                clearable
              />
            </div>
          </template>
          <el-table :data="filteredProcesses" style="width: 100%" height="400">
            <el-table-column prop="pid" label="PID" width="80" />
            <el-table-column prop="name" label="进程名" />
            <el-table-column prop="cpu_percent" label="CPU使用率" width="100">
              <template #default="scope">
                {{ scope.row.cpu_percent.toFixed(1) }}%
              </template>
            </el-table-column>
            <el-table-column prop="memory_percent" label="内存使用率" width="100">
              <template #default="scope">
                {{ scope.row.memory_percent.toFixed(1) }}%
              </template>
            </el-table-column>
            <el-table-column prop="memory_rss" label="物理内存" width="120">
              <template #default="scope">
                {{ formatBytes(scope.row.memory_rss) }}
              </template>
            </el-table-column>
            <el-table-column prop="memory_vms" label="虚拟内存" width="120">
              <template #default="scope">
                {{ formatBytes(scope.row.memory_vms) }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100" />
            <el-table-column prop="num_threads" label="线程数" width="100" />
            <el-table-column prop="create_time" label="创建时间" width="180" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted, watch } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'
import { useMonitorStore } from '../stores/monitor'
import { ElMessage } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'

// 注册 ECharts 组件
use([
  CanvasRenderer,
  LineChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent,
])

const monitorStore = useMonitorStore()

// 新结构：快照数据
const systemStats = computed(() => monitorStore.systemStats)
const processes = computed(() => monitorStore.processes)
const networkInfo = computed(() => monitorStore.networkInfo)
const diskInfo = computed(() => monitorStore.diskInfo)
const timeRange = computed(() => monitorStore.timeRange)
const loading = computed(() => monitorStore.loading)
const error = computed(() => monitorStore.error)

// 新结构：趋势数据
const cpuTrend = computed(() => monitorStore.cpuTrend)
const memoryTrend = computed(() => monitorStore.memoryTrend)
const diskTrend = computed(() => monitorStore.diskTrend)
const networkTrend = computed(() => monitorStore.networkTrend)
const processTrend = computed(() => monitorStore.processTrend)

// 选中的网络接口和磁盘
const selectedInterface = ref('')
const selectedDisk = ref('')

const currentNetworkStats = computed(() => {
  if (!selectedInterface.value) return null
  return networkInfo.value.interfaces.find(i => i.name === selectedInterface.value) || null
})

const currentDiskStats = computed(() => {
  if (!selectedDisk.value) return null
  return diskInfo.value.partitions.find(d => d.device === selectedDisk.value) || null
})

const formatBytes = (bytes: number) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
const formatNetworkSpeed = (bytes: number) => formatBytes(bytes) + '/s'
const formatDiskSpeed = (bytes: number) => formatBytes(bytes) + '/s'

// 资源趋势图（CPU/内存）
const resourceChartOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'cross', label: { backgroundColor: '#6a7985' } } },
  legend: { data: ['CPU', '内存'] },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: { type: 'category', boundaryGap: false, data: cpuTrend.value.timestamps },
  yAxis: { type: 'value', axisLabel: { formatter: '{value}%' } },
  series: [
    { name: 'CPU', type: 'line', data: cpuTrend.value.cpu, smooth: true, areaStyle: {} },
    { name: '内存', type: 'line', data: memoryTrend.value.memory, smooth: true, areaStyle: {} }
  ]
}))

// 网络趋势图
const networkChartOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'cross', label: { backgroundColor: '#6a7985' } } },
  legend: { data: ['发送', '接收'] },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: { type: 'category', boundaryGap: false, data: networkTrend.value.timestamps },
  yAxis: { type: 'value', axisLabel: { formatter: (value: number) => formatBytes(value) + '/s' } },
  series: [
    { name: '发送', type: 'line', data: networkTrend.value.network_sent, smooth: true, areaStyle: {} },
    { name: '接收', type: 'line', data: networkTrend.value.network_recv, smooth: true, areaStyle: {} }
  ]
}))

// 磁盘趋势图
const diskChartOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'cross', label: { backgroundColor: '#6a7985' } } },
  legend: { data: ['读取', '写入', 'IOPS'] },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: { type: 'category', boundaryGap: false, data: diskTrend.value.timestamps },
  yAxis: { type: 'value', axisLabel: { formatter: (value: number) => formatBytes(value) + '/s' } },
  series: [
    { name: '读取', type: 'line', data: diskTrend.value.disk_read, smooth: true, areaStyle: {} },
    { name: '写入', type: 'line', data: diskTrend.value.disk_write, smooth: true, areaStyle: {} },
    { name: 'IOPS', type: 'line', data: diskTrend.value.disk_iops, smooth: true, areaStyle: {} }
  ]
}))

// 进程趋势图（可选：进程数/线程数）
const processChartOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'cross', label: { backgroundColor: '#6a7985' } } },
  legend: { data: ['进程数', '线程数'] },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: { type: 'category', boundaryGap: false, data: processTrend.value.timestamps },
  yAxis: { type: 'value' },
  series: [
    { name: '进程数', type: 'line', data: processTrend.value.process_count, smooth: true, areaStyle: {} },
    { name: '线程数', type: 'line', data: processTrend.value.thread_count, smooth: true, areaStyle: {} }
  ]
}))

const handleTimeRangeChange = (range: '1h' | '6h' | '24h') => {
  monitorStore.setTimeRange(range)
}

const processSearch = ref('')
const filteredProcesses = computed(() => {
  if (!processSearch.value) return processes.value
  const search = processSearch.value.toLowerCase()
  return processes.value.filter(p => 
    p.name.toLowerCase().includes(search) ||
    p.pid.toString().includes(search)
  )
})

onMounted(() => {
  const cleanup = monitorStore.init()
  onUnmounted(cleanup)
})

watch(error, (newError) => {
  if (newError) {
    ElMessage.error(newError)
  }
})
</script>

<style scoped>
.monitor-container {
  padding: 20px;
}

.mb-4 {
  margin-bottom: 20px;
}

.mt-4 {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-value {
  text-align: center;
  padding: 20px 0;
}

.metric-value .value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}

.sub-metrics {
  margin-top: 10px;
  font-size: 12px;
  color: #666;
}

.chart-container {
  height: 300px;
}

.chart {
  height: 100%;
}

.network-stats,
.disk-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  padding: 10px;
  margin-top: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px;
  font-size: 12px;
}

.stat-item span:first-child {
  color: #666;
}

.stat-item span:last-child {
  font-weight: bold;
  color: #409EFF;
}
</style> 