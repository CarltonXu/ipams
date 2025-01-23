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
        style="width: 100%;height: 672px"
        stripe
        border
      >
        <el-table-column prop="id" :label="t('scan.results.resourceId')" width="360"></el-table-column>
        <el-table-column prop="ip_address" :label="t('scan.results.ipAddress')" width="180"></el-table-column>
        <el-table-column prop="open_ports" :label="t('scan.results.openPorts')">
          <template #default="{ row }">
            <el-tag
              v-for="port in row.open_ports.split(',')"
              :key="port"
              type="success"
              effect="light"
              style="margin: 2px"
            >
              {{ port }}
            </el-tag>
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
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useScanPolicyStore } from '../stores/scanPolicy'
import { useI18n } from 'vue-i18n'
import dayjs from 'dayjs'
import { Search } from '@element-plus/icons-vue'

const { t } = useI18n()
const route = useRoute()
const results = ref([])
const searchQuery = ref('')
const scanPolicyStore = useScanPolicyStore()
const loading = ref(false)

const pagination = ref({
  currentPage: 1,
  pageSize: 10
})

onMounted(async () => {
  loading.value = true
  try {
    const jobId = route.params.jobId as string
    results.value = await scanPolicyStore.fetchJobResults(jobId)
  } finally {
    loading.value = false
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
  width: 300px; /* 缩短搜索框的宽度 */
}

.table-container {
  overflow-y: auto; /* 允许垂直滚动 */
}

.el-table th {
  position: sticky;
  top: 0;
  background-color: #fff;
  z-index: 1;
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
</style> 