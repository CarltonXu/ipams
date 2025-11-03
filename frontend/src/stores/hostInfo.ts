import { defineStore } from 'pinia';
import axios from 'axios';
import type {
  HostInfo,
  HostInfoListResponse,
  HostInfoBindCredentialRequest,
  HostInfoCollectRequest,
  HostInfoCollectResponse,
  HostInfoBatchCollectRequest,
  HostInfoBatchCollectResponse,
  HostInfoBatchBindRequest,
  HostInfoBatchUnbindRequest,
  HostInfoCollectionHistory,
  ExportRequest,
  ExportTemplate,
  ExportField
} from '../types/hostInfo';
import { API_CONFIG } from '../config/api';
import i18n from '../i18n';

const { t } = i18n.global;

interface FetchParams {
  page: number;
  pageSize: number;
  query?: string;
  host_type?: string;
  collection_status?: string;
  sort_by?: string;
  sort_order?: string;
}

export const useHostInfoStore = defineStore('hostInfo', {
  state: () => ({
    hosts: [] as HostInfo[],
    loading: false,
    error: null as string | null,
    currentPage: 1,
    pageSize: 10,
    total: 0,
    pages: 0
  }),

  getters: {
    getHostById: (state) => (id: string) => {
      return state.hosts.find(host => host.id === id);
    }
  },

  actions: {
    /**
     * 获取主机信息列表
     */
    async fetchHosts(params: FetchParams) {
      this.loading = true;
      try {
        const response = await axios.get<HostInfoListResponse>(
          `${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.HOST.LIST}`,
          { params }
        );
        this.hosts = response.data.hosts;
        this.total = response.data.total;
        this.pages = response.data.pages;
        this.currentPage = response.data.current_page;
        this.pageSize = response.data.page_size;
      } catch (error: any) {
        this.error = error.response?.data?.error || t('common.fetchError');
        console.error('Failed to fetch hosts:', error);
      } finally {
        this.loading = false;
      }
    },

    /**
     * 获取单个主机详细信息
     */
    async fetchHostById(id: string): Promise<HostInfo | null> {
      try {
        const response = await axios.get(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.HOST.LIST_BY_ID(id)}`);
        return response.data.host;
      } catch (error: any) {
        console.error(`Failed to fetch host ${id}:`, error);
        return null;
      }
    },

    /**
     * 更新主机信息
     */
    async updateHost(id: string, data: any) {
      this.loading = true;
      try {
        const response = await axios.put(
          `${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.HOST.UPDATE(id)}`,
          data
        );
        const index = this.hosts.findIndex(host => host.id === id);
        if (index !== -1) {
          this.hosts[index] = response.data.host;
        }
        return response.data;
      } catch (error: any) {
        this.error = error.response?.data?.error || t('common.updateError');
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * 绑定凭证到主机
     */
    async bindCredential(id: string, data: HostInfoBindCredentialRequest) {
      try {
        const response = await axios.post(
          `${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.HOST.BIND_CREDENTIAL(id)}`,
          data
        );
        return response.data;
      } catch (error: any) {
        this.error = error.response?.data?.error || t('common.bindError');
        throw error;
      }
    },

    /**
     * 解绑主机凭证
     */
    async unbindCredential(id: string, credentialId: string) {
      try {
        await axios.delete(
          `${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.HOST.UNBIND_CREDENTIAL(id)}`,
          { params: { credential_id: credentialId } }
        );
      } catch (error: any) {
        this.error = error.response?.data?.error || t('common.unbindError');
        throw error;
      }
    },

    /**
     * 触发单个主机信息采集
     */
    async collectHostInfo(id: string, data?: HostInfoCollectRequest): Promise<HostInfoCollectResponse> {
      this.loading = true;
      try {
        const response = await axios.post<HostInfoCollectResponse>(
          `${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.HOST.COLLECT(id)}`,
          data || {}
        );
        return response.data;
      } catch (error: any) {
        this.error = error.response?.data?.error || t('common.collectError');
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * 批量触发主机信息采集
     */
    async batchCollectHosts(data: HostInfoBatchCollectRequest): Promise<HostInfoBatchCollectResponse> {
      this.loading = true;
      try {
        const response = await axios.post<HostInfoBatchCollectResponse>(
          `${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.HOST.BATCH_COLLECT}`,
          data
        );
        return response.data;
      } catch (error: any) {
        this.error = error.response?.data?.error || t('common.batchCollectError');
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * 获取采集历史
     */
    async fetchCollectionHistory(id: string): Promise<HostInfoCollectionHistory> {
      try {
        const response = await axios.get<HostInfoCollectionHistory>(
          `${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.HOST.COLLECTION_HISTORY(id)}`
        );
        return response.data;
      } catch (error: any) {
        console.error(`Failed to fetch collection history for host ${id}:`, error);
        throw error;
      }
    },

    /**
     * 导出主机信息到Excel
     */
    async exportHosts(data: ExportRequest) {
      try {
        const response = await axios.post(
          `${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.HOST.EXPORT}`,
          data,
          { responseType: 'blob' }
        );
        
        // 创建下载链接
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `hosts_export_${new Date().getTime()}.xlsx`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } catch (error: any) {
        this.error = error.response?.data?.error || t('common.exportError');
        throw error;
      }
    },

    /**
     * 获取导出模板列表
     */
    async fetchExportTemplates(): Promise<ExportTemplate[]> {
      try {
        const response = await axios.get(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.HOST.EXPORT_TEMPLATES}`);
        return response.data.templates;
      } catch (error: any) {
        console.error('Failed to fetch export templates:', error);
        return [];
      }
    },

    /**
     * 获取可用导出字段列表
     */
    async fetchExportFields(): Promise<ExportField[]> {
      try {
        const response = await axios.get(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.HOST.EXPORT_FIELDS}`);
        return response.data.fields;
      } catch (error: any) {
        console.error('Failed to fetch export fields:', error);
        return [];
      }
    },

    /**
     * 批量绑定凭证到主机
     */
    async batchBindCredentials(data: HostInfoBatchBindRequest) {
      this.loading = true;
      try {
        const response = await axios.post(
          `${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.HOST.BATCH_BIND}`,
          data
        );
        return response.data;
      } catch (error: any) {
        this.error = error.response?.data?.error || t('common.bindError');
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * 批量解绑凭证
     */
    async batchUnbindCredentials(data: HostInfoBatchUnbindRequest) {
      this.loading = true;
      try {
        const response = await axios.post(
          `${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.HOST.BATCH_UNBIND}`,
          data
        );
        return response.data;
      } catch (error: any) {
        this.error = error.response?.data?.error || t('common.unbindError');
        throw error;
      } finally {
        this.loading = false;
      }
    }
  }
});

