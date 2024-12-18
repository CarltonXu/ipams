<template>
  <div class="ip-list">
    <!-- 未登录跳转到登录 -->
    <el-card>
      <div v-if="!isAuthenticated" class="login-container">
        <Login />
      </div>
      <!-- 登录后的内容 -->
      <!-- 工具栏 -->
      <div class="toolbar" v-else>
        <div class="toolbar-header">
          <h2>IP Address Management</h2>
          <p class="subtitle">Easily manage your IP addresses with filters and search functionality.</p>
        </div>
        <div class="filters">
          <el-input
            v-model="searchQuery"
            @input="debouncedSearch"
            placeholder="Search IPs, devices, or purpose"
            prefix-icon="Search"
            clearable
            class="search-input"
          />
          <el-select v-model="statusFilter" class="status-filter" placeholder="Filter by Status">
            <el-option label="All Status" value="all" />
            <el-option label="Active" value="active" />
            <el-option label="Inactive" value="inactive" />
            <el-option label="Unclaimed" value="unclaimed" />
          </el-select>
        </div>
      </div>

      <div class="table-container">
        <!-- 表格 -->
        <el-table
          v-loading="ipStore.loading"
          :data="filteredIPs"
          style="width: 100%"
          :height="tableHeight"
          empty-text="No IP addresses found"
          class="ip-table"
          stripe
          highlight-current-row
          border
          @sort-change="handleSortChange">
          <el-table-column
            v-for="column in tableColumns"
            :key="column.prop"
            :prop="column.prop"
            :label="column.label"
            :sortable="column.sortable ? 'custom' : false"
            :width="column.width"
            :min-width="column.minWidth">
            <template v-if="column.slotName" #default="{ row }">
              <el-tooltip :content="statusDescriptions[row.status]" placement="top">
                <el-tag :type="getStatusType(row.status)" effect="light">
                  {{ row.status }}
                </el-tag>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="120" align="center">
            <template #default="{ row }">
              <el-button
                v-if="row.status === 'unclaimed'"
                type="success"
                size="small"
                @click="openClaimDialog(row)"
                round>
                Claim
              </el-button>
              <!-- 只有当前用户的资源才可以修改 -->
              <el-button
              v-if="row.status !== 'unclaimed' && (row.assigned_user && row.assigned_user.username === authStore.user.username || authStore.user.is_admin) || (row.status === 'active' && !row.assigned_user)"
              type="primary"
              size="small"
              @click="openUpdateDialog(row)"
              round>
              Edit
            </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page.sync="ipStore.currentPage"
        :page-size.sync="ipStore.pageSize"
        :total="ipStore.total"
        background
        layout="prev, pager, next, sizes, jumper"
        @size-change="handleSizeChange"
        class="pagination"
      />

      <!-- Claim IP Dialog -->
      <ClaimIPDialog
        v-model="claimDialogVisible"
        :ip="claimSelectedIP"
        @claimSuccess="handleClaimSuccess"
      />

      <!-- Update IP Dialog -->
      <UPdateIPDialog
        v-model="updateDialogVisible"
        :ip="updateSelectedIP"
        @claimSuccess="handleUpdateSuccess"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useIPStore } from '../stores/ip';
import { debounce } from 'lodash';
import type { IP } from '../types/ip';
import { ElMessage } from 'element-plus';
import ClaimIPDialog from './ClaimIPDialog.vue';
import UPdateIPDialog from './UpdateIPDialog.vue';
import Login from '../views/Login.vue';
import { Search } from '@element-plus/icons-vue';

const router = useRouter();
const authStore = useAuthStore();
const ipStore = useIPStore();

const searchQuery = ref('');
const statusFilter = ref('all');
const claimDialogVisible = ref(false);
const updateDialogVisible = ref(false);
const claimSelectedIP = ref<IP | null>(null); // 当前选中的 IP 信息
const updateSelectedIP = ref<IP | null>(null); // 当前选中的 IP 信息

// 计算属性：是否已登录
const isAuthenticated = computed(() => !!authStore.user);

const statusDescriptions: Record<string, string> = {
  active: 'This IP is currently active.',
  inactive: 'This IP is not in use.',
  unclaimed: 'This IP is available for claiming.',
  danger: 'Unknown status.',
};

