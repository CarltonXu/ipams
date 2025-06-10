import axios from 'axios'
import type { NotificationConfig, NotificationResponse, NotificationFilters } from '../types/notification'

export const notificationApi = {
  // 获取通知配置
  getConfig() {
    return axios.get<NotificationConfig>('/api/v1/notification/config')
  },

  // 更新通知配置
  updateConfig(config: Partial<NotificationConfig>) {
    return axios.put('/api/v1/notification/config', config)
  },

  // 测试通知配置
  testConfig(type: 'email' | 'wechat', config: Record<string, any>) {
    return axios.post('/api/v1/notification/test', { type, config })
  },

  // 获取通知历史
  getHistory(params: NotificationFilters) {
    return axios.get<NotificationResponse>('/api/v1/notification/history', { params })
  },

  // 标记通知为已读
  markAsRead(id: number) {
    return axios.put(`/api/v1/notification/${id}/read`)
  },

  // 标记所有通知为已读
  markAllAsRead() {
    return axios.put('/api/v1/notification/read-all')
  },

  // 删除通知
  delete(id: number) {
    return axios.delete(`/api/v1/notification/${id}`)
  },

  // 清空所有通知
  clearAll() {
    return axios.delete('/api/v1/notification/clear-all')
  }
} 