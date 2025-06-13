<template>
  <el-drawer
    v-model="visible"
    :title="t('scan.policy.jobs.title')"
    :size="drawerWidth"
    direction="rtl"
  >
    <template #header>
      <div class="drawer-header">
        <span>{{ t('scan.policy.jobs.title') }}</span>
        <div class="header-controls">
          <el-select
            v-model="refreshInterval"
            size="small"
            style="width: 145px; margin-right: 12px;"
          >
            <el-option
              v-for="item in refreshOptions"
              :key="item.value"
              :label="t(`scan.policy.jobs.refresh.${item.label}`)"
              :value="item.value"
            />
          </el-select>
          
          <el-button
            :loading="loading"
            circle
            @click="fetchJobs"
          >
            <el-icon><Refresh /></el-icon>
          </el-button>
        </div>
      </div>
    </template>

    <el-tabs v-model="activeTab" class="policy-tabs">
      <el-tab-pane :label="t('scan.policy.details.title')" name="details">
        <div v-loading="loading" class="policy-details">
          <el-descriptions :column="1" border>
            <el-descriptions-item :label="t('scan.policy.show.columns.name')">
              {{ policyDetails?.name }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('scan.policy.show.columns.description')">
              {{ policyDetails?.description }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('scan.policy.show.columns.threads')">
              <el-tag size="small" type="info">{{ policyDetails?.threads }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item :label="t('scan.policy.show.columns.status.title')">
              <el-tag :type="getStatusType(policyDetails?.status || '')">
                {{ t(`scan.policy.show.columns.status.${policyDetails?.status || ''}`) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item :label="t('scan.policy.show.columns.createdAt')">
              {{ formatDateTime(policyDetails?.created_at || '') }}
            </el-descriptions-item>
          </el-descriptions>
          <div class="strategies-section">
            <h3>{{ t('scan.policy.schedules') }}</h3>
            <div v-for="(strategy, index) in policyDetails?.strategies" :key="index" class="strategy-item">
              <div class="strategy-header">
                <span class="strategy-label">{{ t('scan.policy.schedules') }} {{ index + 1 }}</span>
              </div>
              <div class="strategy-content">
                <div class="strategy-row">
                  <span class="strategy-field">{{ t('scan.policy.cronExpression') }}:</span>
                  <div class="cron-info">
                    <el-tag size="small" type="info" class="mr-2">
                      {{ strategy.cron }}
                    </el-tag>
                    <el-tooltip
                      :content="parseCronExpression(strategy.cron)"
                      placement="top"
                      effect="light"
                    >
                      <el-icon class="cron-help"><QuestionFilled /></el-icon>
                    </el-tooltip>
                  </div>
                </div>
                <div class="strategy-row">
                  <span class="strategy-field">{{ t('scan.policy.show.columns.startTime') }}:</span>
                  <el-tag size="small" type="warning">{{ formatDateTime(strategy.start_time) }}</el-tag>
                </div>
                <div class="strategy-row">
                  <span class="strategy-field">{{ t('scan.policy.show.columns.subnets') }}:</span>
                  <div class="subnet-tags">
                    <el-tag 
                      v-for="subnetId in strategy.subnet_ids" 
                      :key="subnetId"
                      size="small"
                      type="success"
                      class="subnet-tag"
                    >
                      {{ getSubnetName(policyDetails?.subnets || [], subnetId) }}
                    </el-tag>
                  </div>
                </div>
                <div class="strategy-row">
                  <span class="strategy-field">{{ t('scan.policy.show.columns.scan_type') }}:</span>
                  <div class="scan-params">
                    <el-tag 
                      v-if="strategy.scan_params?.enable_custom_scan_type"
                      size="small"
                      type="warning"
                      class="scan-param-tag"
                    >
                      {{ t(`scan.policy.scanParams.types.${strategy.scan_params.scan_type}.label`) }}
                    </el-tag>
                  </div>
                </div>
                <div class="strategy-row" v-if="strategy.scan_params?.enable_custom_ports">
                  <span class="strategy-field">{{ t('scan.policy.show.columns.scan_params') }}:</span>
                  <div class="scan-params">
                    <el-tag 
                      size="small"
                      type="info"
                      class="scan-param-tag"
                    >
                      {{ t('scan.policy.scanParams.ports') }}: {{ strategy.scan_params.ports }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane :label="t('scan.policy.jobs.title')" name="jobs">
        <div v-loading="loading" class="jobs-table-container">
          <el-table
            :data="jobs"
            border
            style="width: 100%"
          >
            <el-table-column
              prop="id"
              :label="t('scan.policy.jobs.jobId')"
              width="300"
            >
              <template #default="{ row }">
                <el-button
                  type="text"
                  @click="$router.push({ name: 'JobResults', params: { jobId: row.id } })"
                >
                  {{ row.id }}
                </el-button>
              </template>
            </el-table-column>
            <el-table-column
              prop="subnets.name"
              :label="t('scan.policy.jobs.subnet')"
              width="260"
            >
              <template #default="{ row }">
                {{ row.subnets.name }} ({{ row.subnets.subnet }})
              </template>
            </el-table-column>

            <el-table-column
              prop="machines_found"
              :label="t('scan.policy.jobs.machinesFound')"
              width="200"
              align="center"
            />

            <el-table-column
              prop="status"
              :label="t('scan.policy.jobs.status')"
              width="120"
            >
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ t(`scan.policy.show.columns.status.${row.status}`) }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column
              prop="progress"
              :label="t('scan.policy.jobs.progress')"
              width="200"
            >
              <template #default="{ row }">
                <div class="progress-cell">
                  <el-progress 
                    :percentage="row.progress"
                    :status="row.status === 'failed' ? 'exception' : undefined"
                  />
                </div>
              </template>
            </el-table-column>

            <el-table-column
              prop="start_time"
              :label="t('scan.policy.jobs.startTime')"
              width="180"
            >
              <template #default="{ row }">
                {{ formatDateTime(row.start_time) }}
              </template>
            </el-table-column>

            <el-table-column
              prop="end_time"
              :label="t('scan.policy.jobs.endTime')"
              width="180"
            >
              <template #default="{ row }">
                {{ formatDateTime(row.end_time) }}
              </template>
            </el-table-column>

            <el-table-column
              prop="error_message"
              :label="t('scan.policy.jobs.errorMessage')"
              min-width="200"
              show-overflow-tooltip
            >
              <template #default="{ row }">
                <el-tag 
                  v-if="row.error_message"
                  type="danger"
                  effect="dark"
                >
                  {{ row.error_message }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column
              :label="t('scan.policy.jobs.actions')"
              width="120"
              fixed="right"
            >
              <template #default="{ row }">
                <el-button
                  v-if="['pending', 'running'].includes(row.status)"
                  type="danger"
                  size="small"
                  :loading="cancellingJobs[row.id]"
                  @click="handleCancelJob(row)"
                >
                  {{ t('scan.policy.jobs.cancel') }}
                </el-button>
                <el-button
                  v-else
                  type="primary"
                  size="small"
                  @click="$router.push({ name: 'JobResults', params: { jobId: row.id } })"
                >
                  {{ t('scan.policy.jobs.viewResults') }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, watch, computed, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Refresh, QuestionFilled } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { useScanPolicyStore } from '../stores/scanPolicy'
import { useTaskStore } from '../stores/task'

interface PolicyDetails {
  id: string;
  name: string;
  description: string;
  threads: number;
  status: string;
  created_at: string;
  strategies: Array<{
    cron: string;
    start_time: string;
    subnet_ids: string[];
    scan_params: {
      enable_custom_ports: boolean;
      ports: string;
      enable_custom_scan_type: boolean;
      scan_type: string;
    };
  }>;
  subnets: Array<{
    id: string;
    name: string;
    subnet: string;
  }>;
}

interface Job {
  id: string;
  status: string;
  progress: number;
  start_time: string;
  end_time: string;
  error_message?: string;
  machines_found: number;
  subnets: {
    name: string;
    subnet: string;
  };
}

const props = defineProps<{
  modelValue: boolean
  policyId: string
}>()

const emit = defineEmits(['update:modelValue'])
const { t } = useI18n()
const policyStore = useScanPolicyStore()
const taskStore = useTaskStore()
const jobs = ref<Job[]>([])
const loading = ref(false)
const cancellingJobs = ref<Record<string, boolean>>({})
const activeTab = ref('details')
const policyDetails = ref<PolicyDetails | null>(null)

// 计算抽屉宽度为屏幕宽度的 70%
const drawerWidth = computed(() => {
  return window.innerWidth * 0.7
})

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 获取策略详情
const fetchPolicyDetails = async () => {
  try {
    loading.value = true
    const response = await policyStore.fetchPolicies()
    const policy = response.find((p: PolicyDetails) => p.id === props.policyId)
    if (policy) {
      policyDetails.value = {
        id: policy.id,
        name: policy.name,
        description: policy.description,
        threads: policy.threads,
        status: policy.status,
        created_at: policy.created_at,
        strategies: policy.strategies,
        subnets: policy.subnets
      }
    }
  } catch (error) {
    ElMessage.error(t('scan.policy.details.fetchError'))
  } finally {
    loading.value = false
  }
}

// 获取任务列表
const fetchJobs = async () => {
  try {
    loading.value = true
    const response = await policyStore.fetchPolicyJobs(props.policyId)
    jobs.value = response.jobs || []
  } catch (error) {
    ElMessage.error(t('scan.policy.jobs.fetchError'))
    jobs.value = []
  } finally {
    loading.value = false
  }
}

// 获取状态类型
const getStatusType = (status: string) => {
  switch (status) {
    case 'pending':
      return 'warning'
    case 'running':
      return 'primary'
    case 'completed':
      return 'success'
    case 'failed':
      return 'danger'
    default:
      return 'info'
  }
}

// 格式化日期时间
const formatDateTime = (dateStr: string) => {
  return dateStr ? dayjs(dateStr).format('YYYY-MM-DD HH:mm:ss') : '-'
}

// 获取子网名称
const getSubnetName = (subnets: Array<{ id: string; name: string; subnet: string }>, subnetId: string) => {
  const subnet = subnets.find(s => s.id === subnetId)
  return subnet ? `${subnet.name} (${subnet.subnet})` : subnetId
}

// 解析 Cron 表达式
const parseCronExpression = (cron: string): string => {
  const parts = cron.split(' ')
  if (parts.length !== 5) return 'Invalid cron expression'

  const [minute, hour, dayOfMonth, month, dayOfWeek] = parts
  
  let description = ''

  // 解析分钟
  if (minute === '*') {
    description += t('scan.policy.cron.everyMinute')
  } else if (minute.includes('/')) {
    const [, interval] = minute.split('/')
    description += t('scan.policy.cron.everyXMinutes', { interval })
  } else if (minute.includes(',')) {
    const minutes = minute.split(',').map(m => `${m}分`).join('、')
    description += t('scan.policy.cron.atMinutes', { minutes })
  } else if (minute.includes('-')) {
    const [start, end] = minute.split('-')
    description += t('scan.policy.cron.betweenMinutes', { start, end })
  } else {
    description += t('scan.policy.cron.atMinutes', { minutes: `${minute}分` })
  }

  // 解析小时
  if (hour === '*') {
    description += t('scan.policy.cron.everyHour')
  } else if (hour.includes('/')) {
    const [, interval] = hour.split('/')
    description += t('scan.policy.cron.everyXHours', { interval })
  } else if (hour.includes(',')) {
    const hours = hour.split(',').map(h => `${h}点`).join('、')
    description += t('scan.policy.cron.atHours', { hours })
  } else if (hour.includes('-')) {
    const [start, end] = hour.split('-')
    description += t('scan.policy.cron.betweenHours', { start, end })
  } else {
    description += t('scan.policy.cron.atHours', { hours: `${hour}点` })
  }

  // 解析日期
  if (dayOfMonth === '*') {
    description += t('scan.policy.cron.everyDay')
  } else if (dayOfMonth.includes('/')) {
    const [, interval] = dayOfMonth.split('/')
    description += t('scan.policy.cron.everyXDays', { interval })
  } else if (dayOfMonth.includes(',')) {
    const days = dayOfMonth.split(',').map(d => `${d}日`).join('、')
    description += t('scan.policy.cron.atDays', { days })
  } else if (dayOfMonth.includes('-')) {
    const [start, end] = dayOfMonth.split('-')
    description += t('scan.policy.cron.betweenDays', { start, end })
  } else {
    description += t('scan.policy.cron.atDays', { days: `${dayOfMonth}日` })
  }

  // 解析月份
  if (month === '*') {
    description += t('scan.policy.cron.everyMonth')
  } else if (month.includes('/')) {
    const [, interval] = month.split('/')
    description += t('scan.policy.cron.everyXMonths', { interval })
  } else if (month.includes(',')) {
    const months = month.split(',').map(m => `${m}月`).join('、')
    description += t('scan.policy.cron.atMonths', { months })
  } else if (month.includes('-')) {
    const [start, end] = month.split('-')
    description += t('scan.policy.cron.betweenMonths', { start, end })
  } else {
    description += t('scan.policy.cron.atMonths', { months: `${month}月` })
  }

  // 解析星期
  if (dayOfWeek === '*') {
    description += t('scan.policy.cron.everyWeekday')
  } else if (dayOfWeek.includes('/')) {
    const [, interval] = dayOfWeek.split('/')
    description += t('scan.policy.cron.everyXWeeks', { interval })
  } else if (dayOfWeek.includes(',')) {
    const weekDays = dayOfWeek.split(',').map(day => {
      const dayNum = parseInt(day)
      return ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][dayNum]
    })
    description += t('scan.policy.cron.atWeekdays', { weekdays: weekDays.join('、') })
  } else if (dayOfWeek.includes('-')) {
    const [start, end] = dayOfWeek.split('-')
    const startDay = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][parseInt(start)]
    const endDay = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][parseInt(end)]
    description += t('scan.policy.cron.betweenWeekdays', { start: startDay, end: endDay })
  } else {
    const dayNum = parseInt(dayOfWeek)
    const dayName = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][dayNum]
    description += t('scan.policy.cron.atWeekdays', { weekdays: dayName })
  }

  return description
}

// 取消任务
const handleCancelJob = async (job: Job) => {
  try {
    cancellingJobs.value[job.id] = true
    await taskStore.cancelJob(job.id)
    ElMessage.success(t('scan.policy.jobs.cancelSuccess'))
    await fetchJobs()
  } catch (error: any) {
    ElMessage.error(error.message || t('scan.policy.jobs.cancelFailed'))
  } finally {
    cancellingJobs.value[job.id] = false
  }
}

// 添加刷新间隔选项
const refreshOptions = [
  { label: 'off', value: 0 },
  { label: '1s', value: 1 },
  { label: '5s', value: 5 },
  { label: '10s', value: 10 },
  { label: '30s', value: 30 },
  { label: '60s', value: 60 }
]

const refreshInterval = ref(0)
let refreshTimer: ReturnType<typeof setInterval> | null = null

// 清除定时器
const clearRefreshTimer = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// 设置自动刷新
const setupAutoRefresh = () => {
  clearRefreshTimer()
  if (refreshInterval.value > 0) {
    refreshTimer = setInterval(() => {
      fetchJobs()
    }, refreshInterval.value * 3000)
  }
}

// 监听刷新间隔变化
watch(refreshInterval, () => {
  setupAutoRefresh()
})

// 添加后台刷新逻辑
const backgroundRefreshTimer = ref<ReturnType<typeof setInterval> | null>(null)
const hasRunningJobs = computed(() => {
  return jobs.value.some(job => ['pending', 'running'].includes(job.status))
})

// 后台刷新运行中的任务
const refreshRunningJobs = async () => {
  try {
    const response = await taskStore.fetchRunningJobs()
    const runningJobs = response.jobs || []
    // 更新现有任务的状态
    jobs.value = jobs.value.map(job => {
      const updatedJob = runningJobs.find((rj: Job) => rj.id === job.id)
      if (updatedJob) {
        // 如果找到更新的任务，使用新的状态
        return {
          ...job,
          status: updatedJob.status,
          progress: updatedJob.progress,
          machines_found: updatedJob.machines_found,
          updated_at: updatedJob.updated_at,
          end_time: updatedJob.end_time,
          error_message: updatedJob.error_message
        }
      }
      return job
    })
    
    // 如果没有任何运行中的任务，停止后台刷新
    if (!hasRunningJobs.value) {
      clearBackgroundRefresh()
    }
  } catch (error) {
    console.error('Failed to refresh running jobs:', error)
  }
}

// 清除后台刷新定时器
const clearBackgroundRefresh = () => {
  if (backgroundRefreshTimer.value) {
    clearInterval(backgroundRefreshTimer.value)
    backgroundRefreshTimer.value = null
  }
}

// 启动后台刷新
const startBackgroundRefresh = () => {
  clearBackgroundRefresh()
  if (hasRunningJobs.value) {
    backgroundRefreshTimer.value = setInterval(refreshRunningJobs, 3000)
  }
}

// 监听抽屉可见性
watch(visible, (newVal) => {
  if (newVal) {
    fetchPolicyDetails()
    fetchJobs()
    setupAutoRefresh()
    // 检查是否有运行中的任务，如果有则启动后台刷新
    if (hasRunningJobs.value) {
      startBackgroundRefresh()
    }
  } else {
    clearRefreshTimer()
    clearBackgroundRefresh()
  }
})

// 监听任务列表变化
watch(jobs, (newJobs) => {
  if (visible.value && hasRunningJobs.value) {
    startBackgroundRefresh()
  } else {
    clearBackgroundRefresh()
  }
}, { deep: true })

// 组件卸载时清理所有定时器
onUnmounted(() => {
  clearRefreshTimer()
  clearBackgroundRefresh()
})
</script>

<style scoped>
.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-right: 20px;
}

.header-controls {
  display: flex;
  align-items: center;
}

.policy-tabs {
  height: 100%;
}

.policy-details {
  padding: 20px;
}

.strategies-section {
  margin-top: 20px;
}

.strategies-section h3 {
  margin-bottom: 16px;
  color: var(--el-text-color-primary);
  font-size: 16px;
}

.strategy-item {
  background-color: var(--el-fill-color-light);
  border-radius: 4px;
  padding: 16px;
  margin-bottom: 16px;
}

.strategy-header {
  margin-bottom: 12px;
}

.strategy-label {
  font-weight: bold;
  color: var(--el-text-color-primary);
}

.strategy-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.strategy-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.strategy-field {
  min-width: 120px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.subnet-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.subnet-tag {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cron-info {
  display: flex;
  align-items: center;
  gap: 4px;
}

.cron-help {
  color: var(--el-text-color-secondary);
  cursor: help;
  font-size: 14px;
}

.cron-help:hover {
  color: var(--el-color-primary);
}

.scan-params {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.scan-param-tag {
  margin: 2px;
}

.jobs-table-container {
  padding: 20px;
}

.progress-cell {
  padding: 5px 0;
}

:deep(.el-progress-bar__inner) {
  transition: width 0.3s ease;
}

:deep(.el-table) {
  --el-table-border-color: var(--el-border-color-lighter);
}

:deep(.el-tabs__content) {
  flex: 1;
  overflow-y: auto;
}

:deep(.el-descriptions) {
  margin-bottom: 20px;
}

:deep(.el-descriptions__label) {
  width: 120px;
  color: var(--el-text-color-secondary);
}

:deep(.el-descriptions__content) {
  color: var(--el-text-color-primary);
}

:deep(.el-tabs__header) {
  margin: 0;
  padding: 0 20px;
}

:deep(.el-tabs__nav-wrap) {
  padding: 0;
}

:deep(.el-tabs__item) {
  height: 40px;
  line-height: 40px;
}

:deep(.el-drawer.ltr, .el-drawer.rtl) {
  top: 65px !important;
  height: calc(100% - 65px) !important;
}
</style>