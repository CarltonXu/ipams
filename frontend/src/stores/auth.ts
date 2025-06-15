import { defineStore } from 'pinia';
import axios from 'axios';
import type { AuthState, LoginCredentials, RegisterCredentials, User } from '../types/user';
import i18n from '../i18n';
import { API_CONFIG } from '../config/api';

const { t } = i18n.global;

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null as User | null,
    token: null as string | null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
  },

  actions: {
    async login(credentials: LoginCredentials) {
      try {
        const response = await axios.post(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.AUTH.LOGIN}`, credentials);
        const { token, user } = response.data.data;
        
        this.token = token;
        this.user = user;
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(user));

        // Set token for all subsequent requests
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

        return response.data;
      } catch (error: any) {
        if (error.response?.data) {
          // 直接返回后端错误信息
          throw error;
        } else {
          // 网络错误等其他错误
          throw new Error(t('auth.loginError'));
        }
      }
    },

    async register(credentials: RegisterCredentials) {
      try {
        const response = await axios.post(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.AUTH.REGISTER}`, credentials);
        return response.data;
      } catch (error: any) {
        throw new Error(error.response?.data?.error || t('auth.registerError'));
      }
    },

    async updateUserInfo(userData: Partial<User>) {
      if (this.user) {
        this.user = { ...this.user, ...userData };
      }
      localStorage.setItem('user', JSON.stringify(this.user));
    },

    async logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      delete axios.defaults.headers.common['Authorization'];
    },

    async getCaptcha() {
      return await axios.get(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.AUTH.CAPTCHA}`);
    },
  },
});