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
}

const props = defineProps<Props>();
const emit = defineEmits(['update:modelValue', 'bindSuccess']);

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
});

const selectedCredentialId = ref<string>('');
const loading = ref(false);

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
    selectedCredentialId.value = '';
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

  loading.value = true;
  try {
    // 发送事件让父组件处理绑定
    emit('bindSuccess', {
      hostId: props.hostId,
      credentialId: selectedCredentialId.value
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

      <el-form label-position="top" class="bind-form">
        <el-form-item :label="$t('credential.title')" required>
          <el-select
            v-model="selectedCredentialId"
            :placeholder="$t('hostInfo.actions.selectCredential') || '请选择凭证'"
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

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>

