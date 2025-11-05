<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage } from 'element-plus';
import { useCredentialStore } from '../stores/credential';

const { t } = useI18n();
const credentialStore = useCredentialStore();

interface Props {
  modelValue: boolean;
  hostId: string;
  hostIp: string;
  currentBindings?: any[];  // 当前已绑定的凭证
}

const props = defineProps<Props>();
const emit = defineEmits(['update:modelValue', 'bindSuccess']);

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
});

const selectedCredentialId = ref<string>('');
const loading = ref(false);

// 当前已绑定的凭证（只取第一个，因为只允许一个）
const currentBinding = computed(() => {
  if (props.currentBindings && props.currentBindings.length > 0) {
    return props.currentBindings[0];
  }
  return null;
});

const availableCredentials = computed(() => {
  return credentialStore.credentials.filter(c => !(c as any).deleted);
});

const getTypeTagType = (type: any): string => {
  const typeMap: Record<string, string> = {
    linux: 'success',
    windows: 'primary',
    vmware: 'warning'
  };
  return typeMap[type] || 'info';
};

onMounted(async () => {
  await loadCredentials();
});

watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    loadCredentials();
    // 如果有当前绑定的凭证，默认选中它
    if (currentBinding.value && currentBinding.value.credential_id) {
      selectedCredentialId.value = currentBinding.value.credential_id;
    } else {
      selectedCredentialId.value = '';
    }
  }
});

const loadCredentials = async () => {
  try {
    await credentialStore.fetchCredentials();
  } catch (error) {
    ElMessage.error(t('common.fetchError'));
  }
};

const handleBind = async () => {
  if (!selectedCredentialId.value) {
    ElMessage.warning(t('hostInfo.messages.credentialRequired') || '请选择凭证');
    return;
  }

  // 如果选择的凭证和当前绑定的一样，提示用户
  if (currentBinding.value && currentBinding.value.credential_id === selectedCredentialId.value) {
    ElMessage.info(t('hostInfo.credentialInfo.sameCredential', '选择的凭证与当前绑定的凭证相同'));
    visible.value = false;
    return;
  }

  loading.value = true;
  try {
    // 发送事件让父组件处理绑定（如果已有绑定，会先解绑再绑定新的）
    emit('bindSuccess', {
      hostId: props.hostId,
      credentialId: selectedCredentialId.value,
      currentBindingId: currentBinding.value?.id || null
    });
    visible.value = false;
  } finally {
    loading.value = false;
  }
};

const handleClose = () => {
  visible.value = false;
  selectedCredentialId.value = '';
};
</script>

<template>
  <el-dialog
    v-model="visible"
    :title="$t('hostInfo.actions.bindCredential')"
    width="500px"
    @close="handleClose"
  >
    <div class="bind-credential-content">
      <div class="host-info">
        <p><strong>{{ $t('hostInfo.ip') }}:</strong> {{ hostIp }}</p>
      </div>

      <!-- 显示当前已绑定的凭证 -->
      <div v-if="currentBinding && currentBinding.credential" class="current-credential">
        <el-alert
          :title="$t('hostInfo.credentialInfo.currentCredential', '当前绑定的凭证')"
          type="info"
          :closable="false"
          show-icon
        >
          <template #default>
            <div class="current-credential-info">
              <el-tag type="success" size="small">
                {{ currentBinding.credential.name }}
              </el-tag>
              <el-tag
                :type="getTypeTagType(currentBinding.credential.credential_type)"
                size="small"
                style="margin-left: 8px"
              >
                {{ $t(`credential.types.${currentBinding.credential.credential_type}`) }}
              </el-tag>
            </div>
          </template>
        </el-alert>
      </div>

      <el-form label-position="top" class="bind-form">
        <el-form-item :label="currentBinding ? $t('hostInfo.credentialInfo.changeCredential', '更换凭证') : $t('credential.title')" required>
          <el-select
            v-model="selectedCredentialId"
            :placeholder="currentBinding ? $t('hostInfo.credentialInfo.selectNewCredential', '选择新的凭证') : ($t('hostInfo.actions.selectCredential') || '请选择凭证')"
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
      </el-form>

      <div v-if="availableCredentials.length === 0" class="no-credentials">
        <el-empty :description="$t('credential.messages.noCredentials')" />
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">{{ $t('common.cancel') }}</el-button>
        <el-button 
          type="primary" 
          @click="handleBind" 
          :loading="loading"
          :disabled="availableCredentials.length === 0"
        >
          {{ $t('common.confirm') }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped>
.bind-credential-content {
  padding: 10px 0;
}

.host-info {
  background-color: var(--el-bg-color-secondary);
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.host-info p {
  margin: 0;
}

.bind-form {
  margin-top: 20px;
}

.credential-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.credential-name {
  margin-right: 10px;
}

.no-credentials {
  margin-top: 20px;
}

.current-credential {
  margin-bottom: 20px;
}

.current-credential-info {
  display: flex;
  align-items: center;
  margin-top: 8px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>

