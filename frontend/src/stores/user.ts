import { defineStore } from 'pinia';
import axios from 'axios';
import type { User } from '../types/user';
import i18n from '../i18n';
import { API_CONFIG } from '../config/api';

const { t } = i18n.global;

interface FetchParams {
  page: number;
  pageSize: number;
  query?: string;
  column?: string;
  isAdmin?: boolean;
}

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
    async fetchFilteredUsers(params: FetchParams) {
      this.loading = true;
      try {
        const response = await axios.get(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.USER.LIST_BY_FILTER}`, {
          params: {
            page: params.page ?? this.currentPage,
            page_size: params.pageSize ?? this.pageSize,
            query: params.query || undefined,
            column: params.column === 'all' ? undefined : params.column,
            is_admin: params.isAdmin
          }
        });

        if (!response.data) {
          throw new Error(t('common.fetchError'));
        }

        this.syncUsersMap();

        return {
          users: response.data.users,
          total: response.data.total,
          currentPage: response.data.current_page,
          pages: response.data.pages
        };
      } catch (error: any) {
        console.error('Failed to fetch users:', error);
        throw new Error(error.response?.data?.message || t('settings.messages.fetchUsersFailed'));
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

        const response = await axios.get(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.USER.LIST_BY_ID(userId)}`);
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

        const response = await axios.get(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.USER.ME}`);
        this.currentUser = response.data;
        localStorage.setItem('user', JSON.stringify(response.data));
        return response.data;
      } catch (error: any) {
        if (onLogout) onLogout();
        throw new Error(error.response?.data?.message || t('settings.messages.fetchCurrentUserFailed'));
      }
    },

    /**
     * 添加用户
     */
    async addUser(userData: Partial<User>) {
      this.loading = true;
      try {
        const response = await axios.post(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.USER.CREATE}`, userData);
        return response.data;
      } catch (error: any) {
        console.error('Failed to add user:', error);
        if (error.response?.data?.error == 'Email already exists') {
          throw new Error(t('settings.messages.addUserFailed', { error: t('settings.messages.emailAlreadyExists') }));
        }
        if (error.response?.data?.error == 'Username already exists') {
          throw new Error(t('settings.messages.addUserFailed', { error: t('settings.messages.usernameAlreadyExists') }));
        }
        throw new Error(t('settings.messages.addUserFailed', { error: error.response?.data?.error }));
      } finally {
        this.loading = false;
      }
    },

    /**
     * 更新用户密码
     */
    async updatePassword(user_id: string, oldPassword: string, newPassword: string) {
      this.loading = true;
      try {
        const response = await axios.post(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.USER.CHANGE_PASSWORD}`, {
          user_id,
          old_password: oldPassword,
          new_password: newPassword
        });
        return response.data;
      } catch (error: any) {
        throw new Error(error.response?.data?.message || t('settings.messages.passwordFailed'));
      } finally {
        this.loading = false;
      }
    },
    /**
     * 更新用户信息
     */
    async updateUser(userData: Partial<User>) {
      this.loading = true;
      try {
        if (!userData.id) {
          throw new Error(t('settings.messages.userIdRequired'));
        }
        const response = await axios.put(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.USER.UPDATE(userData.id)}`, userData);
        const index = this.users.findIndex((user) => user.id === userData.id);
        if (index !== -1) {
          this.users[index] = { ...this.users[index], ...response.data };
          this.syncUsersMap();
        }
      } catch (error: any) {
        throw new Error(error.response?.data?.message || t('settings.messages.updateUserFailed'));
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
        await axios.delete(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.USER.DELETE(userId)}`);
        this.users = this.users.filter((user) => user.id !== userId);
        this.syncUsersMap();
      } catch (error: any) {
        throw new Error(error.response?.data?.message || t('settings.messages.deleteUserFailed'));
      } finally {
        this.loading = false;
      }
    },

    /**
     * 获取所有用户（不分页）
     */
    async fetchAllUsers() {
      try {
        const response = await axios.get(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.USER.LIST}`, {
          params: {
            no_pagination: true
          }
        });
        
        if (!response.data || !response.data.users) {
          throw new Error(t('common.fetchError'));
        }
        
        this.users = response.data.users;
        return this.users;
      } catch (err: any) {
        throw new Error(t('common.fetchError'));
      }
    },

    // 检查用户关联的 IP
    async checkUsersIPs(userIds: string[]) {
      try {
        const response = await axios.post(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.USER.LIST_IPS}`, { user_ids: userIds });
        return response.data;
      } catch (error: any) {
        throw new Error(error.response?.data?.message || t('common.fetchError'));
      }
    },

    // 批量删除用户
    async batchDeleteUsers(userIds: string[]) {
      this.loading = true;
      try {
        await axios.post(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.USER.BATCH_DELETE}`, { user_ids: userIds });
        // 更新本地数据
        this.users = this.users.filter(user => !userIds.includes(user.id));
        this.syncUsersMap();
      } catch (error: any) {
        if (error.response?.status === 400) {
          // 如果有关联的 IP，抛出特定错误
          if (error.response.data.error === 'Users have associated IPs') {
            throw new Error(t('user.management.messages.hasAssociatedIPs'));
          }
        }
        throw new Error(error.response?.data?.message || t('common.fetchError'));
      } finally {
        this.loading = false;
      }
    },

    // 更新用户状态
    async updateUserStatus(userId: string, isActive: boolean) {
      try {
        const response = await axios.put(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.USER.UPDATE_STATUS(userId)}`, { is_active: isActive });
        return response.data;
      } catch (error) {
        throw error;
      }
    }
  },
});
