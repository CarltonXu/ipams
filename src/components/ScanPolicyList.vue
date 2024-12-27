<template>
  <div class="scan-policy">
    <el-card class="card">
      <div class="toolbar">
        <div class="toolbar-header">
          <h2 class="title">{{ t('scan.policy.title') }}</h2>
          <p class="subtitle">{{ t('scan.policy.subtitle') }}</p>
        </div>
        <el-button type="primary" @click="showAddPolicyDialog">
          <el-icon><Plus /></el-icon> {{ t('scan.form.buttons.add') }}
        </el-button>
      </div>

      <!-- 策略列表 -->
      <el-table 
        :data="policies" 
        style="width: 100%" 
        border
      >
        <el-table-column prop="name" :label="t('scan.policy.show.columns.name')" width="180" />
        <el-table-column prop="description" :label="t('scan.policy.show.columns.description')" min-width="250" show-overflow-tooltip />
        <el-table-column prop="subnets" :label="t('scan.policy.show.columns.subnets')" min-width="200">
          <template #default="{ row }">
            <el-tag 
              v-for="subnet in row.subnets" 
              :key="subnet.subnet"
              class="mx-1"
              size="small"
            >
              {{ subnet.name }} ({{ subnet.subnet }})
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" :label="t('scan.policy.show.columns.createdAt')" width="180" />
        <el-table-column prop="status" :label="t('scan.policy.show.columns.status.title')" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ t(`scan.policy.show.columns.status.${row.status}`) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('scan.policy.show.columns.actions.title')" width="200" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button 
                :type="row.status === 'active' ? 'warning' : 'success'"
                size="small"
                @click="togglePolicyStatus(row)"
              >
                {{ t(`scan.policy.show.columns.actions.${row.status === 'active' ? 'disable' : 'enable'}`) }}
              </el-button>
              <el-button 
                type="primary"
                size="small"
                @click="editPolicy(row)"
              >
                {{ t('scan.policy.show.columns.actions.edit') }}
              </el-button>
              <el-button 
                type="danger"
                size="small"
                @click="deletePolicy(row)"
              >
                {{ t('scan.policy.show.columns.actions.delete') }}
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑策略对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="t(editingPolicy ? 'scan.policy.show.dialog.editTitle' : 'scan.policy.show.dialog.addTitle')"
      width="80%"
      destroy-on-close
    >
      <ScanPolicyForm
        :initial-data="editingPolicy"
        @save="handleSavePolicy"
        @cancel="dialogVisible = false"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';
import { useI18n } from 'vue-i18n';
import ScanPolicyForm from './ScanPolicyForm.vue';
import type { Policy } from '@/types/policy';

const { t } = useI18n();
const dialogVisible = ref(false);
const editingPolicy = ref<Policy | null>(null);

// 模拟数据 - 实际应用中应从API获取
const policies = ref<Policy[]>([
  {
    id: '1',
    name: '每日扫描',
    description: '每天 00:00 执行扫描',
    subnets: [
      { name: '办公网', subnet: '192.168.1.0/24' },
      { name: '测试网', subnet: '192.168.2.0/24' }
    ],
    created_at: '2024-03-15 10:00:00',
    status: 'active',
    schedule: {
      type: '每天',
      config: {
        startTime: new Date('2024-03-15T00:00:00'),
        intervalDays: 1
      }
    }
  }
]);

const showAddPolicyDialog = () => {
  editingPolicy.value = null;
  dialogVisible.value = true;
};

const editPolicy = (policy: Policy) => {
  editingPolicy.value = { ...policy };
  dialogVisible.value = true;
};

const deletePolicy = async (policy: Policy) => {
  try {
    await ElMessageBox.confirm(
      t('scan.policy.show.dialog.deleteConfirm', { name: policy.name }),
      t('scan.policy.show.dialog.deleteTitle'),
      {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
        type: 'warning'
      }
    );
    
    policies.value = policies.value.filter(p => p.id !== policy.id);
    ElMessage.success(t('scan.policy.show.messages.deleteSuccess'));
  } catch {
    // 用户取消删除
  }
};

const togglePolicyStatus = (policy: Policy) => {
  policy.status = policy.status === 'active' ? 'inactive' : 'active';
  const action = policy.status === 'active' ? 'enabled' : 'disabled';
  ElMessage.success(t('scan.policy.show.messages.updateSuccess', { action }));
};

const handleSavePolicy = (policyData: Policy) => {
  if (editingPolicy.value) {
    const index = policies.value.findIndex(p => p.id === editingPolicy.value?.id);
    if (index !== -1) {
      policies.value[index] = { ...policyData, id: editingPolicy.value.id };
    }
    ElMessage.success(t('scan.policy.show.messages.editSuccess'));
  } else {
    policies.value.push({
      ...policyData,
      id: Date.now().toString(),
      created_at: new Date().toLocaleString(),
      status: 'active'
    });
    ElMessage.success(t('scan.policy.show.messages.addSuccess'));
  }
  
  dialogVisible.value = false;
};
</script>

<style scoped>
.scan-policy {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.toolbar-header h2 {
  margin: 0;
  font-size: 24px;
  color: var(--el-text-color-primary);
}

.toolbar-header .subtitle {
  margin: 5px 0 0;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.el-tag {
  margin-right: 8px;
  margin-bottom: 4px;
}

:deep(.el-dialog__body) {
  padding: 20px;
}
</style>