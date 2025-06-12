<template>
  <div class="tasks">
    <el-card shadow="always" class="main-tasks-card">
      <div class="page-title">
        <div class="page-header">
          <h2>{{ t('tasks.title') }}</h2>
          <p class="subtitle">{{ t('tasks.subtitle') }}</p>
        </div>
        <div class="page-actions">
          <el-select
            v-model="refreshInterval"
            size="small"
            style="width: 145px; margin-right: 12px;"
          >
            <el-option
              v-for="item in refreshOptions"
              :key="item.value"
              :label="t(`tasks.refresh.${item.label}`)"
              :value="item.value"
            />
          </el-select>
          
          <el-button
            :loading="loading"
            circle
            @click="fetchTasks"
          >
            <el-icon><Refresh /></el-icon>
          </el-button>

          <el-button type="primary" @click="createNewTask">
            <el-icon><Plus /></el-icon>
            {{ t('tasks.actions.create') }}
          </el-button>
        </div>
      </div>

      <el-tabs v-model="activeTab" class="task-tabs">
        <el-tab-pane :label="t('tasks.tabs.running')" name="running">
          <div class="task-list">
            <el-table :data="runningTasks" style="width: 100%" v-loading="loading">
              <el-table-column :label="t('tasks.table.name')" prop="name" min-width="150">
                <template #default="{ row }">
                  <div class="task-name">
                    <el-icon><Document /></el-icon>
                    <span>{{ row.name }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column :label="t('tasks.table.type')" prop="type" width="120">
                <template #default="{ row }">
                  <el-tag :type="getTaskTypeTag(row.type)">
                    {{ row.type ? t(`tasks.types.${row.type}`) : t('tasks.types.scan') }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column :label="t('tasks.table.status')" prop="status" width="120">
                <template #default="{ row }">
                  <el-tag :type="getStatusType(row.status)">
                    {{ t(`tasks.status.${row.status}`) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column :label="t('tasks.table.progress')" width="200">
                <template #default="{ row }">
                  <div class="progress-cell">
                    <el-progress 
                      :percentage="row.progress" 
                      :status="row.status === 'failed' ? 'exception' : undefined"
                    />
                  </div>
                </template>
              </el-table-column>
              <el-table-column :label="t('tasks.table.startTime')" prop="startTime" width="180">
                <template #default="{ row }">
                  {{ formatDate(row.start_time) }}
                </template>
              </el-table-column>
              <el-table-column :label="t('tasks.table.actions')" width="150" fixed="right">
                <template #default="{ row }">
                  <el-button-group>
                    <el-button 
                      type="primary" 
                      link
                      @click="viewTaskDetails(row)"
                    >
                      {{ t('common.view') }}
                    </el-button>
                    <el-button 
                      type="danger" 
                      link
                      @click="stopTask(row)"
                      v-if="['pending', 'running'].includes(row.status)"
                      :loading="cancellingTasks[row.id]"
                    >
                      {{ t('common.stop') }}
                    </el-button>
                  </el-button-group>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <el-tab-pane :label="t('tasks.tabs.history')" name="history">
          <div class="task-list">
            <el-table :data="historyTasks" style="width: 100%" v-loading="loading">
              <el-table-column :label="t('tasks.table.name')" prop="name" min-width="150">
                <template #default="{ row }">
                  <div class="task-name">
                    <el-icon><Document /></el-icon>
                    <span>{{ row.name }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column :label="t('tasks.table.type')" prop="type" width="120">
                <template #default="{ row }">
                  <el-tag :type="getTaskTypeTag(row.type)">
                    {{ row.type ? t(`tasks.types.${row.type}`) : t('tasks.types.scan') }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column :label="t('tasks.table.status')" prop="status" width="120">
                <template #default="{ row }">
                  <el-tag :type="getStatusType(row.status)">
                    {{ t(`tasks.status.${row.status}`) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column :label="t('tasks.table.startTime')" prop="startTime" width="180">
                <template #default="{ row }">
                  {{ formatDate(row.start_time) }}
                </template>
              </el-table-column>
              <el-table-column :label="t('tasks.table.endTime')" prop="endTime" width="180">
                <template #default="{ row }">
                  {{ row.end_time ? formatDate(row.end_time) : '-' }}
                </template>
              </el-table-column>
              <el-table-column :label="t('tasks.table.actions')" width="120" fixed="right">
                <template #default="{ row }">
                  <el-button 
                    type="primary" 
                    link
                    @click="viewTaskDetails(row)"
                  >
                    {{ t('common.view') }}
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 任务详情对话框 -->
    <el-dialog
      v-model="detailsVisible"
      :title="t('tasks.details.title')"
      width="80%"
      destroy-on-close
    >
      <div v-if="currentTask" class="task-details">
        <el-descriptions :column="2" border>
          <el-descriptions-item :label="t('tasks.details.name')">
            {{ currentTask.name }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('tasks.details.type')">
            <el-tag :type="getTaskTypeTag(currentTask.type)">
              {{ currentTask.type ? t(`tasks.types.${currentTask.type}`) : t('tasks.types.scan') }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="t('tasks.details.status')">
            <el-tag :type="getStatusType(currentTask.status)">
              {{ t(`tasks.status.${currentTask.status}`) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="t('tasks.details.progress')">
            <el-progress 
              :percentage="currentTask.progress" 
              :status="getProgressStatus(currentTask.status)"
            />
          </el-descriptions-item>
          <el-descriptions-item :label="t('tasks.details.startTime')">
            {{ formatDate(currentTask.start_time) }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('tasks.details.endTime')">
            {{ currentTask.end_time ? formatDate(currentTask.end_time) : '-' }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 扫描结果展示 -->
        <div v-if="currentTask.type === 'scan'" class="scan-results">
          <h3>{{ t('tasks.details.scanResults') }}</h3>
          <el-table :data="currentTask.results" style="width: 100%">
            <el-table-column :label="t('tasks.details.ip')" prop="ip" width="150" />
            <el-table-column :label="t('tasks.details.resultStatus')" prop="status" width="120">
              <template #default="{ row }">
                <el-tag :type="getScanResultStatus(row.status)">
                  {{ t(`tasks.scanStatus.${row.status}`) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="t('tasks.details.details')" prop="details" />
            <el-table-column :label="t('tasks.details.scanTime')" prop="scanTime" width="180">
              <template #default="{ row }">
                {{ formatDate(row.scanTime) }}
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 任务日志 -->
        <div class="task-logs">
          <h3>{{ t('tasks.details.logs') }}</h3>
          <el-scrollbar height="200px">
            <pre class="log-content">{{ currentTask.logs }}</pre>
          </el-scrollbar>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted, onUnmounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, Document, Refresh } from '@element-plus/icons-vue';
import { formatDate } from '../utils/date';
import { useTaskStore } from '../stores/task';

const { t } = useI18n();
const taskStore = useTaskStore();

interface Task {
  id: string;
  name: string;
  type: 'scan' | 'backup' | 'sync' | 'other';
  status: 'running' | 'completed' | 'failed' | 'stopped' | 'pending' | 'cancelled';
  progress: number;
  start_time: Date;
  end_time: Date | null;
  results?: ScanResult[];
  logs?: string;
}

interface ScanResult {
  ip: string;
  status: 'success' | 'failed' | 'warning' | 'info';
  details: string;
  scanTime: Date;
}

// 状态变量
const activeTab = ref('running');
const loading = ref(false);
const detailsVisible = ref(false);
const currentTask = ref<Task | null>(null);
const runningTasks = ref<Task[]>([]);
const historyTasks = ref<Task[]>([]);
const cancellingTasks = ref<Record<string, boolean>>({});

// 刷新选项
const refreshOptions = [
  { label: 'off', value: 0 },
  { label: '1s', value: 1 },
  { label: '5s', value: 5 },
  { label: '10s', value: 10 },
  { label: '30s', value: 30 },
  { label: '60s', value: 60 }
];

const refreshInterval = ref(0);
let refreshTimer: ReturnType<typeof setInterval> | null = null;

// 清除定时器
const clearRefreshTimer = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer);
    refreshTimer = null;
  }
};

// 设置自动刷新
const setupAutoRefresh = () => {
  clearRefreshTimer();
  if (refreshInterval.value > 0) {
    refreshTimer = setInterval(() => {
      fetchTasks();
    }, refreshInterval.value * 1000);
  }
};

// 监听刷新间隔变化
watch(refreshInterval, () => {
  setupAutoRefresh();
});

// 获取任务类型标签样式
const getTaskTypeTag = (type: Task['type']) => {
  const types: Record<Task['type'], string> = {
    scan: 'primary',
    backup: 'success',
    sync: 'warning',
    other: 'info'
  };
  return types[type];
};

// 获取状态标签样式
const getStatusType = (status: Task['status']) => {
  const types: Record<Task['status'], string> = {
    running: 'primary',
    completed: 'success',
    failed: 'danger',
    stopped: 'warning',
    pending: 'info',
    cancelled: 'info'
  };
  return types[status];
};

// 获取进度条状态
const getProgressStatus = (status: Task['status']) => {
  const types: Record<Task['status'], string> = {
    running: '',
    completed: 'success',
    failed: 'exception',
    stopped: 'warning',
    pending: '',
    cancelled: 'warning'
  };
  return types[status];
};

// 获取扫描结果状态样式
const getScanResultStatus = (status: ScanResult['status']) => {
  const types: Record<ScanResult['status'], string> = {
    success: 'success',
    failed: 'danger',
    warning: 'warning',
    info: 'info'
  };
  return types[status];
};

// 查看任务详情
const viewTaskDetails = async (task: Task) => {
  try {
    loading.value = true;
    const response = await taskStore.getJobStatus(task.id);
    currentTask.value = response.job;
    detailsVisible.value = true;
  } catch (error: any) {
    ElMessage.error(error.message || t('tasks.messages.loadDetailsFailed'));
  } finally {
    loading.value = false;
  }
};

// 停止任务
const stopTask = async (task: Task) => {
  try {
    await ElMessageBox.confirm(
      t('tasks.messages.confirmStop'),
      t('common.warning'),
      {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
        type: 'warning'
      }
    );
    
    cancellingTasks.value[task.id] = true;
    await taskStore.cancelJob(task.id);
    ElMessage.success(t('tasks.messages.stopSuccess'));
    await fetchTasks();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || t('tasks.messages.stopFailed'));
    }
  } finally {
    cancellingTasks.value[task.id] = false;
  }
};

// 创建新任务
const createNewTask = () => {
  // TODO: 实现创建新任务的逻辑
};

// 加载任务数据
const fetchTasks = async () => {
  try {
    loading.value = true;
    const response = await taskStore.fetchAllTasks();
    const tasks = response.jobs || [];
    
    // 分离运行中和历史任务
    runningTasks.value = tasks.filter(task => ['pending', 'running'].includes(task.status));
    historyTasks.value = tasks.filter(task => !['pending', 'running'].includes(task.status));
  } catch (error: any) {
    ElMessage.error(error.message || t('tasks.messages.loadFailed'));
  } finally {
    loading.value = false;
  }
};

// 添加后台刷新逻辑
const backgroundRefreshTimer = ref<ReturnType<typeof setInterval> | null>(null);
const hasRunningTasks = computed(() => {
  return runningTasks.value.some(task => ['pending', 'running'].includes(task.status));
});

// 后台刷新运行中的任务
const refreshRunningTasks = async () => {
  try {
    const response = await taskStore.fetchRunningJobs();
    const runningTasksData = response.jobs || [];
    
    // 更新现有任务的状态
    runningTasks.value = runningTasks.value.map(task => {
      const updatedTask = runningTasksData.find((rt: Task) => rt.id === task.id);
      if (updatedTask) {
        return {
          ...task,
          status: updatedTask.status,
          progress: updatedTask.progress,
        };
      }
      return task;
    });
    
    // 如果没有任何运行中的任务，停止后台刷新
    if (!hasRunningTasks.value) {
      clearBackgroundRefresh();
    }
  } catch (error) {
    console.error('Failed to refresh running tasks:', error);
  }
};

// 清除后台刷新定时器
const clearBackgroundRefresh = () => {
  if (backgroundRefreshTimer.value) {
    clearInterval(backgroundRefreshTimer.value);
    backgroundRefreshTimer.value = null;
  }
};

// 启动后台刷新
const startBackgroundRefresh = () => {
  clearBackgroundRefresh();
  if (hasRunningTasks.value) {
    backgroundRefreshTimer.value = setInterval(refreshRunningTasks, 3000);
  }
};

// 监听任务列表变化
watch(runningTasks, (newTasks) => {
  if (hasRunningTasks.value) {
    startBackgroundRefresh();
  } else {
    clearBackgroundRefresh();
  }
}, { deep: true });

// 初始化
onMounted(() => {
  fetchTasks();
  if (hasRunningTasks.value) {
    startBackgroundRefresh();
  }
});

// 组件卸载时清理所有定时器
onUnmounted(() => {
  clearRefreshTimer();
  clearBackgroundRefresh();
});
</script>

<style scoped>
.tasks {
  padding: 20px;
}

.main-tasks-card {
  margin-bottom: 20px;
  box-shadow: var(--el-box-shadow-light);
}

.page-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-header h2 {
  font-size: 24px;
  margin: 0;
  color: var(--el-text-color-primary);
}

.page-header .subtitle {
  color: var(--el-text-color-regular);
  margin: 5px 0 0;
  font-size: 14px;
}

.page-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.task-list {
  margin-top: 20px;
}

.task-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.task-name .el-icon {
  color: var(--el-text-color-secondary);
}

.progress-cell {
  padding: 5px 0;
}

:deep(.el-progress-bar__inner) {
  transition: width 0.3s ease;
}

.task-details {
  padding: 20px;
}

.scan-results {
  margin-top: 20px;
}

.scan-results h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 15px;
  color: var(--el-text-color-primary);
}

.task-logs {
  margin-top: 20px;
}

.task-logs h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 15px;
  color: var(--el-text-color-primary);
}

.log-content {
  font-family: monospace;
  font-size: 14px;
  line-height: 1.5;
  color: var(--el-text-color-regular);
  background-color: var(--el-fill-color-light);
  padding: 10px;
  border-radius: var(--el-border-radius-base);
  margin: 0;
}

:deep(.el-descriptions) {
  margin-bottom: 20px;
}

:deep(.el-descriptions__label) {
  width: 120px;
  justify-content: flex-end;
}

:deep(.el-table) {
  --el-table-border-color: var(--el-border-color-lighter);
}
</style> 