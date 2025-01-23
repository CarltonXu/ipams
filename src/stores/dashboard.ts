import { defineStore } from 'pinia';
import axios from 'axios';

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
                const response = await axios.get('/api/dashboard');
                this.stats = response.data.stats;
                this.resources = response.data.resources;
                this.recent_jobs = response.data.recent_jobs;
            } catch (error: any) {
                this.error = error.message;
            }
        }
    }
});
