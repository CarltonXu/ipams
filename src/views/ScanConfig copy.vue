<template>
  <div class="scan-config">
    <el-card class="card">
      <h3 class="title">扫描配置</h3>

      <!-- 添加扫描网段 -->
      <div class="section">
        <h4>添加扫描网段</h4>
        <el-form class="add-subnet-form" inline>
          <el-form-item label="网段">
            <el-input v-model="newSubnet" placeholder="请输入扫描网段 (例如: 192.168.0.0/24)" style="width: 300px;" />
          </el-form-item>
          <el-button type="primary" @click="handleAddSubnet" :disabled="loading">添加</el-button>
        </el-form>
      </div>

      <!-- 显示网段列表 -->
      <div class="section">
        <h4>已添加网段</h4>
        <el-table :data="cachedSubnets" border empty-text="暂无网段数据">
          <el-table-column prop="subnet" label="网段" />
          <el-table-column prop="created_at" label="创建时间" />
          <el-table-column label="操作">
            <template #default="scope">
              <el-button type="danger" size="mini" @click="removeSubnet(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <el-divider />

      <!-- 策略配置 -->
      <div class="section">
        <h4>扫描策略配置</h4>
        <el-form label-position="top">
          <!-- 策略名称 -->
          <el-form-item label="策略名称" required>
            <el-input v-model="strategyName" placeholder="请输入策略名称" style="width: 300px;" />
          </el-form-item>

          <el-form-item label="策略类型" :rules="[{ required: true, message: '请选择策略类型', trigger: 'change' }]">
            <el-radio-group v-model="scheduleType">
              <el-radio value="每分钟">每分钟</el-radio>
              <el-radio value="每小时">每小时</el-radio>
              <el-radio value="每天">每天</el-radio>
              <el-radio value="每周">每周</el-radio>
              <el-radio value="每月">每月</el-radio>
              <el-radio value="自定义">自定义</el-radio>
            </el-radio-group>
          </el-form-item>

          <!-- 每几分钟 -->
          <el-form-item v-if="scheduleType === '每分钟'" label="间隔N分钟" :rules="[{ required: true, message: '请选择时间', trigger: 'blur' }]">
            <el-input-number v-model="intervalMinutes" :min="1" style="width: 100px;" default="30"/>
          </el-form-item>

          <!-- 每几小时 -->
          <el-form-item v-if="scheduleType === '每小时'" label="间隔N小时" :rules="[{ required: true, message: '请选择时间', trigger: 'blur' }]">
            <el-input-number v-model="intervalHours" :min="1" style="width: 100px;" />
          </el-form-item>

          <!-- 每几天 -->
          <el-form-item v-if="scheduleType === '每天'" label="间隔N天" :rules="[{ required: true, message: '请选择时间', trigger: 'blur' }]">
            <el-input-number v-model="intervalDays" :min="1" style="width: 100px;" />
          </el-form-item>

          <!-- 开始执行时间 -->
          <el-form-item v-if="['每分钟', '每小时', '每天'].includes(scheduleType)" label="开始时间" :rules="[{ required: true, message: '请选择开始时间', trigger: 'blur' }]">
            <el-date-picker v-model="startExecutionTime" type="datetime" placeholder="开始执行时间" style="width: 200px;" />
          </el-form-item>

          <!-- 每周 -->
          <el-form-item v-if="scheduleType === '每周'" label="日期">
            <el-checkbox-group v-model="weeklyDays">
              <el-checkbox label="周一" value="1"/>
              <el-checkbox label="周二" value="2"/>
              <el-checkbox label="周三" value="3"/>
              <el-checkbox label="周四" value="4"/>
              <el-checkbox label="周五" value="5"/>
              <el-checkbox label="周六" value="6"/>
              <el-checkbox label="周日" value="7"/>
            </el-checkbox-group>
          </el-form-item>

          <!-- 每周开始时间 -->
           <el-form-item v-if="scheduleType === '每周'" label="时间" :rules="[{ required: true, message: '请选择开始时间', trigger: 'blur' }]">
            <el-time-picker v-model="startExecutionTime" placeholder="选择时间" format="HH:mm" style="width: 120px;" />
           </el-form-item>

          <!-- 每月 -->
          <!-- 多选日期 -->
          <el-form-item v-if="scheduleType === '每月'" label="日期" :rules="[{ required: true, message: '请选择日期', trigger: 'blur' }]">
            <el-checkbox-group v-model="monthlyDays">
              <el-checkbox label="1" value="1"/>
              <el-checkbox label="2" value="2"/>
              <el-checkbox label="3" value="3"/>
              <el-checkbox label="4" value="4"/>
              <el-checkbox label="5" value="5"/>
              <el-checkbox label="6" value="6"/>
              <el-checkbox label="7" value="7"/>
              <el-checkbox label="8" value="8"/>
              <el-checkbox label="9" value="9"/>
              <el-checkbox label="10" value="10"/>
              <el-checkbox label="11" value="11"/>
              <el-checkbox label="12" value="12"/>
              <el-checkbox label="13" value="13"/>
              <el-checkbox label="14" value="14"/>
              <el-checkbox label="15" value="15"/>
              <el-checkbox label="16" value="16"/>
              <el-checkbox label="17" value="17"/>
              <el-checkbox label="18" value="18"/>
              <el-checkbox label="19" value="19" />
              <el-checkbox label="20" value="20"/>
              <el-checkbox label="21" value="21" />
              <el-checkbox label="22" value="22"/>
              <el-checkbox label="23" value="23" />
              <el-checkbox label="24" value="24"/>
              <el-checkbox label="25" value="25" />
              <el-checkbox label="26" value="26"/>
              <el-checkbox label="27" value="27" />
              <el-checkbox label="28" value="28"/>
              <el-checkbox label="29" value="29" />
              <el-checkbox label="30" value="30"/>
              <el-checkbox label="31" value="31" />
              <el-checkbox label="月末" value="last_day"/>
            </el-checkbox-group>
          </el-form-item>

          <!-- 执行时间 -->
          <el-form-item v-if="scheduleType === '每月'" label="时间" :rules="[{ required: true, message: '请选择开始时间', trigger: 'blur' }]">
            <el-time-picker v-model="startExecutionTime" placeholder="选择时间" format="HH:mm" style="width: 120px;"/>
          </el-form-item>

          <!-- 自定义 -->
          <el-form-item v-if="scheduleType === '自定义'" label="Cron 表达式" :rules="[{ required: true, message: '请输入 Cron 表达式', trigger: 'blur' }]">
            <el-input v-model="customCron" placeholder="输入 Cron 表达式" style="width: 300px;" />
            <el-time-picker v-model="startExecutionTime" placeholder="选择时间" format="HH:mm" style="width: 120px;"/>
          </el-form-item>
          <!-- 添加策略 -->
          <el-button type="primary" @click="handlePolicy" :disabled="loading">添加策略</el-button>
        </el-form>
      </div>

      <!-- 显示策略列表 -->
      <div class="section">
        <h4>已添加策略</h4>
        <el-table :data="cachedPolicies" border empty-text="暂无策略数据">
          <el-table-column prop="name" label="策略名称" />
          <el-table-column prop="description" label="策略描述" />
          <el-table-column prop="created_at" label="创建时间" />
          <el-table-column label="操作">
            <template #default="scope">
              <el-button type="danger" size="mini" @click="removePolicy(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <el-button type="success" @click="handleSavePolicy" :disabled="loading">保存策略</el-button>
      <el-divider />

      <!-- 执行扫描 -->
      <div class="section">
        <h4>执行扫描</h4>
        <el-select v-model="selectedSubnet" placeholder="选择网段" style="width: 200px;">
          <el-option
            v-for="(subnet, index) in cachedSubnets"
            :key="index"
            :label="subnet.subnet"
            :value="subnet.subnet"
          />
        </el-select>
        <el-button type="primary" @click="handleExecuteScan" :disabled="loading">执行扫描</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { ElMessage } from 'element-plus';

