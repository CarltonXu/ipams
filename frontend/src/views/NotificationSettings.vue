<template>
  <n-card title="通知配置">
    <!-- 邮件通知配置 -->
    <n-divider>邮件通知</n-divider>
    <n-form
      ref="emailFormRef"
      :model="emailConfig"
      :rules="emailRules"
      label-placement="left"
      label-width="auto"
      require-mark-placement="right-hanging"
    >
      <n-form-item label="启用邮件通知">
        <n-switch v-model:value="emailConfig.enabled" @update:value="handleEmailEnabledChange" />
      </n-form-item>
      
      <template v-if="emailConfig.enabled">
        <n-form-item label="SMTP服务器" path="smtpServer">
          <n-input v-model:value="emailConfig.smtpServer" placeholder="smtp.example.com" />
        </n-form-item>
        
        <n-form-item label="SMTP端口" path="smtpPort">
          <n-input-number v-model:value="emailConfig.smtpPort" :min="1" :max="65535" />
        </n-form-item>
        
        <n-form-item label="SMTP用户名" path="smtpUsername">
          <n-input v-model:value="emailConfig.smtpUsername" placeholder="your-username" />
        </n-form-item>
        
        <n-form-item label="SMTP密码" path="smtpPassword">
          <n-input
            v-model:value="emailConfig.smtpPassword"
            type="password"
            placeholder="your-password"
            show-password-on="click"
          />
        </n-form-item>
        
        <n-form-item label="发件人地址" path="smtpFrom">
          <n-input v-model:value="emailConfig.smtpFrom" placeholder="noreply@example.com" />
        </n-form-item>
        
        <n-form-item>
          <n-button
            type="primary"
            @click="testEmailConfig"
            :loading="testingEmail"
          >
            测试邮件配置
          </n-button>
        </n-form-item>
      </template>
    </n-form>

    <!-- 微信通知配置 -->
    <n-divider>微信通知</n-divider>
    <n-form
      ref="wechatFormRef"
      :model="wechatConfig"
      :rules="wechatRules"
      label-placement="left"
      label-width="auto"
      require-mark-placement="right-hanging"
    >
      <n-form-item label="启用微信通知">
        <n-switch v-model:value="wechatConfig.enabled" @update:value="handleWechatEnabledChange" />
      </n-form-item>
      
      <template v-if="wechatConfig.enabled">
        <n-form-item label="Webhook地址" path="webhookUrl">
          <n-input
            v-model:value="wechatConfig.webhookUrl"
            placeholder="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"
          />
        </n-form-item>
        
        <n-form-item>
          <n-button
            type="primary"
            @click="testWechatConfig"
            :loading="testingWechat"
          >
            测试微信配置
          </n-button>
        </n-form-item>
      </template>
    </n-form>

    <!-- 通知事件配置 -->
    <n-divider>通知事件</n-divider>
    <n-form
      ref="eventFormRef"
      :model="eventConfig"
      label-placement="left"
      label-width="auto"
    >
      <n-form-item label="扫描任务完成">
        <n-switch v-model:value="eventConfig.scanCompleted" />
      </n-form-item>
      
      <n-form-item label="扫描任务失败">
        <n-switch v-model:value="eventConfig.scanFailed" />
      </n-form-item>
      
      <n-form-item label="IP地址认领">
        <n-switch v-model:value="eventConfig.ipClaimed" />
      </n-form-item>
      
      <n-form-item label="IP地址释放">
        <n-switch v-model:value="eventConfig.ipReleased" />
      </n-form-item>
      
      <n-form-item label="策略创建">
        <n-switch v-model:value="eventConfig.policyCreated" />
      </n-form-item>
      
      <n-form-item label="策略更新">
        <n-switch v-model:value="eventConfig.policyUpdated" />
      </n-form-item>
      
      <n-form-item label="策略删除">
        <n-switch v-model:value="eventConfig.policyDeleted" />
      </n-form-item>
    </n-form>

    <!-- 保存按钮 -->
    <div class="action-buttons">
      <n-button
        type="primary"
        @click="saveConfig"
        :loading="saving"
      >
        保存配置
      </n-button>
    </div>
  </n-card>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import type { FormInst, FormRules } from 'naive-ui'
import { useNotificationStore } from '../stores/notification'

const notificationStore = useNotificationStore()

// 表单引用
const emailFormRef = ref<FormInst | null>(null)
const wechatFormRef = ref<FormInst | null>(null)
const eventFormRef = ref<FormInst | null>(null)

// 邮件配置
const emailConfig = reactive({
  enabled: false,
  smtpServer: '',
  smtpPort: 587,
  smtpUsername: '',
  smtpPassword: '',
  smtpFrom: ''
})

// 微信配置
const wechatConfig = reactive({
  enabled: false,
  webhookUrl: ''
})

// 事件配置
const eventConfig = reactive({
  scanCompleted: true,
  scanFailed: true,
  ipClaimed: true,
  ipReleased: true,
  policyCreated: true,
  policyUpdated: true,
  policyDeleted: true
})

