<script setup lang="ts">
import { ref, onMounted, computed, defineProps, defineEmits, watch } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useUserStore } from '../stores/user'
import { useIPStore } from '../stores/ip';
import { ElMessage } from 'element-plus';

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
    assigned_user_id: ip.assigned_user_id || '', // 新增字段
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

// 提交认领操作
const handleUpdate = async () => {
  if (!validateForm()) return;

  loading.value = true;
  try {
    const store = useIPStore();
    await store.updateIP(props.ip.id, {
      os_type: form.value.os_type,
      device_name: form.value.device_name,
      device_type: form.value.device_type,
      manufacturer: form.value.manufacturer,
      model: form.value.model,
      purpose: form.value.purpose,
      assigned_user_id: form.value.assigned_user_id,
    });

    ElMessage.success('IP updated successfully');
    emit('updateSuccess', props.ip);
    handleClose();
  } catch (error: any) {
    ElMessage.error(`Failed to update IP: ${error.message || 'Unknown error'}`);
  } finally {
    loading.value = false;
  }
};

// 表单验证
const validateForm = () => {
  if (!form.value.device_name.trim()) {
    ElMessage.error('Device Name is required');
    return false;
  }
  if (!form.value.purpose.trim()) {
    ElMessage.error('Purpose is required');
    return false;
  }
  return true;
};

onMounted(() => {
   userStore.fetchUsers();
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
    title="Update IP Address"
    :before-close="handleClose"
    width="500px"
    class="update-dialog"
  >
    <div v-if="ip" class="dialog-content">
      <!-- IP信息展示 -->
      <div class="ip-info-group">
        <div class="ip-info">
          <span class="label">Host UUID:</span>
          <span class="value">{{ ip.id || 'N/A' }}</span>
        </div>
        <div class="ip-info">
          <span class="label">Host IP:</span>
          <span class="value">{{ ip.ip_address || 'N/A' }}</span>
        </div>
      </div>
      <el-form :model="form" label-position="top" class="update-form">
        <el-form-item v-if="isAdmin" label="Assign to User">
        <el-select v-model="form.assigned_user_id" placeholder="Select a user">
          <el-option
          :label="'Unassigned'"
          :value="null" 
          />
          <el-option
            v-for="user in users"
            :key="user.id"
            :label="user.username"
            :value="user.id"
          />
        </el-select>
      </el-form-item>
        <el-form-item label="Device Name" required>
            <el-input v-model="form.device_name" placeholder="Enter your device name, Like (e.g., Nginx, Other)." />
        </el-form-item>
        <el-form-item label="OS Type" required>
          <el-tooltip content="Select the operating system running on this device (e.g., Linux, Windows, Other)." placement="top">
            <el-select v-model="form.os_type" placeholder="Select OS Type">
              <el-option v-for="os in osOptions" :key="os" :label="os" :value="os" />
            </el-select>
          </el-tooltip>
        </el-form-item>

        <!-- Device Type -->
        <el-form-item label="Device Type" required>
          <el-tooltip content="Specify the type of device using this IP (e.g., Router, Switch, Server)." placement="top">
            <el-select v-model="form.device_type" placeholder="Select Device Type">
              <el-option v-for="type in deviceTypeOptions" :key="type" :label="type" :value="type" />
            </el-select>
          </el-tooltip>
        </el-form-item>

        <!-- Manufacturer -->
        <el-form-item label="Manufacturer" required>
          <el-tooltip content="Indicate where the device is deployed (e.g., VMware, OpenStack, Physical)." placement="top">
            <el-select v-model="form.manufacturer" placeholder="Select Manufacturer">
              <el-option v-for="manufacturer in manufacturerOptions" :key="manufacturer" :label="manufacturer" :value="manufacturer" />
            </el-select>
          </el-tooltip>
        </el-form-item>

        <!-- Model -->
        <el-form-item label="Model" required>
          <el-tooltip content="Provide the device model (e.g., PowerEdge R730, DELL R720)." placement="top">
            <el-select v-model="form.model" placeholder="Select Model">
              <el-option v-for="model in modelOptions" :key="model" :label="model" :value="model" />
            </el-select>
          </el-tooltip>
        </el-form-item>

        <!-- Purpose -->
        <el-form-item label="Purpose" required>
          <el-input
            v-model="form.purpose"
            type="textarea"
            :rows="3"
            placeholder="Describe the purpose of this IP address"
          />
        </el-form-item>
      </el-form>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">Cancel</el-button>
        <el-button type="primary" @click="handleUpdate" :loading="loading">
          Confirm Update
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