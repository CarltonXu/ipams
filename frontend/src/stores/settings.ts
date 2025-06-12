import { defineStore } from 'pinia';
import axios from 'axios';
import type { Notification, NotificationConfig } from '../types/notification';
import { API_CONFIG } from '../config/api';

interface SettingsState {
  // 基本设置
  language: string;
  theme: 'light' | 'dark';
  notificationsEnabled: boolean;
  timeFormat: '12h' | '24h';
  
  // 通知配置
  emailConfig: {
    enabled: boolean;
    smtpServer: string;
    smtpPort: number;
    smtpUsername: string;
    smtpPassword: string;
    smtpFrom: string;
  };
  wechatConfig: {
    enabled: boolean;
    webhookUrl: string;
  };
  eventConfig: {
    scanCompleted: boolean;
    scanFailed: boolean;
    ipClaimed: boolean;
    ipReleased: boolean;
    policyCreated: boolean;
    policyUpdated: boolean;
    policyDeleted: boolean;
  };
  
  // 通知历史
  notificationList: Notification[];
  total: number;
  loading: boolean;
}

export const useSettingsStore = defineStore('settings', {
  state: (): SettingsState => ({
    // 基本设置
    language: localStorage.getItem('language') || 'zh',
    theme: (localStorage.getItem('theme') as 'light' | 'dark') || 'light',
    notificationsEnabled: localStorage.getItem('notifications') === 'true',
    timeFormat: (localStorage.getItem('timeFormat') as '12h' | '24h') || '24h',
    
    // 通知配置
    emailConfig: {
      enabled: false,
      smtpServer: '',
      smtpPort: 587,
      smtpUsername: '',
      smtpPassword: '',
      smtpFrom: ''
    },
    wechatConfig: {
      enabled: false,
      webhookUrl: ''
    },
    eventConfig: {
      scanCompleted: true,
      scanFailed: true,
      ipClaimed: true,
      ipReleased: true,
      policyCreated: true,
      policyUpdated: true,
      policyDeleted: true
    },
    
    // 通知历史
    notificationList: [],
    total: 0,
    loading: false
  }),

  getters: {
    // 未读通知数量
    unreadCount: (state) => {
      return state.notificationList.filter(n => !n.read).length;
    }
  },

  actions: {
    // 基本设置
    setLanguage(lang: string) {
      this.language = lang;
      localStorage.setItem('language', lang);
    },

    setTheme(theme: 'light' | 'dark') {
      this.theme = theme;
      localStorage.setItem('theme', theme);
    },

    setNotificationsEnabled(enabled: boolean) {
      this.notificationsEnabled = enabled;
      localStorage.setItem('notifications', String(enabled));
    },

    setTimeFormat(format: '12h' | '24h') {
      this.timeFormat = format;
      localStorage.setItem('timeFormat', format);
    },

    // 通知配置
    async fetchConfig() {
      try {
        const { data } = await axios.get(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.NOTIFICATION.CONFIG}`);
        this.emailConfig = data.emailConfig;
        this.wechatConfig = data.wechatConfig;
        this.eventConfig = data.eventConfig;
      } catch (error) {
        console.error('获取通知配置失败:', error);
      }
    },

    async updateConfig(newConfig: Partial<NotificationConfig>) {
      try {
        await axios.put(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.NOTIFICATION.CONFIG}`, newConfig);
        await this.fetchConfig();
        return true;
      } catch (error) {
        console.error('更新配置失败:', error);
        return false;
      }
    },

    async testConfig(type: 'email' | 'wechat', config: Record<string, any>) {
      try {
        await axios.post(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.NOTIFICATION.TEST}`, { type, config });
        return true;
      } catch (error) {
        console.error('测试发送失败:', error);
        return false;
      }
    },

    // 通知历史
    async fetchHistory(params: {
      type?: 'scan' | 'ip' | 'policy';
      status?: 'read' | 'unread';
      dateRange?: [Date, Date];
      page: number;
      per_page: number;
    }) {
      try {
        this.loading = true;
        const { data } = await axios.get(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.NOTIFICATION.HISTORY}`, { params });
        this.notificationList = data.notifications;
        this.total = data.total;
      } catch (error) {
        console.error('获取通知历史失败:', error);
      } finally {
        this.loading = false;
      }
    },

    async markAsRead(id: string) {
      try {
        await axios.put(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.NOTIFICATION.MARK_READ(id)}`);
        const notification = this.notificationList.find(n => n.id === id);
        if (notification) {
          notification.read = true;
        }
        return true;
      } catch (error) {
        console.error('标记已读失败:', error);
        return false;
      }
    },

    async markAllAsRead() {
      try {
        await axios.put(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.NOTIFICATION.MARK_ALL_READ}`);
        this.notificationList.forEach(n => n.read = true);
        return true;
      } catch (error) {
        console.error('全部标记已读失败:', error);
        return false;
      }
    },

    async deleteNotification(id: string) {
      try {
        await axios.delete(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.NOTIFICATION.DELETE(id)}`);
        this.notificationList = this.notificationList.filter(n => n.id !== id);
        return true;
      } catch (error) {
        console.error('删除通知失败:', error);
        return false;
      }
    },

    async clearAll() {
      try {
        await axios.delete(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.NOTIFICATION.CLEAR_ALL}`);
        this.notificationList = [];
        this.total = 0;
        return true;
      } catch (error) {
        console.error('清空通知失败:', error);
        return false;
      }
    }
  }
}); 