// 表单验证规则
const emailRules: FormRules = {
  smtpServer: {
    required: true,
    message: '请输入SMTP服务器地址',
    trigger: 'blur'
  },
  smtpPort: {
    required: true,
    message: '请输入SMTP端口',
    trigger: 'blur'
  },
  smtpUsername: {
    required: true,
    message: '请输入SMTP用户名',
    trigger: 'blur'
  },
  smtpPassword: {
    required: true,
    message: '请输入SMTP密码',
    trigger: 'blur'
  },
  smtpFrom: {
    required: true,
    message: '请输入发件人地址',
    trigger: 'blur'
  }
}

const wechatRules: FormRules = {
  webhookUrl: {
    required: true,
    message: '请输入Webhook地址',
    trigger: 'blur'
  }
}

// 状态
const testingEmail = ref(false)
const testingWechat = ref(false)
const saving = ref(false)

// 加载配置
const loadConfig = async () => {
  await notificationStore.fetchConfig()
  const config = notificationStore.config
  
  if (config) {
    emailConfig.enabled = config.ENABLE_EMAIL_NOTIFICATION === 'true'
    emailConfig.smtpServer = config.SMTP_SERVER
    emailConfig.smtpPort = parseInt(config.SMTP_PORT)
    emailConfig.smtpUsername = config.SMTP_USERNAME
    emailConfig.smtpPassword = config.SMTP_PASSWORD
    emailConfig.smtpFrom = config.SMTP_FROM
    
    wechatConfig.enabled = config.ENABLE_WECHAT_NOTIFICATION === 'true'
    wechatConfig.webhookUrl = config.WECHAT_WEBHOOK_URL
    
    eventConfig.scanCompleted = config.NOTIFY_SCAN_COMPLETED === 'true'
    eventConfig.scanFailed = config.NOTIFY_SCAN_FAILED === 'true'
    eventConfig.ipClaimed = config.NOTIFY_IP_CLAIMED === 'true'
    eventConfig.ipReleased = config.NOTIFY_IP_RELEASED === 'true'
    eventConfig.policyCreated = config.NOTIFY_POLICY_CREATED === 'true'
    eventConfig.policyUpdated = config.NOTIFY_POLICY_UPDATED === 'true'
    eventConfig.policyDeleted = config.NOTIFY_POLICY_DELETED === 'true'
  }
}

// 保存配置
const saveConfig = async () => {
  try {
    saving.value = true
    
    // 验证表单
    if (emailConfig.enabled) {
      await emailFormRef.value?.validate()
    }
    if (wechatConfig.enabled) {
      await wechatFormRef.value?.validate()
    }
    
    const config = {
      ENABLE_EMAIL_NOTIFICATION: emailConfig.enabled.toString(),
      SMTP_SERVER: emailConfig.smtpServer,
      SMTP_PORT: emailConfig.smtpPort.toString(),
      SMTP_USERNAME: emailConfig.smtpUsername,
      SMTP_PASSWORD: emailConfig.smtpPassword,
      SMTP_FROM: emailConfig.smtpFrom,
      
      ENABLE_WECHAT_NOTIFICATION: wechatConfig.enabled.toString(),
      WECHAT_WEBHOOK_URL: wechatConfig.webhookUrl,
      
      NOTIFY_SCAN_COMPLETED: eventConfig.scanCompleted.toString(),
      NOTIFY_SCAN_FAILED: eventConfig.scanFailed.toString(),
      NOTIFY_IP_CLAIMED: eventConfig.ipClaimed.toString(),
      NOTIFY_IP_RELEASED: eventConfig.ipReleased.toString(),
      NOTIFY_POLICY_CREATED: eventConfig.policyCreated.toString(),
      NOTIFY_POLICY_UPDATED: eventConfig.policyUpdated.toString(),
      NOTIFY_POLICY_DELETED: eventConfig.policyDeleted.toString()
    }
    
    await notificationStore.updateConfig(config)
  } catch (error) {
    // 表单验证失败
  } finally {
    saving.value = false
  }
}

// 测试邮件配置
const testEmailConfig = async () => {
  try {
    await emailFormRef.value?.validate()
    testingEmail.value = true
    await notificationStore.testConfig('email', {
      smtpServer: emailConfig.smtpServer,
      smtpPort: emailConfig.smtpPort,
      smtpUsername: emailConfig.smtpUsername,
      smtpPassword: emailConfig.smtpPassword,
      smtpFrom: emailConfig.smtpFrom
    })
  } catch (error) {
    // 表单验证失败
  } finally {
    testingEmail.value = false
  }
}

// 测试微信配置
const testWechatConfig = async () => {
  try {
    await wechatFormRef.value?.validate()
    testingWechat.value = true
    await notificationStore.testConfig('wechat', {
      webhookUrl: wechatConfig.webhookUrl
    })
  } catch (error) {
    // 表单验证失败
  } finally {
    testingWechat.value = false
  }
}

// 处理邮件通知开关
const handleEmailEnabledChange = (checked: boolean) => {
  if (!checked) {
    emailConfig.smtpServer = ''
    emailConfig.smtpPort = 587
    emailConfig.smtpUsername = ''
    emailConfig.smtpPassword = ''
    emailConfig.smtpFrom = ''
  }
}

// 处理微信通知开关
const handleWechatEnabledChange = (checked: boolean) => {
  if (!checked) {
    wechatConfig.webhookUrl = ''
  }
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.action-buttons {
  margin-top: 24px;
  text-align: center;
}
</style> 