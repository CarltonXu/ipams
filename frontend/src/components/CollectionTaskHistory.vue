<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Grid, Clock, Check, Close, Loading, Refresh } from '@element-plus/icons-vue';
import { useHostInfoStore } from '../stores/hostInfo';
import CollectionProgress from './CollectionProgress.vue';

const { t } = useI18n();
const hostInfoStore = useHostInfoStore();

interface Props {
  hostId?: string | null; // 可选：过滤特定主机的任务
}

const props = defineProps<Props>();
const emit = defineEmits(['task-selected']);

interface CollectionTask {
  id: string;
  trigger_type: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  total_hosts: number;
  success_count: number;
  failed_count: number;
  created_at: string;
  end_time: string | null;
  progress?: {
    task_id: string;
    total_count: number;
    completed_count: number;
    failed_count: number;
    current_step: string;
    status: string;
    progress_percent: number;
    error_message?: string;
  };
  related_host?: {
    id: string;
    hostname: string | null;
    ip_address: string;
  };
  related_hosts?: Array<{
    id: string;
    hostname: string | null;
    ip_address: string | null;
    host_type?: string;
    collection_status?: string;
    collection_error?: string | null;
  }>;
}

const tasks = ref<CollectionTask[]>([]);
const loading = ref(false);
const viewMode = ref<'table' | 'timeline'>('table');
const statusFilter = ref<string>('all');
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);

// 进度对话框
const progressDialogVisible = ref(false);
const currentTaskId = ref<string | null>(null);

// 自动刷新相关
const autoRefreshEnabled = ref(true); // 是否启用自动刷新
const refreshIntervalOptions = [3, 5, 20, 60, 120]; // 刷新间隔选项（秒）
const refreshInterval = ref(3); // 当前刷新间隔（秒）
let refreshTimer: ReturnType<typeof setInterval> | null = null;

// 计算属性：是否有进行中的任务
const hasRunningTasks = computed(() => {
  return tasks.value.some(task => task.status === 'running');
});

// 获取任务列表
const fetchTasks = async () => {
  if (loading.value) return;
  
  try {
    loading.value = true;
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value
    };
    
    if (statusFilter.value !== 'all') {
      params.status = statusFilter.value;
    }
    
    if (props.hostId) {
      params.host_id = props.hostId;
    }
    
    const response = await hostInfoStore.getCollectionTasks(params);
    tasks.value = response.tasks || [];
    total.value = response.total || 0;
  } catch (error: any) {
    ElMessage.error(error.message || t('common.fetchError'));
  } finally {
    loading.value = false;
  }
};

// 设置自动刷新
const setupAutoRefresh = () => {
  clearAutoRefresh();
  if (autoRefreshEnabled.value && hasRunningTasks.value) {
    refreshTimer = setInterval(() => {
      fetchTasks();
    }, refreshInterval.value * 1000); // 转换为毫秒
  }
};

// 切换自动刷新
const toggleAutoRefresh = () => {
  if (autoRefreshEnabled.value) {
    setupAutoRefresh();
  } else {
    clearAutoRefresh();
  }
};

// 刷新间隔变化时重新设置
const onRefreshIntervalChange = () => {
  if (autoRefreshEnabled.value) {
    setupAutoRefresh();
  }
  // 保存用户偏好到localStorage
  localStorage.setItem('collectionTaskHistoryAutoRefresh', JSON.stringify({
    enabled: autoRefreshEnabled.value,
    interval: refreshInterval.value
  }));
};

// 清除自动刷新
const clearAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer);
    refreshTimer = null;
  }
};

// 切换视图模式
const toggleViewMode = () => {
  viewMode.value = viewMode.value === 'table' ? 'timeline' : 'table';
  localStorage.setItem('collectionTaskHistoryViewMode', viewMode.value);
};

// 查看任务详情
const viewTaskDetails = (task: CollectionTask) => {
  currentTaskId.value = task.id;
  progressDialogVisible.value = true;
  emit('task-selected', task);
};

// 取消任务
const cancelTask = async (task: CollectionTask) => {
  try {
    await ElMessageBox.confirm(
      t('hostInfo.collectionTask.confirmCancel', '确定要取消此采集任务吗？取消后可以重新发起采集。'),
      t('hostInfo.collectionTask.cancelTask', '取消任务'),
      {
        confirmButtonText: t('common.confirm', '确定'),
        cancelButtonText: t('common.cancel', '取消'),
        type: 'warning'
      }
    );
    
    await hostInfoStore.cancelCollectionTask(task.id);
    ElMessage.success(t('hostInfo.collectionTask.cancelSuccess', '任务已取消'));
    
    // 刷新任务列表
    await fetchTasks();
  } catch (error: any) {
    if (error !== 'cancel') {  // 用户取消操作不算错误
      ElMessage.error(error.message || t('hostInfo.collectionTask.cancelFailed', '取消任务失败'));
    }
  }
};

