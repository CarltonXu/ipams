<template>
  <div class="notification-history">
    <el-card shadow="always" class="main-card">
      <div class="page-title">
        <div class="page-header">
          <h2>{{ t('notifications.history.title') }}</h2>
          <p class="subtitle">{{ t('notifications.history.subtitle') }}</p>
        </div>
      </div>

      <div class="action-bar">
        <el-button type="primary" @click="handleMarkAllAsRead" :disabled="!hasUnread">
          <el-icon><Check /></el-icon>
          {{ t('notifications.history.actions.markAllAsRead') }}
        </el-button>
        <el-button type="danger" @click="handleClearAll" :disabled="!notifications.length">
          <el-icon><Delete /></el-icon>
          {{ t('notifications.history.actions.clearAll') }}
        </el-button>
    </div>
    
      <el-table
      :data="notifications"
        v-loading="loading"
        style="width: 100%"
        border
        class="notification-table"
    >
        <el-table-column prop="title" :label="t('notifications.history.columns.title')" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span :class="{ 'read-notification': row.read }">{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="content" :label="t('notifications.history.columns.content')" min-width="300" show-overflow-tooltip>
          <template #default="{ row }">
            <span :class="{ 'read-notification': row.read }">{{ row.content }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="type" :label="t('notifications.history.columns.type')" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.type)" effect="light">
              {{ t(`notifications.history.types.${row.type}`) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="read" :label="t('notifications.history.columns.status')" width="100">
          <template #default="{ row }">
            <el-tag :type="row.read ? 'info' : 'danger'" effect="light">
              {{ row.read ? t('notifications.history.status.read') : t('notifications.history.status.unread') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" :label="t('notifications.history.columns.createdAt')" width="180">
          <template #default="{ row }">
            <span :class="{ 'read-notification': row.read }">{{ formatDate(row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('notifications.history.columns.actions')" width="200" fixed="right">
          <template #default="{ row }">
            <el-space>
              <el-button
                v-if="!row.read"
                type="primary"
                size="small"
                @click="handleMarkAsRead(row.id)"
              >
                <el-icon><Check /></el-icon>
                {{ t('notifications.history.status.read') }}
              </el-button>
              <el-button
                type="danger"
                    size="small"
                @click="handleDelete(row.id)"
              >
                <el-icon><Delete /></el-icon>
                {{ t('common.delete') }}
              </el-button>
            </el-space>
            </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
        :page-sizes="[10, 20, 30, 40]"
          :total="total"
          background
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handlePageSizeChange"
          @current-change="handlePageChange"
      />
    </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useNotificationStore } from '../stores/notification'
import { ElMessage } from 'element-plus'
import type { Notification } from '../types/notification'
import { formatDate } from '../utils/date'
import { Check, Delete } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const notificationStore = useNotificationStore()

const loading = ref(false)
const notifications = ref<Notification[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const hasUnread = computed(() => {
  return notifications.value.some(n => !n.read)
})

const getTypeTagType = (type: string) => {
  const typeMap: Record<string, string> = {
    scan: 'info',
    ip: 'success',
    policy: 'warning'
  }
  return typeMap[type] || 'default'
}

const loadNotifications = async () => {
  try {
    loading.value = true
    await notificationStore.fetchHistory({
      page: currentPage.value,
      per_page: pageSize.value
    })
    notifications.value = notificationStore.notifications
    total.value = notificationStore.total
  } catch (error) {
    ElMessage.error(t('notifications.history.messages.fetchFailed'))
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  loadNotifications()
}

const handlePageSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  loadNotifications()
}

const handleMarkAsRead = async (id: string) => {
  try {
    const success = await notificationStore.markAsRead(id)
    if (success) {
      ElMessage.success(t('notifications.history.messages.markAsReadSuccess'))
      loadNotifications()
    } else {
      ElMessage.error(t('notifications.history.messages.markAsReadFailed'))
    }
  } catch (error) {
    ElMessage.error(t('notifications.history.messages.markAsReadFailed'))
  }
}

const handleMarkAllAsRead = async () => {
  try {
    const success = await notificationStore.markAllAsRead()
    if (success) {
      ElMessage.success(t('notifications.history.messages.markAllAsReadSuccess'))
      loadNotifications()
    } else {
      ElMessage.error(t('notifications.history.messages.markAllAsReadFailed'))
    }
  } catch (error) {
    ElMessage.error(t('notifications.history.messages.markAllAsReadFailed'))
  }
}

const handleDelete = async (id: string) => {
      try {
    const success = await notificationStore.deleteNotification(id)
    if (success) {
      ElMessage.success(t('notifications.history.messages.deleteSuccess'))
      loadNotifications()
    } else {
      ElMessage.error(t('notifications.history.messages.deleteFailed'))
    }
  } catch (error) {
    ElMessage.error(t('notifications.history.messages.deleteFailed'))
}
}

const handleClearAll = async () => {
  try {
    const success = await notificationStore.clearAll()
    if (success) {
      ElMessage.success(t('notifications.history.messages.clearAllSuccess'))
  loadNotifications()
    } else {
      ElMessage.error(t('notifications.history.messages.clearAllFailed'))
    }
  } catch (error) {
    ElMessage.error(t('notifications.history.messages.clearAllFailed'))
  }
}

onMounted(() => {
  loadNotifications()
})
</script>

<style scoped>
.notification-history {
  padding: 20px;
}

.main-card {
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

.action-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 12px;
}

.notification-table {
  margin-bottom: 20px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

:deep(.el-button) {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

:deep(.el-button .el-icon) {
  margin-right: 4px;
}

:deep(.el-table .el-table__cell) {
  padding: 12px 0;
}

:deep(.el-tag) {
  border-radius: 4px;
}

:deep(.el-table) {
  --el-table-border-color: var(--el-border-color-lighter);
  --el-table-header-bg-color: var(--el-fill-color-light);
}

:deep(.el-table th) {
  font-weight: 600;
  background-color: var(--el-fill-color-light);
}

:deep(.el-table--border) {
  border-radius: 4px;
  overflow: hidden;
}

.read-notification {
  color: #909399; /* Element Plus 的灰色文字颜色 */
}
</style> 