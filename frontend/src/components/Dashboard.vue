<template>
  <div ref="Container" class="dashboard">
    <div class="dashboard-header">
      <div class="header-left">
    <h1>{{ t('dashboard.title') }}</h1>
        <p class="subtitle">{{ t('dashboard.subtitle') }}</p>
      </div>
    <div class="header-controls">
        <el-button type="primary" :icon="Refresh" @click="refreshData">
          {{ t('common.refresh') }}
        </el-button>
        <el-select v-model="refreshInterval" :placeholder="t('dashboard.autoRefresh')" style="width: 145px">
          <el-option
            v-for="option in refreshOptions"
            :key="option.value"
            :label="t(`dashboard.refresh.${option.label}`)"
            :value="option.value"
          />
      </el-select>
      </div>
    </div>

    <div ref="refreshContainer" class="dashboard-content">
      <!-- 统计卡片 -->
    <div class="stats-container">
        <el-card class="stat-card" v-for="(stat, key) in stats" :key="key">
        <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="24" :color="getStatColor(key)">
                <component :is="getStatIcon(key)" />
              </el-icon>
            </div>
            <div class="stat-info">
              <h3>{{ t(`dashboard.stats.${key}`) }}</h3>
              <h2>{{ formatStatValue(stat, key) }}</h2>
            </div>
        </div>
      </el-card>
    </div>

    <!-- 系统信息区域 -->
    <el-card class="system-info-section">
      <template #header>
        <div class="card-header">
          <h3>
            <el-icon><Monitor /></el-icon>
            {{ t('dashboard.systemInfo.title') }}
          </h3>
        </div>
      </template>
      <div class="system-info-content">
        <div class="info-item">
          <el-icon><Timer /></el-icon>
          <span class="label">{{ t('dashboard.systemInfo.uptime') }}:</span>
          <span class="value">{{ formatUptime(resources.system_info.uptime) }}</span>
        </div>
        <div class="info-item">
          <el-icon><Platform /></el-icon>
          <span class="label">{{ t('dashboard.systemInfo.platform') }}:</span>
          <span class="value">{{ resources.system_info.platform }}</span>
        </div>
        <template v-for="(value, key) in resources.system_info" :key="key">
          <div class="info-item" v-if="!['platform', 'uptime'].includes(key)">
            <el-icon><InfoFilled /></el-icon>
            <span class="label">{{ t(`dashboard.systemInfo.${key}`) }}:</span>
            <span class="value">{{ value }}</span>
          </div>
        </template>
      </div>
    </el-card>

      <!-- 图表区域 -->
      <div class="charts-container">
        <el-card class="chart-card">
          <template #header>
            <div class="chart-header">
              <h3>{{ t('dashboard.charts.jobStatus') }}</h3>
            </div>
          </template>
          <div ref="jobStatusChartRef" class="chart"></div>
        </el-card>
      </div>

      <!-- 表格区域 -->
      <div class="grid-container">
        <div class="recent-jobs-container">
          <el-card class="recent-jobs-card">
            <template #header>
              <div class="card-header">
            <h3>{{ t('dashboard.recentJobs.title') }}</h3>
                <el-button type="primary" link @click="viewAllJobs">
                  {{ t('dashboard.viewAll') }}
                </el-button>
              </div>
            </template>
            <div class="table-wrapper">
              <el-table 
                :data="recentJobs"
                style="width: 100%"
                :max-height="400"
                :header-cell-style="{ backgroundColor: '#f5f7fa', color: '#333' }"
                stripe
                border
              >
                <el-table-column
                  prop="id"
                  :label="t('dashboard.recentJobs.columns.id')"
                  width="300"
                  align="center"
                >
                  <template #default="{ row }">
                    <el-button link @click="handleJobClick(row)">
                      {{ row.id }}
                    </el-button>
                  </template>
                </el-table-column>
                <el-table-column
                  prop="status"
                  :label="t('dashboard.recentJobs.columns.status')"
                  width="120"
                  align="center"
                >
                  <template #default="scope">
                    <el-tag :type="getJobStatusType(scope.row.status)">
                      {{ t(`dashboard.recentJobs.status.${scope.row.status}`) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column
                  prop="machines_found"
                  :label="t('dashboard.recentJobs.columns.machines_found')"
                  width="150"
                  align="center"
                />
                <el-table-column
                  prop="error_message"
                  :label="t('dashboard.recentJobs.columns.result')"
                  width="220"
                  align="center"
                />
                <el-table-column
                  prop="created_at"
                  :label="t('dashboard.recentJobs.columns.created_at')"
                  width="200"
                  align="center"
                >
                  <template #default="{ row }">
                    {{ formatDateTime(row.created_at) }}
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-card>
        </div>

        <div class="resource-container">
          <el-card class="resource-card">
            <template #header>
              <div class="card-header">
            <h3>{{ t('dashboard.resources.audit') }}</h3>
                <el-button type="primary" link @click="viewAllAudits">
                  {{ t('dashboard.viewAll') }}
                </el-button>
              </div>
            </template>
            <div class="table-wrapper">
              <el-table
                :data="resources.audit_resources"
                style="width: 100%"
                :max-height="400"
                :header-cell-style="{ backgroundColor: '#f5f7fa', color: '#333' }"
                stripe
                border
              >
                <el-table-column
                  prop="id"
                  :label="t('dashboard.resources.columns.id')"
                  width="300"
                  align="center"
                />
                <el-table-column
                  prop="action"
                  :label="t('dashboard.resources.columns.action')"
                  width="160"
                  align="center"
                >
                  <template #default="{ row }">
                    <el-tag :type="getAuditActionType(row.action)">
                      {{ row.action }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column
                  prop="details"
                  :label="t('dashboard.resources.columns.details')"
                  width="200"
                  align="center"
                />
                <el-table-column
                  prop="source_ip"
                  :label="t('dashboard.resources.columns.source_ip')"
                  width="120"
                  align="center"
                />
                <el-table-column
                  prop="created_at"
                  :label="t('dashboard.resources.columns.created_at')"
                  width="200"
                  align="center"
                >
                  <template #default="{ row }">
                    {{ formatDateTime(row.created_at) }}
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDashboardStore } from '../stores/dashboard'
import { useUserStore } from '../stores/user'
import { ElLoading, ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import type { DashboardStats, DashboardResources, RecentJob } from '../stores/dashboard'
import {
  Refresh,
  Monitor,
  Connection,
  Histogram,
  TrendCharts,
  Warning,
  SuccessFilled,
  Platform,
  InfoFilled,
  Timer
} from '@element-plus/icons-vue'
import dayjs from 'dayjs'

const dashboardStore = useDashboardStore()
const userStore = useUserStore()
const { t } = useI18n()
const stats = ref<DashboardStats>({
  total_ips: 0,
  claimed_ips: 0,
  unclaimed_ips: 0,
  total_policies: 0,
  running_jobs: 0,
  failed_jobs: 0,
  successful_jobs: 0,
})
const resources = ref<DashboardResources>({
  audit_resources: [],
  system_info: {
    platform: ''
  }
})
const recentJobs = ref<RecentJob[]>([])
const router = useRouter()

const refreshOptions = [
  { label: 'off', value: 0 },
  { label: '5s', value: 5 },
  { label: '10s', value: 10 },
  { label: '30s', value: 30 },
  { label: '60s', value: 60 },
]

const refreshInterval = ref(0)
let refreshTimer: NodeJS.Timeout | null = null

const refreshContainer = ref<HTMLElement | null>(null)

const resourceChartType = ref('line')
const resourceChartRef = ref<HTMLElement | null>(null)
const jobStatusChartRef = ref<HTMLElement | null>(null)
let jobStatusChart: echarts.ECharts | null = null

const fetchData = async () => {
  const loadingInstance = ElLoading.service({
    target: refreshContainer.value || undefined,
    lock: true,
    text: t('common.loading'),
    background: 'rgba(0, 0, 0, 0.1)',
  })
  try {
    await dashboardStore.fetchDashboardData()
    stats.value = { 
      total_ips: dashboardStore.stats.total_ips,
      claimed_ips: dashboardStore.stats.claimed_ips,
      unclaimed_ips: dashboardStore.stats.unclaimed_ips,
      total_policies: dashboardStore.stats.total_policies,
      running_jobs: dashboardStore.stats.running_jobs,
      failed_jobs: dashboardStore.stats.failed_jobs,
      successful_jobs: dashboardStore.stats.successful_jobs,
    }
    resources.value = {
      audit_resources: dashboardStore.resources.audit_resources,
      system_info: dashboardStore.resources.system_info,
    }
    recentJobs.value = dashboardStore.recent_jobs
  } finally {
    loadingInstance.close()
  }
}

const refreshData = () => {
  fetchData()
}

const setupAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  if (refreshInterval.value > 0) {
    refreshTimer = setInterval(() => {
      fetchData()
    }, refreshInterval.value * 1000)
  }
}

watch(refreshInterval, setupAutoRefresh)

onMounted(async () => {
  try {
    await userStore.fetchCurrentUser()
    await fetchData()
    setupAutoRefresh()
    initJobStatusChart()
    window.addEventListener('resize', handleResize)
  } catch (error) {
    console.error('Failed to initialize dashboard:', error)
    ElMessage.error(t('common.initFailed'))
  }
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  window.removeEventListener('resize', handleResize)
  jobStatusChart?.dispose()
})

const handleJobClick = (row: RecentJob) => {
  // 检查用户权限
  const isAdmin = userStore.isAdmin
  const isOwner = row.user_id === userStore.currentUser?.id

  console.log('User store state:', {
    currentUser: userStore.currentUser,
    isAdmin: userStore.isAdmin,
    rowUserId: row.user_id
  })

  if (!isAdmin && !isOwner) {
    ElMessage.error(t('auth.message.noPermisstions'))
    return
  }

  // 有权限，跳转到结果页面
  router.push({ name: 'JobResults', params: { jobId: row.id } })
}

// 获取统计图标
const getStatIcon = (key: string) => {
  const iconMap: Record<string, any> = {
    total_ips: Monitor,
    claimed_ips: Connection,
    unclaimed_ips: Warning,
    total_policies: Histogram,
    running_jobs: TrendCharts,
    failed_jobs: Warning,
    successful_jobs: SuccessFilled,
  }
  return iconMap[key] || Monitor
}

// 获取统计颜色
const getStatColor = (key: string) => {
  const colorMap: Record<string, string> = {
    total_ips: '#409EFF',
    claimed_ips: '#67C23A',
    unclaimed_ips: '#E6A23C',
    user_claimed_ips: '#909399',
    total_policies: '#F56C6C',
    running_jobs: '#409EFF',
    failed_jobs: '#F56C6C',
    successful_jobs: '#67C23A',
  }
  return colorMap[key] || '#909399'
}

// 格式化统计值
const formatStatValue = (value: any, key: string) => {
  if (key.includes('usage')) {
    return `${value}%`
  }
  return value
}

// 格式化日期时间
const formatDateTime = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

// 获取任务状态类型
const getJobStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    completed: 'success',
    running: 'primary',
    failed: 'danger',
    pending: 'warning'
  }
  return typeMap[status] || 'info'
}

