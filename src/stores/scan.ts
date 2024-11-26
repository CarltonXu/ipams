import { defineStore } from 'pinia';
import axios from 'axios';

export const useScanStore = defineStore('scan', {
  state: () => ({
    subnets: [] as Array<{ id: string; subnet: string; created_at: string }>,
    threads: 1,
    schedule: 'daily',
  }),
  actions: {
    async fetchSubnets() {
      try {
        const response = await axios.get('/api/scan/subnets');
        this.subnets = response.data;
      } catch (error) {
        console.error('Failed to fetch subnets:', error);
      }
    },
    async addSubnet(newSubnet: string) {
      try {
        await axios.post('/api/scan/subnets', { subnet: newSubnet });
        this.fetchSubnets();
      } catch (error) {
        console.error('Failed to add subnet:', error);
      }
    },
    async addPolicy(subnetId: string) {
      try {
        await axios.post('/api/scan/policies', {
          subnet_id: subnetId,
          threads: this.threads,
          schedule: this.schedule,
        });
      } catch (error) {
        console.error('Failed to add policy:', error);
      }
    },

    async executeScan(subnetId: string) {
      try {
        const response = await axios.post('/api/scan/execute', { subnet_id: subnetId });
        return response.data;
      } catch (error) {
        console.error('Execute scan failed:', error);
        throw error;
      }
    }
  },
});