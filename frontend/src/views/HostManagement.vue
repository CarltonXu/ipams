<template>
  <div class="host-management">
    <el-card>
      <div class="toolbar">
        <div class="toolbar-header">
          <h2>{{ $t('hostInfo.title') }}</h2>
          <p class="subtitle">{{ $t('hostInfo.subtitle') }}</p>
        </div>
      </div>

      <!-- 标签页切换 -->
      <el-tabs v-model="activeTab" class="host-tabs">
        <el-tab-pane :label="$t('hostInfo.tabs.hostList', '主机列表')" name="hosts">

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
          :lazy="true"
          :load="loadChildren"
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
                  v-if="row.collection_status === 'collecting'"
                  type="danger"
                  size="small"
                  @click="handleCancelCollection(row)"
                  :loading="cancellingTasks[row.id]"
                >
                  {{ $t('hostInfo.actions.cancelCollection', '取消采集') }}
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
        </el-tab-pane>
        
        <!-- 任务历史标签页 -->
        <el-tab-pane :label="$t('hostInfo.tabs.taskHistory', '采集任务历史')" name="tasks">
          <CollectionTaskHistory />
        </el-tab-pane>
      </el-tabs>
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

    <!-- 采集进度对话框 -->
    <CollectionProgress
      v-model="progressDialogVisible"
      :task-id="currentTaskId"
      @completed="handleProgressCompleted"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Search, Refresh } from '@element-plus/icons-vue';
import { useHostInfoStore } from '../stores/hostInfo';
import { useCredentialStore } from '../stores/credential';
import ExportDialog from '../components/ExportDialog.vue';
import BindCredentialDialog from '../components/BindCredentialDialog.vue';
import CollectionProgress from '../components/CollectionProgress.vue';
import CollectionTaskHistory from '../components/CollectionTaskHistory.vue';
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

// 采集进度相关
const progressDialogVisible = ref(false);
const currentTaskId = ref<string | null>(null);

// 标签页
const activeTab = ref('hosts');

// 取消任务相关
const cancellingTasks = ref<Record<string, boolean>>({});

const pagination = ref({
  currentPage: 1,
  pageSize: 10,
  total: 0
});

// 存储原始数据（包含子节点）
const originalHostsData = ref<HostInfo[]>([]);

const tableData = computed(() => {
  return originalHostsData.value.map(host => {
    const hasChildren = !!(host.child_hosts && host.child_hosts.length > 0);
    
    const result: any = {
      ...host,
      child_hosts: hasChildren ? [] : undefined,
      hasChildren: hasChildren,
      _hasLoadedChildren: false,
      _loading: false
    };
    
    return result;
  });
});

// 存储已加载的子节点数据
const loadedChildrenMap = ref<Map<string, HostInfo[]>>(new Map());

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
    originalHostsData.value = JSON.parse(JSON.stringify(hostInfoStore.hosts));
    loadedChildrenMap.value.clear();
  } catch (error) {
    ElMessage.error(t('common.fetchError'));
  }
};

// 懒加载子节点
const loadChildren = async (row: any, _treeNode: any, resolve: (data: HostInfo[]) => void) => {
  if (loadedChildrenMap.value.has(row.id)) {
    const cachedChildren = loadedChildrenMap.value.get(row.id)!;
    resolve(cachedChildren);
    return;
  }

  try {
    const originalHost = originalHostsData.value.find(h => h.id === row.id);
    
    if (originalHost && originalHost.child_hosts && originalHost.child_hosts.length > 0) {
      await new Promise(resolveDelay => setTimeout(resolveDelay, 300));
      
      const children = originalHost.child_hosts.map((child: HostInfo) => {
        const childHasChildren = !!(child.child_hosts && child.child_hosts.length > 0);
        return {
          ...child,
          child_hosts: undefined,
          hasChildren: childHasChildren,
          _hasLoadedChildren: false,
          _loading: false
        };
      });
      
      loadedChildrenMap.value.set(row.id, children);
      resolve(children);
      return;
    }

    resolve([]);
  } catch (error) {
    ElMessage.error(t('hostInfo.messages.loadChildrenFailed') || '加载子节点失败');
    resolve([]);
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
    // 立即更新本地主机状态为'collecting'，防止重复点击
    const hostIndex = originalHostsData.value.findIndex(h => h.id === host.id);
    if (hostIndex !== -1) {
      originalHostsData.value[hostIndex].collection_status = 'collecting';
    }
    
    const response = await hostInfoStore.collectHostInfo(host.id);
    // 单个主机采集现在也返回task_id，显示进度对话框
    if (response.task_id) {
      currentTaskId.value = response.task_id;
      progressDialogVisible.value = true;
      ElMessage.success(t('hostInfo.messages.collectStarted', '采集任务已启动'));
    } else {
      ElMessage.success(t('hostInfo.messages.collectSuccess'));
      await loadHosts();
    }
  } catch (error) {
    ElMessage.error(t('hostInfo.messages.collectFailed'));
    // 如果失败，重新加载主机列表以恢复正确状态
    await loadHosts();
  }
};

