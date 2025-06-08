<template>
  <div class="job-results" v-loading="loading">
    <h2>{{ t('scan.results.title') }}</h2>
    <div class="header-controls">
      <div class="host-count">
        <el-tag type="success" effect="dark">
          {{ t('scan.results.hostCount', { count: results.length }) }}
        </el-tag>
      </div>
      <el-input
        v-model="searchQuery"
        :placeholder="t('scan.results.searchPlaceholder')"
        :prefix-icon="Search"
        clearable
        class="search-input"
      />
    </div>
    <div class="table-container">
      <el-table
        :data="paginatedResults"
        v-if="paginatedResults.length"
        style="width: 100%"
        stripe
        border
        :max-height="tableHeight"
      >
        <el-table-column prop="id" :label="t('scan.results.resourceId')" width="360"></el-table-column>
        <el-table-column prop="ip_address" :label="t('scan.results.ipAddress')" width="180"></el-table-column>
        <el-table-column prop="open_ports" :label="t('scan.results.openPorts')">
          <template #default="{ row }">
            <div class="ports-container">
              <el-tag
                v-for="(info, port) in row.open_ports"
                :key="port"
                type="success"
                effect="light"
                class="port-tag"
              >
                <el-tooltip
                  :content="`${info.service}${info.version ? ' ' + info.version : ''}`"
                  placement="top"
                >
                  <span>{{ port }}</span>
                </el-tooltip>
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" :label="t('scan.results.createdAt')" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" :label="t('scan.results.updatedAt')" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.updated_at) }}
          </template>
        </el-table-column>
      </el-table>
      <div v-else class="no-data">{{ t('scan.results.noData') }}</div>
    </div>
    <el-pagination
      v-model:current-page="pagination.currentPage"
      v-model:page-size="pagination.pageSize"
      :total="filteredResults.length"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handlePageChange"
      class="pagination"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useScanPolicyStore } from '../stores/scanPolicy'
import { useI18n } from 'vue-i18n'
import dayjs from 'dayjs'
import { Search } from '@element-plus/icons-vue'

const { t } = useI18n()
const route = useRoute()

interface PortInfo {
  protocol: string;
  service: string;
  version: string;
  banner: string;
  state: string;
}

interface ScanResult {
  id: string;
  job_id: string;
  ip_address: string;
  open_ports: Record<string, PortInfo>;
  os_info: string;
  status: string;
  raw_data: any;
  created_at: string;
  updated_at: string;
}

const results = ref<ScanResult[]>([])
const searchQuery = ref('')
const scanPolicyStore = useScanPolicyStore()
const loading = ref(false)
const updateInterval = ref<number>()

const pagination = ref({
  currentPage: 1,
  pageSize: 10
})

// 计算表格高度
const tableHeight = computed(() => {
  return window.innerHeight - 300 // 减去其他元素的高度
})

// 更新结果
const updateResults = async () => {
  try {
    const jobId = route.params.jobId as string
    const newResults = await scanPolicyStore.getJobResults(jobId)
    if (JSON.stringify(newResults) !== JSON.stringify(results.value)) {
      results.value = newResults
    }
  } catch (error) {
    console.error('Failed to update results:', error)
  }
}

onMounted(async () => {
  loading.value = true
  try {
    await updateResults()
    // 每5秒更新一次结果
    updateInterval.value = window.setInterval(updateResults, 5000)
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  if (updateInterval.value) {
    clearInterval(updateInterval.value)
  }
})

const filteredResults = computed(() => {
  if (!searchQuery.value) {
    return results.value
  }
  return results.value.filter(result =>
    result.ip_address.includes(searchQuery.value)
  )
})

const paginatedResults = computed(() => {
  const start = (pagination.value.currentPage - 1) * pagination.value.pageSize
  const end = start + pagination.value.pageSize
  return filteredResults.value.slice(start, end)
})

const handlePageChange = (page: number) => {
  pagination.value.currentPage = page
}

const handleSizeChange = (size: number) => {
  pagination.value.pageSize = size
  pagination.value.currentPage = 1
}

const formatDateTime = (dateStr: string) => {
  return dateStr ? dayjs(dateStr).format('YYYY-MM-DD HH:mm:ss') : '-'
}
</script>

<style scoped>
.job-results {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.header-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.host-count {
  font-size: 16px;
  color: #333;
}

.search-input {
  width: 300px;
}

.table-container {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.el-table {
  --el-table-border-color: var(--el-border-color-lighter);
}

.el-tag {
  margin: 2px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}

.no-data {
  text-align: center;
  padding: 40px;
  color: var(--el-text-color-secondary);
}

.ports-container {
  display: flex;
  flex-wrap: wrap;
}

.port-tag {
  margin: 2px;
}
</style> 