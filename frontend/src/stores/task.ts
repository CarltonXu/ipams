import { defineStore } from 'pinia';
import axios from 'axios';
import { ref } from 'vue';
import type { Policy, Subnet } from '../types/policy';
import { API_CONFIG } from '../config/api';

interface ScanJob {
  id: string;
  policy_id: string;
  subnet_ids: string[];
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  start_time: string;
  end_time?: string;
  error?: string;
  results?: {
    machines_found: number;
    scan_duration: number;
    subnet_results: {
      subnet_id: string;
      machines_found: number;
      scan_duration: number;
    }[];
  };
}

interface SchedulerJob {
  id: string;
  policy_id: string;
  subnet_ids: string[];
  schedule: string;
  last_run?: string;
  next_run?: string;
  status: 'active' | 'paused';
}

export const useTaskStore = defineStore('Task', {
  state: () => ({
    policies: ref<Policy[]>([]),
    subnets: ref<Subnet[]>([]),
    loading: ref(false),
    error: ref<string | null>(null),
    currentPolicy: null as Policy | null,
    schedulerJobs: ref<SchedulerJob[]>([]),
    currentJob: null as ScanJob | null
  }),

  actions: {
    async fetchAllTasks() {
      try {
        const { data } = await axios.get(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.TASK.LIST}`);
        return data;
      } catch (error) {
        console.error('Failed to fetch all jobs:', error);
        throw error;
      }
    },

    // 获取运行中的任务
    async fetchRunningJobs() {
      try {
        const { data } = await axios.get(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.TASK.LIST}`, {
          params: { status: "running" }
        });
        return data;
      } catch (error) {
        console.error('Failed to fetch running jobs:', error);
        throw error;
      }
    },

    // 提交扫描任务
    async executeScan(params: { policy_id: string; subnet_ids: string[] }) {
      try {
        const { data } = await axios.post(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.TASK.SUBMIT}`, params);
        return data;
      } catch (error: any) {
        this.error = error.response?.data?.error || '执行扫描失败';
        throw error;
      }
    },

    // 获取任务进度
    async getJobProgress(jobId: string) {
      try {
        const { data } = await axios.get(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.TASK.PROGRESS(jobId)}`);
        return data;
      } catch (error: any) {
        if (error.response?.data?.message) {
          throw new Error(error.response.data.message);
        }
        throw new Error('Failed to get job progress');
      }
    },

    // 获取任务状态
    async getJobStatus(jobId: string) {
      try {
        const { data } = await axios.get(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.TASK.JOBS(jobId)}`);
        this.currentJob = data;
        return data;
      } catch (error: any) {
        if (error.response?.data?.message) {
          throw new Error(error.response.data.message);
        }
        throw new Error('Failed to get job status');
      }
    },

    // 获取任务结果
    async getJobResults(jobId: string) {
      try {
        const { data } = await axios.get(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.TASK.JOB_RESULTS(jobId)}`);
        return data;
      } catch (error: any) {
        if (error.response?.data?.message) {
          throw new Error(error.response.data.message);
        }
        throw new Error('Failed to get job results');
      }
    },

    // 取消任务
    async cancelJob(jobId: string) {
      try {
        const response = await axios.post(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.TASK.JOB_CANCEL(jobId)}`);
        return response.data;
      } catch (error: any) {
        if (error.response?.data?.message) {
          throw new Error(error.response.data.message);
        }
        throw new Error('Failed to cancel job');
      }
    },
  }
});