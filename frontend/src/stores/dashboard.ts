import { defineStore } from 'pinia';
import { ref } from 'vue';
import axios from 'axios';
import { API_CONFIG } from '../config/api';

export interface ResourceHistory {
    timestamps: string[];
    cpu: number[];
    memory: number[];
    disk: number[];
}

export interface SystemInfo {
    platform: string;
    [key: string]: any;
}

export interface DashboardStats {
    total_ips: number;
    claimed_ips: number;
    unclaimed_ips: number;
    total_policies: number;
    running_jobs: number;
    failed_jobs: number;
    successful_jobs: number;
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
}

export interface AuditResource {
    id: string;
    action: string;
    details: string;
    source_ip: string;
    created_at: string;
}

export interface RecentJob {
    id: string;
    status: string;
    machines_found: number;
    error_message: string;
    created_at: string;
    user_id: string;
}

export interface DashboardResources {
    audit_resources: AuditResource[];
    resource_history: ResourceHistory;
    system_info: SystemInfo;
}

export const useDashboardStore = defineStore('dashboard', {
    state: () => ({
        stats: ref<DashboardStats>({
            total_ips: 0,
            claimed_ips: 0,
            unclaimed_ips: 0,
            total_policies: 0,
            running_jobs: 0,
            failed_jobs: 0,
            successful_jobs: 0,
            cpu_usage: 0,
            memory_usage: 0,
            disk_usage: 0
        }),
        resources: ref<DashboardResources>({
            audit_resources: [],
            resource_history: {
                timestamps: [],
                cpu: [],
                memory: [],
                disk: []
            },
            system_info: {
                platform: ''
            }
        }),
        recent_jobs: ref<RecentJob[]>([]),
        loading: ref(false),
        error: ref<string | null>(null)
    }),
    getters: {
        getStats: (state: any) => state.stats,
        getResources: (state: any) => state.resources,
        getRecentJobs: (state: any) => state.recent_jobs,
        systemInfo: (state) => state.resources.system_info,
        resourceHistory: (state) => state.resources.resource_history
    },
    actions: {
        async fetchDashboardData() {
            try {
                this.loading = true;
                const response = await axios.get(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.DASHBOARD.LIST}`);
                const data = response.data.data;

                this.stats = data.stats;
                this.resources = data.resources;
                this.recent_jobs = data.recent_jobs;
            } catch (error: any) {
                this.error = error.response?.data?.message || '获取仪表盘数据失败';
                throw error;
            } finally {
                this.loading = false;
            }
        }
    }
});
