<template>
  <div class="scan-config">
    <el-card class="card">
      <div class="toolbar">
        <div class="toolbar-header">
          <h2 class="title">{{ $t('scan.title') }}</h2>
          <p class="subtitle">{{ $t('scan.subtitle') }}</p>
        </div>
      </div>
      <!-- 添加扫描网段 -->
      <div class="section">
        <el-form label-position="top">
          <h4>{{ $t('scan.subnet.title') }}</h4>
          <el-form-item :label="$t('scan.subnet.name')" required>
            <el-input v-model="subnetName" :placeholder="$t('scan.subnet.namePlaceholder')" style="width: 300px;" />
          </el-form-item>

          <el-form-item :label="$t('scan.subnet.range')" required>
            <el-input v-model="newSubnet" :placeholder="$t('scan.subnet.rangePlaceholder')" style="width: 300px;" />
          </el-form-item>
          <el-button type="primary" @click="handleAddSubnet" :disabled="loading">{{ $t('scan.subnet.add') }}</el-button>
        </el-form>
      </div>

      <!-- 显示网段列表 -->
      <div class="section">
        <h4>{{ $t('scan.subnet.list') }}</h4>
        <el-table :data="cachedSubnets" border :empty-text="$t('scan.subnet.noData')">
          <el-table-column prop="name" :label="$t('scan.subnet.columns.name')" />
          <el-table-column prop="subnet" :label="$t('scan.subnet.columns.subnet')" />
          <el-table-column prop="created_at" :label="$t('scan.subnet.columns.createdAt')" />
          <el-table-column :label="$t('scan.subnet.columns.actions')">
            <template #default="scope">
              <el-button type="danger" size="mini" @click="removeSubnet(scope.row)">{{ $t('scan.subnet.delete') }}</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <el-divider />

      <!-- 策略配置 -->
      <div class="section">
        <h4>{{ $t('scan.policy.title') }}</h4>
        <el-form label-position="top">
          <!-- 策略名称 -->
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

          <!-- 每几分钟 -->
          <el-form-item 
            v-if="scheduleType === t('scan.policy.types.everyMinute')" 
            :label="t('scan.form.interval.minutes')" 
            :rules="[{ required: true, message: t('scan.form.interval.selectTime'), trigger: 'blur' }]"
          >
            <el-input-number v-model="intervalMinutes" :min="1" style="width: 100px;" default="30"/>
          </el-form-item>

          <!-- 每几小时 -->
          <el-form-item 
            v-if="scheduleType === t('scan.policy.types.everyHour')" 
            :label="t('scan.form.interval.hours')" 
            :rules="[{ required: true, message: t('scan.form.interval.selectTime'), trigger: 'blur' }]"
          >
            <el-input-number v-model="intervalHours" :min="1" style="width: 100px;" />
          </el-form-item>

          <!-- 每几天 -->
          <el-form-item 
            v-if="scheduleType === t('scan.policy.types.everyDay')" 
            :label="t('scan.form.interval.days')" 
            :rules="[{ required: true, message: t('scan.form.interval.selectTime'), trigger: 'blur' }]"
          >
            <el-input-number v-model="intervalDays" :min="1" style="width: 100px;" />
          </el-form-item>

          <!-- 开始执行时间 -->
          <el-form-item 
            v-if="[t('scan.policy.types.everyMinute'), t('scan.policy.types.everyHour'), t('scan.policy.types.everyDay')].includes(scheduleType)" 
            :label="t('scan.form.time.start')" 
            :rules="[{ required: true, message: t('scan.form.time.select'), trigger: 'blur' }]"
          >
            <el-date-picker 
              v-model="startExecutionTime" 
              type="datetime" 
              :placeholder="t('scan.form.time.execution')" 
              style="width: 200px;" 
            />
          </el-form-item>

          <!-- 每周 -->
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

          <!-- 每周开始时间 -->
          <el-form-item 
            v-if="scheduleType === t('scan.form.types.everyWeek')" 
            :label="t('scan.form.time.execution')" 
            :rules="[{ required: true, message: t('scan.form.time.select'), trigger: 'blur' }]"
          >
            <el-time-picker 
              v-model="startExecutionTime" 
              :placeholder="t('scan.form.time.select')" 
              format="HH:mm" 
              style="width: 120px;" 
            />
          </el-form-item>

          <!-- 每月 -->
          <!-- 多选日期 -->
          <el-form-item 
            v-if="scheduleType === t('scan.form.types.everyMonth')" 
            :label="t('scan.form.monthDays.select')"
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
                {{ t('scan.form.monthDays.last') }}
              </el-checkbox>
            </el-checkbox-group>
          </el-form-item>

          <!-- 执行时间 -->
          <el-form-item 
            v-if="scheduleType === t('scan.form.types.everyMonth')" 
            :label="t('scan.form.time.execution')" 
            :rules="[{ required: true, message: t('scan.form.time.select'), trigger: 'blur' }]"
          >
            <el-time-picker 
              v-model="startExecutionTime" 
              :placeholder="t('scan.form.time.select')" 
              format="HH:mm" 
              style="width: 120px;"
            />
          </el-form-item>

          <!-- 自定义 -->
          <el-form-item 
            v-if="scheduleType === t('scan.form.types.custom')" 
            :label="t('scan.form.cronExpression.label')"
          >
            <el-input 
              v-model="customCron" 
              :placeholder="t('scan.form.cronExpression.placeholder')"
            >
              <template #append>
                <el-tooltip :content="cronExpressionTip" placement="top">
                  <i class="el-icon-info"></i>
                </el-tooltip>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item 
            v-if="scheduleType === t('scan.policy.types.custom')" 
            :label="t('scan.form.time.select')" 
            :rules="[{ required: true, message: t('scan.form.time.select'), trigger: 'blur' }]"
          >
            <el-date-picker
              v-model="startExecutionTime"
              :placeholder="t('scan.form.time.select')"
              type="datetime"
              format="YYYY-MM-DD HH:mm"
              style="width: 180px;" />
          </el-form-item>

          <!-- 加载状态 -->
          <div v-if="loading" class="loading-status">
            {{ t('scan.form.status.loading') }}
          </div>

          <!-- 添加策略 -->
          <el-button type="primary" @click="handleAddPolicy" :disabled="loading">{{ $t('scan.form.buttons.add') }}</el-button>
        </el-form>
      </div>

      <!-- 显示策略列表 -->
      <div class="section">
        <h4>{{ $t('scan.policy.list') }}</h4>
        <el-table :data="cachedPolicies" border :empty-text="$t('scan.policy.noData')">
          <el-table-column prop="name" :label="$t('scan.policy.columns.name')" />
          <el-table-column prop="description" :label="$t('scan.policy.columns.description')" />
          <el-table-column prop="created_at" :label="$t('scan.policy.columns.createdAt')" />
          <el-table-column :label="$t('scan.policy.columns.actions')">
            <template #default="scope">
              <el-button type="danger" size="mini" @click="removePolicy(scope.row)">{{ $t('scan.form.buttons.delete') }}</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <el-button type="success" @click="handleSavePolicy" :disabled="loading">{{ $t('scan.form.buttons.save') }}</el-button>
      <el-divider />

      <!-- 执行扫描 -->
      <div class="section">
        <h4>{{ $t('scan.execution.title') }}</h4>
        <el-select v-model="selectedSubnet" :placeholder="$t('scan.execution.selectSubnet')" style="width: 200px;">
          <el-option
            v-for="(subnet, index) in cachedSubnets"
            :key="index"
            :label="subnet.subnet"
            :value="subnet.subnet"
          />
        </el-select>
        <el-button type="primary" @click="handleExecuteScan" :disabled="loading">{{ $t('scan.execution.execute') }}</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useScanPolicyStore } from '../stores/scanPolicy';