const handleBatchCollect = async () => {
  try {
    // 立即更新本地所有选中主机状态为'collecting'，防止重复点击
    selectedHostIds.value.forEach(hostId => {
      const hostIndex = originalHostsData.value.findIndex(h => h.id === hostId);
      if (hostIndex !== -1) {
        originalHostsData.value[hostIndex].collection_status = 'collecting';
      }
    });
    
    const response = await hostInfoStore.batchCollectHosts({ host_ids: selectedHostIds.value });
    // 如果返回了task_id，显示进度对话框
    if (response.task_id) {
      currentTaskId.value = response.task_id;
      progressDialogVisible.value = true;
      ElMessage.success(t('hostInfo.messages.collectStarted', '采集任务已启动'));
    } else {
      ElMessage.success(t('hostInfo.messages.collectSuccess'));
      await loadHosts();
    }
  } catch (error) {
    ElMessage.error(t('hostInfo.messages.collectFailed'));
    // 如果失败，重新加载主机列表以恢复正确状态
    await loadHosts();
  }
};

// 处理进度完成事件
const handleProgressCompleted = async () => {
  ElMessage.success(t('hostInfo.messages.collectSuccess'));
  await loadHosts();
  // 可以选择自动关闭对话框或保持打开让用户查看结果
  // progressDialogVisible.value = false;
};

// 取消采集任务
const handleCancelCollection = async (host: HostInfo) => {
  try {
    // 查找该主机正在进行的任务（包括pending和running状态）
    // 先查找running状态
    let tasksResponse = await hostInfoStore.getCollectionTasks({
      status: 'running',
      host_id: host.id,
      page: 1,
      page_size: 10
    });
    
    // 如果没找到running，再查找pending状态
    if (!tasksResponse.tasks || tasksResponse.tasks.length === 0) {
      tasksResponse = await hostInfoStore.getCollectionTasks({
        status: 'pending',
        host_id: host.id,
        page: 1,
        page_size: 10
      });
    }
    
    // 如果还是没找到，尝试不指定状态查找（可能任务刚创建，状态还没更新）
    if (!tasksResponse.tasks || tasksResponse.tasks.length === 0) {
      tasksResponse = await hostInfoStore.getCollectionTasks({
        host_id: host.id,
        page: 1,
        page_size: 10
      });
      
      // 过滤出pending或running状态的任务
      if (tasksResponse.tasks) {
        tasksResponse.tasks = tasksResponse.tasks.filter(
          (task: any) => task.status === 'pending' || task.status === 'running'
        );
      }
    }
    
    if (!tasksResponse.tasks || tasksResponse.tasks.length === 0) {
      // 如果确实找不到任务，可能是任务已完成或状态已更新，直接刷新主机列表
      ElMessage.info(t('hostInfo.messages.noRunningTask', '未找到正在进行的采集任务，已刷新列表'));
      await loadHosts();
      return;
    }
    
    // 选择最新的任务（通常是第一个，因为按创建时间倒序）
    const runningTask = tasksResponse.tasks[0];
    
    await ElMessageBox.confirm(
      t('hostInfo.collectionTask.confirmCancel', '确定要取消此采集任务吗？取消后可以重新发起采集。'),
      t('hostInfo.collectionTask.cancelTask', '取消任务'),
      {
        confirmButtonText: t('common.confirm', '确定'),
        cancelButtonText: t('common.cancel', '取消'),
        type: 'warning'
      }
    );
    
    cancellingTasks.value[host.id] = true;
    try {
      await hostInfoStore.cancelCollectionTask(runningTask.id);
      ElMessage.success(t('hostInfo.collectionTask.cancelSuccess', '任务已取消'));
      
      // 刷新主机列表和任务列表
      await loadHosts();
      
      // 如果当前进度对话框打开的是这个任务，关闭它
      if (currentTaskId.value === runningTask.id) {
        progressDialogVisible.value = false;
        currentTaskId.value = null;
      }
    } finally {
      cancellingTasks.value[host.id] = false;
    }
  } catch (error: any) {
    if (error !== 'cancel') {  // 用户取消操作不算错误
      ElMessage.error(error.message || t('hostInfo.collectionTask.cancelFailed', '取消任务失败'));
    }
    cancellingTasks.value[host.id] = false;
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

/* 加载动画样式 */
.is-loading {
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 表格行加载状态样式 */
.table-container :deep(.el-table__body-wrapper) {
  transition: opacity 0.3s;
}

.table-container :deep(.el-table__row) {
  transition: background-color 0.2s;
}
</style>