// 获取审计操作类型
const getAuditActionType = (action: string) => {
  const typeMap: Record<string, string> = {
    create: 'success',
    update: 'warning',
    delete: 'danger',
    login: 'info'
  }
  return typeMap[action.toLowerCase()] || 'info'
}


// 初始化任务状态图表
const initJobStatusChart = () => {
  nextTick(() => {
    if (!jobStatusChartRef.value) return

    if (!jobStatusChart) {
      jobStatusChart = echarts.init(jobStatusChartRef.value)
    }

    const option = {
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [
        {
          name: t('dashboard.charts.jobStatus'),
          type: 'pie',
          radius: '50%',
          data: [
            { 
              value: stats.value.successful_jobs || 0, 
              name: t('dashboard.recentJobs.status.completed'),
              itemStyle: { color: '#67C23A' }
            },
            { 
              value: stats.value.running_jobs || 0, 
              name: t('dashboard.recentJobs.status.running'),
              itemStyle: { color: '#409EFF' }
            },
            { 
              value: stats.value.failed_jobs || 0, 
              name: t('dashboard.recentJobs.status.failed'),
              itemStyle: { color: '#F56C6C' }
            }
          ],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    }

    jobStatusChart.setOption(option)
  })
}

// 监听窗口大小变化
const handleResize = () => {
  jobStatusChart?.resize()
}

watch(() => stats.value, () => {
  initJobStatusChart()
}, { deep: true })

// 查看所有任务
const viewAllJobs = () => {
  router.push('/tasks')
}

// 查看所有审计记录
const viewAllAudits = () => {
  router.push('/audits')
}

// 格式化运行时间
const formatUptime = (uptime: { days: number; hours: number; minutes: number }) => {
  const parts = []
  if (uptime?.days > 0) {
    parts.push(`${uptime.days} ${t('dashboard.systemInfo.days')}`)
  }
  if (uptime?.hours > 0) {
    parts.push(`${uptime.hours} ${t('dashboard.systemInfo.hours')}`)
  }
  if (uptime?.minutes > 0) {
    parts.push(`${uptime.minutes} ${t('dashboard.systemInfo.minutes')}`)
  }
  return parts.join(' ')
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
  background-color: var(--el-bg-color-page);
  min-height: 100vh;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  flex-direction: column;
}

.header-left h1 {
  margin: 0;
  font-size: 24px;
  color: var(--el-text-color-primary);
}

.subtitle {
  margin: 8px 0 0;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.header-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background-color: var(--el-color-primary-light-9);
}

.stat-info {
  flex: 1;
}

.stat-info h3 {
  margin: 0;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.stat-info h2 {
  margin: 8px 0 0;
  font-size: 24px;
  color: var(--el-text-color-primary);
}

.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  height: 400px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-header h3 {
  margin: 0;
  font-size: 16px;
  color: var(--el-text-color-primary);
}

.chart {
  height: 320px;
}

.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  color: var(--el-text-color-primary);
}

.table-wrapper {
  margin-top: 16px;
}

@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .header-controls {
    width: 100%;
  }

  .charts-container {
    grid-template-columns: 1fr;
  }

  .grid-container {
    grid-template-columns: 1fr;
  }
}

.system-info-section {
  margin: 24px 0;
}

.system-info-section :deep(.el-card__header) {
  padding: 12px 20px;
}

.system-info-section .card-header h3 {
  margin: 0;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--el-text-color-primary);
}

.system-info-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 12px;
  padding: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background-color: var(--el-bg-color-page);
  border-radius: 3px;
  gap: 8px;
}

.info-item .el-icon {
  font-size: 16px;
  color: var(--el-color-primary);
}

.info-item .label {
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-right: 4px;
  min-width: 100px;
  white-space: nowrap;
}

.info-item .value {
  color: var(--el-text-color-regular);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 768px) {
  .system-info-content {
    grid-template-columns: 1fr;
  }
  
  .info-item {
    padding: 6px 10px;
  }
  
  .info-item .label {
    min-width: 80px;
  }
}
</style> 