const newSubnet = ref('');
const loading = ref(false);
const selectedSubnet = ref(null);

// 输入字段
const strategyName = ref('');
const scheduleType = ref('每天');
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

// Cron 表达式
const cronExpression = ref('');

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

// 格式化时间函数
const formatTime = (time: Date | null) => time ? `${time.getHours()}点${time.getMinutes() > 0 ? time.getMinutes() + '分' : ''}` : '';

// 策略描述生成
const generatePolicyDescription = () => {
  let description = '';
  switch (scheduleType.value) {
    case '每分钟':
      description = `每${intervalMinutes.value}分钟，从 ${formatTime(startExecutionTime.value)} 开始执行`;
      break;
    case '每小时':
      description = `每${intervalHours.value}小时，从 ${formatTime(startExecutionTime.value)} 开始执行`;
      break;
    case '每天':
      description = `每天 ${formatTime(dailyTime.value)} 执行，从 ${formatTime(startExecutionTime.value)} 开始`;
      break;
    case '每周':
      const days = weeklyDays.value.map(day => `每周${day}`).join('、');
      description = `${days} ${formatTime(weeklyTime.value)} 执行`;
      break;
    case '每月':
      description = `每月${monthlyDays.value}日 ${formatTime(monthlyTime.value)} 执行`;
      break;
    case '自定义':
      description = `自定义策略 (${customCron.value} ${formatTime(customCronTime.value)} 执行)`;
      break;
    default:
      description = '未知策略';
  }
  return description;
};

