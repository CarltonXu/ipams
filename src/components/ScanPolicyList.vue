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

      <el-table 
        v-loading="loading"
        :data="policies" 
        style="width: 100%" 
        border
      >
        <el-table-column prop="name" :label="t('scan.policy.show.columns.name')" width="150">
          <template #default="{ row }">
            <el-button
              link
              type="primary"
              @click="showPolicyJobs(row)">
              {{ row.name }}
            </el-button>
          </template>
        </el-table-column>
        <el-table-column prop="description" :label="t('scan.policy.show.columns.description')" min-width="200" show-overflow-tooltip />
        <el-table-column prop="strategies" :label="t('scan.policy.show.columns.strategy')" width="150" />
        <el-table-column prop="start_time" :label="t('scan.policy.show.columns.startTime')" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.start_time) }}
          </template>
        </el-table-column>
        <el-table-column :label="t('scan.policy.show.columns.subnets')" min-width="250">
          <template #default="{ row }">
            <el-tag 
              v-for="subnet in row.subnets" 
              :key="subnet.id"
              class="mx-1 mb-1"
              size="small"
            >
              {{ subnet.name }} ({{ subnet.subnet }})
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" :label="t('scan.policy.show.columns.createdAt')" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" :label="t('scan.policy.show.columns.status.title')" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ t(`scan.policy.show.columns.status.${row.status}`) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('scan.policy.show.columns.actions.title')" width="200" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button 
                type="primary"
                size="small"
                @click="editPolicy(row)"
              >
                {{ t('scan.policy.show.columns.actions.edit') }}
              </el-button>
              <el-button 
                type="success"
                size="small"
                @click="showExecuteScanDialog(row)"
              >
                {{ t('scan.policy.show.columns.actions.scan') }}
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

    <el-dialog
      v-model="dialogVisible"
      :title="t(editingPolicy ? 'scan.policy.show.dialog.editTitle' : 'scan.policy.show.dialog.addTitle')"
      width="60%"
      destroy-on-close
    >
      <ScanPolicyForm
        :initial-data="editingPolicy"
        @save="handleSavePolicy"
        @cancel="dialogVisible = false"
      />
    </el-dialog>
    <el-dialog
      v-model="scanDialogVisible"
      :title="t('scan.policy.execute.title')"
      width="600px"
    >
      <div class="scan-dialog-content">
        <p class="policy-info">
          {{ t('scan.policy.execute.policyName') }}: {{ currentPolicy?.name }}
        </p>
        <el-form>
          <el-form-item :label="t('scan.policy.execute.selectSubnets')">
            <el-checkbox-group v-model="selectedSubnets">
              <el-checkbox 
                v-for="subnet in currentPolicy?.subnets" 
                :key="subnet.id" 
                :label="subnet.id"
              >
                {{ subnet.name }} ({{ subnet.subnet }})
              </el-checkbox>
            </el-checkbox-group>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="scanDialogVisible = false">
          {{ t('common.cancel') }}
        </el-button>
        <el-button 
          type="primary" 
          :loading="executingScan"
          @click="executeScan"
        >
          {{ t('scan.policy.execute.confirm') }}
        </el-button>
      </template>
    </el-dialog>    
    <PolicyJobsDrawer
      v-model="jobsDrawerVisible"
      :policy-id="selectedPolicyId"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import dayjs from 'dayjs'
import ScanPolicyForm from './ScanPolicyForm.vue'
import PolicyJobsDrawer from './PolicyJobsDrawer.vue'
import { useScanPolicyStore } from '../stores/scanPolicy'

const { t } = useI18n()
const dialogVisible = ref(false)
const editingPolicy = ref<Policy | null>(null)
const loading = ref(false)
const policies = ref<Policy[]>([])

const scanDialogVisible = ref(false)
const currentPolicy = ref<Policy | null>(null)
const selectedSubnets = ref<string[]>([])
const executingScan = ref(false)

const jobsDrawerVisible = ref(false)
const selectedPolicyId = ref('')

// 格式化日期时间
const formatDateTime = (dateStr: string) => {
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm:ss')
}

