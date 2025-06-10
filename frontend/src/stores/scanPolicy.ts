import { defineStore } from 'pinia';
import axios from 'axios';
import { ref } from 'vue';
import type { Policy, Subnet } from '../types/policy';
import { API_CONFIG } from '../config/api';

interface PolicyData {
  name: string;
  description: string;
  threads: number;
  strategies: Array<{
    cron: string;
    start_time: string;
    subnet_ids: string[];
    scan_params: {
      enable_custom_ports: boolean;
      ports: string;
      enable_custom_scan_type: boolean;
      scan_type: string;
    };
  }>;
}

export interface SchedulerJob {
  id: string;
  policy_id: string;
  policy_name: string;
  next_run_time: string | null;
  trigger: string;
  is_start_job: boolean;
}

export const useScanPolicyStore = defineStore('scanPolicy', {
  state: () => ({
    policies: ref<Policy[]>([]),
    subnets: ref<Subnet[]>([]),
    loading: ref(false),
    error: ref<string | null>(null),
    currentPolicy: null,
    schedulerJobs: ref<SchedulerJob[]>([])
  }),

  actions: {
    async fetchPolicies() {
      try {
        this.loading = true;
        const response = await axios.get(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.POLICY.LIST}`);
        this.policies = response.data;
        return response.data;
      } catch (error: any) {
        this.error = error.response?.data?.message || '获取扫描策略失败';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async createPolicy(data: {
      subnets: Array<{ name: string; subnet: string }>;
      policies: PolicyData[];
    }) {
      try {
        this.loading = true;
        const response = await axios.post(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.POLICY.CREATE}`, data);
        return response.data;
      } catch (error: any) {
        this.error = error.response?.data?.message || '保存扫描策略失败';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async updatePolicy(policyId: string, data: {
      name: string;
      description: string;
      threads: number;
      subnets: Array<{ name: string; subnet: string }>;
      strategies: Array<{
        cron: string;
        start_time: string;
        subnet_ids: string[];
        scan_params: {
          enable_custom_ports: boolean;
          ports: string;
          enable_custom_scan_type: boolean;
          scan_type: string;
        };
      }>;
    }) {
      try {
        this.loading = true;
        const response = await axios.put(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.POLICY.UPDATE(policyId)}`, data);
        return response.data;
      } catch (error: any) {
        this.error = error.response?.data?.message || '更新扫描策略失败';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async deletePolicy(policyId: string) {
      try {
        this.loading = true;
        const response = await axios.delete(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.POLICY.DELETE(policyId)}`);
        return response.data;
      } catch (error: any) {
        this.error = error.response?.data?.message || '删除扫描策略失败';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchPolicyJobs(policyId: string) {
      try {
        const response = await axios.get(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.POLICY.JOBS(policyId)}`);
        return response.data;
      } catch (error: any) {
        this.error = error.response?.data?.error || '获取策略任务失败';
        throw error;
      }
    },

    async getSchedulerJobs() {
      try {
        this.loading = true;
        const response = await axios.get(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.POLICY.SCHEDULER_JOBS}`);
        this.schedulerJobs = response.data;
      } catch (error: any) {
        this.error = error.response?.data?.message || '获取定时任务信息失败';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async updatePolicyStatus(policyId: string, status: 'active' | 'inactive') {
      try {
        this.loading = true;
        await axios.put(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.POLICY.UPDATE_STATUS(policyId)}`, { status });
        // 刷新策略列表
        await this.fetchPolicies();
      } catch (error: any) {
        this.error = error.response?.data?.message || '更新策略状态失败';
        throw error;
      } finally {
        this.loading = false;
      }
    }
  }
}); 
