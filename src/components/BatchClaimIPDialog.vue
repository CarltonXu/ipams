<template>
  <el-dialog
    :title="t('ip.dialog.batchClaim.title')"
    v-model="props.modelValue"
    width="80%"
    @close="handleClose"
  >
    <div class="batch-claim-container">
      <!-- 公共配置部分 -->
      <div class="common-config">
        <h3>{{ $t('ip.dialog.batchClaim.commonConfig') }}</h3>
        <el-form :model="commonForm" label-width="120px">
          <el-form-item :label="$t('ip.dialog.claim.assignUser')" v-if="isAdmin">
            <el-select 
              v-model="commonForm.assigned_user_id" 
              :placeholder="$t('ip.dialog.claim.selectUser')"
              clearable
            >
              <el-option
                v-for="user in users"
                :key="user.id"
                :label="user.username"
                :value="user.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item :label="$t('ip.dialog.claim.osType')">
            <el-select v-model="commonForm.os_type" clearable>
              <el-option label="Windows" value="Windows" />
              <el-option label="Linux" value="Linux" />
              <el-option label="macOS" value="macOS" />
              <el-option label="Other" value="Other" />
            </el-select>
          </el-form-item>
          <el-form-item :label="$t('ip.dialog.claim.deviceType')">
            <el-select v-model="commonForm.device_type" clearable>
              <el-option label="Server" value="Server" />
              <el-option label="Desktop" value="Desktop" />
              <el-option label="Laptop" value="Laptop" />
              <el-option label="Other" value="Other" />
            </el-select>
          </el-form-item>
          <el-form-item :label="$t('ip.dialog.claim.manufacturer')">
            <el-select v-model="commonForm.manufacturer" clearable>
              <el-option label="Dell" value="Dell" />
              <el-option label="HP" value="HP" />
              <el-option label="Lenovo" value="Lenovo" />
              <el-option label="Other" value="Other" />
            </el-select>
          </el-form-item>
          <el-form-item :label="$t('ip.dialog.claim.model')">
            <el-select v-model="commonForm.model" clearable>
              <el-option label="PowerEdge R730" value="PowerEdge R730" />
              <el-option label="DELL R720" value="DELL R720" />
              <el-option label="Other" value="Other" />
            </el-select>
          </el-form-item>
          <el-form-item :label="$t('ip.dialog.claim.purpose')">
            <el-input v-model="commonForm.purpose" />
          </el-form-item>
          <el-button type="primary" @click="applyCommonConfig">
            {{ $t('ip.dialog.batchClaim.applyToAll') }}
          </el-button>
        </el-form>
      </div>

      <!-- IP 列表配置 -->
      <div class="ip-configs">
        <h3>{{ $t('ip.dialog.batchClaim.individualConfig') }}</h3>
        <el-table :data="ipConfigs" border stripe>
          <el-table-column prop="ip_address" :label="$t('ip.columns.ipAddress')" width="140" />
          <el-table-column :label="$t('ip.dialog.claim.deviceName')" width="200">
            <template #default="{ row }">
              <el-input v-model="row.device_name" />
            </template>
          </el-table-column>
          <el-table-column :label="$t('ip.dialog.claim.assignUser')" width="200" v-if="isAdmin">
            <template #default="{ row }">
              <el-select v-model="row.assigned_user_id" style="width: 100%" clearable>
                <el-option
                  v-for="user in users"
                  :key="user.id"
                  :label="user.username"
                  :value="user.id"
                />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column :label="$t('ip.dialog.claim.osType')" width="150">
            <template #default="{ row }">
              <el-select v-model="row.os_type" style="width: 100%">
                <el-option label="Windows" value="Windows" />
                <el-option label="Linux" value="Linux" />
                <el-option label="macOS" value="macOS" />
                <el-option label="Other" value="Other" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column :label="$t('ip.dialog.claim.deviceType')" width="150">
            <template #default="{ row }">
              <el-select v-model="row.device_type" style="width: 100%">
                <el-option label="Server" value="Server" />
                <el-option label="Desktop" value="Desktop" />
                <el-option label="Laptop" value="Laptop" />
                <el-option label="Other" value="Other" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column :label="$t('ip.dialog.claim.manufacturer')" width="150">
            <template #default="{ row }">
              <el-select v-model="row.manufacturer" style="width: 100%">
                <el-option label="VMware" value="VMware" />
                <el-option label="OpenStack" value="OpenStack" />
                <el-option label="Physical" value="Physical" />
                <el-option label="Other" value="Other" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column :label="$t('ip.dialog.claim.model')" width="150">
            <template #default="{ row }">
              <el-select v-model="row.model" style="width: 100%">
                <el-option label="PowerEdge R730" value="PowerEdge R730" />
                <el-option label="DELL R720" value="DELL R720" />
                <el-option label="Other" value="Other" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column :label="$t('ip.dialog.claim.purpose')" width="200">
            <template #default="{ row }">
              <el-input v-model="row.purpose" />
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <template #footer>
      <el-button @click="handleClose">{{ $t('common.cancel') }}</el-button>
      <el-button type="primary" @click="handleBatchClaim" :loading="loading">
        {{ $t('common.confirm') }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useAuthStore } from '../stores/auth';
