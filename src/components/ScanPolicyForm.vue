<template>
  <div class="scan-config">
    <el-card class="card">
      <div class="card-content">
        <div class="toolbar">
          <div class="toolbar-header">
            <h2 class="title">{{ $t('scan.title') }}</h2>
            <p class="subtitle">{{ $t('scan.subtitle') }}</p>
          </div>
        </div>

        <div class="scrollable-content">
          <el-collapse v-model="activeCollapse">
            <!-- 子网配置面板 -->
            <el-collapse-item :title="$t('scan.subnet.title')" name="subnet">
              <div class="section">
                <el-form label-position="top">
                  <el-form-item :label="$t('scan.subnet.name')" required>
                    <el-input v-model="subnetName" :placeholder="$t('scan.subnet.namePlaceholder')" style="width: 300px;" />
                  </el-form-item>
                  <el-form-item :label="$t('scan.subnet.range')" required>
                    <el-input v-model="newSubnet" :placeholder="$t('scan.subnet.rangePlaceholder')" style="width: 300px;" />
                  </el-form-item>
                  <el-button type="primary" @click="handleAddSubnet">{{ $t('scan.subnet.add') }}</el-button>
                </el-form>

                <el-table class="subnet-table" :data="cachedSubnets" border :empty-text="$t('scan.subnet.noData')">
                  <el-table-column prop="name" :label="$t('scan.subnet.columns.name')" />
                  <el-table-column prop="subnet" :label="$t('scan.subnet.columns.subnet')" />
                  <el-table-column prop="created_at" :label="$t('scan.subnet.columns.createdAt')" />
                  <el-table-column :label="$t('scan.subnet.columns.actions')">
                    <template #default="scope">
                      <el-button type="danger" size="small" @click="removeSubnet(scope.row)">
                        {{ $t('scan.subnet.delete') }}
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-collapse-item>

            <!-- 策略配置面板 -->
            <el-collapse-item :title="$t('scan.policy.title')" name="policy">
              <div class="section">
                <el-form label-position="top">
                  <el-form-item :label="$t('scan.policy.name')" required>
                    <el-input v-model="policyName" :placeholder="$t('scan.policy.namePlaceholder')" style="width: 300px;" />
                  </el-form-item>

                  <el-form-item :label="$t('scan.policy.description')" required>
                    <el-input v-model="policyDescription" :placeholder="$t('scan.policy.descriptionPlaceholder')" style="width: 300px;" />
                  </el-form-item>

                  <el-form-item :label="$t('scan.policy.threads')" required>
                    <el-input-number v-model="policyThreads" :min="1" :max="10" style="width: 100px;" />
                  </el-form-item>

                  <div class="schedules-section">
                    <div class="schedules-header">
                      <h3>{{ $t('scan.policy.schedules') }}</h3>
                      <el-button type="primary" @click="addSchedule">
                        <el-icon><Plus /></el-icon> {{ $t('scan.policy.addSchedule') }}
                      </el-button>
                    </div>

                    <div v-for="(schedule, index) in schedules" :key="index" class="schedule-item">
                      <div class="schedule-header">
                        <h4>{{ $t('scan.policy.schedules') }} {{ index + 1 }}</h4>
                        <el-button type="danger" size="small" @click="removeSchedule(index)">
                          {{ $t('scan.policy.removeSchedule') }}
                        </el-button>
                      </div>

                      <el-form-item :label="$t('scan.policy.cronExpression')" required>
                        <el-input v-model="schedule.cron" :placeholder="$t('scan.policy.cronPlaceholder')" />
                      </el-form-item>

                      <el-form-item :label="$t('scan.policy.startTime')" required>
                        <el-date-picker
                          v-model="schedule.start_time"
                          type="datetime"
                          :placeholder="$t('scan.policy.startTimePlaceholder')"
                        />
                      </el-form-item>

                      <el-form-item :label="$t('scan.policy.subnets')" required>
                        <el-select
                          v-model="schedule.subnet_ids"
                          multiple
                          filterable
                          :placeholder="$t('scan.policy.subnetsPlaceholder')"
                          style="width: 100%"
                        >
                          <el-option
                            v-for="subnet in cachedSubnets"
                            :key="subnet.id"
                            :label="`${subnet.name} (${subnet.subnet})`"
                            :value="subnet.id"
                          >
                            <span style="float: left">{{ subnet.name }}</span>
                            <span style="float: right; color: #8492a6; font-size: 13px">
                              {{ subnet.subnet }}
                            </span>
                          </el-option>
                        </el-select>
                      </el-form-item>

                      <div class="scan-params-section">
                        <div class="section-header">
                          <h4 class="section-title">{{ $t('scan.policy.scanParams.title') }}</h4>
                          <el-tooltip
                            :content="$t('scan.policy.scanParams.help')"
                            placement="top"
                            raw-content
                          >
                            <el-icon class="help-icon"><QuestionFilled /></el-icon>
                          </el-tooltip>
                        </div>

                        <el-form-item :label="$t('scan.policy.scanParams.scanType')">
                          <el-radio-group v-model="schedule.scan_params.scan_type" @change="handleScanTypeChange(schedule)">
                            <el-radio-button 
                              v-for="type in scanTypes" 
                              :key="type.value" 
                              :label="type.value"
                            >
                              {{ type.label }}
                              <el-tag size="small" :type="type.tagType" class="ml-2">
                                {{ type.tag }}
                              </el-tag>
                            </el-radio-button>
                          </el-radio-group>
                          <div class="scan-type-desc mt-2">
                            {{ $t(`scan.policy.scanParams.types.${schedule.scan_params.scan_type}.description`) }}
                          </div>
                        </el-form-item>
                        <template v-if="schedule.scan_params.scan_type !== 'quick'">
                          <el-form-item :label="$t('scan.policy.scanParams.ports')">
                            <div class="port-config">
                              <el-switch
                                v-model="schedule.scan_params.enable_custom_ports"
                                :disabled="schedule.scan_params.scan_type == 'quick'"
                                :active-text="$t('scan.policy.scanParams.enableCustomPorts')"
                              />
                              <el-input
                                v-if="schedule.scan_params.enable_custom_ports"
                                v-model="schedule.scan_params.ports"
                                :placeholder="$t('scan.policy.scanParams.portsPlaceholder')"
                                class="port-input"
                              />
                            </div>
                            <div class="port-help text-xs text-gray-400 mt-1">
                              <el-tooltip
                                :content="$t('scan.policy.scanParams.portsHelp')"
                                placement="top"
                                raw-content
                              >
                                <span class="cursor-help">{{ $t('scan.policy.scanParams.portsHelpDisplay') }}</span>
                              </el-tooltip>
                            </div>
                          </el-form-item>
                        </template>
                      </div>
                    </div>
                  </div>
                </el-form>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>

        <div class="footer">
          <el-button type="success" @click="handleSavePolicy" :disabled="loading">
            {{ $t('scan.form.buttons.save') }}
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, QuestionFilled } from '@element-plus/icons-vue';

