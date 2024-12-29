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
    policies: ScanPolicy[];
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

  // 执行扫描
  const executeScan = async (subnet: string) => {
    loading.value = true;
    try {
      const response = await axios.post('/api/scan/execute', { subnet });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || '执行扫描失败');
    } finally {
      loading.value = false;
    }
  };

  return {
    policies,
    subnets,
    loading,
    fetchPolicies,
    savePolicyConfig,
    executeScan,
    deletePolicyById
  };
}); 
