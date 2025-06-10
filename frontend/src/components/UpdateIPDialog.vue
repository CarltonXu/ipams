<script setup lang="ts">
import { ref, onMounted, computed, defineProps, defineEmits, watch } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useUserStore } from '../stores/user'
import { useIPStore } from '../stores/ip';
import { ElMessage } from 'element-plus';
import { useI18n } from 'vue-i18n';

// Props 和 Emits
const props = defineProps({
  modelValue: Boolean, // 控制对话框显示状态
  ip: {
    type: Object as () => { id: number; ip_address: string; device_name?: string; purpose?: string },
    required: false,
  },
});

const emit = defineEmits(['update:modelValue', 'updateSuccess']); // 更新 visible 和更新成功事件

const userStore = useUserStore()
const authStore = useAuthStore()
const ipStore = useIPStore()

// 表单数据
const form = ref({
  id: '',
  ip_address: '',
  status: '',
  os_type: '',
  device_name: '',
  device_type: '',
  manufacturer: '',
  model: '',
  purpose: '',
  assigned_user_id: '',
});

// 下拉选项
const osOptions = ['Linux', 'Windows', 'Other'];
const deviceTypeOptions = ['Router', 'Switch', 'Storage', 'Server', 'Other'];
const manufacturerOptions = ['VMware', 'OpenStack', 'Physical', 'Other'];
const modelOptions = ['PowerEdge R730', 'DELL R720', 'Other'];

// 加载状态
const loading = ref(false);

const isAdmin = computed(() => authStore.user?.is_admin);
const users = computed(() => userStore.users);

const { t } = useI18n();

// 表单初始化
const initForm = (ip: typeof props.ip) => {
  form.value = {
    id: ip.id,
    ip_address: ip.ip_address || 'Unknown',
    status: ip.status,
    os_type: ip.os_type || 'Other',
    device_name: ip.device_name || '',
    device_type: ip.device_type || 'Other',
    manufacturer: ip.manufacturer || 'Other',
    model: ip.model || 'Other',
    purpose: ip.purpose || '',
    assigned_user_id: ip.assigned_user_id || '',
  };
};

// 关闭对话框
const handleClose = () => {
  emit('update:modelValue', false);
  resetForm();
};

// 重置表单
const resetForm = () => {
  initForm(props.ip);
};

// 修改更新处理函数
const handleUpdate = async () => {
  if (!validateForm()) return;
  
  loading.value = true;
  try {
    await ipStore.updateIP(form.value.id, {
      os_type: form.value.os_type,
      device_name: form.value.device_name,
      device_type: form.value.device_type,
      manufacturer: form.value.manufacturer,
      model: form.value.model,
      purpose: form.value.purpose,
      assigned_user_id: form.value.assigned_user_id
    });
    
    emit('updateSuccess', form.value);
    handleClose();
  } catch (error: any) {
    ElMessage.error(error.message);
  } finally {
    loading.value = false;
  }
};

// 表单验证
const validateForm = () => {
  if (!form.value.device_name.trim()) {
    ElMessage.error(t('ip.dialog.claim.deviceNameRequired'));
    return false;
  }
  if (!form.value.purpose.trim()) {
    ElMessage.error(t('ip.dialog.claim.purposeRequired'));
    return false;
  }
  return true;
};

onMounted(async () => {
  try {
    await userStore.fetchAllUsers();
  } catch (error) {
    ElMessage.error(t('common.fetchError'));
  }
});

// 监听 props.ip 的变化并重新初始化表单
watch(
  () => props.ip,
  (newIP) => {
    if (newIP) {
      initForm(newIP);
    }
  },
  { immediate: true }
);
</script>