const { t } = useI18n();

const props = defineProps<{
  initialData?: {
    name: string;
    description: string;
    subnet_ids: string[];
    strategies: Array<{
      cron: string;
      start_time: string;
      subnet_ids: string[];
      scan_params?: {
        enable_custom_ports: boolean;
        ports: string;
        enable_custom_scan_type: boolean;
        scan_type: string;
      };
    }>;
    start_time: string;
    threads: number;
    subnets?: Array<{
      id: string;
      name: string;
      subnet: string;
    }>;
  } | null;
}>();

const subnetName = ref('');
const newSubnet = ref('');
const loading = ref(false);

interface Subnet {
  id?: string;
  name: string;
  subnet: string;
  created_at?: string;
}

const cachedSubnets = ref<Subnet[]>([]);

const policyName = ref('')
const policyDescription = ref('')
const policyThreads = ref(5)

interface Schedule {
  cron: string;
  start_time: Date | null;
  subnet_ids: string[];
  scan_params: {
    enable_custom_ports: boolean;
    ports: string;
    enable_custom_scan_type: boolean;
    scan_type: string;
  };
}

const schedules = ref<Schedule[]>([])

const scanTypes = [
  { value: 'default', label: t('scan.policy.scanParams.types.default.label'), tagType: 'info', tag: t('scan.policy.scanParams.types.default.tag') },
  { value: 'quick', label: t('scan.policy.scanParams.types.quick.label'), tagType: 'success', tag: t('scan.policy.scanParams.types.quick.tag') },
  { value: 'intense', label: t('scan.policy.scanParams.types.intense.label'), tagType: 'warning', tag: t('scan.policy.scanParams.types.intense.tag') },
  { value: 'vulnerability', label: t('scan.policy.scanParams.types.vulnerability.label'), tagType: 'danger', tag: t('scan.policy.scanParams.types.vulnerability.tag') },
]

const emit = defineEmits(['cancel', 'save'])

