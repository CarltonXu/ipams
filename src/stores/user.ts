import { defineStore } from 'pinia';
import axios from 'axios';
import type { User } from '../types/user';

export const useUserStore = defineStore('user', {
  state: () => ({
    users: [] as User[], // 用户列表
    usersMap: new Map<string, User>(), // 用户映射
    currentUser: null as User | null, // 当前用户
    loading: false, // 全局加载状态

    currentPage: 1, // 当前页码
    pageSize: 10, // 每页条数
    total: 0, // 总记录数
    pages: 0, // 总页数
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
     * 同步用户映射
     */
    syncUsersMap() {
      this.usersMap = new Map(this.users.map((user: User) => [user.id, user]));
    },

    /**
     * 获取用户列表（分页）
     */
    async fetchUsers(page?: number, pageSize?: number) {
      this.loading = true;
      const currentPage = page ?? this.currentPage;
      const currentPageSize = pageSize ?? this.pageSize;

      try {
        const response = await axios.get('/api/users', {
          params: { page: currentPage, page_size: currentPageSize },
        });
        const { users = [], total = 0 } = response.data;

        this.users = Array.isArray(users) ? users : [];
        this.total = total;
        this.pages = Math.ceil(total / currentPageSize);
        this.currentPage = currentPage;
        this.pageSize = currentPageSize;

        this.syncUsersMap();
      } catch (error: any) {
        console.error('Failed to fetch users:', error);
        throw new Error(error.response?.data?.message || '无法获取用户列表');
      } finally {
        this.loading = false;
      }
    },

    /**
     * 获取指定用户信息（支持缓存）
     */
    async fetchUserById(userId: string) {
      try {
        if (this.usersMap.has(userId)) {
          return this.usersMap.get(userId)!;
        }

        const response = await axios.get(`/api/users/${userId}`);
        const user = response.data;
        this.users.push(user);
        this.syncUsersMap();
        return user;
      } catch (error: any) {
        console.warn(`User with ID ${userId} not found.`);
        return null;
      }
    },

    /**
     * 获取当前用户信息（带缓存）
     */
    async fetchCurrentUser(onLogout?: () => void) {
      try {
        const cachedUser = localStorage.getItem('user');
        if (cachedUser) {
          const parsedUser = JSON.parse(cachedUser);
          this.currentUser = parsedUser;
          return parsedUser;
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
      this.loading = true;
      try {
        const response = await axios.post('/api/users', newUser);
        this.users.push(response.data);
        this.syncUsersMap();
      } catch (error: any) {
        console.error('Failed to add user:', error);
        throw new Error(error.response?.data?.message || '无法添加用户');
      } finally {
        this.loading = false;
      }
    },

    /**
     * 更新用户信息
     */
    async updateUser(updatedUser: Partial<User>) {
      this.loading = true;
      try {
        const response = await axios.put(`/api/users/${updatedUser.id}`, updatedUser);
        const index = this.users.findIndex((user) => user.id === updatedUser.id);
        if (index !== -1) {
          this.users[index] = { ...this.users[index], ...response.data };
          this.syncUsersMap();
        }
      } catch (error: any) {
        console.error('Failed to update user:', error);
        throw new Error(error.response?.data?.message || '无法更新用户');
      } finally {
        this.loading = false;
      }
    },

    /**
     * 删除用户
     */
    async deleteUser(userId: string) {
      this.loading = true;
      try {
        await axios.delete(`/api/users/${userId}`);
        this.users = this.users.filter((user) => user.id !== userId);
        this.syncUsersMap();
      } catch (error: any) {
        console.error('Failed to delete user:', error);
        throw new Error(error.response?.data?.message || '无法删除用户');
      } finally {
        this.loading = false;
      }
    },
  },
});
