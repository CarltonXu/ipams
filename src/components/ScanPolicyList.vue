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
        :empty-text="$t('scan.policy.noData')"
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
        <el-table-column :label="t('scan.policy.show.columns.strategy')" min-width="300">
          <template #default="{ row }">
            <div v-for="(strategy, index) in row.strategies" :key="index" class="strategy-item">
              <div class="strategy-header">
                <span class="strategy-label">{{ t('scan.policy.schedules') }} {{ index + 1 }}</span>
              </div>
              <div class="strategy-content">
                <div class="strategy-row">
                  <span class="strategy-field">{{ t('scan.policy.cronExpression') }}:</span>
                  <div class="cron-info">
                    <el-tag size="small" type="info" class="mr-2">
                      {{ strategy.cron }}
                    </el-tag>
                    <el-tooltip
                      :content="parseCronExpression(strategy.cron)"
                      placement="top"
                      effect="light"
                    >
                      <el-icon class="cron-help"><QuestionFilled /></el-icon>
                    </el-tooltip>
                  </div>
                </div>
                <div class="strategy-row">
                  <span class="strategy-field">{{ t('scan.policy.show.columns.startTime') }}:</span>
                  <el-tag size="small" type="warning">{{ formatDateTime(strategy.start_time) }}</el-tag>
                </div>
                <div class="strategy-row">
                  <span class="strategy-field">{{ t('scan.policy.show.columns.subnets') }}:</span>
                  <div class="subnet-tags">
                    <el-tag 
                      v-for="subnetId in strategy.subnet_ids" 
                      :key="subnetId"
                      size="small"
                      type="success"
                      class="subnet-tag"
                    >
                      {{ getSubnetName(row.subnets, subnetId) }}
                    </el-tag>
                  </div>
                </div>
                <div class="strategy-row">
                  <span class="strategy-field">{{ t('scan.policy.show.columns.scan_type') }}:</span>
                  <div class="scan-params">
                    <el-tag 
                      v-if="strategy.scan_params?.enable_custom_scan_type"
                      size="small"
                      type="warning"
                      class="scan-param-tag"
                    >
                      {{ t(`scan.policy.scanParams.types.${strategy.scan_params.scan_type}.label`) }}
                    </el-tag>
                  </div>
                </div>
                <div class="strategy-row" v-if="strategy.scan_params?.enable_custom_ports">
                  <span class="strategy-field">{{ t('scan.policy.show.columns.scan_params') }}:</span>
                  <div class="scan-params">
                    <el-tag 
                      size="small"
                      type="info"
                      class="scan-param-tag"
                    >
                      {{ t('scan.policy.scanParams.ports') }}: {{ strategy.scan_params.ports }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column :label="t('scan.policy.show.columns.subnets')" min-width="250">
          <template #default="{ row }">
            <el-tag 
              v-for="subnet in row.subnets" 
              :key="subnet.id"
              class="mx-1 mb-1"
              size="small"
              type="success"
            >
              {{ subnet.name }} ({{ subnet.subnet }})
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="threads" :label="t('scan.policy.show.columns.threads')" width="150">
          <template #default="{ row }">
            <el-tag size="small" type="info">
              {{ row.threads }}
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
import { Plus, QuestionFilled } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import dayjs from 'dayjs'
import ScanPolicyForm from './ScanPolicyForm.vue'
import PolicyJobsDrawer from './PolicyJobsDrawer.vue'
import { useScanPolicyStore } from '../stores/scanPolicy'

interface Policy {
  id: string;
  name: string;
  description: string;
  subnet_ids: string[];
  threads: number;
  strategies: Array<{
    cron: string;
    start_time: string;
    subnet_ids: string[];
    scan_params: {
      enable_custom_ports: boolean;
      ports: string;
      enable_custom_scan_type: boolean;
      scan_type: string;
    };
  }>;
  subnets: Array<{
    id: string;
    name: string;
    subnet: string;
  }>;
  created_at: string;
  status: string;
  start_time: string;
}

interface SavePolicyData {
  subnets: Array<{
    name: string;
    subnet: string;
  }>;
  policies: Array<{
    name: string;
    description: string;
    threads: number;
    strategies: Array<{
      cron: string;
      start_time: string;
      subnet_ids: string[];
      scan_params: {
        enable_custom_ports: boolean;
        ports: string;
        enable_custom_scan_type: boolean;
        scan_type: string;
      };
    }>;
  }>;
}

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

// 解析 Cron 表达式
const parseCronExpression = (cron: string): string => {
  const parts = cron.split(' ')
  if (parts.length !== 5) return 'Invalid cron expression'

  const [minute, hour, dayOfMonth, month, dayOfWeek] = parts
  
  let description = ''

  // 解析分钟
  if (minute === '*') {
    description += t('scan.policy.cron.everyMinute')
  } else if (minute.includes('/')) {
    const [, interval] = minute.split('/')
    description += t('scan.policy.cron.everyXMinutes', { interval })
  } else if (minute.includes(',')) {
    const minutes = minute.split(',').map(m => `${m}分`).join('、')
    description += t('scan.policy.cron.atMinutes', { minutes })
  } else if (minute.includes('-')) {
    const [start, end] = minute.split('-')
    description += t('scan.policy.cron.betweenMinutes', { start, end })
  } else {
    description += t('scan.policy.cron.atMinutes', { minutes: `${minute}分` })
  }

  // 解析小时
  if (hour === '*') {
    description += t('scan.policy.cron.everyHour')
  } else if (hour.includes('/')) {
    const [, interval] = hour.split('/')
    description += t('scan.policy.cron.everyXHours', { interval })
  } else if (hour.includes(',')) {
    const hours = hour.split(',').map(h => `${h}点`).join('、')
    description += t('scan.policy.cron.atHours', { hours })
  } else if (hour.includes('-')) {
    const [start, end] = hour.split('-')
    description += t('scan.policy.cron.betweenHours', { start, end })
  } else {
    description += t('scan.policy.cron.atHours', { hours: `${hour}点` })
  }

  // 解析日期
  if (dayOfMonth === '*') {
    description += t('scan.policy.cron.everyDay')
  } else if (dayOfMonth.includes('/')) {
    const [, interval] = dayOfMonth.split('/')
    description += t('scan.policy.cron.everyXDays', { interval })
  } else if (dayOfMonth.includes(',')) {
    const days = dayOfMonth.split(',').map(d => `${d}日`).join('、')
    description += t('scan.policy.cron.atDays', { days })
  } else if (dayOfMonth.includes('-')) {
    const [start, end] = dayOfMonth.split('-')
    description += t('scan.policy.cron.betweenDays', { start, end })
  } else {
    description += t('scan.policy.cron.atDays', { days: `${dayOfMonth}日` })
  }

  // 解析月份
  if (month === '*') {
    description += t('scan.policy.cron.everyMonth')
  } else if (month.includes('/')) {
    const [, interval] = month.split('/')
    description += t('scan.policy.cron.everyXMonths', { interval })
  } else if (month.includes(',')) {
    const months = month.split(',').map(m => `${m}月`).join('、')
    description += t('scan.policy.cron.atMonths', { months })
  } else if (month.includes('-')) {
    const [start, end] = month.split('-')
    description += t('scan.policy.cron.betweenMonths', { start, end })
  } else {
    description += t('scan.policy.cron.atMonths', { months: `${month}月` })
  }

  // 解析星期
  if (dayOfWeek === '*') {
    description += t('scan.policy.cron.everyWeekday')
  } else if (dayOfWeek.includes('/')) {
    const [, interval] = dayOfWeek.split('/')
    description += t('scan.policy.cron.everyXWeeks', { interval })
  } else if (dayOfWeek.includes(',')) {
    const weekDays = dayOfWeek.split(',').map(day => {
      const dayNum = parseInt(day)
      return ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][dayNum]
    })
    description += t('scan.policy.cron.atWeekdays', { weekdays: weekDays.join('、') })
  } else if (dayOfWeek.includes('-')) {
    const [start, end] = dayOfWeek.split('-')
    const startDay = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][parseInt(start)]
    const endDay = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][parseInt(end)]
    description += t('scan.policy.cron.betweenWeekdays', { start: startDay, end: endDay })
  } else {
    const dayNum = parseInt(dayOfWeek)
    const dayName = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][dayNum]
    description += t('scan.policy.cron.atWeekdays', { weekdays: dayName })
  }

  return description
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
    await policyStore.deletePolicy(policy.id)
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
    // 构建编辑数据
    editingPolicy.value = {
      id: policy.id,
      name: policy.name,
      description: policy.description,
      subnet_ids: policy.subnet_ids || [],
      threads: policy.threads,
      strategies: policy.strategies.map(strategy => ({
        cron: strategy.cron,
        start_time: strategy.start_time,
        subnet_ids: strategy.subnet_ids || [],
        scan_params: strategy.scan_params || {
          enable_custom_ports: false,
          ports: '',
          enable_custom_scan_type: false,
          scan_type: 'default'
        }
      })),
      subnets: policy.subnets.map(subnet => ({
        id: subnet.id,
        name: subnet.name,
        subnet: subnet.subnet
      })),
      created_at: policy.created_at,
      status: policy.status,
      start_time: policy.strategies[0]?.start_time || new Date().toISOString()
    };
    
    dialogVisible.value = true;
  } catch (error) {
    ElMessage.error(t('scan.policy.show.messages.editFailed'));
  }
}

