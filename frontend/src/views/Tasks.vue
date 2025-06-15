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
                    <span>{{ row.subnet.name }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column :label="t('tasks.table.policy.name')" prop="name" min-width="150">
                <template #default="{ row }">
                  <span class="policy-name">{{ row.policy?.name || '-' }}</span>
                </template>
              </el-table-column>
              <el-table-column :label="t('tasks.table.policy.strategies')" prop="strategies" min-width="200">
                <template #default="{ row }">
                  <div class="strategy-tags">
                    <template v-if="row.policy?.strategies">
                      <span class="strategy-field">{{ t('scan.policy.cronExpression') }}:</span>
                      <el-tag v-for="strategy in row.policy?.strategies" class="strategy-tag">
                        {{ strategy.cron }}
                      </el-tag>
                    </template>
                    <span v-else class="no-strategy">-</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column :label="t('tasks.table.machines_found')" prop="machines_found" width="160">
                <template #default="{ row }">
                  <el-tag>
                    {{ row.machines_found }}
                  </el-tag>
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
            <div class="pagination-container">
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[10, 20, 50, 100]"
                :total="totalTasks"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
              />
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane :label="t('tasks.tabs.history')" name="history">
          <div class="task-list">
            <el-table
              v-loading="loading"
              :data="historyTasks"
              style="width: 100%"
            >
              <el-table-column :label="t('tasks.table.name')" :resizable="true" prop="name" min-width="150">
                <template #default="{ row }">
                  <div class="task-name">
                    <el-icon><Document /></el-icon>
                    <span>{{ row.subnet.name }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column :label="t('tasks.table.policy.name')" prop="name" min-width="150">
                <template #default="{ row }">
                  <span class="policy-name">{{ row.policy?.name || '-' }}</span>
                </template>
              </el-table-column>
              <el-table-column :label="t('tasks.table.policy.strategies')" prop="strategies" min-width="120">
                <template #default="{ row }">
                  <div class="strategy-tags">
                    <template v-if="row.policy?.strategies">
                      <span class="strategy-field">{{ t('scan.policy.cronExpression') }}:</span>
                      <el-tag v-for="strategy in row.policy?.strategies" class="strategy-tag">
                        {{ strategy.cron }}
                      </el-tag>
                    </template>
                    <span v-else class="no-strategy">-</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column :label="t('tasks.table.machines_found')" prop="machines_found" width="160">
                <template #default="{ row }">
                  <el-tag>
                    {{ row.machines_found }}
                  </el-tag>
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
              <el-table-column :label="t('tasks.table.error_message')" prop="error_message" min-width="120" max-width="220">
                <template #default="{ row }">
                  <el-tooltip
                    v-if="row.error_message"
                    effect="dark"
                    :content="row.error_message"
                    placement="top">
                    <el-tag :type="getStatusType(row.status)" class="ellipsis-tag">
                      {{ row.error_message }}
                    </el-tag>
                  </el-tooltip>
                  <el-tag v-else :type="getStatusType(row.status)" class="ellipsis-tag">-</el-tag>
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
            <div class="pagination-container">
              <el-pagination
                v-model:current-page="historyCurrentPage"
                v-model:page-size="historyPageSize"
                :page-sizes="[10, 20, 50, 100]"
                :total="totalHistoryTasks"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleHistorySizeChange"
                @current-change="handleHistoryCurrentChange"
              />
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 任务详情对话框 -->
    <el-dialog
      v-model="detailsVisible"
      :title="t('tasks.details.title')"
      width="80%"
      :close-on-click-modal="false"
      @close="handleCloseDetails"
      class="task-details-dialog"
    >
      <div v-if="currentTask" class="task-details">
        <el-descriptions :column="2" border>
          <el-descriptions-item :label="t('tasks.details.name')">
            {{ currentTask.subnet.name }}
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
        <div v-if="currentTask" class="scan-results">
          <h3>{{ t('tasks.details.scanResults') }}</h3>
          <div class="table-container">
            <el-table 
              :data="currentTask.results"
              highlight-current-row
              @current-change="handleScanResultCurrentChange"
              v-loading="detailLoading"
              style="width: 100%">
              <el-table-column :label="t('tasks.details.ip')" prop="ip" width="150">
                <template #default="{ row }">
                  <span>{{ row.ip_address }}</span>
                </template>
              </el-table-column>
              <el-table-column :label="t('tasks.details.resultStatus')" prop="status" width="120">
                <template #default="{ row }">
                  <el-tag :type="getScanResultStatus(row.status)">
                    {{ t(`tasks.scanStatus.${row.status}`) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column :label="t('tasks.details.details')" prop="details">
                <template #default="{ row }">
                  {{ row.open_ports }}
                </template>
              </el-table-column>
              <el-table-column :label="t('tasks.details.scanTime')" prop="scanTime" width="180">
                <template #default="{ row }">
                  {{ formatDate(row.created_at) }}
                </template>
              </el-table-column>
            </el-table>
          </div>
          
          <div class="pagination-container">
            <el-pagination
              v-model:current-page="resultPage"
              v-model:page-size="resultPageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="resultTotal"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleResultSizeChange"
              @current-change="handleResultCurrentChange"
            />
          </div>
        </div>

        <!-- 任务详情 -->
        <div class="task-logs">
          <h3>{{ t('tasks.details.details') }}</h3>
          <div class="log-container">
            <pre class="log-content">{{ selectedLogContent }}</pre>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, Document, Refresh } from '@element-plus/icons-vue';
import { formatDate } from '../utils/date';
import { useTaskStore } from '../stores/task';
import { useRouter } from 'vue-router';

const { t } = useI18n();
const taskStore = useTaskStore();
const router = useRouter();

interface Policy {
  id: string;
  name: string;
  description?: string;
  strategies: {
    id: string;
    name: string;
    type: string;
    parameters: Record<string, any>;
  }[];
  created_at: Date;
  updated_at: Date;
}

interface Task {
  id: string;
  name: string;
  type: 'scan' | 'backup' | 'sync' | 'other';
  status: 'running' | 'completed' | 'failed' | 'stopped' | 'pending' | 'cancelled';
  progress: number;
  start_time: Date;
  end_time: Date | null;
  policy: Policy;
  subnet: Subnet;
  results?: ScanResult[];
  logs?: string;
}

interface Subnet { 
  id: string;
  name: string;
}

interface ScanResult {
  ip: string;
  status: 'success' | 'failed' | 'warning' | 'info';
  scanTime: Date;
  raw_data: string;
}

// 状态变量
const activeTab = ref('running');
const loading = ref(false);
const detailsVisible = ref(false);
const currentTask = ref<Task | null>(null);
const runningTasks = ref<Task[]>([]);
const historyTasks = ref<Task[]>([]);
const cancellingTasks = ref<Record<string, boolean>>({});
const currentPage = ref(1);
const pageSize = ref(10);
const totalTasks = ref(0);
const historyCurrentPage = ref(1);
const historyPageSize = ref(10);
const totalHistoryTasks = ref(0);
const selectedLogContent = ref('');
const resultPage = ref(1);
const resultPageSize = ref(10);
const resultTotal = ref(0);
const detailLoading = ref(false);

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

// 获取任务详情
const fetchTaskDetail = async (taskId: string, page = 1, pageSize = 10) => {
  try {
    detailLoading.value = true;
    const response = await taskStore.getJobStatus(taskId, {
      page,
      pageSize
    });
    // 使用新对象来更新状态，避免引用问题
    if (currentTask.value) {
      currentTask.value = {
        ...currentTask.value,
        results: response.results
      };
    }
    resultTotal.value = response.total;
  } catch (error: any) {
    console.error('Failed to fetch task detail:', error);
    ElMessage.error(t('tasks.errors.fetchDetailFailed'));
  } finally {
    detailLoading.value = false;
  }
};

// 查看任务详情
const viewTaskDetails = async (task: Task) => {
  try {
    resultPage.value = 1;
    resultPageSize.value = 10;
    // 先设置基本信息
    currentTask.value = task;
    detailsVisible.value = true;
    // 然后获取详细数据
    await fetchTaskDetail(task.id, 1, 10);
  } catch (error: any) {
    console.error('Failed to view task details:', error);
    ElMessage.error(t('tasks.errors.viewDetailsFailed'));
  }
};

// 处理任务详情结果的分页
const handleResultSizeChange = async (val: number) => {
  if (!currentTask.value) return;
  resultPageSize.value = val;
  resultPage.value = 1;
  await fetchTaskDetail(currentTask.value.id, 1, val);
};

const handleResultCurrentChange = async (val: number) => {
  if (!currentTask.value) return;
  resultPage.value = val;
  await fetchTaskDetail(currentTask.value.id, val, resultPageSize.value);
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
  router.push('/scans');
};

// 加载任务数据
const fetchTasks = async () => {
  try {
    loading.value = true;
    const params = {
      page: activeTab.value === 'running' ? currentPage.value : historyCurrentPage.value,
      pageSize: activeTab.value === 'running' ? pageSize.value : historyPageSize.value,
      status: activeTab.value === 'running' 
        ? ['pending', 'running'] 
        : ['completed', 'failed', 'stopped', 'cancelled']
    };
    
    const response = await taskStore.fetchAllTasks(params);
    const tasks = response.jobs || [];
    const total = response.total || 0;
    
    if (activeTab.value === 'running') {
      runningTasks.value = tasks;
      totalTasks.value = total;
    } else {
      historyTasks.value = tasks;
      totalHistoryTasks.value = total;
    }
  } catch (error: any) {
    ElMessage.error(error.message || t('tasks.messages.loadFailed'));
  } finally {
    loading.value = false;
  }
};

// 初始化
onMounted(async () => {
  await fetchTasks();
  setupAutoRefresh();
});

// 组件卸载时清理定时器
onUnmounted(() => {
  clearRefreshTimer();
});

// 处理运行中任务的分页
const handleSizeChange = (val: number) => {
  pageSize.value = val;
  currentPage.value = 1;
  fetchTasks();
};

const handleCurrentChange = (val: number) => {
  currentPage.value = val;
  fetchTasks();
};

// 处理历史任务的分页
const handleHistorySizeChange = (val: number) => {
  historyPageSize.value = val;
  fetchTasks();
};

const handleHistoryCurrentChange = (val: number) => {
  historyCurrentPage.value = val;
  fetchTasks();
};

// 监听标签页切换
watch(activeTab, () => {
  if (activeTab.value === 'running') {
    currentPage.value = 1;
  } else {
    historyCurrentPage.value = 1;
  }
  fetchTasks();
});

const handleScanResultCurrentChange = (row: ScanResult | null) => {
  if (!row) {
    selectedLogContent.value = '';
    return;
  }
  selectedLogContent.value = row.raw_data || '';
};

// 关闭详情对话框
const handleCloseDetails = () => {
  detailsVisible.value = false;
  currentTask.value = null;
  resultPage.value = 1;
  resultPageSize.value = 10;
  resultTotal.value = 0;
};
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
  font-weight: 500;
}

.task-name .el-icon {
  color: var(--el-text-color-secondary);
}

.policy-name {
  color: var(--el-text-color-primary);
}

.strategy-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.strategy-tag {
  margin-right: 4px;
}

.no-strategy {
  color: var(--el-text-color-secondary);
  font-size: 0.9em;
}

.strategy-field {
  min-width: 50px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.ellipsis-tag {
  display: contents;
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  vertical-align: middle;
}

.progress-cell {
  padding: 5px 0;
}

:deep(.el-progress-bar__inner) {
  transition: width 0.3s ease;
}

:deep(.el-overlay-dialog) {
  bottom: 0;
  left: 0;
  overflow: hidden;
  position: fixed;
  right: 0;
  top: -50px;
}

:deep(.el-dialog) {
  --el-dialog-width: 50% !important;
}

.task-details-dialog :deep(.el-dialog__body) {
  padding: 0;
  height: 80vh;
  overflow: hidden;
}

.task-details {
  height: 75%;
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.scan-results {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  margin-top: 20px;
}

.table-container {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.table-container :deep(.el-table) {
  height: 100%;
}

.table-container :deep(.el-table__body-wrapper) {
  overflow-y: auto;
}

.task-logs {
  margin-top: 20px;
  height: 300px;
  display: flex;
  flex-direction: column;
}

.log-container {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  background-color: var(--el-fill-color-light);
  border-radius: var(--el-border-radius-base);
}

.log-content {
  height: 100%;
  margin: 0;
  padding: 10px;
  overflow-y: auto;
  font-family: monospace;
  font-size: 14px;
  line-height: 1.5;
  color: var(--el-text-color-regular);
}

.pagination-container {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
}
</style> 