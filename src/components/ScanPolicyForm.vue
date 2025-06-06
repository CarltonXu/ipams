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
                <!-- 原有的策略表单内容 -->
                <el-form label-position="top">
                  <el-form-item :label="$t('scan.policy.name')" required>
                    <el-input v-model="strategyName" :placeholder="$t('scan.policy.namePlaceholder')" style="width: 300px;" />
                  </el-form-item>

                  <el-form-item :label="$t('scan.policy.type')" :rules="[{ required: true, message: $t('scan.policy.typeRequired'), trigger: 'change' }]">
                    <el-radio-group v-model="scheduleType">
                      <el-radio :value="$t('scan.policy.types.everyMinute')">{{ $t('scan.policy.types.everyMinute') }}</el-radio>
                      <el-radio :value="$t('scan.policy.types.everyHour')">{{ $t('scan.policy.types.everyHour') }}</el-radio>
                      <el-radio :value="$t('scan.policy.types.everyDay')">{{ $t('scan.policy.types.everyDay') }}</el-radio>
                      <el-radio :value="$t('scan.policy.types.everyWeek')">{{ $t('scan.policy.types.everyWeek') }}</el-radio>
                      <el-radio :value="$t('scan.policy.types.everyMonth')">{{ $t('scan.policy.types.everyMonth') }}</el-radio>
                      <el-radio :value="$t('scan.policy.types.custom')">{{ $t('scan.policy.types.custom') }}</el-radio>
                    </el-radio-group>
                  </el-form-item>

                  <el-form-item 
                    v-if="scheduleType === $t('scan.policy.types.everyMinute')" 
                    :label="$t('scan.form.interval.minutes')" 
                    :rules="[{ required: true, message: $t('scan.form.interval.selectTime'), trigger: 'blur' }]"
                  >
                    <el-input-number v-model="intervalMinutes" :min="1" style="width: 100px;" default="30"/>
                  </el-form-item>

                  <el-form-item 
                    v-if="scheduleType === $t('scan.policy.types.everyHour')" 
                    :label="$t('scan.form.interval.hours')" 
                    :rules="[{ required: true, message: $t('scan.form.interval.selectTime'), trigger: 'blur' }]"
                  >
                    <el-input-number v-model="intervalHours" :min="1" style="width: 100px;" />
                  </el-form-item>

                  <el-form-item 
                    v-if="scheduleType === $t('scan.policy.types.everyDay')" 
                    :label="$t('scan.form.interval.days')" 
                    :rules="[{ required: true, message: $t('scan.form.interval.selectTime'), trigger: 'blur' }]"
                  >
                    <el-input-number v-model="intervalDays" :min="1" style="width: 100px;" />
                  </el-form-item>

                  <el-form-item 
                    v-if="[$t('scan.policy.types.everyMinute'), $t('scan.policy.types.everyHour'), $t('scan.policy.types.everyDay')].includes(scheduleType)" 
                    :label="$t('scan.form.time.start')" 
                    :rules="[{ required: true, message: $t('scan.form.time.select'), trigger: 'blur' }]"
                  >
                    <el-date-picker 
                      v-model="startExecutionTime" 
                      type="datetime" 
                      :placeholder="$t('scan.form.time.execution')" 
                      style="width: 200px;" 
                    />
                  </el-form-item>

                  <el-form-item 
                    v-if="scheduleType === t('scan.policy.types.everyWeek')" 
                    :label="t('scan.policy.monthDays')"
                  >
                    <el-checkbox-group v-model="weeklyDays">
                      <el-checkbox :label="t('scan.policy.weekDays.1')" value="1"/>
                      <el-checkbox :label="t('scan.policy.weekDays.2')" value="2"/>
                      <el-checkbox :label="t('scan.policy.weekDays.3')" value="3"/>
                      <el-checkbox :label="t('scan.policy.weekDays.4')" value="4"/>
                      <el-checkbox :label="t('scan.policy.weekDays.5')" value="5"/>
                      <el-checkbox :label="t('scan.policy.weekDays.6')" value="6"/>
                      <el-checkbox :label="t('scan.policy.weekDays.0')" value="0"/>
                    </el-checkbox-group>
                  </el-form-item>

                  <el-form-item 
                    v-if="scheduleType === $t('scan.form.types.everyWeek')" 
                    :label="$t('scan.form.time.execution')" 
                    :rules="[{ required: true, message: $t('scan.form.time.select'), trigger: 'blur' }]"
                  >
                    <el-time-picker 
                      v-model="startExecutionTime" 
                      :placeholder="$t('scan.form.time.select')" 
                      format="HH:mm" 
                      style="width: 120px;" 
                    />
                  </el-form-item>

                  <el-form-item 
                    v-if="scheduleType === $t('scan.form.types.everyMonth')" 
                    :label="$t('scan.form.monthDays.select')"
                  >
                    <el-checkbox-group v-model="monthlyDays">
                      <el-checkbox 
                        v-for="day in 31" 
                        :key="day" 
                        :label="day.toString()"
                      >
                        {{ day }}
                      </el-checkbox>
                      <el-checkbox label="last_day">
                        {{ $t('scan.form.monthDays.last') }}
                      </el-checkbox>
                    </el-checkbox-group>
                  </el-form-item>

                  <el-form-item 
                    v-if="scheduleType === $t('scan.form.types.everyMonth')" 
                    :label="$t('scan.form.time.execution')" 
                    :rules="[{ required: true, message: $t('scan.form.time.select'), trigger: 'blur' }]"
                  >
                    <el-time-picker 
                      v-model="startExecutionTime" 
                      :placeholder="$t('scan.form.time.select')" 
                      format="HH:mm" 
                      style="width: 120px;"
                    />
                  </el-form-item>

                  <el-form-item 
                    v-if="scheduleType === $t('scan.form.types.custom')" 
                    :label="$t('scan.form.cronExpression.label')"
                  >
                    <el-input 
                      v-model="customCron" 
                      :placeholder="$t('scan.form.cronExpression.placeholder')"
                    >
                      <template #append>
                        <el-tooltip :content="$t('scan.form.cronExpression.tip')" placement="top">
                          <i class="el-icon-info"></i>
                        </el-tooltip>
                      </template>
                    </el-input>
                  </el-form-item>

                  <el-form-item 
                    v-if="scheduleType === $t('scan.policy.types.custom')" 
                    :label="$t('scan.form.time.select')" 
                    :rules="[{ required: true, message: $t('scan.form.time.select'), trigger: 'blur' }]"
                  >
                    <el-date-picker
                      v-model="startExecutionTime"
                      :placeholder="$t('scan.form.time.select')"
                      type="datetime"
                      format="YYYY-MM-DD HH:mm"
                      style="width: 180px;" />
                  </el-form-item>

                  <div v-if="loading" class="loading-status">
                    {{ $t('scan.form.status.loading') }}
                  </div>

                  <el-button type="primary" @click="handleAddPolicy" :disabled="loading">{{ $t('scan.form.buttons.add') }}</el-button>
                </el-form>

                <!-- 策略列表 -->
                <el-table class="policy-table" :data="cachedPolicies" border :empty-text="$t('scan.policy.noData')">
                  <el-table-column prop="name" :label="$t('scan.policy.columns.name')" />
                  <el-table-column prop="description" :label="$t('scan.policy.columns.description')" />
                  <el-table-column prop="created_at" :label="$t('scan.policy.columns.createdAt')" />
                  <el-table-column :label="$t('scan.policy.columns.actions')">
                    <template #default="scope">
                      <el-button type="danger" size="small" @click="removePolicy(scope.row)">
                        {{ $t('scan.form.buttons.delete') }}
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
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
    if (!cachedPolicies.value || cachedPolicies.value.length === 0) {
      ElMessage.warning(t('scan.validation.noPolicy'))
      return
    }

    // 添加确认弹框
    await ElMessageBox.confirm(
      `${t('scan.form.confirm.saveContent')}\n` + 
      `${t('scan.form.confirm.subnets')} ${cachedSubnets.value.length}\n` +
      `${t('scan.form.confirm.policies')} ${cachedPolicies.value.length}`,
      t('scan.form.confirm.title'),
      {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
        type: 'warning',
        dangerouslyUseHTMLString: true
      }
    )

    // 触发保存事件，传递数据给父组件
    await emit('save', {
      subnets: cachedSubnets.value,
      policies: cachedPolicies.value
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
  cachedPolicies.value = []
  resetForm()

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
</style>