import { useUserStore } from '../stores/user';
import { useIPStore } from '../stores/ip';
import { ElMessage } from 'element-plus';

interface IPConfig {
  id: string;
  ip_address: string;
  device_name: string;
  os_type: string;
  device_type: string;
  manufacturer: string;
  model: string;
  purpose: string;
  assigned_user_id?: string | null;
}

const props = defineProps<{
  modelValue: boolean;
  ips: Array<{ id: string; ip_address: string }>;
}>();

const emit = defineEmits(['update:modelValue', 'claimSuccess']);

const { t } = useI18n();
const authStore = useAuthStore();
const userStore = useUserStore();
const ipStore = useIPStore();

const loading = ref(false);
const isAdmin = computed(() => authStore.user?.is_admin);
const users = computed(() => userStore.users);

// 公共配置表单
const commonForm = ref({
  os_type: 'Linux',
  device_type: 'Server',
  manufacturer: 'VMware',
  model: 'PowerEdge R730',
  assigned_user_id: '',
  purpose: '',
});

// IP 配置列表初始化
const ipConfigs = ref<IPConfig[]>([]);

// 监听 props.ips 变化，初始化 ipConfigs
watch(() => props.ips, (newIPs) => {
  if (!newIPs) return;
  
  ipConfigs.value = newIPs.map(ip => ({
    id: ip.id,
    ip_address: ip.ip_address,
    device_name: '',
    os_type: 'Other',
    device_type: 'Other',
    manufacturer: 'Other',
    model: 'Other',
    purpose: '',
    assigned_user_id: null
  }));
}, { immediate: true });

// 应用公共配置
const applyCommonConfig = () => {
  ipConfigs.value = ipConfigs.value.map(config => ({
    ...config,
    os_type: commonForm.value.os_type || config.os_type,
    device_type: commonForm.value.device_type || config.device_type,
    manufacturer: commonForm.value.manufacturer || config.manufacturer,
    model: commonForm.value.model || config.model,
    purpose: commonForm.value.purpose || config.purpose,
    assigned_user_id: commonForm.value.assigned_user_id || config.assigned_user_id
  }));
};

// 关闭对话框
const handleClose = () => {
  emit('update:modelValue', false);
};

// 批量认领处理
const handleBatchClaim = async () => {
  if (!validateConfigs()) return;

  loading.value = true;
  try {
    // 直接传递完整的配置数组
    await ipStore.batchClaimIPs(ipConfigs.value);
    ElMessage.success(t('ip.dialog.batchClaim.success'));
    console.log(ipConfigs.value);
    emit('claimSuccess', ipConfigs.value);
    handleClose();
  } catch (error: any) {
    ElMessage.error(error.message);
  } finally {
    loading.value = false;
  }
};

// 验证配置
const validateConfigs = () => {
  const invalidConfigs = ipConfigs.value.filter(
    config => !config.device_name || !config.purpose
  );
  
  if (invalidConfigs.length > 0) {
    ElMessage.error(t('ip.dialog.batchClaim.validation'));
    return false;
  }
  return true;
};
</script>

<style scoped>
.batch-claim-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.common-config {
  padding: 1rem;
  border: 1px solid var(--el-border-color-light);
  border-radius: 4px;
}

.ip-configs {
  padding: 1rem;
  border: 1px solid var(--el-border-color-light);
  border-radius: 4px;
}

h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: var(--el-text-color-primary);
}
</style>