// 格式化日期时间
const formatDateTime = (dateStr: string | null) => {
  if (!dateStr) return '-';
  const date = new Date(dateStr);
  return date.toLocaleString('zh-CN');
};

// 获取状态标签类型
const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: 'info',
    running: 'primary',
    completed: 'success',
    failed: 'danger'
  };
  return statusMap[status] || 'info';
};

// 获取状态文本
const getStatusText = (status: string) => {
  return t(`hostInfo.collectionTask.status.${status}`, status);
};

// 获取主机状态标签类型
const getHostStatusType = (status?: string) => {
  if (!status) return 'info';
  const statusMap: Record<string, string> = {
    pending: 'info',
    collecting: 'primary',
    success: 'success',
    failed: 'danger'
  };
  return statusMap[status] || 'info';
};

// 监听状态过滤变化
watch(statusFilter, () => {
  currentPage.value = 1;
  fetchTasks();
});

// 监听hostId变化
watch(() => props.hostId, () => {
  currentPage.value = 1;
  fetchTasks();
});

// 监听自动刷新开关变化
watch(autoRefreshEnabled, () => {
  toggleAutoRefresh();
  localStorage.setItem('collectionTaskHistoryAutoRefresh', JSON.stringify({
    enabled: autoRefreshEnabled.value,
    interval: refreshInterval.value
  }));
});

// 监听刷新间隔变化
watch(refreshInterval, () => {
  onRefreshIntervalChange();
});

// 监听进行中任务变化
watch(hasRunningTasks, (newVal) => {
  if (newVal && autoRefreshEnabled.value) {
    setupAutoRefresh();
  } else {
    clearAutoRefresh();
  }
});

// 组件挂载
onMounted(() => {
  // 从localStorage恢复视图偏好
  const savedViewMode = localStorage.getItem('collectionTaskHistoryViewMode');
  if (savedViewMode === 'table' || savedViewMode === 'timeline') {
    viewMode.value = savedViewMode;
  }
  
  // 从localStorage恢复自动刷新设置
  const savedAutoRefresh = localStorage.getItem('collectionTaskHistoryAutoRefresh');
  if (savedAutoRefresh) {
    try {
      const settings = JSON.parse(savedAutoRefresh);
      autoRefreshEnabled.value = settings.enabled !== false; // 默认启用
      if (settings.interval && refreshIntervalOptions.includes(settings.interval)) {
        refreshInterval.value = settings.interval;
      }
    } catch (e) {
      // 忽略解析错误，使用默认值
    }
  }
  
  fetchTasks();
  setupAutoRefresh();
});

// 组件卸载
onUnmounted(() => {
  clearAutoRefresh();
});
</script>

