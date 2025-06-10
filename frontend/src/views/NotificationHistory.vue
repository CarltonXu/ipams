<template>
  <n-card title="通知历史">
    <!-- 工具栏 -->
    <div class="toolbar">
      <n-space>
        <n-button
          type="primary"
          @click="markAllAsRead"
          :loading="markingAllAsRead"
        >
          全部标记为已读
        </n-button>
        <n-button
          type="error"
          @click="clearAll"
          :loading="clearingAll"
        >
          清空通知
        </n-button>
      </n-space>
      
      <n-space>
        <n-select
          v-model:value="filters.type"
          style="width: 120px"
          placeholder="通知类型"
          clearable
          :options="typeOptions"
        />
        
        <n-select
          v-model:value="filters.status"
          style="width: 120px"
          placeholder="状态"
          clearable
          :options="statusOptions"
        />
        
        <n-date-picker
          v-model:value="filters.dateRange"
          type="daterange"
          clearable
          :show-time="true"
          format="yyyy-MM-dd HH:mm:ss"
        />
        
        <n-button
          type="primary"
          @click="handleSearch"
        >
          搜索
        </n-button>
      </n-space>
    </div>
    
    <!-- 通知列表 -->
    <n-list
      :loading="loading"
      :data="notifications"
    >
      <template #render-item="{ item }">
        <n-list-item>
          <n-thing
            :title="item.title"
            :title-extra="item.created_at"
          >
            <template #header-extra>
              <n-tag
                :type="getTypeTagType(item.type)"
                size="small"
              >
                {{ getTypeLabel(item.type) }}
              </n-tag>
            </template>
            
            <template #description>
              <div class="notification-content">
                <p>{{ item.content }}</p>
                <div class="notification-meta">
                  <n-tag
                    :type="item.read ? 'default' : 'warning'"
                    size="small"
                  >
                    {{ item.read ? '已读' : '未读' }}
                  </n-tag>
                </div>
              </div>
            </template>
            
            <template #action>
              <n-space>
                <n-button
                  v-if="!item.read"
                  type="primary"
                  text
                  @click="markAsRead(item.id)"
                >
                  标记已读
                </n-button>
                <n-button
                  type="error"
                  text
                  @click="deleteNotification(item.id)"
                >
                  删除
                </n-button>
              </n-space>
            </template>
          </n-thing>
        </n-list-item>
      </template>
    </n-list>
    
    <!-- 分页 -->
    <div class="pagination">
      <n-pagination
        v-model:page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :item-count="total"
        :page-sizes="[10, 20, 30, 40]"
        show-size-picker
        show-quick-jumper
        @update:page="handlePageChange"
        @update:page-size="handlePageSizeChange"
      />
    </div>
  </n-card>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useDialog } from 'naive-ui'
import { useNotificationStore } from '../stores/notification'
import type { Notification } from '../types/notification'

const dialog = useDialog()
const notificationStore = useNotificationStore()

// 状态
const loading = ref(false)
const markingAllAsRead = ref(false)
const clearingAll = ref(false)
const total = ref(0)

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10
})

// 筛选条件
const filters = reactive({
  type: undefined as 'scan' | 'ip' | 'policy' | undefined,
  status: undefined as 'read' | 'unread' | undefined,
  dateRange: null as [Date, Date] | null
})

// 选项
const typeOptions = [
  { label: '扫描通知', value: 'scan' },
  { label: 'IP管理通知', value: 'ip' },
  { label: '策略通知', value: 'policy' }
]

const statusOptions = [
  { label: '未读', value: 'unread' },
  { label: '已读', value: 'read' }
]

// 获取通知列表
const notifications = computed(() => notificationStore.notifications)

// 加载通知历史
const loadNotifications = async () => {
  try {
    loading.value = true
    await notificationStore.fetchHistory({
      type: filters.type,
      status: filters.status,
      dateRange: filters.dateRange || undefined,
      page: pagination.page,
      per_page: pagination.pageSize
    })
    total.value = notificationStore.total
  } catch (error) {
    // 错误处理已在 store 中完成
  } finally {
    loading.value = false
  }
}

// 标记为已读
const markAsRead = async (id: number) => {
  await notificationStore.markAsRead(id)
}

// 全部标记为已读
const markAllAsRead = async () => {
  try {
    markingAllAsRead.value = true
    await notificationStore.markAllAsRead()
  } finally {
    markingAllAsRead.value = false
  }
}

// 删除通知
const deleteNotification = async (id: number) => {
  dialog.warning({
    title: '确认删除',
    content: '确定要删除这条通知吗？',
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      await notificationStore.deleteNotification(id)
    }
  })
}

// 清空所有通知
const clearAll = () => {
  dialog.warning({
    title: '确认清空',
    content: '确定要清空所有通知吗？此操作不可恢复。',
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        clearingAll.value = true
        await notificationStore.clearAll()
      } finally {
        clearingAll.value = false
      }
    }
  })
}

// 处理搜索
const handleSearch = () => {
  pagination.page = 1
  loadNotifications()
}

// 处理分页变化
const handlePageChange = (page: number) => {
  pagination.page = page
  loadNotifications()
}

// 处理每页条数变化
const handlePageSizeChange = (pageSize: number) => {
  pagination.pageSize = pageSize
  pagination.page = 1
  loadNotifications()
}

// 获取通知类型标签样式
const getTypeTagType = (type: Notification['type']) => {
  const typeMap = {
    scan: 'info',
    ip: 'success',
    policy: 'warning'
  }
  return typeMap[type]
}

// 获取通知类型标签文本
const getTypeLabel = (type: Notification['type']) => {
  const typeMap = {
    scan: '扫描通知',
    ip: 'IP管理通知',
    policy: '策略通知'
  }
  return typeMap[type]
}

onMounted(() => {
  loadNotifications()
})
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 24px;
}

.notification-content {
  .notification-meta {
    margin-top: 8px;
  }
}

.pagination {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}
</style> 