// 监听 initialData 变化，更新表单数据
watch(() => props.initialData, (newData) => {
  if (newData) {
    console.log('Initial data received:', newData); // 调试日志
    
    // 更新策略基本信息
    policyName.value = newData.name;
    policyDescription.value = newData.description;
    policyThreads.value = newData.threads || 5;
    
    // 更新子网数据
    if (newData.subnets && newData.subnets.length > 0) {
      cachedSubnets.value = newData.subnets;
    }
    
    // 更新调度数据
    if (newData.strategies && newData.strategies.length > 0) {
      schedules.value = newData.strategies.map(strategy => ({
        cron: strategy.cron,
        start_time: new Date(strategy.start_time),
        subnet_ids: strategy.subnet_ids || [],
        scan_params: strategy.scan_params || {
          enable_custom_ports: false,
          ports: '',
          enable_custom_scan_type: false,
          scan_type: 'default'
        }
      }));
    }
  }
}, { immediate: true });

const isValidIP = (ip: string) => {
  const ipRegex = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
  return ipRegex.test(ip);
};

const isValidSubnet = (subnet: string) => {
  const subnetRegex = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\/([8-9]|[1-2][0-9]|3[0-2])$/;
  return subnetRegex.test(subnet);
};

const validateSubnet = () => {
  if (!subnetName.value.trim()) {
    ElMessage.error(t('scan.validation.subnetName'));
    return false;
  }

  if (!newSubnet.value.trim()) {
    ElMessage.error(t('scan.validation.subnetRange'));
    return false;
  }

  const [ip] = newSubnet.value.split('/');
  if (!isValidIP(ip)) {
    ElMessage.error(t('scan.validation.invalidIPFormat'));
    return false;
  }

  if (!isValidSubnet(newSubnet.value)) {
    ElMessage.error(t('scan.validation.invalidSubnetFormat'));
    return false;
  }

  return true;
};

const handleAddSubnet = () => {
  if (!validateSubnet()) return;

  cachedSubnets.value.push({
    name: subnetName.value,
    subnet: newSubnet.value,
    created_at: new Date().toLocaleString()
  });

  ElMessage.success(t('scan.messages.success.addSubnet'));
  subnetName.value = '';
  newSubnet.value = '';
};

const removeSubnet = async (subnet: any) => {
  try {
    await ElMessageBox.confirm(
      t('scan.messages.confirm.deleteSubnet'),
      t('common.warning'),
      {
        type: 'warning'
      }
    );
    cachedSubnets.value = cachedSubnets.value.filter(s => s !== subnet);
    ElMessage.success(t('scan.messages.success.deleteSubnet'));
  } catch (error) {
    // 用户取消删除操作
  }
};

const handleSavePolicy = async () => {
  try {
    // 检查是否有网段配置
    if (!cachedSubnets.value || cachedSubnets.value.length === 0) {
      ElMessage.warning(t('scan.validation.noSubnets'))
      return
    }

    // 检查是否有策略配置
    if (!schedules.value || schedules.value.length === 0) {
      ElMessage.warning(t('scan.validation.noSchedule'))
      return
    }

    // 验证每个时间点
    for (const schedule of schedules.value) {
      if (!schedule.cron || !schedule.start_time || !schedule.subnet_ids || schedule.subnet_ids.length === 0) {
        ElMessage.warning(t('scan.validation.incompleteSchedule'))
        return
      }
    }

    // 添加确认弹框
    await ElMessageBox.confirm(
      `${t('scan.form.confirm.saveContent')}\n` + 
      `${t('scan.form.confirm.subnets')} ${cachedSubnets.value.length}\n` +
      `${t('scan.form.confirm.policies')} ${schedules.value.length}`,
      t('scan.form.confirm.title'),
      {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
        type: 'warning',
        dangerouslyUseHTMLString: true
      }
    )

    // 处理子网数据
    const subnets = cachedSubnets.value.map(subnet => ({
      name: subnet.name,
      subnet: subnet.subnet
    }))

    // 处理策略数据
    const policies = [{
      name: policyName.value,
      description: policyDescription.value,
      threads: policyThreads.value,
      strategies: schedules.value.map(schedule => ({
        cron: schedule.cron,
        start_time: schedule.start_time ? schedule.start_time.toISOString() : new Date().toISOString(),
        subnet_ids: schedule.subnet_ids,
        scan_params: {
          enable_custom_ports: schedule.scan_params.enable_custom_ports,
          ports: schedule.scan_params.ports,
          enable_custom_scan_type: schedule.scan_params.enable_custom_scan_type,
          scan_type: schedule.scan_params.scan_type
        }
      }))
    }]

    // 触发保存事件，传递数据给父组件
    await emit('save', {
      subnets,
      policies
    })

    // 重置所有数据
    resetAllData()
    
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || t('common.error.unknown'))
    }
  }
}

// 重置所有数据
const resetAllData = () => {
  // 重置子网数据
  cachedSubnets.value = []
  subnetName.value = ''
  newSubnet.value = ''

  // 重置策略数据
  policyName.value = ''
  policyDescription.value = ''
  policyThreads.value = 5
  schedules.value = []

  // 重置扫描参数
  schedules.value.forEach(schedule => {
    schedule.scan_params = {
      enable_custom_ports: false,
      ports: '',
      enable_custom_scan_type: false,
      scan_type: 'default'
    }
  })

  // 重置折叠面板状态
  activeCollapse.value = ['subnet', 'policy']
}