const { t } = useI18n();

const subnetName = ref('');
const newSubnet = ref('');
const loading = ref(false);
const selectedSubnet = ref(null);

// 输入字段
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

// 缓存数据
const cachedSubnets = ref([]);
const cachedPolicies = ref([]);

// 正则表达式：验证 IP 地址
const isValidIP = (ip: string) => {
  const ipRegex = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
  return ipRegex.test(ip);
};

// 正则表达式：验证网段（如：192.168.0.0/24）
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

// 格式化时间函数
const formatTime = (time: Date | null) => {
  if (!time) return '';
  return `${time.getHours()}:${time.getMinutes().toString().padStart(2, '0')}`;
};

// 策略描述生成
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

// 生成 Cron 表达式
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

// 添加网段验证
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

// 处理添加网段
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

// 删除网段
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

// 处理添加策略
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
  // 检查是否有网段配置
  if (!cachedSubnets.value || cachedSubnets.value.length === 0) {
    ElMessage.warning(t('scan.validation.noSubnets'));
    return;
  }

  // 检查是否有策略配置
  if (!cachedPolicies.value || cachedPolicies.value.length === 0) {
    ElMessage.warning(t('scan.validation.noPolicy'));
    return;
  }

  try {
    await ElMessageBox.confirm(
      t('scan.form.confirm.save'),
      t('common.warning'),
      {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
        type: 'warning'
      }
    );
    
    loading.value = true;
    const scanPolicyStore = useScanPolicyStore();
    await scanPolicyStore.savePolicyConfig({
      subnets: cachedSubnets.value,
      policies: cachedPolicies.value
    });
    
    ElMessage.success(t('scan.messages.success.savePolicy'));
  } catch (error: any) {
    if (error.message) {
      ElMessage.error(error.message);
    }
  } finally {
    loading.value = false;
  }
};

// 重置表单
const resetForm = () => {
  strategyName.value = '';
  scheduleType.value = t('scan.form.types.everyDay');
  intervalMinutes.value = null;
  intervalHours.value = null;
  intervalDays.value = null;
  startExecutionTime.value = null;
  dailyTime.value = null;
  weeklyDays.value = [];
  weeklyTime.value = null;
  monthlyDays.value = [];
  monthlyTime.value = null;
  customCron.value = '';
  customCronTime.value = null;
};

// 删除策略
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

// 执行扫描
const handleExecuteScan = async () => {
  if (!selectedSubnet.value) {
    ElMessage.warning(t('scan.form.validation.subnetRequired'));
    return;
  }

  try {
    await ElMessageBox.confirm(
      t('scan.form.confirm.execute'),
      t('common.warning'),
      {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
        type: 'warning'
      }
    );
    
    loading.value = true;
    ElMessage.info(t('scan.form.status.executing'));
    
    // 执行扫描逻辑
    console.log(`执行扫描：${selectedSubnet.value}`);
    
  } catch (error) {
    // 用户取消操作
  } finally {
    loading.value = false;
  }
};

// 监听策略类型变化
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

// 自定义Cron表达式提示
const cronExpressionTip = computed(() => {
  return scheduleType.value === t('scan.form.types.custom') 
    ? t('scan.form.tips.customCron') 
    : '';
});
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.toolbar-header h2 {
  font-size: 24px;
  margin: 0;
  color: #333;
}

.toolbar-header .subtitle {
  color: #666;
  margin: 0;
  font-size: 14px;
}

.add-subnet-form {
  display: flex;
} 

.scan-config {
  padding: 20px;
}

.section {
  margin-bottom: 20px;
}
</style>