<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    :title="t('ip.dialog.claim.title')"
    :before-close="handleClose"
    width="500px"
    class="update-dialog"
  >
    <div v-if="ip" class="dialog-content">
      <div class="ip-info-group">
        <div class="ip-info">
          <span class="label">{{ t('ip.dialog.claim.hostUUID') }}:</span>
          <span class="value">{{ ip.id || 'N/A' }}</span>
        </div>
        <div class="ip-info">
          <span class="label">{{ t('ip.dialog.claim.hostIP') }}:</span>
          <span class="value">{{ ip.ip_address || 'N/A' }}</span>
        </div>
      </div>
      <el-form :model="form" label-position="top" class="update-form">
        <el-form-item v-if="isAdmin" :label="$t('ip.dialog.claim.assignUser')">
          <el-select v-model="form.assigned_user_id" :placeholder="$t('ip.dialog.claim.selectUser')">
            <el-option 
              :label="$t('ip.status.unassigned')" 
              value="" 
            />
            <el-option
              v-for="user in users"
              :key="user.id"
              :label="user.username"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('ip.dialog.claim.deviceName')" required>
            <el-input v-model="form.device_name" 
            :placeholder="$t('ip.dialog.claim.deviceNamePlaceholder')" />
        </el-form-item>
        <el-form-item :label="$t('ip.dialog.claim.osType')" required>
          <el-tooltip :content="$t('ip.dialog.claim.osTypeTip')" placement="top">
            <el-select v-model="form.os_type" :placeholder="$t('ip.dialog.claim.osType')">
              <el-option v-for="os in osOptions" :key="os" :label="os" :value="os" />
            </el-select>
          </el-tooltip>
        </el-form-item>

        <!-- Device Type -->
        <el-form-item :label="$t('ip.dialog.claim.deviceType')" required>
          <el-tooltip :content="$t('ip.dialog.claim.deviceTypeTip')" placement="top">
            <el-select v-model="form.device_type" :placeholder="$t('ip.dialog.claim.deviceType')">
              <el-option v-for="type in deviceTypeOptions" :key="type" :label="type" :value="type" />
            </el-select>
          </el-tooltip>
        </el-form-item>

        <!-- Manufacturer -->
        <el-form-item :label="$t('ip.dialog.claim.manufacturer')" required>
          <el-tooltip :content="$t('ip.dialog.claim.manufacturerTip')" placement="top">
            <el-select v-model="form.manufacturer" :placeholder="$t('ip.dialog.claim.manufacturer')">
              <el-option v-for="manufacturer in manufacturerOptions" :key="manufacturer" :label="manufacturer" :value="manufacturer" />
            </el-select>
          </el-tooltip>
        </el-form-item>

        <!-- Model -->
        <el-form-item :label="$t('ip.dialog.claim.model')" required>
          <el-tooltip :content="$t('ip.dialog.claim.modelTip')" placement="top">
            <el-select v-model="form.model" :placeholder="$t('ip.dialog.claim.model')">
              <el-option v-for="model in modelOptions" :key="model" :label="model" :value="model" />
            </el-select>
          </el-tooltip>
        </el-form-item>

        <!-- Purpose -->
        <el-form-item :label="$t('ip.dialog.claim.purpose')" required>
          <el-input
            v-model="form.purpose"
            type="textarea"
            :rows="3"
            :placeholder="$t('ip.dialog.claim.purposePlaceholder')"
          />
        </el-form-item>
      </el-form>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="handleUpdate" :loading="loading">
          {{ t('ip.dialog.claim.confirmUpdate') }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped>
.dialog-content {
  padding: 10px 20px;
}

.ip-info-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
}

.ip-info {
  display: flex;
  align-items: center;
  background-color: var(--el-bg-color-secondary);
  padding: 8px 16px;
  border-radius: 4px;
}

.label {
  font-weight: 500;
  color: var(--el-text-color-secondary);
  margin-right: 8px;
}

.value {
  flex: 1;
  color: var(--el-text-color-primary);
  text-align: right;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.update-form {
  margin-top: 10px;
}

/* 可选的自定义 Tooltip 样式 */
.el-tooltip__popper {
  background-color: #fff;
  max-width: 200px; /* 限制宽度，避免过宽 */
  font-size: 12px;
  color: #333;
}
</style>