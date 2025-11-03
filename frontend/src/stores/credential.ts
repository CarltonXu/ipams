import { defineStore } from 'pinia';
import axios from 'axios';
import type {
  Credential,
  CredentialCreateRequest,
  CredentialUpdateRequest,
  CredentialTestResponse,
  CredentialResponse,
  CredentialBindRequest,
  CredentialUnbindRequest
} from '../types/credential';
import { API_CONFIG } from '../config/api';
import i18n from '../i18n';

const { t } = i18n.global;

export const useCredentialStore = defineStore('credential', {
  state: () => ({
    credentials: [] as Credential[],
    loading: false,
    error: null as string | null
  }),

  getters: {
    getCredentialById: (state) => (id: string) => {
      return state.credentials.find(cred => cred.id === id);
    },
    getCredentialsByType: (state) => (type: string) => {
      return state.credentials.filter(cred => cred.credential_type === type);
    },
    defaultCredential: (state) => {
      return state.credentials.find(cred => cred.is_default);
    }
  },

  actions: {
    /**
     * 获取凭证列表
     */
    async fetchCredentials() {
      this.loading = true;
      try {
        const response = await axios.get<CredentialResponse>(
          `${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.CREDENTIAL.LIST}`
        );
        this.credentials = response.data.credentials;
      } catch (error: any) {
        this.error = error.response?.data?.error || t('common.fetchError');
        console.error('Failed to fetch credentials:', error);
      } finally {
        this.loading = false;
      }
    },

    /**
     * 创建凭证
     */
    async createCredential(data: CredentialCreateRequest) {
      this.loading = true;
      try {
        const response = await axios.post(
          `${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.CREDENTIAL.CREATE}`,
          data
        );
        this.credentials.push(response.data.credential);
        return response.data;
      } catch (error: any) {
        this.error = error.response?.data?.error || t('common.createError');
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * 更新凭证
     */
    async updateCredential(id: string, data: CredentialUpdateRequest) {
      this.loading = true;
      try {
        const response = await axios.put(
          `${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.CREDENTIAL.UPDATE(id)}`,
          data
        );
        const index = this.credentials.findIndex(cred => cred.id === id);
        if (index !== -1) {
          this.credentials[index] = response.data.credential;
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
     * 删除凭证
     */
    async deleteCredential(id: string) {
      this.loading = true;
      try {
        await axios.delete(
          `${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.CREDENTIAL.DELETE(id)}`
        );
        this.credentials = this.credentials.filter(cred => cred.id !== id);
      } catch (error: any) {
        this.error = error.response?.data?.error || t('common.deleteError');
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * 测试凭证连接
     */
    async testCredential(id: string, hostIp?: string): Promise<CredentialTestResponse> {
      try {
        const testData = hostIp ? { host_ip: hostIp } : {};
        const response = await axios.post<CredentialTestResponse>(
          `${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.CREDENTIAL.TEST(id)}`,
          testData
        );
        return response.data;
      } catch (error: any) {
        this.error = error.response?.data?.message || t('common.testError');
        throw error;
      }
    },

    /**
     * 获取凭证详情（包含解密后的密码）
     */
    async getCredentialDetail(id: string) {
      try {
        const response = await axios.get(
          `${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.CREDENTIAL.DETAIL(id)}`
        );
        return response.data;
      } catch (error: any) {
        this.error = error.response?.data?.error || t('common.fetchError');
        throw error;
      }
    },

    /**
     * 获取凭证绑定的主机列表
     */
    async getCredentialBindings(id: string) {
      try {
        const response = await axios.get(
          `${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.CREDENTIAL.BINDINGS(id)}`
        );
        return response.data;
      } catch (error: any) {
        this.error = error.response?.data?.error || t('common.fetchError');
        throw error;
      }
    },

    /**
     * 批量绑定主机到凭证
     */
    async batchBindHosts(id: string, data: CredentialBindRequest) {
      try {
        const response = await axios.post(
          `${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.CREDENTIAL.BATCH_BIND(id)}`,
          data
        );
        return response.data;
      } catch (error: any) {
        this.error = error.response?.data?.error || t('common.bindError');
        throw error;
      }
    },

    /**
     * 批量解绑主机
     */
    async batchUnbindHosts(id: string, data: CredentialUnbindRequest) {
      try {
        const response = await axios.post(
          `${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.CREDENTIAL.BATCH_UNBIND(id)}`,
          data
        );
        return response.data;
      } catch (error: any) {
        this.error = error.response?.data?.error || t('common.unbindError');
        throw error;
      }
    }
  }
});

