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
          clearable
          @change="handleFilterChange"
          @clear="() => handleFilterClear('hostType')"
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
          clearable
          @change="handleFilterChange"
          @clear="() => handleFilterClear('status')"
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
          <el-table-column prop="ip.ip_address" :label="$t('hostInfo.ip')" min-width="60">
            <template #default="{ row }">
              {{ row.parent_host_id ? '-' : row.ip?.ip_address }}
            </template>
          </el-table-column>
          <el-table-column prop="hostname" :label="$t('hostInfo.hostname')" min-width="150">
            <template #default="{ row }">
              {{ row.hostname || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="ip.host_type" :label="$t('hostInfo.hostType')" width="190" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.host_type" :type="getHostTypeTagType(row.host_type)">
                {{ $t(`hostInfo.types.${row.host_type}`) }}
              </el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="ip.os_type" :label="$t('hostInfo.osType')" width="120" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.ip?.os_type" type="info">
                {{ row.parent_host_id ? 'N/A' : (row.ip.os_type || 'N/A') }}
              </el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="os_name" :label="$t('hostInfo.osName')" min-width="120">
            <template #default="{ row }">
              {{ row.os_name || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="collection_status" :label="$t('hostInfo.collectionStatus')" width="160" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.collection_status)">
                {{ $t(`hostInfo.status.${row.collection_status}`) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column :label="$t('hostInfo.credential', '凭证')" width="250">
            <template #default="{ row }">
                <div v-if="row.credential_bindings && row.credential_bindings.length > 0" class="credential-display">
                  <el-tag
                    v-for="binding in row.credential_bindings"
                    :key="binding.id"
                    type="success"
                    size="small"
                    style="margin-right: 4px"
                  >
                    {{ binding.credential?.name || '-' }}
                  </el-tag>
                  <el-tag
                    v-if="row.credential_bindings[0]?.credential"
                    :type="getCredentialTypeTagType(row.credential_bindings[0].credential.credential_type)"
                    size="small"
                  >
                    {{ $t(`credential.types.${row.credential_bindings[0].credential.credential_type}`) }}
                  </el-tag>
                </div>
                <span v-else class="no-credential">-</span>
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
                <!-- VMware子主机不显示绑定凭证按钮 -->
                <el-button
                  v-if="!row.parent_host_id"
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
          <CollectionTaskHistory ref="taskHistoryRef" />
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 主机详情抽屉 -->
    <el-drawer
      v-model="detailDrawerVisible"
      :title="selectedHost?.ip?.ip_address + ' / ' + selectedHost?.hostname || ''"
      size="50%"
    >
      <div v-if="selectedHost" class="host-detail" v-loading="detailLoading" :element-loading-text="t('common.loading')">
        <el-tabs @tab-change="handleDetailTabChange">
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
            <div v-if="selectedHost.network_interfaces && networkInterfacesList.length > 0" class="network-container">
              <el-card
                v-for="(iface, index) in networkInterfacesList"
                :key="index"
                shadow="hover"
                class="network-card"
                :style="{ marginBottom: '15px' }"
              >
                <template #header>
                  <div class="network-card-header">
                    <el-tag :type="iface.connected ? 'success' : 'info'" size="large">
                      {{ iface.label || iface.device || `${t('hostInfo.detail.network.interface')} ${index + 1}` }}
                    </el-tag>
                    <el-tag v-if="iface.connected" type="success" size="small">
                      {{ t('hostInfo.detail.network.connected') }}
                    </el-tag>
                    <el-tag v-else type="info" size="small">
                      {{ t('hostInfo.detail.network.disconnected') }}
                    </el-tag>
                  </div>
                </template>
                <el-descriptions :column="2" border>
                  <el-descriptions-item :label="t('hostInfo.detail.network.deviceName')" v-if="iface.label || iface.device || iface.name">
                    <code>{{ iface.label || iface.device || iface.name }}</code>
                  </el-descriptions-item>
                  <el-descriptions-item :label="t('hostInfo.detail.network.deviceId')" v-if="iface.deviceConfigId || iface.device">
                    <code>{{ iface.deviceConfigId || iface.device }}</code>
                  </el-descriptions-item>
                  <el-descriptions-item :label="t('hostInfo.detail.network.macAddress')" v-if="iface.mac_address">
                    <el-tag type="primary">{{ iface.mac_address }}</el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item :label="t('hostInfo.detail.network.ipAddress')" v-if="iface.ip_addresses && iface.ip_addresses.length > 0">
                    <div class="ip-list">
                      <el-tag
                        v-for="(ip, ipIndex) in iface.ip_addresses"
                        :key="ipIndex"
                        :type="ip.includes(':') ? 'warning' : 'success'"
                        style="margin-right: 8px; margin-bottom: 4px;"
                      >
                        {{ ip }}
                      </el-tag>
                    </div>
                  </el-descriptions-item>
                  <el-descriptions-item :label="t('hostInfo.detail.network.connectionStatus')" v-if="iface.connected !== undefined && iface.connected !== null">
                    <el-tag :type="iface.connected ? 'success' : 'info'">
                      {{ iface.connected ? t('hostInfo.detail.network.connected') : t('hostInfo.detail.network.disconnected') }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item :label="t('hostInfo.detail.network.networkName')" v-if="iface.network_name">
                    {{ iface.network_name }}
                  </el-descriptions-item>
                  <el-descriptions-item :label="t('hostInfo.detail.network.network')" v-if="iface.network">
                    {{ iface.network }}
                  </el-descriptions-item>
                  <el-descriptions-item :label="t('hostInfo.detail.network.addressType')" v-if="iface.address_type">
                    <el-tag type="info" size="small">{{ iface.address_type }}</el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item :label="t('hostInfo.detail.network.portgroup')" v-if="iface.portgroup_key">
                    <code>{{ iface.portgroup_key }}</code>
                  </el-descriptions-item>
                  <el-descriptions-item :label="t('hostInfo.detail.network.wakeOnLan')" v-if="iface.wake_on_lan_enabled !== undefined">
                    <el-tag :type="iface.wake_on_lan_enabled ? 'success' : 'info'" size="small">
                      {{ iface.wake_on_lan_enabled ? t('hostInfo.detail.network.enabled') : t('hostInfo.detail.network.disabled') }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item :label="t('hostInfo.detail.network.interfaceType')" v-if="iface.type">
                    <el-tag type="info" size="small">{{ iface.type }}</el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item :label="t('hostInfo.detail.network.speed')" v-if="iface.speed">
                    {{ formatNetworkSpeed(iface.speed) }}
                  </el-descriptions-item>
                  <el-descriptions-item :label="t('hostInfo.detail.network.state')" v-if="iface.state">
                    <el-tag :type="iface.state === 'UP' ? 'success' : 'info'" size="small">
                      {{ iface.state }}
                    </el-tag>
                  </el-descriptions-item>
                </el-descriptions>
              </el-card>
            </div>
            <el-empty v-else :description="t('hostInfo.detail.network.noData')" />
          </el-tab-pane>

          <el-tab-pane :label="$t('hostInfo.tabs.disk')">
            <div v-if="selectedHost.disk_info && diskInfoList.length > 0" class="disk-container">
              <el-card
                v-for="(disk, index) in diskInfoList"
                :key="index"
                shadow="hover"
                class="disk-card"
                :style="{ marginBottom: '15px' }"
              >
                <template #header>
                  <div class="disk-card-header">
                    <el-tag type="primary" size="large">
                      {{ disk.label || disk.device || disk.DeviceID || disk.DEVICE || disk.disk_path || disk.MOUNT || disk.mount || `${t('hostInfo.detail.disk.disk')} ${index + 1}` }}
                    </el-tag>
                    <el-tag
                      v-if="getDiskUsePercent(disk) !== null"
                      :type="getDiskUsePercentType(getDiskUsePercent(disk) || 0)"
                      size="small"
                    >
                      {{ t('hostInfo.detail.disk.usageRate') }}: {{ getDiskUsePercent(disk) }}%
                    </el-tag>
                  </div>
                </template>
                <el-descriptions :column="2" border>
                  <el-descriptions-item :label="t('hostInfo.detail.disk.deviceName')" v-if="disk.label || disk.device || disk.DeviceID || disk.DEVICE">
                    <code>{{ disk.label || disk.device || disk.DeviceID || disk.DEVICE }}</code>
                  </el-descriptions-item>
                  <el-descriptions-item :label="t('hostInfo.detail.disk.mountPoint')" v-if="disk.disk_path || disk.MOUNT || disk.mount">
                    <code>{{ disk.disk_path || disk.MOUNT || disk.mount }}</code>
                  </el-descriptions-item>
                  <el-descriptions-item :label="t('hostInfo.detail.disk.capacity')" v-if="getDiskCapacity(disk)">
                    {{ formatDiskSize(getDiskCapacity(disk)) }}
                  </el-descriptions-item>
                  <el-descriptions-item :label="t('hostInfo.detail.disk.capacityKB')" v-if="disk.capacity_kb">
                    {{ formatBytes(disk.capacity_kb * 1024) }}
                  </el-descriptions-item>
                  <el-descriptions-item :label="t('hostInfo.detail.disk.freeSpace')" v-if="getDiskFreeSpace(disk)">
                    <el-tag type="success">{{ formatDiskSize(getDiskFreeSpace(disk)) }}</el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item :label="t('hostInfo.detail.disk.usedSpace')" v-if="getDiskUsedSpace(disk)">
                    <el-tag type="warning">{{ formatDiskSize(getDiskUsedSpace(disk)) }}</el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item :label="t('hostInfo.detail.disk.usageRate')" v-if="getDiskUsePercent(disk) !== null">
                    <el-tag :type="getDiskUsePercentType(getDiskUsePercent(disk) || 0)" size="small">
                      {{ getDiskUsePercent(disk) }}%
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item :label="t('hostInfo.detail.disk.fileSystem')" v-if="disk.file_system || disk.FileSystem || disk.FSTYPE || disk.fstype">
                    <el-tag type="info">{{ disk.file_system || disk.FileSystem || disk.FSTYPE || disk.fstype }}</el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item :label="t('hostInfo.detail.disk.volumeName')" v-if="disk.VolumeName">
                    {{ disk.VolumeName }}
                  </el-descriptions-item>
                  <el-descriptions-item :label="t('hostInfo.detail.disk.diskMode')" v-if="disk.disk_mode">
                    <el-tag :type="disk.disk_mode.includes('persistent') ? 'success' : 'warning'">
                      {{ disk.disk_mode }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item :label="t('hostInfo.detail.disk.thinProvisioned')" v-if="disk.thin_provisioned !== undefined">
                    <el-tag :type="disk.thin_provisioned ? 'warning' : 'success'">
                      {{ disk.thin_provisioned ? t('hostInfo.detail.disk.yes') : t('hostInfo.detail.disk.no') }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item :label="t('hostInfo.detail.disk.eagerlyScrub')" v-if="disk.eagerly_scrub !== undefined">
                    <el-tag :type="disk.eagerly_scrub ? 'warning' : 'success'" size="small">
                      {{ disk.eagerly_scrub ? t('hostInfo.detail.disk.yes') : t('hostInfo.detail.disk.no') }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item :label="t('hostInfo.detail.disk.uuid')" v-if="disk.uuid">
                    <code style="font-size: 11px;">{{ disk.uuid }}</code>
                  </el-descriptions-item>
                  <el-descriptions-item :label="t('hostInfo.detail.disk.fileName')" v-if="disk.file_name">
                    <code style="font-size: 11px;">{{ disk.file_name }}</code>
                  </el-descriptions-item>
                  <el-descriptions-item :label="t('hostInfo.detail.disk.datastore')" v-if="disk.datastore">
                    {{ disk.datastore }}
                  </el-descriptions-item>
                  <el-descriptions-item :label="t('hostInfo.detail.disk.deviceType')" v-if="disk.TYPE || disk.DriveType">
                    <el-tag type="info" size="small">{{ disk.TYPE || getDriveTypeName(disk.DriveType) }}</el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item :label="t('hostInfo.detail.disk.vendor')" v-if="disk.VENDOR">
                    {{ disk.VENDOR }}
                  </el-descriptions-item>
                  <el-descriptions-item :label="t('hostInfo.detail.disk.model')" v-if="disk.MODEL">
                    {{ disk.MODEL }}
                  </el-descriptions-item>
                </el-descriptions>
                <div v-if="getDiskUsePercent(disk) !== null" class="disk-progress" style="margin-top: 15px;">
                  <el-progress
                    :percentage="getDiskUsePercent(disk) || 0"
                    :status="getDiskUsePercentStatus(getDiskUsePercent(disk) || 0)"
                    :stroke-width="12"
                  />
                </div>
              </el-card>
            </div>
            <el-empty v-else :description="t('hostInfo.detail.disk.noData')" />
          </el-tab-pane>

          <el-tab-pane :label="$t('hostInfo.tabs.raw')">
            <div v-if="selectedHost.raw_data" class="raw-data-container">
              <JsonTreeView :data="selectedHost.raw_data" />
            </div>
            <el-empty v-else :description="t('hostInfo.detail.raw.noData')" />
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
      :host-type="currentBindingHost?.host_type"
      :os-type="currentBindingHost?.os_type"
      :current-bindings="currentBindingHost?.credential_bindings || []"
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
      @failed="handleProgressFailed"
      @statusChanged="handleProgressStatusChanged"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Search, Refresh } from '@element-plus/icons-vue';
import { useHostInfoStore } from '../stores/hostInfo';
import { useCredentialStore } from '../stores/credential';
import ExportDialog from '../components/ExportDialog.vue';
import BindCredentialDialog from '../components/BindCredentialDialog.vue';
import CollectionProgress from '../components/CollectionProgress.vue';
import CollectionTaskHistory from '../components/CollectionTaskHistory.vue';
import JsonTreeView from '../components/JsonTreeView.vue';
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
const detailLoading = ref(false);
const hostDetailLoaded = ref(false); // 标记是否已加载完整详情
const currentBindingHost = ref<{id: string, ip: string, host_type?: string, os_type?: string, credential_bindings?: any[]} | null>(null);

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

// 任务历史组件引用
const taskHistoryRef = ref<InstanceType<typeof CollectionTaskHistory> | null>(null);

// 监听tab切换，自动刷新数据
watch(activeTab, (newTab) => {
  if (newTab === 'hosts') {
    // 切换到主机列表标签时，刷新主机列表
    loadHosts();
  } else if (newTab === 'tasks') {
    // 切换到任务历史标签时，刷新任务列表
    // 使用 nextTick 确保组件已经渲染
    nextTick(() => {
      if (taskHistoryRef.value) {
        // 调用子组件的刷新方法
        (taskHistoryRef.value as any).fetchTasks?.();
      }
    });
  }
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

// 处理筛选器变化，自动触发接口调用
const handleFilterChange = () => {
  pagination.value.currentPage = 1;
  loadHosts();
};

// 处理筛选器清除，重置为all并触发接口调用
const handleFilterClear = (filterType: 'hostType' | 'status') => {
  // clearable触发时，v-model已经是null或undefined，需要重置为'all'
  if (filterType === 'hostType') {
    hostTypeFilter.value = 'all';
  } else if (filterType === 'status') {
    statusFilter.value = 'all';
  }
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
    // 检查凭证绑定情况
    let hasCredential = false;
    let parentHost: HostInfo | null = null;
    
    if (host.parent_host_id) {
      // 如果是VMware子主机，检查父主机是否有凭证
      parentHost = originalHostsData.value.find(h => h.id === host.parent_host_id) || null;
      if (parentHost && parentHost.credential_bindings && parentHost.credential_bindings.length > 0) {
        hasCredential = true;
      }
    } else {
      // 普通主机，检查自己是否有凭证
      if (host.credential_bindings && host.credential_bindings.length > 0) {
        hasCredential = true;
      }
    }
    
    if (!hasCredential) {
      // 没有凭证，提示用户先绑定凭证
      const hostToBind = parentHost || host;
      const hostName = hostToBind.ip?.ip_address || hostToBind.hostname || hostToBind.id;
      
      try {
        await ElMessageBox.confirm(
          parentHost 
            ? t('hostInfo.messages.vmwareChildNeedParentCredential', { hostName }, `VMware子主机需要使用父主机(${hostName})的凭证进行采集，请先为父主机绑定凭证。`)
            : t('hostInfo.messages.credentialRequiredForCollection', { hostName }, `主机 ${hostName} 未绑定凭证，请先绑定凭证后再进行采集。`),
          t('hostInfo.messages.credentialRequiredTitle', '需要绑定凭证'),
          {
            confirmButtonText: t('hostInfo.actions.bindCredential', '绑定凭证'),
            cancelButtonText: t('common.cancel', '取消'),
            type: 'warning'
          }
        );
        
        // 用户确认后，打开绑定凭证对话框
        handleBindCredential(hostToBind);
      } catch {
        // 用户取消，不进行任何操作
      }
      return;
    }
    
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
    // 检查所有选中主机是否有凭证
    const hostsWithoutCredential: HostInfo[] = [];
    const hostsToCollect: string[] = [];
    
    for (const hostId of selectedHostIds.value) {
      const host = originalHostsData.value.find(h => h.id === hostId);
      if (!host) continue;
      
      let hasCredential = false;
      let parentHost: HostInfo | null = null;
      
      if (host.parent_host_id) {
        // 如果是VMware子主机，检查父主机是否有凭证
        parentHost = originalHostsData.value.find(h => h.id === host.parent_host_id) || null;
        if (parentHost && parentHost.credential_bindings && parentHost.credential_bindings.length > 0) {
          hasCredential = true;
        }
      } else {
        // 普通主机，检查自己是否有凭证
        if (host.credential_bindings && host.credential_bindings.length > 0) {
          hasCredential = true;
        }
      }
      
      if (!hasCredential) {
        hostsWithoutCredential.push(parentHost || host);
      } else {
        hostsToCollect.push(hostId);
      }
    }
    
    // 如果有主机没有凭证，提示用户
    if (hostsWithoutCredential.length > 0) {
      const hostNames = hostsWithoutCredential.map(h => h.ip?.ip_address || h.hostname || h.id).join('、');
      await ElMessageBox.alert(
        t('hostInfo.messages.batchCollectCredentialRequired', { hostNames }, `以下主机未绑定凭证，请先绑定凭证后再进行采集：${hostNames}`),
        t('hostInfo.messages.credentialRequiredTitle', '需要绑定凭证'),
        {
          confirmButtonText: t('common.confirm', '确定'),
          type: 'warning'
        }
      );
      
      // 如果有未绑定凭证的主机，不进行批量采集
      if (hostsToCollect.length === 0) {
        return;
      }
      
      // 如果部分主机有凭证，询问是否只采集有凭证的主机
      if (hostsToCollect.length < selectedHostIds.value.length) {
        try {
          await ElMessageBox.confirm(
            t('hostInfo.messages.batchCollectPartial', { count: hostsToCollect.length }, `只有 ${hostsToCollect.length} 台主机已绑定凭证，是否只采集这些主机？`),
            t('hostInfo.messages.confirmBatchCollect', '确认批量采集'),
            {
              confirmButtonText: t('common.confirm', '确定'),
              cancelButtonText: t('common.cancel', '取消'),
              type: 'info'
            }
          );
        } catch {
          // 用户取消，不进行采集
          return;
        }
      }
    }
    
    // 如果没有可采集的主机，返回
    if (hostsToCollect.length === 0) {
      ElMessage.warning(t('hostInfo.messages.noValidHostsForCollect', '没有可采集的主机（所有主机都未绑定凭证）'));
      return;
    }
    
    // 立即更新本地所有选中主机状态为'collecting'，防止重复点击
    hostsToCollect.forEach(hostId => {
      const hostIndex = originalHostsData.value.findIndex(h => h.id === hostId);
      if (hostIndex !== -1) {
        originalHostsData.value[hostIndex].collection_status = 'collecting';
      }
    });
    
    const response = await hostInfoStore.batchCollectHosts({ host_ids: hostsToCollect });
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

// 处理进度失败事件
const handleProgressFailed = async () => {
  // 采集失败后刷新主机列表，确保状态更新
  await loadHosts();
};

// 处理进度状态变化事件（完成/失败/取消）
const handleProgressStatusChanged = async () => {
  // 无论任务完成、失败或取消，都刷新主机列表以确保状态同步
  await loadHosts();
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

const handleViewDetails = async (host: HostInfo) => {
  // 先设置基础信息，立即显示抽屉
  selectedHost.value = host;
  detailDrawerVisible.value = true;
  hostDetailLoaded.value = false;
  
  // 热加载完整详情数据
  detailLoading.value = true;
  try {
    const fullHostData = await hostInfoStore.fetchHostById(host.id);
    if (fullHostData) {
      // 合并完整数据到selectedHost
      selectedHost.value = { ...host, ...fullHostData };
      hostDetailLoaded.value = true;
    }
  } catch (error) {
    console.error('Failed to load host details:', error);
    ElMessage.warning(t('hostInfo.messages.loadDetailsFailed', '加载主机详情失败，显示基础信息'));
  } finally {
    detailLoading.value = false;
  }
};

// 处理详情标签页切换（备用：如果数据加载失败，切换标签时可以重新尝试加载）
const handleDetailTabChange = (tabName: string | number) => {
  // 如果详情数据还未加载完成，切换到需要详细数据的标签页时，可以重新尝试加载
  if (!hostDetailLoaded.value && selectedHost.value && typeof tabName === 'number') {
    // 索引2、3、4分别对应network、disk、raw标签页（需要详细数据）
    const detailTabIndices = [2, 3, 4];
    if (detailTabIndices.includes(tabName)) {
      // 重新尝试加载完整数据
      handleViewDetails(selectedHost.value);
    }
  }
};

// 网络接口列表计算属性
const networkInterfacesList = computed(() => {
  if (!selectedHost.value?.network_interfaces) return [];
  const interfaces = selectedHost.value.network_interfaces;
  if (Array.isArray(interfaces)) {
    return interfaces.map((iface: any) => {
      // 处理IP地址数组
      let ip_addresses: string[] = [];
      if (iface.ip_addresses && Array.isArray(iface.ip_addresses)) {
        ip_addresses = iface.ip_addresses;
      } else if (iface.ip_address) {
        ip_addresses = Array.isArray(iface.ip_address) ? iface.ip_address : [iface.ip_address];
      }
      
      return {
        ...iface,
        ip_addresses,
        connected: iface.connected !== undefined ? iface.connected : true // 默认已连接
      };
    });
  }
  return [];
});

// 磁盘信息列表计算属性
const diskInfoList = computed(() => {
  if (!selectedHost.value?.disk_info) return [];
  const disks = selectedHost.value.disk_info;
  return Array.isArray(disks) ? disks : [];
});

// 格式化字节数
const formatBytes = (bytes: number | string | null | undefined): string => {
  if (bytes === null || bytes === undefined) return '-';
  const numBytes = typeof bytes === 'string' ? parseInt(bytes) : bytes;
  if (isNaN(numBytes) || numBytes < 0) return '-';
  
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let size = numBytes;
  let unitIndex = 0;
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }
  
  return `${size.toFixed(2)} ${units[unitIndex]}`;
};

// 获取磁盘容量（兼容多种格式）
const getDiskCapacity = (disk: any): string | number | null => {
  // 优先检查字节数格式
  if (disk.capacity_bytes) return disk.capacity_bytes;
  if (disk.capacity_guest) return disk.capacity_guest;
  // 检查Windows格式
  if (disk.Size !== undefined && disk.Size !== null) return disk.Size;
  // 检查Linux小写格式（可能是格式化的字符串如"50G"）
  if (disk.size) return disk.size;
  // 检查其他格式
  if (disk.capacity) return disk.capacity;
  return null;
};

// 获取磁盘可用空间（兼容多种格式）
const getDiskFreeSpace = (disk: any): string | number | null => {
  // 优先检查字节数格式
  if (disk.free_space !== undefined && disk.free_space !== null) return disk.free_space;
  // 检查Windows格式
  if (disk.FreeSpace !== undefined && disk.FreeSpace !== null) return disk.FreeSpace;
  // 检查Linux小写格式（可能是格式化的字符串如"10G"）
  if (disk.avail) return disk.avail;
  return null;
};

// 获取磁盘已用空间（兼容多种格式）
const getDiskUsedSpace = (disk: any): string | number | null => {
  // 优先检查Windows格式
  if (disk.UsedSpace !== undefined && disk.UsedSpace !== null) return disk.UsedSpace;
  // 检查Linux小写格式（可能是格式化的字符串如"40G"）
  if (disk.used) return disk.used;
  // 计算方式：如果有容量和可用空间，计算已用空间
  const capacity = getDiskCapacity(disk);
  const freeSpace = getDiskFreeSpace(disk);
  if (capacity && freeSpace && typeof capacity === 'number' && typeof freeSpace === 'number') {
    return capacity - freeSpace;
  }
  return null;
};

// 格式化磁盘大小（支持字符串格式如"50G"和数字字节）
const formatDiskSize = (size: string | number | null | undefined): string => {
  if (!size) return '-';
  // 如果是字符串格式（如"50G", "100M"），直接返回
  if (typeof size === 'string') {
    // 移除百分号（如果是use_percent）
    if (size.endsWith('%')) {
      return size;
    }
    // 如果已经是格式化的大小，直接返回
    if (/^\d+[KMGT]?[B]?$/.test(size.toUpperCase())) {
      return size;
    }
    // 尝试解析为数字
    const numSize = parseFloat(size);
    if (!isNaN(numSize)) {
      return formatBytes(numSize);
    }
    return size;
  }
  // 如果是数字，格式化为字节
  return formatBytes(size);
};

// 计算磁盘使用率（兼容多种格式）
const diskUsePercent = (disk: any): number | null => {
  // 优先检查Windows格式
  if (disk.UsePercent !== undefined && disk.UsePercent !== null) {
    return typeof disk.UsePercent === 'string' ? parseFloat(disk.UsePercent) : disk.UsePercent;
  }
  // 检查Linux小写格式（可能包含%符号）
  if (disk.use_percent !== undefined && disk.use_percent !== null) {
    const percent = typeof disk.use_percent === 'string' 
      ? parseFloat(disk.use_percent.replace('%', '')) 
      : disk.use_percent;
    if (!isNaN(percent)) return Math.round(percent);
  }
  // 计算方式：如果有容量和可用空间，计算使用率
  const capacity = getDiskCapacity(disk);
  const freeSpace = getDiskFreeSpace(disk);
  if (capacity && freeSpace) {
    // 如果都是数字，直接计算
    if (typeof capacity === 'number' && typeof freeSpace === 'number' && capacity > 0) {
      const used = capacity - freeSpace;
      return Math.round((used / capacity) * 100);
    }
    // 如果是字符串格式，需要解析
    if (typeof capacity === 'string' && typeof freeSpace === 'string') {
      const capacityBytes = parseSizeString(capacity);
      const freeBytes = parseSizeString(freeSpace);
      if (capacityBytes > 0 && freeBytes >= 0) {
        const used = capacityBytes - freeBytes;
        return Math.round((used / capacityBytes) * 100);
      }
    }
  }
  return null;
};

// 解析大小字符串（如"50G", "100M", "1.5T"）为字节数
const parseSizeString = (sizeStr: string): number => {
  if (!sizeStr || typeof sizeStr !== 'string') return 0;
  const cleanStr = sizeStr.trim().toUpperCase().replace(/[B]/g, ''); // 移除可能的B后缀
  // 匹配格式：数字（可能带小数点）+ 单位（K/M/G/T）
  const match = cleanStr.match(/^([\d.]+)\s*([KMGT]?)$/);
  if (!match) {
    // 如果没有单位，尝试直接解析为数字
    const numValue = parseFloat(cleanStr);
    return isNaN(numValue) ? 0 : Math.round(numValue);
  }
  
  const value = parseFloat(match[1]);
  const unit = match[2] || '';
  
  const multipliers: Record<string, number> = {
    '': 1,
    'K': 1024,
    'M': 1024 * 1024,
    'G': 1024 * 1024 * 1024,
    'T': 1024 * 1024 * 1024 * 1024
  };
  
  return Math.round(value * (multipliers[unit] || 1));
};

// 获取磁盘使用率（统一接口）
const getDiskUsePercent = (disk: any): number | null => {
  return diskUsePercent(disk);
};

// 计算磁盘已用空间（兼容多种格式）- 保留作为备用，主要用于进度条计算
const diskUseSpace = (disk: any): number | null => {
  const usedSpace = getDiskUsedSpace(disk);
  if (usedSpace === null) return null;
  if (typeof usedSpace === 'number') return usedSpace;
  if (typeof usedSpace === 'string') {
    const bytes = parseSizeString(usedSpace);
    return bytes > 0 ? bytes : null;
  }
  return null;
};

// 获取磁盘使用率标签类型
const getDiskUsePercentType = (percent: number): string => {
  if (percent >= 90) return 'danger';
  if (percent >= 70) return 'warning';
  return 'success';
};

// 获取磁盘使用率进度条状态
const getDiskUsePercentStatus = (percent: number): string | undefined => {
  if (percent >= 90) return 'exception';
  if (percent >= 70) return 'warning';
  return undefined;
};

// 格式化网络速度
const formatNetworkSpeed = (speed: number | string): string => {
  if (!speed) return '-';
  const numSpeed = typeof speed === 'string' ? parseInt(speed) : speed;
  if (isNaN(numSpeed)) return String(speed);
  
  if (numSpeed >= 1000000000) {
    return `${(numSpeed / 1000000000).toFixed(2)} Gbps`;
  } else if (numSpeed >= 1000000) {
    return `${(numSpeed / 1000000).toFixed(2)} Mbps`;
  } else if (numSpeed >= 1000) {
    return `${(numSpeed / 1000).toFixed(2)} Kbps`;
  }
  return `${numSpeed} bps`;
};

// 获取Windows驱动器类型名称
const getDriveTypeName = (driveType: number | string): string => {
  const typeMap: Record<number, string> = {
    0: t('hostInfo.driveTypes.unknown'),
    1: t('hostInfo.driveTypes.noRoot'),
    2: t('hostInfo.driveTypes.removable'),
    3: t('hostInfo.driveTypes.fixed'),
    4: t('hostInfo.driveTypes.network'),
    5: t('hostInfo.driveTypes.cdrom'),
    6: t('hostInfo.driveTypes.ram')
  };
  const numType = typeof driveType === 'string' ? parseInt(driveType) : driveType;
  return typeMap[numType] || `${t('hostInfo.driveTypes.type')}${driveType}`;
};

const handleBindCredential = (host: HostInfo) => {
  currentBindingHost.value = {
    id: host.id,
    ip: host.ip?.ip_address || '',
    host_type: host.ip?.host_type,
    os_type: host.ip?.os_type,
    credential_bindings: host.credential_bindings || []
  };
  bindCredentialDialogVisible.value = true;
};

const handleBindSuccess = async (data: {hostId: string, credentialId: string, currentBindingId?: string | null}) => {
  try {
    // 如果已有绑定，先解绑旧的
    if (data.currentBindingId) {
      const host = originalHostsData.value.find(h => h.id === data.hostId);
      if (host && host.credential_bindings && host.credential_bindings.length > 0) {
        const binding = host.credential_bindings.find((b: any) => b.id === data.currentBindingId);
        if (binding && binding.credential_id) {
          try {
            await hostInfoStore.unbindCredential(data.hostId, binding.credential_id);
          } catch (error: any) {
            // 解绑失败不影响绑定新凭证
            console.warn('Failed to unbind old credential:', error);
          }
        }
      }
    }
    
    // 绑定新凭证
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
  
  // 过滤掉VMware子主机（不应该绑定凭证）
  const validHostIds = selectedHostIds.value.filter(hostId => {
    const host = originalHostsData.value.find(h => h.id === hostId);
    return host && !host.parent_host_id;
  });
  
  if (validHostIds.length === 0) {
    ElMessage.warning(t('hostInfo.messages.noValidHostsForBind', '没有可绑定凭证的主机（VMware子主机不能绑定凭证）'));
    return;
  }
  
  if (validHostIds.length < selectedHostIds.value.length) {
    const skippedCount = selectedHostIds.value.length - validHostIds.length;
    ElMessage.warning(t('hostInfo.messages.someHostsSkipped', { count: skippedCount }, `已跳过 ${skippedCount} 个VMware子主机`));
  }
  
  loading.value = true;
  try {
    await hostInfoStore.batchBindCredentials({
      host_ids: validHostIds,
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

const getCredentialTypeTagType = (type: string) => {
  const typeMap: Record<string, string> = {
    linux: 'success',
    windows: 'primary',
    vmware: 'warning'
  };
  return typeMap[type] || 'info';
};
</script>

<style scoped>
.host-management {
  padding: 20px;
}

.credential-display {
  display: flex;
  align-items: center;
  gap: 4px;
}

.no-credential {
  color: var(--el-text-color-placeholder);
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

/* 网络接口卡片样式 */
.network-container {
  padding: 10px 0;
}

.network-card {
  transition: all 0.3s;
}

.network-card:hover {
  box-shadow: var(--el-box-shadow-light);
}

.network-card-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.ip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

/* 磁盘卡片样式 */
.disk-container {
  padding: 10px 0;
}

.disk-card {
  transition: all 0.3s;
}

.disk-card:hover {
  box-shadow: var(--el-box-shadow-light);
}

.disk-card-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.disk-progress {
  margin-top: 15px;
}

/* Raw Data 容器样式 */
.raw-data-container {
  padding: 10px 0;
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

