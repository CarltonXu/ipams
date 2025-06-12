import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios';
import type { Notification, NotificationConfig } from '../types/notification'
import { API_CONFIG } from '../config/api';

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref<Notification[]>([])
  const total = ref(0)
  const loading = ref(false)
  const config = ref<NotificationConfig | null>(null)
  const _unreadCount = ref(0)

  // 获取通知配置
  const fetchConfig = async () => {
    try {
      const { data } = await axios.get(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.NOTIFICATION.CONFIG}`)
      config.value = data
    } catch (error) {
      console.error('获取通知配置失败:', error)
    }
  }

  // 更新通知配置
  const updateConfig = async (newConfig: Partial<NotificationConfig>) => {
    try {
      await axios.put(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.NOTIFICATION.CONFIG}`, newConfig)
      await fetchConfig()
      return true
    } catch (error) {
      console.error('更新配置失败:', error)
      return false
    }
  }

  // 测试通知配置
  const testConfig = async (type: 'email' | 'wechat', config: Record<string, any>) => {
    try {
      await axios.post(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.NOTIFICATION.TEST}`, { type, config })
      return true
    } catch (error) {
      console.error('测试发送失败:', error)
      return false
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
      console.error('获取通知历史失败:', error)
    } finally {
      loading.value = false
    }
  }

  // 标记通知为已读
  const markAsRead = async (id: string) => {
    try {
      await axios.put(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.NOTIFICATION.MARK_READ(id)}`)
      const notification = notifications.value.find(n => n.id === id)
      if (notification) {
        notification.read = true
      }
      await fetchUnreadCount()
      return true
    } catch (error) {
      console.error('标记已读失败:', error)
      return false
    }
  }

  // 标记所有通知为已读
  const markAllAsRead = async () => {
    try {
      await axios.put(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.NOTIFICATION.MARK_ALL_READ}`)
      notifications.value.forEach(n => n.read = true)
      await fetchUnreadCount()
      return true
    } catch (error) {
      console.error('全部标记已读失败:', error)
      return false
    }
  }

  // 删除通知
  const deleteNotification = async (id: string) => {
    try {
      await axios.delete(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.NOTIFICATION.DELETE(id)}`)
      notifications.value = notifications.value.filter(n => n.id !== id)
      total.value = total.value - 1
      await fetchUnreadCount()
      return true
    } catch (error) {
      console.error('删除通知失败:', error)
      return false
    }
  }

  // 清空所有通知
  const clearAll = async () => {
    try {
      await axios.delete(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.NOTIFICATION.CLEAR_ALL}`)
      notifications.value = []
      total.value = 0
      _unreadCount.value = 0
      return true
    } catch (error) {
      console.error('清空通知失败:', error)
      return false
    }
  }

  // 获取未读通知数量
  const fetchUnreadCount = async () => {
    try {
      const { data } = await axios.get(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.NOTIFICATION.UNREAD_COUNT}`)
      _unreadCount.value = data.count
    } catch (error) {
      console.error('获取未读通知数量失败:', error)
      _unreadCount.value = 0
    }
  }

  // 未读通知数量（对外暴露）
  const unreadCount = computed(() => _unreadCount.value)

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
    clearAll,
    fetchUnreadCount
  }
}) 