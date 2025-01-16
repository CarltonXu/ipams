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
        <el-table-column prop="name" :label="t('scan.policy.show.columns.name')" width="150" />
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
      width="500px"
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import dayjs from 'dayjs'
import ScanPolicyForm from './ScanPolicyForm.vue'
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

// 执行扫描
const executeScan = async () => {
  if (!selectedSubnets.value.length) {
    ElMessage.warning(t('scan.policy.execute.noSubnets'))
    return
  }

  try {
    executingScan.value = true
    const policyStore = useScanPolicyStore()
    await policyStore.executeScan({
      policy_id: currentPolicy.value!.id,
      subnet_ids: selectedSubnets.value
    })
    
    ElMessage.success(t('scan.policy.execute.success'))
    scanDialogVisible.value = false
  } catch (error: any) {
    ElMessage.error(error.message || t('scan.policy.execute.error'))
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
  editingPolicy.value = { ...policy }
  dialogVisible.value = true
}

// 显示添加策略对话框
const showAddPolicyDialog = () => {
  editingPolicy.value = null
  dialogVisible.value = true
}

// 保存策略
const handleSavePolicy = async (policyData: any) => {
  try {
    const policyStore = useScanPolicyStore()
    if (editingPolicy.value) {
      // 处理编辑逻辑
      ElMessage.success(t('scan.policy.show.messages.editSuccess'))
    } else {
      await policyStore.savePolicyConfig(policyData)
      ElMessage.success(t('scan.policy.show.messages.addSuccess'))
    }
    dialogVisible.value = false  // 关闭对话框
    await getPolicies()  // 刷新列表
  } catch (error: any) {
    ElMessage.error(error.message || t('common.error.unknown'))
  }
}

onMounted(() => {
  getPolicies()
})
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
</style>