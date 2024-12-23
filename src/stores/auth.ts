import { defineStore } from 'pinia';
import axios from 'axios';
import type { AuthState, LoginCredentials, RegisterCredentials } from '../types/user';

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')!) : null,
    token: localStorage.getItem('token'),
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
  },

  actions: {
    async login(credentials: LoginCredentials) {
      try {
        const response = await axios.post('/api/auth/login', credentials);
        const { token, user } = response.data;

        this.token = token;
        this.user = user;
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(user));  // 保存 user 信息

        // Set token for all subsequent requests
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

        return user;
      } catch (error: any) {
        throw new Error(error.response?.data?.message || 'Login failed');
      }
    },

    async register(credentials: RegisterCredentials) {
      try {
        const response = await axios.post('/api/auth/register', credentials);
        return response.data;
      } catch (error: any) {
        throw new Error(error.response?.data?.error || 'Registration failed');
      }
    },

    async logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      delete axios.defaults.headers.common['Authorization'];
    },
  },
});