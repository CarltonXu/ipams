<template>
  <div class="monitor-container">
    <!-- 系统概览卡片 -->
    <el-row :gutter="20" class="mb-4">
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>CPU 使用率</span>
            </div>
          </template>
          <div class="metric-value">
            <span class="value">{{ systemStats.cpu_usage }}%</span>
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
            </div>
          </template>
          <div class="chart-container">
            <v-chart class="chart" :option="networkChartOption" autoresize />
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>磁盘IO</span>
            </div>
          </template>
          <div class="chart-container">
            <v-chart class="chart" :option="diskChartOption" autoresize />
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
            <el-table-column prop="status" label="状态" width="100" />
            <el-table-column prop="num_threads" label="线程数" width="100" />
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

// 注册 ECharts 组件
use([
  CanvasRenderer,
  LineChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent,
])

// 在 setup 中
const monitorStore = useMonitorStore()

// 使用 store 中的状态
const systemStats = computed(() => monitorStore.systemStats)
const resourceHistory = computed(() => monitorStore.resourceHistory)
const processes = computed(() => monitorStore.processes)
const timeRange = computed(() => monitorStore.timeRange)
const loading = computed(() => monitorStore.loading)
const error = computed(() => monitorStore.error)

// 使用 store 中的计算属性
const resourceChartData = computed(() => monitorStore.resourceChartData)
const networkChartData = computed(() => monitorStore.networkChartData)
const diskChartData = computed(() => monitorStore.diskChartData)

// 图表配置
const resourceChartOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'cross',
      label: {
        backgroundColor: '#6a7985'
      }
    }
  },
  legend: {
    data: ['CPU', '内存', '磁盘']
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: resourceHistory.value.timestamps
  },
  yAxis: {
    type: 'value',
    axisLabel: {
      formatter: '{value}%'
    }
  },
  series: [
    {
      name: 'CPU',
      type: 'line',
      data: resourceHistory.value.cpu,
      smooth: true,
      areaStyle: {}
    },
    {
      name: '内存',
      type: 'line',
      data: resourceHistory.value.memory,
      smooth: true,
      areaStyle: {}
    },
    {
      name: '磁盘',
      type: 'line',
      data: resourceHistory.value.disk,
      smooth: true,
      areaStyle: {}
    }
  ]
}))

const networkChartOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'cross',
      label: {
        backgroundColor: '#6a7985'
      }
    }
  },
  legend: {
    data: ['发送', '接收']
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: resourceHistory.value.timestamps
  },
  yAxis: {
    type: 'value',
    axisLabel: {
      formatter: (value) => {
        return (value / 1024 / 1024).toFixed(2) + ' MB/s'
      }
    }
  },
  series: [
    {
      name: '发送',
      type: 'line',
      data: resourceHistory.value.network_sent,
      smooth: true,
      areaStyle: {}
    },
    {
      name: '接收',
      type: 'line',
      data: resourceHistory.value.network_recv,
      smooth: true,
      areaStyle: {}
    }
  ]
}))

const diskChartOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'cross',
      label: {
        backgroundColor: '#6a7985'
      }
    }
  },
  legend: {
    data: ['读取', '写入']
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: resourceHistory.value.timestamps
  },
  yAxis: {
    type: 'value',
    axisLabel: {
      formatter: (value) => {
        return (value / 1024 / 1024).toFixed(2) + ' MB/s'
      }
    }
  },
  series: [
    {
      name: '读取',
      type: 'line',
      data: resourceHistory.value.disk_read,
      smooth: true,
      areaStyle: {}
    },
    {
      name: '写入',
      type: 'line',
      data: resourceHistory.value.disk_write,
      smooth: true,
      areaStyle: {}
    }
  ]
}))

// 处理时间范围变化
const handleTimeRangeChange = (range: '1h' | '6h' | '24h') => {
  monitorStore.setTimeRange(range)
}

// 处理进程搜索
const processSearch = ref('')
const filteredProcesses = computed(() => monitorStore.searchProcesses(processSearch.value))

// 初始化
onMounted(() => {
  const cleanup = monitorStore.init()
  onUnmounted(cleanup)
})

// 错误提示
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

.chart-container {
  height: 300px;
}

.chart {
  height: 100%;
}
</style> 