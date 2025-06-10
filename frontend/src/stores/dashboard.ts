import { defineStore } from 'pinia';
import axios from 'axios';
import { API_CONFIG } from '../config/api';

export const useDashboardStore = defineStore('dashboard', {
    state: () => ({
        stats: [] as any[],
        resources: [] as any[],
        recent_jobs: [] as any[],
        loading: false,
        error: null as string | null,
    }),
    getters: {
        getStats: (state: any) => state.stats,
        getResources: (state: any) => state.resources,
        getRecentJobs: (state: any) => state.recent_jobs
    },
    actions: {
        async fetchDashboardData() {
            try {
                const response = await axios.get(`${API_CONFIG.BASE_API_URL}${API_CONFIG.ENDPOINTS.DASHBOARD.LIST}`);
                this.stats = response.data.stats;
                this.resources = response.data.resources;
                this.recent_jobs = response.data.recent_jobs;
            } catch (error: any) {
                this.error = error.message;
            }
        }
    }
});