// 获取策略列表
const getPolicies = async () => {
  try {
    loading.value = true
    const policyStore = useScanPolicyStore()
    const response = await policyStore.fetchPolicies()
    policies.value = response
  } catch (error: any) {
    ElMessage.error(t('scan.policy.show.messages.fetchFailed'))
  } finally {
    loading.value = false
  }
}

// 显示执行扫描对话框
const showExecuteScanDialog = (policy: Policy) => {
  currentPolicy.value = policy
  selectedSubnets.value = policy.subnets.map(subnet => subnet.id)
  scanDialogVisible.value = true
}

// 获取策略的状态展示不同的颜色标签
const getStatusType = (status: string) => {
  switch (status) {
    case 'active':
      return 'warning'
    case 'running':
      return 'primary'
    case 'completed':
      return 'success'
    case 'failed':
      return 'danger'
    default:
      return 'info'
  }
}

const showPolicyJobs = (policy: Policy) => {
  selectedPolicyId.value = policy.id
  jobsDrawerVisible.value = true
}

// 执行扫描
const executeScan = async () => {
  if (!currentPolicy.value || selectedSubnets.value.length === 0) {
    ElMessage.warning(t('scan.policy.execute.selectSubnets'))
    return
  }

  try {
    executingScan.value = true
    const policyStore = useScanPolicyStore()
    await policyStore.executeScan({
      policy_id: currentPolicy.value.id,
      subnet_ids: selectedSubnets.value
    })
    
    ElMessage.success(t('scan.policy.execute.success'))
    scanDialogVisible.value = false
    
    // 刷新策略列表
    await getPolicies()
    
    // 显示任务抽屉
    selectedPolicyId.value = currentPolicy.value.id
    jobsDrawerVisible.value = true
  } catch (error: any) {
    ElMessage.error(error.message || t('scan.policy.execute.failed'))
  } finally {
    executingScan.value = false
  }
}

// 删除策略
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
    )
    
    const policyStore = useScanPolicyStore()
    await policyStore.deletePolicyById(policy.id)
    ElMessage.success(t('scan.policy.show.messages.deleteSuccess'))
    await getPolicies()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || t('scan.policy.show.messages.deleteFailed'))
    }
  }
}

// 编辑策略
const editPolicy = (policy: Policy) => {
  try {
    // 获取策略关联的子网信息
    const policySubnets = (policy.subnet_ids || []).map(subnetId => {
      const subnet = policies.value.find(p => p.subnets?.some(s => s.id === subnetId))?.subnets.find(s => s.id === subnetId);
      return subnet;
    }).filter(Boolean);

    // 构建编辑数据
    editingPolicy.value = {
      name: policy.name,
      description: policy.description,
      subnet_ids: policy.subnet_ids || [],
      strategies: policy.strategies,
      start_time: policy.start_time,
      threads: policy.threads,
      subnets: policySubnets
    };
    
    console.log('Editing policy data:', editingPolicy.value); // 调试日志
    dialogVisible.value = true;
  } catch (error) {
    console.error('Error editing policy:', error);
    ElMessage.error(t('scan.policy.show.messages.editFailed'));
  }
}

// 显示添加策略对话框
const showAddPolicyDialog = () => {
  editingPolicy.value = null
  dialogVisible.value = true
}

// 处理保存策略
const handleSavePolicy = async () => {
  await getPolicies()
  dialogVisible.value = false
}

onMounted(() => {
  getPolicies()
})
</script>

<style scoped>
.scan-policy {
  padding: 20px;
}

.card {
  margin-bottom: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.toolbar-header {
  display: flex;
  flex-direction: column;
}

.title {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.subtitle {
  margin: 5px 0 0;
  font-size: 14px;
  color: #666;
}

.scan-dialog-content {
  padding: 20px;
}

.policy-info {
  margin-bottom: 20px;
  font-size: 16px;
  color: #333;
}

:deep(.el-table) {
  --el-table-border-color: var(--el-border-color-lighter);
}

:deep(.el-tag) {
  margin: 2px;
}
</style>