<template>
  <div class="collection-task-history">
    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-select
          v-model="statusFilter"
          :placeholder="t('hostInfo.collectionTask.filterStatus', '过滤状态')"
          style="width: 150px; margin-right: 10px;"
        >
          <el-option :label="t('common.all', '全部')" value="all" />
          <el-option :label="t('hostInfo.collectionTask.status.pending', '待处理')" value="pending" />
          <el-option :label="t('hostInfo.collectionTask.status.running', '进行中')" value="running" />
          <el-option :label="t('hostInfo.collectionTask.status.completed', '已完成')" value="completed" />
          <el-option :label="t('hostInfo.collectionTask.status.failed', '失败')" value="failed" />
        </el-select>
        
        <el-button @click="fetchTasks" :loading="loading">
          <el-icon><Refresh /></el-icon>
          <span>{{ t('common.refresh', '刷新') }}</span>
        </el-button>
        
        <el-divider direction="vertical" style="margin: 0 10px;" />
        
        <!-- 自动刷新开关 -->
        <el-switch
          v-model="autoRefreshEnabled"
          :active-text="t('hostInfo.collectionTask.autoRefresh', '自动刷新')"
          style="margin-right: 10px;"
        />
        
        <!-- 刷新间隔选择 -->
        <el-select
          v-model="refreshInterval"
          :disabled="!autoRefreshEnabled"
          style="width: 120px;"
          :placeholder="t('hostInfo.collectionTask.refreshInterval', '刷新间隔')"
        >
          <el-option
            v-for="interval in refreshIntervalOptions"
            :key="interval"
            :label="`${interval}${t('common.second', '秒')}`"
            :value="interval"
          />
        </el-select>
      </div>
      
      <div class="toolbar-right">
        <el-button-group>
          <el-button
            :type="viewMode === 'table' ? 'primary' : 'default'"
            @click="viewMode = 'table'"
          >
            <el-icon><Grid /></el-icon>
            <span>{{ t('hostInfo.collectionTask.tableView', '表格视图') }}</span>
          </el-button>
          <el-button
            :type="viewMode === 'timeline' ? 'primary' : 'default'"
            @click="viewMode = 'timeline'"
          >
            <el-icon><Clock /></el-icon>
            <span>{{ t('hostInfo.collectionTask.timelineView', '时间线视图') }}</span>
          </el-button>
        </el-button-group>
      </div>
    </div>

    <!-- 表格视图 -->
    <div v-if="viewMode === 'table'" class="table-view">
      <el-table
        :data="tasks"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" :label="t('hostInfo.collectionTask.taskId', '任务ID')" width="200">
          <template #default="{ row }">
            <el-text truncated style="max-width: 200px;">{{ row.id }}</el-text>
          </template>
        </el-table-column>
        
        <el-table-column :label="t('hostInfo.collectionTask.taskStatus', '任务状态')" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column :label="t('hostInfo.collectionTask.progress', '进度')" width="200">
          <template #default="{ row }">
            <div v-if="row.progress">
              <el-progress
                :percentage="row.progress.progress_percent"
                :status="row.status === 'failed' ? 'exception' : undefined"
              />
              <div class="progress-text">
                {{ row.progress.completed_count + row.progress.failed_count }} / {{ row.progress.total_count }}
              </div>
            </div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column :label="t('hostInfo.collectionTask.totalHosts', '总主机数')" width="100" align="center">
          <template #default="{ row }">
            {{ row.total_hosts }}
          </template>
        </el-table-column>
        
        <el-table-column :label="t('hostInfo.collectionTask.successCount', '成功')" width="80" align="center">
          <template #default="{ row }">
            <el-text type="success">{{ row.success_count }}</el-text>
          </template>
        </el-table-column>
        
        <el-table-column :label="t('hostInfo.collectionTask.failedCount', '失败')" width="80" align="center">
          <template #default="{ row }">
            <el-text type="danger">{{ row.failed_count }}</el-text>
          </template>
        </el-table-column>
        
        <el-table-column :label="t('hostInfo.collectionTask.relatedHosts', '关联主机')" min-width="200">
          <template #default="{ row }">
            <div v-if="row.related_hosts && row.related_hosts.length > 0" class="hosts-list">
              <el-tag
                v-for="host in row.related_hosts"
                :key="host.id"
                :type="getHostStatusType(host.collection_status)"
                size="small"
                style="margin-right: 5px; margin-bottom: 5px;"
                :title="host.hostname || host.ip_address"
              >
                {{ host.hostname || host.ip_address || host.id.substring(0, 8) }}
              </el-tag>
              <el-text v-if="row.related_hosts.length > 3" type="info" size="small">
                +{{ row.related_hosts.length - 3 }}
              </el-text>
            </div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column :label="t('hostInfo.collectionTask.createdAt', '创建时间')" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column :label="t('hostInfo.collectionTask.endTime', '结束时间')" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.end_time) }}
          </template>
        </el-table-column>
        
        <el-table-column :label="t('common.actions', '操作')" width="180" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="viewTaskDetails(row)"
            >
              {{ t('hostInfo.collectionTask.viewDetails', '查看详情') }}
            </el-button>
            <el-button
              v-if="row.status === 'pending' || row.status === 'running'"
              type="danger"
              size="small"
              @click="cancelTask(row)"
              :loading="loading"
            >
              {{ t('hostInfo.collectionTask.cancel', '取消') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          background
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchTasks"
          @current-change="fetchTasks"
        />
      </div>
    </div>

    <!-- 时间线视图 -->
    <div v-else class="timeline-view">
      <el-timeline>
        <el-timeline-item
          v-for="task in tasks"
          :key="task.id"
          :timestamp="formatDateTime(task.created_at)"
          :type="getStatusType(task.status)"
          placement="top"
        >
          <el-card shadow="hover" class="task-card" @click="viewTaskDetails(task)">
            <div class="task-card-header">
              <div class="task-card-title">
                <el-tag :type="getStatusType(task.status)" size="large">
                  {{ getStatusText(task.status) }}
                </el-tag>
                <span class="task-id">{{ task.id }}</span>
              </div>
              <div class="task-card-actions">
                <el-button type="primary" size="small" @click.stop="viewTaskDetails(task)">
                  {{ t('hostInfo.collectionTask.viewDetails', '查看详情') }}
                </el-button>
                <el-button
                  v-if="task.status === 'pending' || task.status === 'running'"
                  type="danger"
                  size="small"
                  @click.stop="cancelTask(task)"
                  :loading="loading"
                >
                  {{ t('hostInfo.collectionTask.cancel', '取消') }}
                </el-button>
              </div>
            </div>
            
            <div class="task-card-content">
              <!-- 关联主机信息 -->
              <div v-if="task.related_hosts && task.related_hosts.length > 0" class="task-related-hosts">
                <div class="hosts-header">
                  <span class="hosts-label">{{ t('hostInfo.collectionTask.relatedHosts', '关联主机') }}:</span>
                  <span class="hosts-count">({{ task.related_hosts.length }})</span>
                </div>
                <div class="hosts-tags">
                  <el-tag
                    v-for="host in task.related_hosts"
                    :key="host.id"
                    :type="getHostStatusType(host.collection_status)"
                    size="small"
                    style="margin-right: 8px; margin-bottom: 8px;"
                    :title="`${host.hostname || ''} ${host.ip_address || ''} ${host.collection_error || ''}`"
                  >
                    <span class="host-tag-content">
                      <el-icon v-if="host.collection_status === 'success'" style="margin-right: 4px;"><Check /></el-icon>
                      <el-icon v-else-if="host.collection_status === 'failed'" style="margin-right: 4px;"><Close /></el-icon>
                      <el-icon v-else-if="host.collection_status === 'collecting'" style="margin-right: 4px;"><Loading /></el-icon>
                      {{ host.hostname || host.ip_address || host.id.substring(0, 8) }}
                    </span>
                  </el-tag>
                </div>
              </div>
              
              <div class="task-stats">
                <div class="stat-item">
                  <span class="stat-label">{{ t('hostInfo.collectionTask.totalHosts', '总主机数') }}:</span>
                  <span class="stat-value">{{ task.total_hosts }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">{{ t('hostInfo.collectionTask.successCount', '成功') }}:</span>
                  <span class="stat-value success">{{ task.success_count }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">{{ t('hostInfo.collectionTask.failedCount', '失败') }}:</span>
                  <span class="stat-value danger">{{ task.failed_count }}</span>
                </div>
              </div>
              
              <div v-if="task.progress" class="task-progress">
                <el-progress
                  :percentage="task.progress.progress_percent"
                  :status="task.status === 'failed' ? 'exception' : undefined"
                />
                <div class="progress-text">
                  {{ task.progress.current_step }}
                </div>
              </div>
              
              <div v-if="task.progress?.error_message" class="task-error">
                <el-alert
                  type="error"
                  :title="t('hostInfo.collectionTask.errorMessage', '错误信息')"
                  :description="task.progress.error_message"
                  show-icon
                  :closable="false"
                />
              </div>
              
              <div v-if="task.end_time" class="task-end-time">
                <el-text type="info" size="small">
                  {{ t('hostInfo.collectionTask.endTime', '结束时间') }}: {{ formatDateTime(task.end_time) }}
                </el-text>
              </div>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
      
      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          background
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchTasks"
          @current-change="fetchTasks"
        />
      </div>
    </div>

    <!-- 进度对话框 -->
    <CollectionProgress
      v-model="progressDialogVisible"
      :task-id="currentTaskId"
      @completed="fetchTasks"
    />
  </div>
</template>

<style scoped>
.collection-task-history {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
}

.table-view {
  margin-bottom: 20px;
}

.progress-text {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 5px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.timeline-view {
  padding: 20px 0;
}

.task-card {
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 10px;
}

.task-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--el-box-shadow-light);
}

.task-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.task-card-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.task-id {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  font-family: monospace;
}

.task-card-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.task-stats {
  display: flex;
  gap: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.stat-label {
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.stat-value {
  font-weight: bold;
  font-size: 16px;
}

.stat-value.success {
  color: var(--el-color-success);
}

.stat-value.danger {
  color: var(--el-color-danger);
}

.task-progress {
  margin-top: 10px;
}

.task-error {
  margin-top: 10px;
}

.task-end-time {
  margin-top: 10px;
}

.hosts-list {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.task-related-hosts {
  margin-bottom: 15px;
  padding: 10px;
  background-color: var(--el-fill-color-lighter);
  border-radius: var(--el-border-radius-base);
}

.hosts-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  font-weight: 500;
  font-size: 14px;
}

.hosts-label {
  color: var(--el-text-color-primary);
}

.hosts-count {
  color: var(--el-text-color-secondary);
  margin-left: 5px;
  font-size: 12px;
}

.hosts-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.host-tag-content {
  display: flex;
  align-items: center;
}

.task-card-actions {
  display: flex;
  gap: 8px;
}
</style>