const tableColumns = ref([
  { prop: 'id', label: 'Host UUID', minWidth: 110 },
  { prop: 'ip_address', label: 'IP Address', minWidth: 120, sortable: true },
  { prop: 'os_type', label: 'OS Version', minWidth: 150, sortable: true },
  { prop: 'status', label: 'Status', width: 120, slotName: 'status', sortable: true},
  { prop: 'device_name', label: 'Device Name', minWidth: 150, sortable: true },
  { prop: 'device_type', label: 'Device Type', minWidth: 150, sortable: true },
  { prop: 'manufacturer', label: 'Architerture', minWidth: 150, sortable: true },
  { prop: 'model', label: 'Model', minWidth: 150, sortable: true },
  { prop: 'assigned_user.username', label: 'Owning User', minWidth: 150, sortable: true },
  { prop: 'purpose', label: 'Purpose', minWidth: 180 },
  { prop: 'last_scanned', label: 'Last Scanned', minWidth: 180, sortable: true },
]);

const tableHeight = ref(window.innerHeight - 394);

const updateTableHeight = () => {
  tableHeight.value = window.innerHeight - 394;
};

const debouncedSearch = debounce((query) => {
  searchQuery.value = query;
}, 300);

const handleSizeChange = (page: number) => {
  ipStore.pageSize = page;
};

// 计算属性：过滤后的表格数据
const filteredIPs = computed(() => {
  let filtered = ipStore.sortedIPs
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = ipStore.ips.filter((ip) =>
      [ip.ip_address, ip.device_name, ip.purpose].some((field) =>
        field.toLowerCase().includes(query)
      )
    )
  }
  if (statusFilter.value !== 'all') {
    filtered = ipStore.ips.filter((ip) => ip.status === statusFilter.value);
    console.log('Filtered by Status:', filtered);
  }
  
  return filtered;
});

// 组件挂载时检查登录状态
onMounted(() => {
  if (isAuthenticated.value) {
    ipStore.fetchAllIPs()
    window.addEventListener('resize', updateTableHeight);
  } else {
    router.push('/login');
  }
});

onUnmounted(() => {
  window.removeEventListener('resize', updateTableHeight);
});

// 映射状态到标签类型
const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    active: 'success',
    inactive: 'info',
    unclaimed: 'warning',
  };
  return statusMap[status] || 'danger';
};

// 打开 Claim IP 对话框
const openClaimDialog = (ip: IP) => {
  claimSelectedIP.value = ip;
  claimDialogVisible.value = true;
};

// 处理认领成功事件
const handleClaimSuccess = (ip: IP) => {
  ElMessage.success(`Successfully claimed IP: ${ip.ip_address}`);
  ipStore.fetchAllIPs(); // 刷新表格数据
  claimDialogVisible.value = false;
};

// 打开 Update IP 对话框
const openUpdateDialog = (ip: IP) => {
  updateSelectedIP.value = ip;
  updateDialogVisible.value = true;
};

// 处理更新成功事件
const handleUpdateSuccess = (ip: IP) => {
  ElMessage.success(`Successfully updated IP: ${ip.ip_address}`);
  ipStore.fetchAllIPs(); // 刷新表格数据
  updateDialogVisible.value = false;
};

const handleSortChange = ({ prop, order }: { prop: string; order: string }) => {
  if (!prop || !order) return;

  const sortOrder = order === 'ascending' ? 1 : -1;
  ipStore.sortedIPs.sort((a, b) => {
    if (a[prop] < b[prop]) return -sortOrder;
    if (a[prop] > b[prop]) return sortOrder;
    return 0;
  });
};
</script>

<style scoped>
.ip-list {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.toolbar-header h2 {
  font-size: 24px;
  margin: 0;
  color: #333;
}

.toolbar-header .subtitle {
  color: #666;
  margin: 0;
  font-size: 14px;
}

.filters {
  display: flex;
  gap: 1rem;
}

.search-input {
  width: 300px;
}

.status-filter {
  width: 150px;
}

.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(to right, #1d3557, #457b9d);
}

.table-container {
  height: 100%;
  position: relative;
}

.ip-table {
  margin-top: 20px;
}

@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
    align-items: flex-start;
  }

  .search-input, .status-filter {
    width: 100%;
  }
}

.pagination {
  margin-top: 20px;
  text-align: right;
}
</style>