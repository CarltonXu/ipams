import { defineStore } from 'pinia';
import axios from 'axios';
import { ref } from 'vue';
import type { Policy, Subnet } from '../types/policy';

export const useScanPolicyStore = defineStore('scanPolicy', {
  state: () => ({
    policies: ref<Policy[]>([]),
    subnets: ref<Subnet[]>([]),
    loading: ref(false),
    error: ref<string | null>(null),
    currentPolicy: null
  }),

  actions: {
    async fetchPolicies() {
      try {
        this.loading = true;
        const response = await axios.get('/api/scan/policies');
        this.policies = response.data.policies;
        return response.data;
      } catch (error: any) {
        this.error = error.response?.data?.message || '获取扫描策略失败';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async deletePolicyById(policyId: string) {
      this.loading = true;
      try {
        const response = await axios.delete(`/api/scan/policies/${policyId}`);
        return response.data;
      } catch (error: any) {
        this.error = error.response?.data?.message || '删除扫描策略失败';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async createPolicy(data: {
      subnets: Subnet[];
      policies: Policy[];
    }) {
      this.loading = true;
      try {
        const response = await axios.post('/api/scan/policies', data);
        return response.data;
      } catch (error: any) {
        this.error = error.response?.data?.message || '保存扫描策略失败';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async executeScan(params: { policy_id: string; subnet_ids: string[] }) {
      try {
        const response = await axios.post('/api/scan/jobs', params);
        return response.data;
      } catch (error: any) {
        this.error = error.response?.data?.error || '执行扫描失败';
        throw error;
      }
    },

    async getJobStatus(jobId: string) {
      try {
        const response = await axios.get(`/api/scan/jobs/${jobId}`);
        return response.data;
      } catch (error: any) {
        if (error.response?.data?.message) {
          throw new Error(error.response.data.message);
        }
        throw new Error('Failed to get job status');
      }
    },

    async getJobProgress(jobId: string) {
      try {
        const response = await axios.get(`/api/scan/jobs/${jobId}/progress`);
        return response.data;
      } catch (error: any) {
        if (error.response?.data?.message) {
          throw new Error(error.response.data.message);
        }
        throw new Error('Failed to get job progress');
      }
    },

    async cancelJob(jobId: string) {
      try {
        const response = await axios.post(`/api/scan/jobs/${jobId}/cancel`);
        return response.data;
      } catch (error: any) {
        if (error.response?.data?.message) {
          throw new Error(error.response.data.message);
        }
        throw new Error('Failed to cancel job');
      }
    },

    async getJobResults(jobId: string) {
      try {
        const response = await axios.get(`/api/scan/jobs/${jobId}/results`);
        return response.data;
      } catch (error: any) {
        if (error.response?.data?.message) {
          throw new Error(error.response.data.message);
        }
        throw new Error('Failed to get job results');
      }
    },

    async fetchPolicyJobs(policyId: string) {
      try {
        const response = await axios.get(`/api/scan/policies/${policyId}/jobs`);
        return response.data;
      } catch (error: any) {
        this.error = error.response?.data?.error || '获取策略任务失败';
        throw error;
      }
    },

    async fetchRunningJobs() {
      try {
        const response = await axios.get('/api/scan/jobs', {
          params: { status: "running"}
        });
        return response.data;
      } catch (error) {
        console.error('Failed to fetch running jobs:', error);
        throw error;
      }
    }
  }
}); 