// 显示添加策略对话框
const showAddPolicyDialog = () => {
  editingPolicy.value = null
  dialogVisible.value = true
}

// 处理保存策略
const handleSavePolicy = async (data: SavePolicyData) => {
  try {
    const policyStore = useScanPolicyStore()
    
    if (editingPolicy.value?.id) {
      // 更新现有策略
      const updateData = {
        name: data.policies[0].name,
        description: data.policies[0].description,
        threads: data.policies[0].threads,
        subnets: data.subnets,
        strategies: data.policies[0].strategies.map(strategy => ({
          cron: strategy.cron,
          start_time: strategy.start_time,
          subnet_ids: strategy.subnet_ids,
          scan_params: strategy.scan_params
        }))
      }
      console.log('Update policy data:', updateData) // 添加日志
      await policyStore.updatePolicy(editingPolicy.value.id, updateData)
      ElMessage.success(t('scan.messages.success.updatePolicy'))
    } else {
      // 创建新策略
      await policyStore.createPolicy({
        subnets: data.subnets,
        policies: data.policies.map(policy => ({
          name: policy.name,
          description: policy.description,
          threads: policy.threads,
          strategies: policy.strategies.map(strategy => ({
            cron: strategy.cron,
            start_time: strategy.start_time,
            subnet_ids: strategy.subnet_ids,
            scan_params: strategy.scan_params
          }))
        }))
      })
      ElMessage.success(t('scan.messages.success.savePolicy'))
    }
    
    // 刷新列表并关闭对话框
    await getPolicies()
    dialogVisible.value = false
  } catch (error: unknown) {
    console.error('Save error:', error)
    if (error instanceof Error) {
      ElMessage.error(error.message || t('common.error.unknown'))
    } else {
      ElMessage.error(t('common.error.unknown'))
    }
  }
}

