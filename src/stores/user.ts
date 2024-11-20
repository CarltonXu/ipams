import { defineStore } from 'pinia';
import axios from 'axios';
import type { User } from '../types/user';

export const useUserStore = defineStore('user', {
  state: () => ({
    users: [] as User[], // 用户列表
    usersMap: new Map<string, User>(), // 用于快速查找的映射
    currentUser: null as User | null, // 当前用户
    totalUsers: 0, // 用户总数
    loading: false, // 加载状态
  }),

  getters: {
    getAllUsers: (state) => state.users,
    getCurrentUser: (state) => state.currentUser,
    getUserById: (state) => (id: string) => state.usersMap.get(id),
    getAdmins: (state) => state.users.filter((user) => user.is_admin),
    isAdmin: (state) => state.currentUser?.is_admin || false,
  },

  actions: {
    /**
     * 获取所有用户
     * 支持分页
     */
    async fetchUsers(page = 1, page_size = 10) {
      this.loading = true;
      try {
        const response = await axios.get(`/api/users?page=${page}&page_size=${page_size}`);
        this.users = response.data.users;
        this.totalUsers = response.data.total;
        this.usersMap = new Map(response.data.users.map((user: User) => [user.id, user]));
      } catch (error: any) {
        console.error('Failed to fetch users:', error);
        throw new Error(error.response?.data?.message || '无法获取用户列表');
      } finally {
        this.loading = false;
      }
    },

    /**
     * 根据用户ID获取用户信息
     */
    async fetchUserById(userId: string) {
      try {
        const cachedUser = this.usersMap.get(userId);
        if (cachedUser) return cachedUser;

        const response = await axios.get(`/api/users/${userId}`);
        return response.data;
      } catch (error: any) {
        console.warn(`User with ID ${userId} not found.`);
        return null;
      }
    },

    /**
     * 获取当前用户信息
     * 支持本地缓存
     */
    async fetchCurrentUser(onLogout?: () => void) {
      try {
        const cachedUser = localStorage.getItem('user');
        if (cachedUser) {
          this.currentUser = JSON.parse(cachedUser);
          return this.currentUser;
        }

        const response = await axios.get('/api/users/me');
        this.currentUser = response.data;
        localStorage.setItem('user', JSON.stringify(response.data));
        return response.data;
      } catch (error: any) {
        if (onLogout) onLogout();
        throw new Error(error.response?.data?.message || '获取当前用户失败');
      }
    },

    /**
     * 添加用户
     */
    async addUser(newUser: Partial<User>) {
      try {
        const response = await axios.post('/api/users', newUser);
        this.users.push(response.data);
        this.usersMap.set(response.data.id, response.data);
      } catch (error: any) {
        console.error('Failed to add user:', error);
        throw new Error(error.response?.data?.message || '无法添加用户');
      }
    },

    /**
     * 更新用户信息
     */
    async updateUser(updatedUser: Partial<User>) {
      try {
        const response = await axios.put(`/api/users/${updatedUser.id}`, updatedUser);
        const index = this.users.findIndex((user) => user.id === updatedUser.id);
        if (index !== -1) {
          this.users[index] = { ...this.users[index], ...response.data };
          this.usersMap.set(response.data.id, response.data);
        }
      } catch (error: any) {
        console.error('Failed to update user:', error);
        throw new Error(error.response?.data?.message || '无法更新用户');
      }
    },

    /**
     * 删除用户
     */
    async deleteUser(userId: string) {
      try {
        await axios.delete(`/api/users/${userId}`);
        this.users = this.users.filter((user) => user.id !== userId);
        this.usersMap.delete(userId);
      } catch (error: any) {
        console.error('Failed to delete user:', error);
        throw new Error(error.response?.data?.message || '无法删除用户');
      }
    },
  },
});
