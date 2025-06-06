<template>
  <div ref="Container" class="dashboard">
    <h1>{{ t('dashboard.title') }}</h1>
    <div class="header-controls">
      <el-button @click="refreshData">{{ t('common.refresh') }}</el-button>
      <el-select v-model="refreshInterval" placeholder="Auto Refresh">
        <el-option v-for="option in refreshOptions" :key="option.value" :label="t(`dashboard.refresh.${option.label}`)" :value="option.value" />
      </el-select>
    </div>
    <div ref="refreshContainer">
    <div class="stats-container">
      <el-card class="stat-card" v-for="(value, key) in stats" :key="key">
        <div class="stat-content">
          <p>{{ t(`dashboard.stats.${key}`) }}</p>
          <h2>{{ value }}</h2>
        </div>
      </el-card>
    </div>
      <div class="grid-container">
        <div class="recent-jobs-container">
          <el-card class="recent-jobs-card">
            <h3>{{ t('dashboard.recentJobs.title') }}</h3>
            <div class="table-wrapper">
              <el-table 
                :data="recentJobs"
                style="min-width: 800px;" height="400"
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
                    <el-button
                      type="text"
                      @click="handleJobClick(row)"
                    >
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
                    <el-tag
                      :type="scope.row.status === 'completed' ? 'success' : scope.row.status === 'running' ? 'primary' : 'error'">{{ scope.row.status }}</el-tag>
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
                />
              </el-table>
            </div>
          </el-card>
        </div>
        <div class="resource-container">
          <el-card class="resource-card">
            <h3>{{ t('dashboard.resources.audit') }}</h3>
            <div class="table-wrapper">
              <el-table
                :data="resources.audit_resources"
                style="min-width: 800px;" height="400" 
                :header-cell-style="{ backgroundColor: '#f5f7fa', color: '#333' }"
                stripe
                border
              >
                <el-table-column
                  prop="id"
                  :label="t('dashboard.resources.columns.id')"
                  style="font-size: 12px;"
                  width="300"
                  align="center"
                />
                <el-table-column
                  prop="action"
                  :label="t('dashboard.resources.columns.action')"
                  width="160"
                />
                <el-table-column
                  prop="details"
                  :label="t('dashboard.resources.columns.details')"
                  width="200"
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
                />
              </el-table>
            </div>
          </el-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDashboardStore } from '../stores/dashboard'
import { useUserStore } from '../stores/user'
import { ElLoading, ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const dashboardStore = useDashboardStore()
const userStore = useUserStore()
const { t } = useI18n()
const stats = ref({})
const resources = ref({})
const recentJobs = ref([])
const router = useRouter()

const refreshOptions = [
  { label: 'off', value: 0 },
  { label: '5s', value: 5 },
  { label: '10s', value: 10 },
  { label: '30s', value: 30 },
  { label: '60s', value: 60 },
]

const refreshInterval = ref(0)
let refreshTimer = null

const refreshContainer = ref(null)

const fetchData = async () => {
  const loadingInstance = ElLoading.service({
    target: refreshContainer.value,
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
      user_claimed_ips: dashboardStore.stats.user_claimed_ips,
      total_policies: dashboardStore.stats.total_policies,
      running_jobs: dashboardStore.stats.running_jobs,
      failed_jobs: dashboardStore.stats.failed_jobs,
      successful_jobs: dashboardStore.stats.successful_jobs,
      cpu_usage: dashboardStore.stats.cpu_usage,
      memory_usage: dashboardStore.stats.memory_usage,
      disk_usage: dashboardStore.stats.disk_usage,
    }
    resources.value = {
      audit_resources: dashboardStore.resources.audit_resources
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
    // 获取当前用户信息
    await userStore.fetchCurrentUser()
    // 获取仪表盘数据
    await fetchData()
    setupAutoRefresh()
  } catch (error) {
    console.error('Failed to initialize dashboard:', error)
    ElMessage.error(t('common.initFailed'))
  }
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})

const handleJobClick = (row) => {
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
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.header-controls {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-bottom: 20px;
  width: 20%;
  margin-left: auto;
}

.stats-container {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.stat-card {
  flex: 1;
  text-align: center;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  min-width: 200px;
  transition: transform 0.3s ease, border 0.3s ease, box-shadow 0.3s ease;
}

.stat-card:hover {
  border: 1px solid #409eff;
  box-shadow: 0 0 10px rgba(64, 158, 255, 0.1);
  transform: scale(1.05);
}

.stat-content h2 {
  font-size: 24px;
  color: #409eff;
}

.stat-content p {
  font-size: 14px;
  color: #666;
}

.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.resource-container, .recent-jobs-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.resource-card, .recent-jobs-card {
  padding: 20px;
}

.table-wrapper {
  overflow-x: auto;
}

.el-table {
  --el-table-border-color: #ebeef5;
}

.el-table th {
  position: sticky;
  top: 0;
  background-color: #f5f7fa;
  z-index: 1;
}

.el-table td, .el-table th {
  text-align: center;
}

.el-table-column {
  padding: 10px;
}

@media (max-width: 768px) {
  .grid-container {
    grid-template-columns: 1fr;
  }
}
</style> 