// 添加折叠面板的激活状态控制
const activeCollapse = ref(['subnet', 'policy'])

// 添加新的时间点
const addSchedule = () => {
  const newSchedule = {
    cron: '',
    start_time: new Date(),
    subnet_ids: [],
    scan_params: {
      enable_custom_ports: false,
      ports: '',
      enable_custom_scan_type: false,
      scan_type: 'default'
    }
  };
  schedules.value.push(newSchedule);
};

// 移除时间点
const removeSchedule = (index: number) => {
  schedules.value.splice(index, 1)
}

const handleScanTypeChange = (schedule: any) => {
  // 如果选择了非默认扫描类型，自动启用自定义扫描类型
  schedule.scan_params.enable_custom_scan_type = schedule.scan_params.scan_type !== 'default';
  
  // 如果是快速扫描，禁用端口配置
  if (schedule.scan_params.scan_type === 'quick') {
    schedule.scan_params.enable_custom_ports = false;
  }
};
</script>

<style scoped>
:deep(.card) {
  border-radius: 0px;
  border: none;
  box-shadow: 0 0 0 0 rgba(0, 0, 0, 0) !important;
}
:deep(.el-card__body) {
  padding: 0px;
}

.card-content {
  height: 600px;
  display: flex;
  flex-direction: column;
}

.toolbar {
  padding: 10px;
  background-color: #fff;
  border-bottom: 1px solid #ebeef5;
}

.toolbar-header h2 {
  font-size: 24px;
  margin: 0;
  color: #333;
}

.toolbar-header .subtitle {
  color: #666;
  margin: 5px 0 0;
  font-size: 14px;
}

.scrollable-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  scroll-padding-top: 50px;
}

.scrollable-content::-webkit-scrollbar {
  width: 6px;
}

.scrollable-content::-webkit-scrollbar-thumb {
  background-color: #dcdfe6;
  border-radius: 3px;
}

.scrollable-content::-webkit-scrollbar-track {
  background-color: #f5f7fa;
}

.footer {
  padding: 20px;
  background-color: #fff;
  border-top: 1px solid #ebeef5;
  display: flex;
  justify-content: flex-end;
}

.section {
  margin-bottom: 20px;
}

.subnet-table {
  z-index:0;
}

.policy-table {
  z-index:0;
}

:deep(.el-collapse) {
  border: none;
}

:deep(.el-collapse-item__header) {
  font-size: 16px;
  font-weight: 500;
  padding: 12px 0;
  position: sticky;
  top: -20px;
  background-color: white;
  z-index: 1;
  border-bottom: 1px solid #ebeef5;
}

:deep(.el-collapse-item__content) {
  padding: 20px 0;
}

:deep(.el-collapse-item:not(:last-child)) {
  margin-bottom: 1px;
}

.schedules-section {
  margin-top: 20px;
}

.schedules-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.schedule-item {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 20px;
  margin-bottom: 20px;
}

.schedule-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.schedule-header h4 {
  margin: 0;
  color: #606266;
}

.scan-params-section {
  margin-bottom: 24px;
  padding: 16px;
  background-color: var(--el-fill-color-light);
  border-radius: 8px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.section-header h3 {
  font-size: 15px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin: 0;
}

.scan-strategy {
  padding: 0 8px;
}

.scan-type-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.scan-type-item {
  display: flex;
  align-items: center;
  padding: 4px 0;
}

.type-name {
  font-size: 14px;
}

.scan-type-desc {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  line-height: 1.5;
  padding: 8px 12px;
  background-color: var(--el-fill-color-blank);
  border-radius: 4px;
}

.scan-type-desc {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  line-height: 1.5;
  padding: 8px 12px;
  background-color: var(--el-fill-color-blank);
  border-radius: 4px;
}

.port-config {
  display: flex;
  flex-direction: column;
  width: 20%;
}

.port-input {
  display: flex;
  flex-direction: column;
}

.port-help {
  line-height: 1.5;
  white-space: pre-line;
  color: darkgray;
  font-size: 12px;
  padding: 10px;
}

.cursor-help {
  cursor: help;
  white-space: pre-line;
}

:deep(.el-radio-button__inner) {
  padding: 8px 16px;
}

:deep(.el-radio-button:first-child .el-radio-button__inner) {
  border-radius: 4px 0 0 4px;
}

:deep(.el-radio-button:last-child .el-radio-button__inner) {
  border-radius: 0 4px 4px 0;
}
</style>