// 生成 Cron 表达式
const generateCrontabExpression = () => {
  let cron = '';
  const startTime = startExecutionTime.value ? startExecutionTime.value : new Date();
  const minutes = startTime.getMinutes();
  const hours = startTime.getHours();

  switch (scheduleType.value) {
    case '每分钟':
      cron = `*/${intervalMinutes.value} * * * *`;
      break;
    case '每小时':
      cron = `0 */${intervalHours.value} * * *`;
      break;
    case '每天':
      cron = `${minutes} ${hours} * * *`;
      break;
    case '每周':
      cron = `${minutes} ${hours} * * ${weeklyDays.value.join(',')}`;
      break;
    case '每月':
      cron = `${minutes} ${hours} ${monthlyDays.value} * *`;
      break;
    case '自定义':
      cron = customCron.value;
      break;
    default:
      cron = '';
  }

  return cron;
};

// 处理添加网段
const handleAddSubnet = () => {
  const subnet = newSubnet.value.trim();

  if (!subnet) {
    ElMessage.error('请输入有效的网段！');
    return;
  }

  // 校验 IP 地址格式
  const [ip] = subnet.split('/');
  if (!isValidIP(ip)) {
    ElMessage.error('无效的 IP 地址格式！');
    return;
  }

  // 校验网段格式
  if (!isValidSubnet(subnet)) {
    ElMessage.error('无效的网段格式，正确格式为：IP/掩码（如：192.168.0.0/24）');
    return;
  }

  cachedSubnets.value.push({
    subnet: subnet,
    created_at: new Date().toISOString(),
  });

  newSubnet.value = '';
};

// 删除网段
const removeSubnet = (subnet: any) => {
  cachedSubnets.value = cachedSubnets.value.filter(s => s !== subnet);
};

// 处理添加策略
const handlePolicy = () => {
  // 校验策略名称是否为空
  if (!strategyName.value.trim()) return ElMessage.warning('策略名称是必填项！');

  // 校验策略描述是否完整
  const description = generatePolicyDescription();
  if (!description) return ElMessage.warning('请完整填写策略信息！');

  // 校验 cron 表达式是否生成
  cronExpression.value = generateCrontabExpression();
  if (!cronExpression.value) return ElMessage.warning('请填写有效的定时任务表达式！');

  if (!startExecutionTime.value) return ElMessage.warning('策略开始时间为必填项！'); 

  // 将策略添加到缓存
  cachedPolicies.value.push({
    name: strategyName.value,
    description,
    cronExpression: cronExpression.value,
    startTime: startExecutionTime,
    created_at: new Date().toISOString(),
  });

  // 重置表单
  resetForm();
};

const handleSavePolicy = () => {
  console.log(cachedPolicies)
};

// 重置表单
const resetForm = () => {
  strategyName.value = '';
  scheduleType.value = '每天';
  intervalMinutes.value = null;
  intervalHours.value = null;
  intervalDays.value = null;
  dailyTime.value = null;
  weeklyDays.value = [];
  weeklyTime.value = null;
  monthlyDays.value = [];
  monthlyTime.value = null;
  customCron.value = '';
  startExecutionTime.value = null;
};

// 删除策略
const removePolicy = (policy: any) => {
  cachedPolicies.value = cachedPolicies.value.filter(p => p !== policy);
};

// 执行扫描
const handleExecuteScan = () => {
  if (!selectedSubnet.value) {
    ElMessage.warning('请选择网段！');
  }
  console.log(`执行扫描：${selectedSubnet.value}`);
};

// 策略类型变化时重置相关字段
watch(scheduleType, (newType) => {
  intervalMinutes.value = null;
  intervalHours.value = null;
  intervalDays.value = null;
  startExecutionTime.value = null;

  if (newType === '每天') {
    dailyTime.value = null;
  } else if (newType === '每周') {
    weeklyTime.value = null;
    weeklyDays.value = [];
  } else if (newType === '每月') {
    monthlyTime.value = null;
    monthlyDays.value = [];
  } else if (newType === '自定义') {
    customCron.value = '';
  }
});
</script>



<style scoped>
.add-subnet-form {
  display: flex;
} 

.section {
  margin-bottom: 20px;
}

.title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 10px;
}
</style>