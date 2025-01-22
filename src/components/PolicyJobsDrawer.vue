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
            style="width: 120px; margin-right: 12px;"
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
      </el-table>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, watch, computed, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { useScanPolicyStore } from '../stores/scanPolicy'

const props = defineProps<{
  modelValue: boolean
  policyId: string
}>()

const emit = defineEmits(['update:modelValue'])
const { t } = useI18n()
const policyStore = useScanPolicyStore()
const jobs = ref([])
const loading = ref(false)

// 计算抽屉宽度为屏幕宽度的 70%
const drawerWidth = computed(() => {
  return window.innerWidth * 0.7
})

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

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
let refreshTimer: number | null = null

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
    }, refreshInterval.value * 1000)
  }
}

// 监听刷新间隔变化
watch(refreshInterval, () => {
  setupAutoRefresh()
})

// 监听抽屉可见性
watch(visible, (newVal) => {
  if (newVal) {
    fetchJobs()
    setupAutoRefresh()
  } else {
    clearRefreshTimer()
  }
})

// 组件卸载时清理定时器
onUnmounted(() => {
  clearRefreshTimer()
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
</style>