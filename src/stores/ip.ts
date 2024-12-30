import { defineStore } from 'pinia';
import axios from 'axios';
import i18n from '../i18n'; // 导入 i18n 实例

const { t } = i18n.global; // 在 store 中使用 global t 函数
import type { IP } from '../types/ip';

interface FetchParams {
  page: number;
  pageSize: number;
  query?: string;
  column?: string;
  status?: string;
  sortBy?: string;
  sortOrder?: string;
}

export const useIPStore = defineStore('ip', {
  state: () => ({
    ips: [] as IP[],          // 所有 IP 数据（用于前端全局筛选）
    paginatedIPs: [] as IP[], // 当前页的 IP 数据（后端分页时使用）
    loading: false,           // 加载状态
    error: null as string | null, // 错误信息

    useGlobalFilter: true,   // 是否使用前端全局筛选
    currentPage: 1,           // 当前页码
    pageSize: 10,             // 每页条数
    total: 0,                 // 总记录数
    pages: 0,                 // 总页数
  }),

  getters: {
    // 获取当前显示的数据，支持全局筛选或分页模式
    displayedIPs: (state) => {
      if (state.useGlobalFilter) {
        const start = (state.currentPage - 1) * state.pageSize;
        return state.ips.slice(start, start + state.pageSize);
      }
      return state.paginatedIPs;
    },

    // 根据 IP 地址排序
    sortedIPs: (state) => [...state.displayedIPs].sort((a, b) => a.ip_address.localeCompare(b.ip_address)),
  },

  actions: {
    // 获取所有数据（全局筛选模式）
    async fetchAllIPs() {
      this.loading = true;
      try {
        const response = await axios.get('/api/ips'); // 不带分页参数
        this.ips = Array.isArray(response.data) ? response.data : [];
        this.total = this.ips.length;
      } catch (err: any) {
        this.error = err.message;
        this.ips = [];
      } finally {
        this.loading = false;
      }
    },

    // 获取分页数据
    async fetchPaginatedIPs(page = this.currentPage, pageSize = this.pageSize) {
      this.loading = true;
      this.currentPage = page;
      this.pageSize = pageSize;
      try {
        const response = await axios.get('/api/ips', {
          params: { page: page, page_size: pageSize } // 发送分页参数
        });
        this.paginatedIPs = Array.isArray(response.data.ips) ? response.data.ips : [];
        this.total = response.data.total || 0;
        this.pages = response.data.pages || 0;
        this.currentPage = response.data.current_page || 1;
      } catch (err: any) {
        this.error = err.message;
        this.paginatedIPs = [];
        this.total = 0;
      } finally {
        this.loading = false;
      }
    },

    // 根据模式加载数据
    async loadIPs() {
      if (this.useGlobalFilter) {
        await this.fetchAllIPs();
      } else {
        await this.fetchPaginatedIPs();
      }
    },

    // 分页处理
    async setPage(page: number) {
      if (page > 0 && page <= Math.ceil(this.total / this.pageSize)) {
        this.currentPage = page;
        if (!this.useGlobalFilter) {
          await this.fetchPaginatedIPs();
        }
      }
    },

    // 分配 IP
    async claimIP(ipId: string, data: { 
      device_name: string; 
      purpose: string;
      os_type: string;
      device_type: string;
      manufacturer: string;
      model: string;
      assigned_user_id?: string;
    }) {
      try {
        await axios.post(`/api/ips/${ipId}/claim`, data);
        await this.fetchAllIPs(); // 更新列表
      } catch (err: any) {
        this.error = err.message;
        throw new Error(t('ip.dialog.claim.error', { error: err.message || t('common.unknownError') }));
      }
    },

    // 更新 IP
    async updateIP(ipId: string, data: {
      os_type: string;
      device_name: string;
      device_type: string;
      manufacturer: string;
      model: string;
      purpose: string;
      assigned_user_id?: string;
    }) {
      try {
        await axios.post(`/api/ips/${ipId}`, data);
        return true;
      } catch (err: any) {
        throw new Error(t('ip.dialog.update.error', { error: err.error }));
      }
    },

    // 批量认领 IP
    async batchClaimIPs(ipConfigs: Array<{
      id: string;
      device_name: string;
      purpose: string;
      os_type: string;
      device_type: string;
      manufacturer: string;
      model: string;
      assigned_user_id?: string | null;
    }>) {
      try {
        await Promise.all(ipConfigs.map(config => 
          axios.post(`/api/ips/${config.id}/claim`, {
            device_name: config.device_name,
            purpose: config.purpose,
            os_type: config.os_type,
            device_type: config.device_type,
            manufacturer: config.manufacturer,
            model: config.model,
            assigned_user_id: config.assigned_user_id,
          })
        ));
        await this.fetchAllIPs();
      } catch (err: any) {
        this.error = err.message;
        throw new Error(t('ip.dialog.claim.error', { error: err.message }));
      }
    },

    // 批量更新 IP
    async batchUpdateIPs(ips: string[], data: {
      os_type: string;
      device_name: string;
      device_type: string;
      manufacturer: string;
      model: string;
      purpose: string;
      assigned_user_id?: string;
    }) {
      try {
        await Promise.all(ips.map(ipId => 
          axios.post(`/api/ips/${ipId}`, data)
        ));
        return true;
      } catch (err: any) {
        this.error = err.message;
        throw new Error(t('ip.dialog.update.error', { error: err.message }));
      }
    },

    // 获取过滤后的分页数据
    async fetchFilteredIPs(params: FetchParams) {
      this.loading = true;
      try {
        const response = await axios.get('/api/ips', {
          params: {
            page: params.page,
            page_size: params.pageSize,
            query: params.query || undefined,
            column: params.column === 'all' ? undefined : params.column,
            status: params.status === 'all' ? undefined : params.status,
            sort_by: params.sortBy || undefined,
            sort_order: params.sortOrder || undefined
          }
        });
        
        // 更新 store 中的状态
        this.total = response.data.total;
        this.currentPage = response.data.current_page;
        
        return {
          ips: response.data.ips,
          total: response.data.total,
          currentPage: response.data.current_page
        };
      } catch (err: any) {
        this.error = err.message;
        throw err;
      } finally {
        this.loading = false;
      }
    },
  },
});
