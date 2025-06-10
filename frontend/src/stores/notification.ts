import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios';
import type { Notification, NotificationConfig } from '../types/notification'
import { notificationApi } from '../utils/notification'
import { useMessage } from 'naive-ui'
import { API_CONFIG } from '../config/api';

export const useNotificationStore = defineStore('notification', () => {
  const message = useMessage()
  const notifications = ref<Notification[]>([])
  const total = ref(0)
  const loading = ref(false)
  const config = ref<NotificationConfig | null>(null)

  // 获取通知配置
  const fetchConfig = async () => {
    try {
      const { data } = await axios.get(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.NOTIFICATION.CONFIG}`)
      config.value = data
    } catch (error) {
      message.error('获取通知配置失败')
    }
  }

  // 更新通知配置
  const updateConfig = async (newConfig: Partial<NotificationConfig>) => {
    try {
      await axios.put(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.NOTIFICATION.CONFIG}`, newConfig)
      await fetchConfig()
      message.success('更新配置成功')
    } catch (error) {
      message.error('更新配置失败')
    }
  }

  // 测试通知配置
  const testConfig = async (type: 'email' | 'wechat', config: Record<string, any>) => {
    try {
      await axios.post(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.NOTIFICATION.TEST}`, { type, config })
      message.success('测试发送成功')
    } catch (error) {
      message.error('测试发送失败')
    }
  }

  // 获取通知历史
  const fetchHistory = async (params: {
    type?: 'scan' | 'ip' | 'policy'
    status?: 'read' | 'unread'
    dateRange?: [Date, Date]
    page: number
    per_page: number
  }) => {
    try {
      loading.value = true
      const { data } = await axios.get(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.NOTIFICATION.HISTORY}`, { params })
      notifications.value = data.notifications
      total.value = data.total
    } catch (error) {
      message.error('获取通知历史失败')
    } finally {
      loading.value = false
    }
  }

  // 标记通知为已读
  const markAsRead = async (id: number) => {
    try {
      await axios.put(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.NOTIFICATION.MARK_READ(id)}`)
      const notification = notifications.value.find(n => n.id === id)
      if (notification) {
        notification.read = true
      }
      message.success('标记已读成功')
    } catch (error) {
      message.error('标记已读失败')
    }
  }

  // 标记所有通知为已读
  const markAllAsRead = async () => {
    try {
      await notificationApi.markAllAsRead()
      await axios.put(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.NOTIFICATION.MARK_ALL_READ}`)
      notifications.value.forEach(n => n.read = true)
      message.success('全部标记已读成功')
    } catch (error) {
      message.error('全部标记已读失败')
    }
  }

  // 删除通知
  const deleteNotification = async (id: number) => {
    try {
      await notificationApi.delete(id)
      notifications.value = notifications.value.filter(n => n.id !== id)
      message.success('删除通知成功')
    } catch (error) {
      message.error('删除通知失败')
    }
  }

  // 清空所有通知
  const clearAll = async () => {
    try {
      await axios.delete(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.NOTIFICATION.CLEAR_ALL}`)
      notifications.value = []
      total.value = 0
      message.success('清空通知成功')
    } catch (error) {
      message.error('清空通知失败')
    }
  }

  // 未读通知数量
  const unreadCount = computed(() => {
    return notifications.value.filter(n => !n.read).length
  })

  return {
    notifications,
    total,
    loading,
    config,
    unreadCount,
    fetchConfig,
    updateConfig,
    testConfig,
    fetchHistory,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    clearAll
  }
}) 