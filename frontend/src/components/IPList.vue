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
          <h2>{{ $t('ip.title') }}</h2>
          <p class="subtitle">{{ $t('ip.subtitle') }}</p>
        </div>
        <div class="filters">
          <!-- 批量操作按钮 -->
          <el-button-group v-if="selectedIPs.length > 0">
            <el-button 
              type="primary"
              @click="handleBatchClaim"
              :disabled="!canBatchClaim">
              {{ $t('ip.actions.batchClaim') }}
            </el-button>
            <el-button 
              type="warning"
              @click="handleBatchUpdate"
              :disabled="!canBatchUpdate">
              {{ $t('ip.actions.batchUpdate') }}
            </el-button>
          </el-button-group>
          <el-select
            v-model="searchColumn"
            class="column-filter"
            :placeholder="$t('ip.search.selectColumn')"
          >
            <el-option value="all" :label="$t('ip.search.allColumns')" />
            <el-option
              v-for="column in searchableColumns"
              :key="column.prop"
              :label="$t(`ip.columns.${column.translationKey}`)"
              :value="column.prop"
            />
          </el-select>
          
          <el-input
            v-model="searchQuery"
            :placeholder="searchColumn === 'all' ? $t('ip.search.all') : $t('ip.search.specific', { column: $t(`ip.columns.${getColumnTranslationKey(searchColumn)}`) })"
            :prefix-icon="Search"
            clearable
            class="search-input"
          />
          
          <el-select 
            v-model="statusFilter" 
            class="status-filter" 
            :placeholder="$t('ip.status.all')"
          >
            <el-option :label="$t('ip.status.all')" value="all" />
            <el-option :label="$t('ip.status.active')" value="active" />
            <el-option :label="$t('ip.status.inactive')" value="inactive" />
            <el-option :label="$t('ip.status.unclaimed')" value="unclaimed" />
            <el-option :label="$t('ip.status.myResources')" value="mine" />
          </el-select>
        </div>
      </div>

      <div class="table-container">
        <!-- 表格 -->
        <el-table
          v-loading="ipStore.loading"
          :data="tableData"
          style="width: 100%"
          :max-height="tableHeight"
          :empty-text="$t('ip.noData')"
          class="ip-table"
          stripe
          highlight-current-row
          border
          @sort-change="handleSortChange"
          @selection-change="handleSelectionChange">
          <el-table-column
            type="selection"
            width="40"
          />
          <el-table-column
            v-for="column in tableColumns"
            :key="column.prop"
            :prop="column.prop"
            :label="$t(`ip.columns.${column.translationKey}`)"
            :sortable="column.sortable ? 'custom' : false"
            :width="column.width"
            :min-width="column.minWidth"
            :align="column.align || 'center'">
            <template v-if="column.slotName" #default="{ row }">
              <el-tooltip :content="$t(`ip.status.description.${row.status}`)" placement="top">
                <el-tag :type="getStatusType(row.status)" effect="light">
                  {{ $t(`ip.status.${row.status}`) }}
                </el-tag>
              </el-tooltip>
            </template>
            <template v-if="column.slotName === 'owningUser'" #default="{ row }">
              <el-tag :type="row.assigned_user ? 'success' : 'info'" effect="plain">
                {{ row.assigned_user ? row.assigned_user.username : t('ip.status.unassigned') }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column :label="$t('common.actions')" width="120" align="center">
            <template #default="{ row }">
              <el-button
                v-if="row.status === 'unclaimed'"
                type="success"
                size="small"
                @click="openClaimDialog(row)"
                round>
                {{ $t('ip.actions.claim') }}
              </el-button>
              <!-- 只有当前用户的资源才可以修改 -->
              <el-button
                v-if="row.status !== 'unclaimed' && (row.assigned_user && row.assigned_user.username === authStore.user?.username || authStore.user?.is_admin) || (row.status === 'active' && !row.assigned_user)"
                type="primary"
                size="small"
                @click="openUpdateDialog(row)"
                round>
                {{ $t('ip.actions.edit') }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :page-sizes="[10, 20, 50, 100]"
            background
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
            class="pagination"
          />
        </div>
      </div>

      <!-- Claim IP Dialog -->
      <ClaimIPDialog
        v-if="!isBatchClaim"
        v-model="claimDialogVisible"
        :ip="claimSelectedIP"
        @claimSuccess="handleClaimSuccess"
      />
      
      <BatchClaimIPDialog
        v-if="isBatchClaim"
        v-model="claimDialogVisible"
        :ips="selectedIPs"
        @claimSuccess="handleClaimSuccess"
      />

      <!-- Update IP Dialog -->
      <UPdateIPDialog
        v-model="updateDialogVisible"
        :ip="updateSelectedIP"
        @updateSuccess="handleUpdateSuccess"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useIPStore } from '../stores/ip';
import { useI18n } from 'vue-i18n';
import { debounce } from 'lodash';
import type { IP } from '../types/ip';
import { ElMessage } from 'element-plus';
import ClaimIPDialog from './ClaimIPDialog.vue';
import UPdateIPDialog from './UpdateIPDialog.vue';
import Login from '../views/Login.vue';
import { Search } from '@element-plus/icons-vue';
import BatchClaimIPDialog from './BatchClaimIPDialog.vue';

const { t } = useI18n();

const router = useRouter();
const authStore = useAuthStore();
const ipStore = useIPStore();

const searchQuery = ref('');
const searchColumn = ref('all');
const statusFilter = ref('all');
const claimDialogVisible = ref(false);
const updateDialogVisible = ref(false);
const claimSelectedIP = ref<IP | undefined>(undefined);
const updateSelectedIP = ref<IP | undefined>(undefined);

// 计算属性：是否已登录
const isAuthenticated = computed(() => !!authStore.user);

const tableColumns = ref([
  // { prop: 'id', translationKey: 'hostUUID', minWidth: 330 },
  { prop: 'ip_address', translationKey: 'ipAddress', minWidth: 120, sortable: true, align: 'center' },
  { prop: 'os_type', translationKey: 'osVersion', minWidth: 150, sortable: true, align: 'center' },
  { prop: 'status', translationKey: 'status', width: 120, slotName: 'status', sortable: true, align: 'center' },
  { prop: 'device_name', translationKey: 'deviceName', minWidth: 150, sortable: true, align: 'center' },
  { prop: 'device_type', translationKey: 'deviceType', minWidth: 150, sortable: true, align: 'center' },
  { prop: 'manufacturer', translationKey: 'architecture', minWidth: 150, sortable: true, align: 'center' },
  { prop: 'model', translationKey: 'model', minWidth: 150, sortable: true, align: 'center' },
  { prop: 'assigned_user.username', translationKey: 'owningUser', slotName: 'owningUser', minWidth: 150, sortable: true, align: 'center' },
  { prop: 'purpose', translationKey: 'purpose', minWidth: 180, align: 'center' },
  { prop: 'last_scanned', translationKey: 'lastScanned', minWidth: 180, sortable: true, align: 'center' },
]);

// 修改表格高度计算逻辑
const tableHeight = computed(() => {
  // 根据数据量动态计算表格高度
  const rowHeight = 53; // 每行的高度（包含边框）
  const headerHeight = 40; // 表头高度
  const minHeight = 200; // 最小高度
  const maxHeight = window.innerHeight - 390; // 最大高度（减去其他元素的高度）
  
  const contentHeight = tableData.value.length * rowHeight + headerHeight;
  return Math.min(Math.max(contentHeight, minHeight), maxHeight);
});

// 可搜索的列
const searchableColumns = computed(() => tableColumns.value.filter(col => 
  ['ip_address', 'device_name', 'os_type', 'device_type', 'manufacturer', 'model', 'purpose', 'assigned_user.username'].includes(col.prop)
));

// 获取列的翻译键
const getColumnTranslationKey = (prop: string) => {
  const column = tableColumns.value.find(col => col.prop === prop);
  return column ? column.translationKey : '';
};

// 组件挂载时检查登录状态
onMounted(() => {
  if (isAuthenticated.value) {
    loadIPsData();
  } else {
    router.push('/login');
  }
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
const handleClaimSuccess = async (ip: IP) => {
  ElMessage.success(t('ip.actions.claimSuccess', { ip: ip.ip_address }));
  await loadIPsData(); // 使用 loadIPsData 替代 fetchAllIPs
  claimDialogVisible.value = false;
};

// 打开 Update IP 对话框
const openUpdateDialog = (ip: IP) => {
  updateSelectedIP.value = ip;
  updateDialogVisible.value = true;
};

// 处理更新成功事件
const handleUpdateSuccess = async (ip: IP) => {
  ElMessage.success(t('ip.actions.updateSuccess', { ip: ip.ip_address }));
  await loadIPsData(); // 使用 loadIPsData 替代 fetchAllIPs
  updateDialogVisible.value = false;
};

// 处理排序变化
const handleSortChange = ({ prop, order }: { prop: string; order: string }) => {
  searchConditions.value.sortBy = prop;
  searchConditions.value.sortOrder = order === 'ascending' ? 'asc' : 'desc';
  loadIPsData();
};

// 选中的 IP 列表
const selectedIPs = ref<IP[]>([]);

// 处理表格选择变化
const handleSelectionChange = (selection: IP[]) => {
  selectedIPs.value = selection;
};

// 判断是否可以批量认领
const canBatchClaim = computed(() => {
  return selectedIPs.value.every(ip => ip.status === 'unclaimed');
});

// 判断是否可以批量更新
const canBatchUpdate = computed(() => {
  return selectedIPs.value.every(ip => 
    ip.status !== 'unclaimed' && 
    (ip.assigned_user?.username === authStore.user?.username || authStore.user?.is_admin)
  );
});

// 添加批量认领标志
const isBatchClaim = ref(false);

// 修改批量认领处理函数
const handleBatchClaim = () => {
  if (!canBatchClaim.value || selectedIPs.value.length === 0) return;
  
  isBatchClaim.value = true;
  claimDialogVisible.value = true;
};

// 修改对话框关闭处理
watch(claimDialogVisible, (newVal) => {
  if (!newVal) {
    isBatchClaim.value = false;
  }
});

// 批量更新处理
const handleBatchUpdate = () => {
  if (!canBatchUpdate.value) return;
  
  // 打开批量更新对话框
  updateSelectedIP.value = selectedIPs.value[0]; // 使用第一个 IP 的信息作为默认值
  updateDialogVisible.value = true;
};

// 搜索和过滤条件
const searchConditions = ref({
  query: '',
  column: 'all',
  status: 'all',
  sortBy: '',
  sortOrder: ''
});

// 分页配置
const pagination = ref({
  currentPage: 1,
  pageSize: 10,
  total: 0,
  loading: false
});

// 表格数据
const tableData = ref<IP[]>([]);

// 加载数据
const loadIPsData = async () => {
  pagination.value.loading = true;
  try {
    const response = await ipStore.fetchFilteredIPs({
      page: pagination.value.currentPage,
      pageSize: pagination.value.pageSize,
      query: searchQuery.value,
      column: searchColumn.value,
      status: statusFilter.value,
      sortBy: searchConditions.value.sortBy,
      sortOrder: searchConditions.value.sortOrder
    });
    
    tableData.value = response.ips;
    pagination.value.total = response.total;
  } catch (error) {
    ElMessage.error(t('common.fetchError'));
  } finally {
    pagination.value.loading = false;
  }
};

// 处理搜索
const handleSearch = debounce(() => {
  pagination.value.currentPage = 1; // 重置到第一页
  loadIPsData();
}, 300);

// 监听搜索条件变化
watch([
  () => searchQuery.value,
  () => searchColumn.value,
  () => statusFilter.value
], () => {
  handleSearch();
});

// 处理分页变化
const handlePageChange = async (page: number) => {
  pagination.value.currentPage = page;
  await loadIPsData();
};

// 处理每页条数变化
const handleSizeChange = async (size: number) => {
  pagination.value.pageSize = size;
  pagination.value.currentPage = 1;
  await loadIPsData();
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
  margin: 5px 0 0;
  font-size: 14px;
}

.filters {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.el-button-group {
  margin-right: 1rem;
}

.column-filter {
  width: 150px;
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
  position: relative;
  display: flex;
  flex-direction: column;
  min-height: 0;
  flex: 1;
}

.ip-table {
  flex: 1;
  margin-bottom: 16px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: 8px 0;
  background-color: var(--el-bg-color);
  border-top: 1px solid var(--el-border-color-lighter);
}

.pagination {
  margin: 0;
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
</style>