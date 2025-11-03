<template>
  <div class="credential-management">
    <el-card>
      <div class="toolbar">
        <div class="toolbar-header">
          <h2>{{ $t('credential.title') }}</h2>
          <p class="subtitle">{{ $t('credential.subtitle') }}</p>
        </div>
        <div class="toolbar-actions">
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            {{ $t('credential.actions.add') }}
          </el-button>
          <el-button @click="handleRefresh">
            <el-icon><Refresh /></el-icon>
            {{ $t('credential.actions.refresh') }}
          </el-button>
        </div>
      </div>

      <div class="table-container">
        <el-table
          v-loading="credentialStore.loading"
          :data="credentialStore.credentials"
          style="width: 100%"
          :empty-text="$t('credential.messages.noCredentials')"
          stripe
          border
        >
          <el-table-column
            prop="name"
            :label="$t('credential.name')"
            min-width="150"
          />
          <el-table-column
            prop="credential_type"
            :label="$t('credential.type')"
            width="100"
          >
            <template #default="{ row }">
              <el-tag :type="getTypeTagType(row.credential_type)">
                {{ $t(`credential.types.${row.credential_type}`) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            prop="username"
            :label="$t('credential.username')"
            min-width="120"
          />
          <el-table-column
            prop="is_default"
            :label="$t('credential.isDefault')"
            width="100"
          >
            <template #default="{ row }">
              <el-tag v-if="row.is_default" type="success" effect="light">
                {{ $t('common.yes') }}
              </el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column
            prop="created_at"
            :label="$t('common.createdAt')"
            min-width="180"
          >
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column :label="$t('common.actions')" width="350" align="center">
            <template #default="{ row }">
              <el-button-group>
                <el-button
                  type="info"
                  size="small"
                  @click="handleViewDetail(row)"
                >
                  {{ $t('credential.actions.viewDetail') }}
                </el-button>
                <el-button
                  type="primary"
                  size="small"
                  @click="handleViewBindings(row)"
                >
                  {{ $t('credential.actions.viewBindings') }}
                </el-button>
                <el-button
                  type="success"
                  size="small"
                  @click="handleTest(row)"
                  :loading="testingCredentialId === row.id"
                >
                  {{ $t('credential.actions.test') }}
                </el-button>
                <el-button
                  type="warning"
                  size="small"
                  @click="handleEdit(row)"
                >
                  {{ $t('common.edit') }}
                </el-button>
                <el-button
                  type="danger"
                  size="small"
                  @click="handleDelete(row)"
                >
                  {{ $t('common.delete') }}
                </el-button>
              </el-button-group>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 添加/编辑对话框 -->
      <el-dialog
        v-model="dialogVisible"
        :title="editMode ? $t('credential.actions.edit') : $t('credential.actions.add')"
        width="600px"
        @close="handleCloseDialog"
      >
        <CredentialForm
          v-model="formData"
          :edit-mode="editMode"
        />
        <template #footer>
          <div class="dialog-footer">
            <el-button @click="handleCloseDialog">{{ $t('common.cancel') }}</el-button>
            <el-button type="primary" @click="handleSubmit" :loading="loading">
              {{ $t('common.save') }}
            </el-button>
          </div>
        </template>
      </el-dialog>

      <!-- 凭证详情对话框 -->
      <el-dialog
        v-model="detailDialogVisible"
        :title="$t('credential.actions.viewDetail')"
        width="600px"
      >
        <div v-if="credentialDetail" class="credential-detail">
          <el-descriptions :column="1" border>
            <el-descriptions-item :label="$t('credential.name')">
              {{ credentialDetail.name }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('credential.type')">
              <el-tag :type="getTypeTagType(credentialDetail.credential_type)">
                {{ $t(`credential.types.${credentialDetail.credential_type}`) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item :label="$t('credential.username')">
              <el-input 
                v-model="credentialDetail.username_plain" 
                readonly
                :prefix-icon="View"
              >
                <template #append>
                  <el-button @click="copyToClipboard(credentialDetail.username_plain)">
                    {{ $t('credential.actions.copy') }}
                  </el-button>
                </template>
              </el-input>
            </el-descriptions-item>
            <el-descriptions-item :label="$t('credential.password')">
              <el-input 
                v-model="credentialDetail.password_plain" 
                :type="showPassword ? 'text' : 'password'"
                readonly
                :prefix-icon="View"
              >
                <template #append>
                  <el-button @click="togglePasswordVisibility">
                    <el-icon><component :is="showPassword ? 'Hide' : 'View'" /></el-icon>
                  </el-button>
                  <el-button @click="copyToClipboard(credentialDetail.password_plain)">
                    {{ $t('credential.actions.copy') }}
                  </el-button>
                </template>
              </el-input>
            </el-descriptions-item>
            <el-descriptions-item :label="$t('credential.privateKey')" v-if="credentialDetail.private_key_plain">
              <el-input 
                v-model="credentialDetail.private_key_plain" 
                type="textarea"
                :rows="4"
                readonly
              />
            </el-descriptions-item>
            <el-descriptions-item :label="$t('credential.isDefault')">
              <el-tag v-if="credentialDetail.is_default" type="success" effect="light">
                {{ $t('common.yes') }}
              </el-tag>
              <span v-else>{{ $t('common.no') }}</span>
            </el-descriptions-item>
            <el-descriptions-item :label="$t('common.createdAt')">
              {{ formatDate(credentialDetail.created_at) }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
        <template #footer>
          <el-button @click="detailDialogVisible = false">{{ $t('common.close') }}</el-button>
        </template>
      </el-dialog>

      <!-- 绑定主机列表对话框 -->
      <el-dialog
        v-model="bindingsDialogVisible"
        :title="$t('credential.actions.viewBindings')"
        width="800px"
      >
        <div v-loading="bindingsLoading">
          <div v-if="credentialBindings" class="bindings-info">
            <div class="bindings-header">
              <p>{{ $t('credential.messages.bindingsCount', { count: credentialBindings.total, name: credentialBindings.credential_name }) }}</p>
              <el-button 
                v-if="selectedBindingHosts.length > 0"
                type="danger" 
                size="small"
                @click="handleBatchUnbindFromCredential"
              >
                {{ $t('credential.actions.batchUnbind') }} ({{ selectedBindingHosts.length }})
              </el-button>
            </div>
            <el-table
              :data="credentialBindings.hosts"
              stripe
              border
              style="margin-top: 20px"
              @selection-change="handleBindingSelectionChange"
            >
              <el-table-column type="selection" width="55" />
              <el-table-column prop="host.ip.ip_address" :label="$t('hostInfo.ip')" />
              <el-table-column prop="host.hostname" :label="$t('hostInfo.hostname')" />
              <el-table-column prop="host.os_name" :label="$t('hostInfo.osName')" />
              <el-table-column prop="bound_at" :label="$t('credential.boundAt')">
                <template #default="{ row }">
                  {{ formatDate(row.bound_at) }}
                </template>
              </el-table-column>
              <el-table-column :label="$t('common.actions')">
                <template #default="{ row }">
                  <el-button
                    type="primary"
                    size="small"
                    @click="navigateToHost(row.host.id)"
                  >
                    {{ $t('credential.actions.viewHost') }}
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
        <template #footer>
          <el-button @click="bindingsDialogVisible = false">{{ $t('common.close') }}</el-button>
        </template>
      </el-dialog>

      <!-- 测试连接对话框 -->
      <el-dialog
        v-model="testDialogVisible"
        :title="$t('credential.actions.test')"
        width="500px"
      >
        <el-form v-if="testingCredential" label-position="top">
          <el-form-item :label="$t('credential.test.hostIp')" required>
            <el-input v-model="testHostIp" :placeholder="$t('credential.test.hostIpPlaceholder')" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="testDialogVisible = false">{{ $t('common.cancel') }}</el-button>
          <el-button type="primary" @click="handleTestWithHost" :loading="testingCredentialId !== null">
            {{ $t('common.confirm') }}
          </el-button>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, Refresh, View, Hide } from '@element-plus/icons-vue';
import { useCredentialStore } from '../stores/credential';
import CredentialForm from '../components/CredentialForm.vue';
import type { Credential, CredentialFormData, CredentialType } from '../types/credential';

const { t } = useI18n();
const credentialStore = useCredentialStore();
const router = useRouter();

const dialogVisible = ref(false);
const editMode = ref(false);
const loading = ref(false);
const testingCredentialId = ref<string | null>(null);

const formData = ref<CredentialFormData>({
  name: '',
  credential_type: 'linux',
  username: '',
  password: '',
  private_key: '',
  is_default: false
});

const currentEditingId = ref<string | null>(null);

// 凭证详情对话框
const detailDialogVisible = ref(false);
const credentialDetail = ref<any>(null);

// 绑定主机列表对话框
const bindingsDialogVisible = ref(false);
const bindingsLoading = ref(false);
const credentialBindings = ref<any>(null);

// 测试连接对话框
const testDialogVisible = ref(false);
const testingCredential = ref<Credential | null>(null);
const testHostIp = ref('');

// 密码可见性
const showPassword = ref(false);

// 批量解绑相关
const selectedBindingHosts = ref<any[]>([]);

onMounted(async () => {
  await loadCredentials();
});

const loadCredentials = async () => {
  try {
    await credentialStore.fetchCredentials();
  } catch (error) {
    ElMessage.error(t('common.fetchError'));
  }
};

const handleRefresh = () => {
  loadCredentials();
};

const handleAdd = () => {
  editMode.value = false;
  formData.value = {
    name: '',
    credential_type: 'linux',
    username: '',
    password: '',
    private_key: '',
    is_default: false
  };
  dialogVisible.value = true;
};

const handleEdit = (credential: Credential) => {
  editMode.value = true;
  currentEditingId.value = credential.id;
  formData.value = {
    name: credential.name,
    credential_type: credential.credential_type,
    username: credential.username,
    password: '', // 不显示现有密码
    private_key: '', // 不显示现有私钥
    is_default: credential.is_default
  };
  dialogVisible.value = true;
};

const handleViewDetail = async (credential: Credential) => {
  try {
    const detail = await credentialStore.getCredentialDetail(credential.id);
    credentialDetail.value = detail.credential;
    detailDialogVisible.value = true;
  } catch (error: any) {
    ElMessage.error(error.response?.data?.error || t('common.fetchError'));
  }
};

const handleViewBindings = async (credential: Credential) => {
  bindingsLoading.value = true;
  try {
    const result = await credentialStore.getCredentialBindings(credential.id);
    credentialBindings.value = result;
    bindingsDialogVisible.value = true;
  } catch (error: any) {
    ElMessage.error(error.response?.data?.error || t('common.fetchError'));
  } finally {
    bindingsLoading.value = false;
  }
};

const handleTest = (credential: Credential) => {
  testingCredential.value = credential;
  testHostIp.value = '';
  testDialogVisible.value = true;
};

const handleTestWithHost = async () => {
  if (!testingCredential.value) return;
  
  if (!testHostIp.value) {
    ElMessage.warning(t('credential.test.hostIpRequired'));
    return;
  }
  
  testingCredentialId.value = testingCredential.value.id;
  try {
    const result = await credentialStore.testCredential(testingCredential.value.id, testHostIp.value);
    if (result.success) {
      ElMessage.success(result.message || t('credential.messages.testSuccess'));
      testDialogVisible.value = false;
    } else {
      ElMessage.error(result.message || t('credential.messages.testFailed'));
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || t('credential.messages.testFailed'));
  } finally {
    testingCredentialId.value = null;
  }
};

const navigateToHost = (hostId: string) => {
  router.push(`/hosts?hostId=${hostId}`);
};

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value;
};

const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text);
    ElMessage.success(t('credential.messages.copySuccess'));
  } catch (error) {
    ElMessage.error(t('credential.messages.copyFailed'));
  }
};

const handleBindingSelectionChange = (selection: any[]) => {
  selectedBindingHosts.value = selection;
};

const handleBatchUnbindFromCredential = async () => {
  if (!credentialBindings.value || selectedBindingHosts.value.length === 0) return;
  
  try {
    await ElMessageBox.confirm(
      t('credential.messages.unbindConfirm', { count: selectedBindingHosts.value.length }),
      t('common.warning'),
      {
        confirmButtonText: t('common.yes'),
        cancelButtonText: t('common.no'),
        type: 'warning'
      }
    );
    
    const hostIds = selectedBindingHosts.value.map(item => item.host.id);
    await credentialStore.batchUnbindHosts(credentialBindings.value.credential_id, { host_ids: hostIds });
    
    ElMessage.success(t('credential.messages.unbindSuccess'));
    
    // 刷新绑定列表
    await handleViewBindings({ id: credentialBindings.value.credential_id } as Credential);
    selectedBindingHosts.value = [];
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.error || t('credential.messages.unbindFailed'));
    }
  }
};

