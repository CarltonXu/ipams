<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage } from 'element-plus';
import { useHostInfoStore } from '../stores/hostInfo';

const { t } = useI18n();
const hostInfoStore = useHostInfoStore();

interface Props {
  modelValue: boolean;
  taskId: string | null;
}

const props = defineProps<Props>();
const emit = defineEmits(['update:modelValue', 'completed']);

interface ProgressData {
  task_id: string;
  total_count: number;
  completed_count: number;
  failed_count: number;
  success_count?: number;
  current_step: string;
  status: 'running' | 'completed' | 'failed' | 'cancelled';
  progress_percent: number;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
});

const progress = ref<ProgressData | null>(null);
const loading = ref(false);
const refreshInterval = ref(2000); // 每2秒刷新一次
let refreshTimer: ReturnType<typeof setInterval> | null = null;

// 计算属性
const progressPercent = computed(() => {
  return progress.value?.progress_percent || 0;
});

const progressStatus = computed(() => {
  if (!progress.value) return '';
  if (progress.value.status === 'completed') return 'success';
  if (progress.value.status === 'failed') return 'exception';
  return '';
});

const isRunning = computed(() => {
  return progress.value?.status === 'running';
});

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
  if (visible.value && props.taskId && isRunning.value) {
    refreshTimer = setInterval(() => {
      fetchProgress();
    }, refreshInterval.value);
  }
};

// 获取进度信息
const fetchProgress = async () => {
  if (!props.taskId) return;
  
  try {
    loading.value = true;
    const data = await hostInfoStore.getCollectionProgress(props.taskId);
    progress.value = data;
    
    // 如果任务完成或失败，停止刷新并触发事件
    if (data.status === 'completed' || data.status === 'failed' || data.status === 'cancelled') {
      clearRefreshTimer();
      if (data.status === 'completed') {
        emit('completed', data);
      }
    }
  } catch (error: any) {
    console.error('Failed to fetch collection progress:', error);
    // 不显示错误消息，避免干扰用户体验
  } finally {
    loading.value = false;
  }
};

// 监听对话框显示状态
watch(visible, (newVal) => {
  if (newVal && props.taskId) {
    fetchProgress();
    setupAutoRefresh();
  } else {
    clearRefreshTimer();
  }
});

// 监听任务ID变化
watch(() => props.taskId, (newTaskId) => {
  if (visible.value && newTaskId) {
    fetchProgress();
    setupAutoRefresh();
  }
});

// 监听运行状态变化
watch(isRunning, (newVal) => {
  if (visible.value && newVal) {
    setupAutoRefresh();
  } else {
    clearRefreshTimer();
  }
});

// 关闭对话框
const handleClose = () => {
  clearRefreshTimer();
  visible.value = false;
};

// 手动刷新
const handleRefresh = () => {
  fetchProgress();
};

// 组件卸载时清理
onUnmounted(() => {
  clearRefreshTimer();
});
</script>

<template>
  <el-dialog
    v-model="visible"
    :title="t('hostInfo.collectionProgress.title', '采集进度')"
    width="600px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div v-loading="loading" class="progress-container">
      <div v-if="progress" class="progress-content">
        <!-- 进度条 -->
        <div class="progress-section">
          <el-progress
            :percentage="progressPercent"
            :status="progressStatus"
            :stroke-width="20"
          />
        </div>

        <!-- 统计信息 -->
        <div class="stats-section">
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="stat-item">
                <div class="stat-label">{{ t('hostInfo.collectionProgress.total', '总数') }}</div>
                <div class="stat-value">{{ progress.total_count }}</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-item">
                <div class="stat-label">{{ t('hostInfo.collectionProgress.completed', '已完成') }}</div>
                <div class="stat-value success">{{ progress.completed_count }}</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-item">
                <div class="stat-label">{{ t('hostInfo.collectionProgress.failed', '失败') }}</div>
                <div class="stat-value error" v-if="progress.failed_count > 0">
                  {{ progress.failed_count }}
                </div>
                <div class="stat-value" v-else>{{ progress.failed_count }}</div>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 当前步骤 -->
        <div class="step-section" v-if="progress.current_step">
          <div class="step-label">{{ t('hostInfo.collectionProgress.currentStep', '当前步骤') }}</div>
          <div class="step-content">{{ progress.current_step }}</div>
        </div>

        <!-- 错误信息 -->
        <div class="error-section" v-if="progress.error_message">
          <el-alert
            :title="t('hostInfo.collectionProgress.error', '错误信息')"
            type="error"
            show-icon
            :closable="false"
          >
            <template #default>
              <div class="error-message-content">
                <pre class="error-text">{{ progress.error_message }}</pre>
              </div>
            </template>
          </el-alert>
        </div>

        <!-- 状态标签 -->
        <div class="status-section">
          <el-tag
            :type="progress.status === 'completed' ? 'success' : progress.status === 'failed' ? 'danger' : 'primary'"
            size="large"
          >
            {{ t(`hostInfo.collectionProgress.status.${progress.status}`, progress.status) }}
          </el-tag>
        </div>
      </div>

      <div v-else class="empty-content">
        <el-empty :description="t('hostInfo.collectionProgress.noData', '暂无进度数据')" />
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleRefresh" :loading="loading">
          {{ t('common.refresh', '刷新') }}
        </el-button>
        <el-button type="primary" @click="handleClose">
          {{ t('common.close', '关闭') }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped>
.progress-container {
  min-height: 200px;
  padding: 10px 0;
}

.progress-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.progress-section {
  margin-bottom: 10px;
}

.stats-section {
  padding: 20px;
  background-color: var(--el-fill-color-lighter);
  border-radius: var(--el-border-radius-base);
}

.stat-item {
  text-align: center;
}

.stat-label {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: var(--el-text-color-primary);
}

.stat-value.success {
  color: var(--el-color-success);
}

.stat-value.error {
  color: var(--el-color-danger);
}

.step-section {
  padding: 15px;
  background-color: var(--el-fill-color-light);
  border-radius: var(--el-border-radius-base);
  border-left: 3px solid var(--el-color-primary);
}

.step-label {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  margin-bottom: 5px;
}

.step-content {
  font-size: 14px;
  color: var(--el-text-color-primary);
  word-break: break-word;
}

.error-section {
  margin-top: 10px;
}

.error-message-content {
  max-height: 300px;
  overflow-y: auto;
}

.error-text {
  margin: 0;
  padding: 0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
  color: var(--el-color-danger);
  background-color: var(--el-fill-color-lighter);
  padding: 10px;
  border-radius: 4px;
}

.status-section {
  text-align: center;
  padding-top: 10px;
}

.empty-content {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

:deep(.el-progress-bar__outer) {
  background-color: var(--el-fill-color-lighter);
}

:deep(.el-progress-bar__inner) {
  transition: width 0.3s ease;
}
</style>
