<template>
  <div class="scan-policy">
    <el-card class="card">
      <div class="toolbar">
        <div class="toolbar-header">
          <h2 class="title">扫描策略管理</h2>
          <p class="subtitle">Manage and monitor your scanning policies effectively</p>
        </div>
        <el-button type="primary" @click="showAddPolicyDialog">
          <el-icon><Plus /></el-icon> 添加策略
        </el-button>
      </div>

      <!-- 策略列表 -->
      <el-table 
        :data="policies" 
        style="width: 100%" 
        border
      >
        <el-table-column prop="name" label="策略名称" width="180" />
        <el-table-column prop="description" label="执行计划" min-width="250" show-overflow-tooltip />
        <el-table-column prop="subnets" label="扫描网段" min-width="200">
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
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button 
                :type="row.status === 'active' ? 'warning' : 'success'"
                size="small"
                @click="togglePolicyStatus(row)"
              >
                {{ row.status === 'active' ? '禁用' : '启用' }}
              </el-button>
              <el-button 
                type="primary"
                size="small"
                @click="editPolicy(row)"
              >
                编辑
              </el-button>
              <el-button 
                type="danger"
                size="small"
                @click="deletePolicy(row)"
              >
                删除
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑策略对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingPolicy ? '编辑策略' : '添加策略'"
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
import ScanPolicyForm from './ScanPolicyForm.vue';
import type { Policy } from '@/types/policy';

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
      `确定要删除策略 "${policy.name}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );
    
    // 实际应用中应调用API
    policies.value = policies.value.filter(p => p.id !== policy.id);
    ElMessage.success('策略已删除');
  } catch {
    // 用户取消删除
  }
};

const togglePolicyStatus = (policy: Policy) => {
  policy.status = policy.status === 'active' ? 'inactive' : 'active';
  ElMessage.success(`策略已${policy.status === 'active' ? '启用' : '禁用'}`);
};

const handleSavePolicy = (policyData: Policy) => {
  if (editingPolicy.value) {
    // 更新现有策略
    const index = policies.value.findIndex(p => p.id === editingPolicy.value?.id);
    if (index !== -1) {
      policies.value[index] = { ...policyData, id: editingPolicy.value.id };
    }
  } else {
    // 添加新策略
    policies.value.push({
      ...policyData,
      id: Date.now().toString(),
      created_at: new Date().toLocaleString(),
      status: 'active'
    });
  }
  
  dialogVisible.value = false;
  ElMessage.success(`策略${editingPolicy.value ? '更新' : '添加'}成功`);
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