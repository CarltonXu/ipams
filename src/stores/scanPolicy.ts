import { defineStore } from 'pinia';
import axios from 'axios';
import { ref } from 'vue';
import type { Policy, Subnet } from '../types/policy';

export const useScanPolicyStore = defineStore('scanPolicy', () => {
  const policies = ref<Policy[]>([]);
  const subnets = ref<Subnet[]>([]);
  const loading = ref(false);

  // 获取所有策略
  const fetchPolicies = async () => {
    try {
      loading.value = true;
      const response = await axios.get('/api/scan/policies');
      policies.value = response.data.policies;
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || '获取扫描策略失败');
    } finally {
      loading.value = false;
    }
  };

  const deletePolicyById = async (policyId: string) => {
    loading.value = true;
    try {
      const response = await axios.delete(`/api/scan/policies/${policyId}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || '删除扫描策略失败');
    } finally {
      loading.value = false;
    }
  };

  // 保存策略配置
  const savePolicyConfig = async (data: {
    subnets: Subnet[];
    policies: Policy[];
  }) => {
    loading.value = true;
    try {
      const response = await axios.post('/api/scan/policies', data);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || '保存扫描策略失败');
    } finally {
      loading.value = false;
    }
  };

  const executeScan = async (params: { policy_id: string, subnet_ids: string[] }) => {
    try {
      await axios.post('/api/scan/execute', params)
    } catch (error: any) {
      throw new Error(error.response?.data?.error || '执行扫描失败')
    }
  }

  const fetchPolicyJobs = async (policyId: string) => {
    try {
      const response = await axios.get(`/api/scan/policies/${policyId}/jobs`)
      return response.data
    } catch (error) {
      throw error
    }
  }

  const fetchJobResults = async (jobId: string) => {
    try {
      const response = await axios.get(`/api/scan/jobs/${jobId}/results`)
      return response.data
    } catch (error) {
      throw error
    }
  }

  return {
    policies,
    subnets,
    loading,
    fetchPolicies,
    savePolicyConfig,
    executeScan,
    deletePolicyById,
    fetchPolicyJobs,
    fetchJobResults
  };
}); 