const handleDelete = async (credential: Credential) => {
  try {
    await ElMessageBox.confirm(
      t('credential.messages.deleteConfirm'),
      t('common.warning'),
      {
        confirmButtonText: t('common.yes'),
        cancelButtonText: t('common.no'),
        type: 'warning'
      }
    );
    
    await credentialStore.deleteCredential(credential.id);
    ElMessage.success(t('credential.messages.deleteSuccess'));
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('common.deleteError'));
    }
  }
};

const handleSubmit = async () => {
  if (!formData.value.name || !formData.value.credential_type || !formData.value.username) {
    ElMessage.warning(t('common.warning'));
    return;
  }

  loading.value = true;
  try {
    if (editMode.value && currentEditingId.value) {
      await credentialStore.updateCredential(currentEditingId.value, formData.value);
      ElMessage.success(t('credential.messages.updateSuccess'));
    } else {
      await credentialStore.createCredential(formData.value as any);
      ElMessage.success(t('credential.messages.createSuccess'));
    }
    handleCloseDialog();
  } catch (error: any) {
    ElMessage.error(error.response?.data?.error || t('common.error'));
  } finally {
    loading.value = false;
  }
};

const handleCloseDialog = () => {
  dialogVisible.value = false;
  currentEditingId.value = null;
  formData.value = {
    name: '',
    credential_type: 'linux',
    username: '',
    password: '',
    private_key: '',
    is_default: false
  };
};

const getTypeTagType = (type: CredentialType) => {
  const typeMap = {
    linux: 'success',
    windows: 'primary',
    vmware: 'warning'
  };
  return typeMap[type] || '';
};

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-';
  return new Date(dateStr).toLocaleString();
};
</script>

<style scoped>
.credential-management {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.toolbar-header h2 {
  margin: 0 0 5px 0;
  font-size: 24px;
  color: var(--el-text-color-primary);
}

.subtitle {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.toolbar-actions {
  display: flex;
  gap: 10px;
}

.table-container {
  margin-top: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.el-button-group .el-button {
  margin-left: 0;
}

.bindings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
</style>

