import { defineStore } from 'pinia';

interface SettingsState {
  language: string;
  theme: string;
  notifications: boolean;
  timeFormat: string;
}

export const useSettingsStore = defineStore('settings', {
  state: (): SettingsState => ({
    language: localStorage.getItem('language') || 'zh',
    theme: localStorage.getItem('theme') || 'light',
    notifications: localStorage.getItem('notifications') === 'true',
    timeFormat: localStorage.getItem('timeFormat') || '24h'
  }),

  actions: {
    setLanguage(lang: string) {
      this.language = lang;
      localStorage.setItem('language', lang);
    },

    setTheme(theme: string) {
      this.theme = theme;
      localStorage.setItem('theme', theme);
    },

    setNotifications(enabled: boolean) {
      this.notifications = enabled;
      localStorage.setItem('notifications', String(enabled));
    },

    setTimeFormat(format: string) {
      this.timeFormat = format;
      localStorage.setItem('timeFormat', format);
    }
  }
}); 