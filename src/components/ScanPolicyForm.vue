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
import { useScanPolicyStore } from '../stores/scanPolicy';
import { Plus } from '@element-plus/icons-vue';

const { t } = useI18n();

const props = defineProps<{
  initialData?: {
    name: string;
    description: string;
    subnet_ids: string[];
    strategies: string;
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

const strategyName = ref('');
const scheduleType = ref(t('scan.form.types.everyDay'));
const intervalMinutes = ref(null);
const intervalHours = ref(null);
const intervalDays = ref(null);
const dailyTime = ref(null);
const weeklyDays = ref([]);
const weeklyTime = ref(null);
const monthlyDays = ref([]);
const monthlyTime = ref(null);
const customCron = ref('');
const customCronTime = ref(null);
const startExecutionTime = ref(null);

const cachedSubnets = ref([]);
const cachedPolicies = ref([]);

const policyName = ref('')
const policyDescription = ref('')
const policyThreads = ref(5)
const schedules = ref([])

const emit = defineEmits(['cancel', 'save'])

// 监听 initialData 变化，更新表单数据
watch(() => props.initialData, (newData) => {
  if (newData) {
    console.log('Initial data received:', newData); // 调试日志
    
    // 更新策略名称
    strategyName.value = newData.name;
    
    // 更新子网数据
    if (newData.subnets && newData.subnets.length > 0) {
      cachedSubnets.value = newData.subnets.map(subnet => ({
        id: subnet.id,
        name: subnet.name,
        subnet: subnet.subnet,
        created_at: new Date().toLocaleString()
      }));
    }
    
    // 解析策略描述来设置调度类型和时间
    const description = newData.description;
    if (description.includes('every minute')) {
      scheduleType.value = t('scan.policy.types.everyMinute');
      const match = description.match(/(\d+) minutes/);
      if (match) {
        intervalMinutes.value = parseInt(match[1]);
      }
    } else if (description.includes('every hour')) {
      scheduleType.value = t('scan.policy.types.everyHour');
      const match = description.match(/(\d+) hours/);
      if (match) {
        intervalHours.value = parseInt(match[1]);
      }
    } else if (description.includes('every day')) {
      scheduleType.value = t('scan.policy.types.everyDay');
      const match = description.match(/(\d+) days/);
      if (match) {
        intervalDays.value = parseInt(match[1]);
      }
    } else if (description.includes('every week')) {
      scheduleType.value = t('scan.policy.types.everyWeek');
      // 解析星期几
      const weekDays = description.match(/on (.*?) at/);
      if (weekDays) {
        weeklyDays.value = weekDays[1].split('、').map(day => 
          Object.entries(t('scan.policy.weekDays')).find(([_, value]) => value === day)?.[0]
        ).filter(Boolean);
      }
    } else if (description.includes('every month')) {
      scheduleType.value = t('scan.policy.types.everyMonth');
      // 解析每月几号
      const monthDays = description.match(/on (.*?) at/);
      if (monthDays) {
        monthlyDays.value = monthDays[1].split('、').map(day => 
          day === t('scan.policy.lastDay') ? 'last_day' : day
        );
      }
    } else {
      scheduleType.value = t('scan.policy.types.custom');
      customCron.value = newData.strategies;
    }
    
    // 设置开始时间
    if (newData.start_time) {
      startExecutionTime.value = new Date(newData.start_time);
    }
    
    // 更新策略列表
    cachedPolicies.value = [{
      name: newData.name,
      description: newData.description,
      cron: newData.strategies,
      created_at: new Date().toLocaleString(),
      startTime: new Date(newData.start_time),
      threads: newData.threads
    }];
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

const validateInputs = () => {
  if (!strategyName.value.trim()) {
    ElMessage.error(t('scan.form.validation.strategyName'));
    return false;
  }

  const scheduleTypes = {
    [t('scan.policy.types.everyMinute')]: true,
    [t('scan.policy.types.everyHour')]: true,
    [t('scan.policy.types.everyDay')]: true
  };

  if (scheduleTypes[scheduleType.value] && !startExecutionTime.value) {
    ElMessage.error(t('scan.form.validation.selectStartTime'));
    return false;
  }

  if (scheduleType.value === t('scan.policy.types.everyMinute') && !intervalMinutes.value) {
    ElMessage.error(t('scan.form.validation.selectInterval'));
    return false;
  }

  if (scheduleType.value === t('scan.policy.types.everyHour') && !intervalHours.value) {
    ElMessage.error(t('scan.form.validation.selectInterval'));
    return false;
  }

  if (scheduleType.value === t('scan.policy.types.everyDay') && !intervalDays.value) {
    ElMessage.error(t('scan.form.validation.selectInterval'));
    return false;
  }

  if (scheduleType.value === t('scan.policy.types.everyWeek') && 
      (weeklyDays.value.length === 0 || !startExecutionTime.value)) {
    ElMessage.error(t('scan.form.validation.weeklyConfig'));
    return false;
  }

  if (scheduleType.value === t('scan.policy.types.everyMonth') && 
      (monthlyDays.value.length === 0 || !startExecutionTime.value)) {
    ElMessage.error(t('scan.form.validation.monthlyConfig'));
    return false;
  }

  if (scheduleType.value === t('scan.policy.types.custom') && 
      (!customCron.value.trim() || !startExecutionTime.value)) {
    ElMessage.error(t('scan.form.validation.cronRequired'));
    return false;
  }

  return true;
};

const formatTime = (time: Date | null) => {
  if (!time) return '';
  return `${time.getHours()}:${time.getMinutes().toString().padStart(2, '0')}`;
};

const generatePolicyDescription = () => {
  if (!startExecutionTime.value) return '';
  const startTime = formatTime(startExecutionTime.value);

  switch (scheduleType.value) {
    case t('scan.policy.types.everyMinute'):
      return t('scan.policy.description.everyMinute', {
        minutes: intervalMinutes.value || 1,
        time: startTime
      });
    case t('scan.policy.types.everyHour'):
      return t('scan.policy.description.everyHour', {
        hours: intervalHours.value || 1,
        time: startTime
      });
    case t('scan.policy.types.everyDay'):
      return t('scan.policy.description.everyDay', {
        days: intervalDays.value || 1,
        time: startTime
      });
    case t('scan.policy.types.everyWeek'):
      const weekDays = weeklyDays.value
        .map(day => t(`scan.policy.weekDays.${day}`))
        .join('、');
      return t('scan.policy.description.everyWeek', {
        weekdays: weekDays,
        time: startTime
      });
    case t('scan.policy.types.everyMonth'):
      const days = monthlyDays.value
        .map(day => day === 'last_day' ? t('scan.policy.lastDay') : day)
        .join('、');
      return t('scan.policy.description.everyMonth', {
        days,
        time: startTime
      });
    case t('scan.policy.types.custom'):
      return t('scan.policy.description.custom', {
        cron: customCron.value
      });
    default:
      return '';
  }
};

const generateCrontabExpression = () => {
  const time = startExecutionTime.value;
  if (!time) {
    ElMessage.error(t('scan.validation.selectExecutionTime'));
    return '';
  }

  const minutes = time.getMinutes();
  const hours = time.getHours();

  switch (scheduleType.value) {
    case t('scan.policy.types.everyMinute'):
      return `*/${intervalMinutes.value || 1} * * * *`;
    case t('scan.policy.types.everyHour'):
      return `${minutes} */${intervalHours.value || 1} * * *`;
    case t('scan.policy.types.everyDay'):
      return `${minutes} ${hours} */${intervalDays.value || 1} * *`;
    case t('scan.policy.types.everyWeek'):
      return `${minutes} ${hours} * * ${weeklyDays.value.join(',')}`;
    case t('scan.policy.types.everyMonth'):
      const days = monthlyDays.value.includes('last_day') 
        ? 'L' 
        : monthlyDays.value.join(',');
      return `${minutes} ${hours} ${days} * *`;
    case t('scan.policy.types.custom'):
      return customCron.value;
    default:
      return '';
  }
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

const handleAddPolicy = () => {
  if (!validateInputs()) return;
  const newPolicy = {
    name: strategyName.value,
    description: generatePolicyDescription(),
    cron: generateCrontabExpression(),
    created_at: new Date().toLocaleString(),
    startTime: startExecutionTime.value,
  };
  cachedPolicies.value.push(newPolicy);
  ElMessage.success(t('scan.messages.success.addPolicy'));
  resetForm();
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
      `${t('scan.form.confirm.schedules')} ${schedules.value.length}`,
      t('scan.form.confirm.title'),
      {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
        type: 'warning',
        dangerouslyUseHTMLString: true
      }
    )

    // 处理策略数据，过滤掉 null 值
    const processedSchedules = schedules.value.map(schedule => ({
      ...schedule
    }))

    // 触发保存事件，传递数据给父组件
    await emit('save', {
      subnets: cachedSubnets.value,
      policies: [{
        name: policyName.value,
        description: policyDescription.value,
        threads: policyThreads.value,
        strategies: processedSchedules
      }]
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

  // 重置折叠面板状态
  activeCollapse.value = ['subnet', 'policy']
}

// 原有的重置表单方法
const resetForm = () => {
  strategyName.value = ''
  scheduleType.value = t('scan.form.types.everyDay')
  intervalMinutes.value = null
  intervalHours.value = null
  intervalDays.value = null
  startExecutionTime.value = null
  dailyTime.value = null
  weeklyDays.value = []
  weeklyTime.value = null
  monthlyDays.value = []
  monthlyTime.value = null
  customCron.value = ''
  customCronTime.value = null
}

const removePolicy = async (policy: any) => {
  try {
    await ElMessageBox.confirm(
      t('scan.messages.confirm.deletePolicy'),
      t('common.warning'),
      {
        type: 'warning'
      }
    );
    cachedPolicies.value = cachedPolicies.value.filter(p => p !== policy);
    ElMessage.success(t('scan.messages.success.deletePolicy'));
  } catch (error) {
    // 用户取消删除操作
  }
};

watch(scheduleType, (newType) => {
  intervalMinutes.value = null;
  intervalHours.value = null;
  intervalDays.value = null;
  startExecutionTime.value = null;

  if (newType === t('scan.form.types.everyDay')) {
    dailyTime.value = null;
  } else if (newType === t('scan.form.types.everyWeek')) {
    weeklyTime.value = null;
    weeklyDays.value = [];
  } else if (newType === t('scan.form.types.everyMonth')) {
    monthlyTime.value = null;
    monthlyDays.value = [];
  } else if (newType === t('scan.form.types.custom')) {
    customCron.value = '';
  }
});

// 添加折叠面板的激活状态控制
const activeCollapse = ref(['subnet', 'policy'])

// 添加新的时间点
const addSchedule = () => {
  schedules.value.push({
    cron: '',
    start_time: null,
    subnet_ids: []
  })
}

// 移除时间点
const removeSchedule = (index) => {
  schedules.value.splice(index, 1)
}
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
</style>