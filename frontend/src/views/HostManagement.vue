<template>
  <div class="host-management">
    <el-card>
      <div class="toolbar">
        <div class="toolbar-header">
          <h2>{{ $t('hostInfo.title') }}</h2>
          <p class="subtitle">{{ $t('hostInfo.subtitle') }}</p>
        </div>
      </div>

      <!-- 筛选器 -->
      <div class="filters">
        <el-select
          v-model="hostTypeFilter"
          class="filter-select"
          :placeholder="$t('hostInfo.hostType')"
        >
          <el-option :label="$t('hostInfo.filters.all')" value="all" />
          <el-option :label="$t('hostInfo.types.physical')" value="physical" />
          <el-option :label="$t('hostInfo.types.vmware')" value="vmware" />
          <el-option :label="$t('hostInfo.types.other_virtualization')" value="other_virtualization" />
        </el-select>

        <el-select
          v-model="statusFilter"
          class="filter-select"
          :placeholder="$t('hostInfo.collectionStatus')"
        >
          <el-option :label="$t('hostInfo.filters.all')" value="all" />
          <el-option :label="$t('hostInfo.status.pending')" value="pending" />
          <el-option :label="$t('hostInfo.status.collecting')" value="collecting" />
          <el-option :label="$t('hostInfo.status.success')" value="success" />
          <el-option :label="$t('hostInfo.status.failed')" value="failed" />
        </el-select>

        <el-input
          v-model="searchQuery"
          :placeholder="$t('hostInfo.filters.search')"
          :prefix-icon="Search"
          class="search-input"
          clearable
          @clear="handleSearch"
          @keyup.enter="handleSearch"
        />

        <el-button
          type="warning"
          @click="handleBatchBindCredential"
          :disabled="selectedHosts.length === 0"
        >
          {{ $t('hostInfo.actions.batchBindCredential') }}
        </el-button>

        <el-button
          type="primary"
          @click="handleBatchCollect"
          :disabled="selectedHosts.length === 0"
        >
          {{ $t('hostInfo.actions.batchCollect') }}
        </el-button>

        <el-button
          type="success"
          @click="handleBatchExport"
          :disabled="selectedHosts.length === 0"
        >
          {{ $t('hostInfo.actions.batchExport') }}
        </el-button>

        <el-button @click="handleRefresh">
          <el-icon><Refresh /></el-icon>
          {{ $t('hostInfo.actions.refresh') }}
        </el-button>
      </div>

      <!-- 表格 -->
      <div class="table-container">
        <el-table
          v-loading="hostInfoStore.loading"
          :data="tableData"
          style="width: 100%"
          :empty-text="$t('hostInfo.messages.noHosts')"
          stripe
          border
          row-key="id"
          :tree-props="{children: 'child_hosts', hasChildren: 'hasChildren'}"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" :selectable="isSelectable" />
          <el-table-column prop="ip.ip_address" :label="$t('hostInfo.ip')" min-width="120">
            <template #default="{ row }">
              {{ row.parent_host_id ? '-' : row.ip?.ip_address }}
            </template>
          </el-table-column>
          <el-table-column prop="hostname" :label="$t('hostInfo.hostname')" min-width="150">
            <template #default="{ row }">
              {{ row.raw_data?.vmware_info?.vm_name || row.hostname || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="host_type" :label="$t('hostInfo.hostType')" width="120">
            <template #default="{ row }">
              <el-tag v-if="row.host_type" :type="getHostTypeTagType(row.host_type)">
                {{ $t(`hostInfo.types.${row.host_type}`) }}
              </el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="os_name" :label="$t('hostInfo.osName')" min-width="120">
            <template #default="{ row }">
              {{ row.os_name || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="collection_status" :label="$t('hostInfo.collectionStatus')" width="120">
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.collection_status)">
                {{ $t(`hostInfo.status.${row.collection_status}`) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="last_collected_at" :label="$t('hostInfo.lastCollected')" width="180">
            <template #default="{ row }">
              {{ formatDate(row.last_collected_at) }}
            </template>
          </el-table-column>
          <el-table-column :label="$t('common.actions')" width="300" align="center">
            <template #default="{ row }">
              <el-button-group>
                <el-button
                  type="warning"
                  size="small"
                  @click="handleBindCredential(row)"
                >
                  {{ $t('hostInfo.actions.bindCredential') }}
                </el-button>
                <el-button
                  type="primary"
                  size="small"
                  @click="handleCollect(row)"
                  :disabled="row.collection_status === 'collecting'"
                >
                  {{ $t('hostInfo.actions.collect') }}
                </el-button>
                <el-button
                  type="info"
                  size="small"
                  @click="handleViewDetails(row)"
                >
                  {{ $t('hostInfo.actions.viewDetails') }}
                </el-button>
              </el-button-group>
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
          />
        </div>
      </div>
    </el-card>

    <!-- 主机详情抽屉 -->
    <el-drawer
      v-model="detailDrawerVisible"
      :title="selectedHost?.ip?.ip_address || ''"
      size="50%"
    >
      <div v-if="selectedHost" class="host-detail">
        <el-tabs>
          <el-tab-pane :label="$t('hostInfo.tabs.basic')">
            <el-descriptions :column="2" border>
              <el-descriptions-item :label="$t('hostInfo.ip')">
                {{ selectedHost.ip?.ip_address }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('hostInfo.hostname')">
                {{ selectedHost.hostname || '-' }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('hostInfo.hostType')">
                <el-tag v-if="selectedHost.host_type" :type="getHostTypeTagType(selectedHost.host_type)">
                  {{ $t(`hostInfo.types.${selectedHost.host_type}`) }}
                </el-tag>
                <span v-else>-</span>
              </el-descriptions-item>
              <el-descriptions-item :label="$t('hostInfo.osName')">
                {{ selectedHost.os_name || '-' }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('hostInfo.osVersion')">
                {{ selectedHost.os_version || '-' }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('hostInfo.kernel')">
                {{ selectedHost.kernel_version || '-' }}
              </el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>

          <el-tab-pane :label="$t('hostInfo.tabs.hardware')">
            <el-descriptions :column="1" border>
              <el-descriptions-item :label="$t('hostInfo.cpu')">
                {{ selectedHost.cpu_model || '-' }} ({{ selectedHost.cpu_cores || '-' }} {{ $t('common.cores') || '核心' }})
              </el-descriptions-item>
              <el-descriptions-item :label="$t('hostInfo.memory')">
                {{ selectedHost.memory_total ? `${selectedHost.memory_total} MB` : '-' }}
              </el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>

          <el-tab-pane :label="$t('hostInfo.tabs.network')">
            <pre v-if="selectedHost.network_interfaces" class="json-display">
              {{ JSON.stringify(selectedHost.network_interfaces, null, 2) }}
            </pre>
            <span v-else>-</span>
          </el-tab-pane>

          <el-tab-pane :label="$t('hostInfo.tabs.disk')">
            <pre v-if="selectedHost.disk_info" class="json-display">
              {{ JSON.stringify(selectedHost.disk_info, null, 2) }}
            </pre>
            <span v-else>-</span>
          </el-tab-pane>

          <el-tab-pane :label="$t('hostInfo.tabs.raw')">
            <pre v-if="selectedHost.raw_data" class="json-display">
              {{ JSON.stringify(selectedHost.raw_data, null, 2) }}
            </pre>
            <span v-else>-</span>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-drawer>

    <!-- 导出对话框 -->
    <ExportDialog
      v-model="exportDialogVisible"
      :selected-hosts="selectedHostIds"
    />

    <!-- 绑定凭证对话框 -->
    <BindCredentialDialog
      v-model="bindCredentialDialogVisible"
      :host-id="currentBindingHost?.id || ''"
      :host-ip="currentBindingHost?.ip || ''"
      @bindSuccess="handleBindSuccess"
    />

    <!-- 批量绑定凭证对话框 -->
    <el-dialog
      v-model="batchBindDialogVisible"
      :title="$t('hostInfo.actions.batchBindCredential')"
      width="500px"
    >
      <el-form label-position="top">
        <el-form-item :label="$t('credential.title')" required>
          <el-select
            v-model="batchBindCredentialId"
            :placeholder="$t('hostInfo.actions.selectCredential')"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="credential in availableCredentials"
              :key="credential.id"
              :label="`${credential.name} (${$t(`credential.types.${credential.credential_type}`)})`"
              :value="credential.id"
            >
              <div class="credential-option">
                <span class="credential-name">{{ credential.name }}</span>
                <el-tag :type="getTypeTagType(credential.credential_type)" size="small">
                  {{ $t(`credential.types.${credential.credential_type}`) }}
                </el-tag>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        <el-alert
          :title="$t('hostInfo.messages.batchBindInfo', { count: selectedHosts.length })"
          type="info"
          :closable="false"
        />
      </el-form>
      <template #footer>
        <el-button @click="batchBindDialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="confirmBatchBind" :loading="loading">
          {{ $t('common.confirm') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage } from 'element-plus';
import { Search, Refresh } from '@element-plus/icons-vue';
import { useHostInfoStore } from '../stores/hostInfo';
import { useCredentialStore } from '../stores/credential';
import ExportDialog from '../components/ExportDialog.vue';
import BindCredentialDialog from '../components/BindCredentialDialog.vue';
import type { HostInfo } from '../types/hostInfo';

const { t } = useI18n();
const hostInfoStore = useHostInfoStore();
const credentialStore = useCredentialStore();

const hostTypeFilter = ref('all');
const statusFilter = ref('all');
const searchQuery = ref('');
const selectedHosts = ref<HostInfo[]>([]);
const detailDrawerVisible = ref(false);
const exportDialogVisible = ref(false);
const bindCredentialDialogVisible = ref(false);
const selectedHost = ref<HostInfo | null>(null);
const currentBindingHost = ref<{id: string, ip: string} | null>(null);

// 批量绑定相关
const batchBindDialogVisible = ref(false);
const batchBindCredentialId = ref('');
const loading = ref(false);

const pagination = ref({
  currentPage: 1,
  pageSize: 10,
  total: 0
});

const tableData = computed(() => {
  return hostInfoStore.hosts;
});

const selectedHostIds = computed(() => {
  return selectedHosts.value.map(h => h.id);
});

const availableCredentials = computed(() => {
  return credentialStore.credentials.filter(c => !(c as any).deleted);
});

onMounted(async () => {
  await loadHosts();
  await credentialStore.fetchCredentials();
});

const loadHosts = async () => {
  try {
    await hostInfoStore.fetchHosts({
      page: pagination.value.currentPage,
      pageSize: pagination.value.pageSize,
      host_type: hostTypeFilter.value === 'all' ? undefined : hostTypeFilter.value,
      collection_status: statusFilter.value === 'all' ? undefined : statusFilter.value,
      query: searchQuery.value || undefined
    });
    pagination.value.total = hostInfoStore.total;
  } catch (error) {
    ElMessage.error(t('common.fetchError'));
  }
};

const handleRefresh = () => {
  loadHosts();
};

const handleSearch = () => {
  pagination.value.currentPage = 1;
  loadHosts();
};

const handlePageChange = () => {
  loadHosts();
};

const handleSizeChange = () => {
  pagination.value.currentPage = 1;
  loadHosts();
};

const handleSelectionChange = (selection: HostInfo[]) => {
  selectedHosts.value = selection;
};

const handleCollect = async (host: HostInfo) => {
  try {
    await hostInfoStore.collectHostInfo(host.id);
    ElMessage.success(t('hostInfo.messages.collectSuccess'));
    await loadHosts();
  } catch (error) {
    ElMessage.error(t('hostInfo.messages.collectFailed'));
  }
};

const handleBatchCollect = async () => {
  try {
    await hostInfoStore.batchCollectHosts({ host_ids: selectedHostIds.value });
    ElMessage.success(t('hostInfo.messages.collectSuccess'));
    await loadHosts();
  } catch (error) {
    ElMessage.error(t('hostInfo.messages.collectFailed'));
  }
};

const handleBatchExport = () => {
  exportDialogVisible.value = true;
};

const handleViewDetails = (host: HostInfo) => {
  selectedHost.value = host;
  detailDrawerVisible.value = true;
};

const handleBindCredential = (host: HostInfo) => {
  currentBindingHost.value = {
    id: host.id,
    ip: host.ip?.ip_address || ''
  };
  bindCredentialDialogVisible.value = true;
};

const handleBindSuccess = async (data: {hostId: string, credentialId: string}) => {
  try {
    await hostInfoStore.bindCredential(data.hostId, {
      credential_id: data.credentialId
    });
    ElMessage.success(t('hostInfo.messages.bindSuccess'));
    await loadHosts();
  } catch (error: any) {
    ElMessage.error(error.response?.data?.error || t('hostInfo.messages.bindFailed'));
  }
};

const handleBatchBindCredential = () => {
  batchBindCredentialId.value = '';
  batchBindDialogVisible.value = true;
};

const confirmBatchBind = async () => {
  if (!batchBindCredentialId.value) {
    ElMessage.warning(t('credential.messages.credentialRequired'));
    return;
  }
  
  loading.value = true;
  try {
    await hostInfoStore.batchBindCredentials({
      host_ids: selectedHostIds.value,
      credential_id: batchBindCredentialId.value
    });
    ElMessage.success(t('hostInfo.messages.bindSuccess'));
    batchBindDialogVisible.value = false;
    await loadHosts();
  } catch (error: any) {
    ElMessage.error(error.response?.data?.error || t('hostInfo.messages.bindFailed'));
  } finally {
    loading.value = false;
  }
};

const getStatusTagType = (status: string) => {
  const typeMap: Record<string, string> = {
    pending: 'info',
    collecting: 'warning',
    success: 'success',
    failed: 'danger'
  };
  return typeMap[status] || '';
};

const getHostTypeTagType = (type: string) => {
  const typeMap: Record<string, string> = {
    physical: 'primary',
    vmware: 'success',
    other_virtualization: 'info'
  };
  return typeMap[type] || '';
};

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-';
  return new Date(dateStr).toLocaleString();
};

const getTypeTagType = (type: string) => {
  const typeMap: Record<string, string> = {
    linux: 'success',
    windows: 'primary',
    vmware: 'warning'
  };
  return typeMap[type] || '';
};

const isSelectable = (row: HostInfo) => {
  // 子主机不可选，避免重复统计
  return !row.parent_host_id;
};
</script>

<style scoped>
.host-management {
  padding: 20px;
}

.toolbar {
  margin-bottom: 20px;
}

.toolbar-header h2 {
  margin: 0 0 5px 0;
  font-size: 24px;
}

.subtitle {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.filters {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filter-select {
  width: 150px;
}

.search-input {
  width: 250px;
}

.table-container {
  margin-top: 20px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.host-detail {
  padding: 20px;
}

.json-display {
  background-color: var(--el-bg-color-page);
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
  font-family: 'Courier New', monospace;
  max-height: 400px;
}

.credential-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.credential-name {
  margin-right: 10px;
}
</style>

