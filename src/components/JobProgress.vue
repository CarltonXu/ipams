<template>
  <div class="job-progress">
    <el-card class="progress-card">
      <template #header>
        <div class="card-header">
          <span>{{ t('scan.job.progress.title') }}</span>
          <el-button 
            v-if="canCancel"
            type="danger" 
            size="small"
            :loading="cancelling"
            @click="handleCancel"
          >
            {{ t('scan.job.progress.cancel') }}
          </el-button>
        </div>
      </template>
      
      <div v-for="job in jobs" :key="job.id" class="job-item">
        <div class="job-header">
          <span class="job-name">{{ job.subnet_name }}</span>
          <el-tag :type="getStatusType(job.status)" size="small">
            {{ t(`scan.job.status.${job.status}`) }}
          </el-tag>
        </div>
        
        <el-progress 
          :percentage="job.progress" 
          :status="getProgressStatus(job.status)"
        />
        
        <div class="job-info">
          <span>{{ t('scan.job.progress.machinesFound') }}: {{ job.machines_found }}</span>
          <span v-if="job.error_message" class="error-message">
            {{ job.error_message }}
          </span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { useScanPolicyStore } from '../stores/scanPolicy'

const props = defineProps<{
  jobIds: string[]
}>()

const { t } = useI18n()
const policyStore = useScanPolicyStore()
const jobs = ref<any[]>([])
const cancelling = ref(false)
const updateInterval = ref<number>()

// 是否可以取消任务
const canCancel = computed(() => {
  return jobs.value.some(job => ['pending', 'running'].includes(job.status))
})

// 是否所有任务都已完成
const allJobsCompleted = computed(() => {
  return jobs.value.every(job => ['completed', 'failed', 'cancelled'].includes(job.status))
})

// 获取状态对应的类型
const getStatusType = (status: string) => {
  switch (status) {
    case 'running':
      return 'primary'
    case 'completed':
      return 'success'
    case 'failed':
      return 'danger'
    case 'cancelled':
      return 'info'
    default:
      return 'warning'
  }
}

// 获取进度条状态
const getProgressStatus = (status: string) => {
  switch (status) {
    case 'running':
      return ''
    case 'completed':
      return 'success'
    case 'failed':
      return 'exception'
    case 'cancelled':
      return 'warning'
    default:
      return ''
  }
}

// 更新任务状态
const updateJobs = async () => {
  try {
    const updatedJobs = await Promise.all(
      props.jobIds.map(async (jobId) => {
        const response = await policyStore.getJobStatus(jobId)
        return response.job
      })
    )
    jobs.value = updatedJobs

    // 如果所有任务都已完成，停止更新
    if (allJobsCompleted.value) {
      if (updateInterval.value) {
        clearInterval(updateInterval.value)
        updateInterval.value = undefined
      }
    }
  } catch (error: any) {
    console.error('Failed to update jobs:', error)
  }
}

// 取消任务
const handleCancel = async () => {
  try {
    cancelling.value = true
    await Promise.all(
      jobs.value
        .filter(job => ['pending', 'running'].includes(job.status))
        .map(job => policyStore.cancelJob(job.id))
    )
    ElMessage.success(t('scan.job.progress.cancelSuccess'))
    await updateJobs()
  } catch (error: any) {
    ElMessage.error(error.message || t('scan.job.progress.cancelFailed'))
  } finally {
    cancelling.value = false
  }
}

// 组件挂载时开始定时更新
onMounted(() => {
  updateJobs()
  // 每1秒更新一次状态
  updateInterval.value = window.setInterval(updateJobs, 1000)
})

// 组件卸载时清除定时器
onUnmounted(() => {
  if (updateInterval.value) {
    clearInterval(updateInterval.value)
  }
})
</script>

<style scoped>
.job-progress {
  margin: 20px 0;
}

.progress-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.job-item {
  margin-bottom: 20px;
  padding: 10px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 4px;
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.job-name {
  font-weight: bold;
}

.job-info {
  margin-top: 10px;
  display: flex;
  justify-content: space-between;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.error-message {
  color: var(--el-color-danger);
}
</style> 