// 获取子网名称
const getSubnetName = (subnets: any[], subnetId: string) => {
  const subnet = subnets.find(s => s.id === subnetId)
  return subnet ? `${subnet.name} (${subnet.subnet})` : subnetId
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

.strategy-item {
  background-color: var(--el-fill-color-light);
  border-radius: 4px;
  padding: 8px;
  margin-bottom: 8px;
}

.strategy-item:last-child {
  margin-bottom: 0;
}

.strategy-header {
  margin-bottom: 8px;
}

.strategy-label {
  font-weight: bold;
  color: var(--el-text-color-primary);
}

.strategy-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.strategy-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.strategy-field {
  min-width: 100px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.subnet-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.subnet-tag {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.el-table) {
  --el-table-border-color: var(--el-border-color-lighter);
}

:deep(.el-tag) {
  margin: 2px;
}

.mr-2 {
  margin-right: 8px;
}

.mx-1 {
  margin-left: 4px;
  margin-right: 4px;
}

.mb-1 {
  margin-bottom: 4px;
}

.cron-info {
  display: flex;
  align-items: center;
  gap: 4px;
}

.cron-help {
  color: var(--el-text-color-secondary);
  cursor: help;
  font-size: 14px;
}

.cron-help:hover {
  color: var(--el-color-primary);
}

.scan-params {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.scan-param-tag {
  margin: 2px;
}
</style>