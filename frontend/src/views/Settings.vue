<template>
  <div class="settings">
    <el-card shadow="always" class="main-settings-card">
      <div class="page-title">
        <div class="page-header">
          <h2>{{ t('settings.title') }}</h2>
          <p class="subtitle">{{ t('settings.subtitle') }}</p>
        </div>
      </div>

      <div class="page-content">
        <el-form :model="settings" label-width="128px" @submit.prevent="saveSettings">
          <!-- 基本设置 -->
          <el-collapse v-model="activeNames">
            <el-collapse-item :title="t('settings.sections.basic')" name="1">
              <div class="section-header">
                <h3>{{ t('settings.sections.basic') }}</h3>
                <div class="section-actions">
                  <el-button 
                    type="primary" 
                    link 
                    @click="toggleEditMode('basic')"
                  >
                    {{ isEditMode.basic ? t('common.cancel') : t('common.edit') }}
                  </el-button>
                  <el-button
                    v-if="isEditMode.basic"
                    type="primary"
                    link
                    @click="saveSettings"
                  >
                    {{ t('common.save') }}
                  </el-button>
                </div>
              </div>
              <el-form-item :label="t('settings.form.language.label')" :rules="[{ required: true, message: t('settings.validation.language') }]">
                <el-select 
                  v-model="settings.language" 
                  :placeholder="t('settings.form.language.placeholder')"
                  :disabled="!isEditMode.basic"
                >
                  <el-option :label="t('settings.form.language.options.zh')" value="zh"></el-option>
                  <el-option :label="t('settings.form.language.options.en')" value="en"></el-option>
                </el-select>
              </el-form-item>

              <el-form-item :label="t('settings.form.theme.label')" :rules="[{ required: true, message: t('settings.validation.theme') }]">
                <el-select 
                  v-model="settings.theme" 
                  :placeholder="t('settings.form.theme.placeholder')"
                  :disabled="!isEditMode.basic"
                >
                  <el-option :label="t('settings.form.theme.options.light')" value="light"></el-option>
                  <el-option :label="t('settings.form.theme.options.dark')" value="dark"></el-option>
                </el-select>
              </el-form-item>
            </el-collapse-item>

            <!-- 界面设置 -->
            <el-collapse-item :title="t('settings.sections.interface')" name="2">
              <div class="section-header">
                <h3>{{ t('settings.sections.interface') }}</h3>
                <div class="section-actions">
                  <el-button 
                    type="primary" 
                    link 
                    @click="toggleEditMode('interface')"
                  >
                    {{ isEditMode.interface ? t('common.cancel') : t('common.edit') }}
                  </el-button>
                  <el-button
                    v-if="isEditMode.interface"
                    type="primary"
                    link
                    @click="saveSettings"
                  >
                    {{ t('common.save') }}
                  </el-button>
                </div>
              </div>
              <el-form-item :label="t('settings.form.notifications.label')">
                <el-switch 
                  v-model="settings.notificationsEnabled" 
                  :active-text="t('settings.form.notifications.on')" 
                  :inactive-text="t('settings.form.notifications.off')"
                  :disabled="!isEditMode.interface"
                ></el-switch>
              </el-form-item>

              <el-form-item :label="t('settings.form.timeFormat.label')">
                <el-select 
                  v-model="settings.timeFormat" 
                  :placeholder="t('settings.form.timeFormat.placeholder')"
                  :disabled="!isEditMode.interface"
                >
                  <el-option :label="t('settings.form.timeFormat.options.12h')" value="12h"></el-option>
                  <el-option :label="t('settings.form.timeFormat.options.24h')" value="24h"></el-option>
                </el-select>
              </el-form-item>
            </el-collapse-item>

            <!-- 通知设置 -->
            <el-collapse-item :title="t('settings.sections.notification')" name="4">
              <div class="section-header">
                <h3>{{ t('settings.sections.notification') }}</h3>
                <div class="section-actions">
                  <el-button 
                    type="primary" 
                    link 
                    @click="toggleEditMode('notification')"
                  >
                    {{ isEditMode.notification ? t('common.cancel') : t('common.edit') }}
                  </el-button>
                  <el-button
                    v-if="isEditMode.notification"
                    type="primary"
                    link
                    @click="saveSettings"
                  >
                    {{ t('common.save') }}
                  </el-button>
                </div>
              </div>
              <div class="notification-section-title">{{ t('settings.form.notifications.email.title') }}</div>
              <el-form-item class="notification-toggle-item" label-width="60px">
                <el-switch
                  v-model="emailEnabled"
                  @change="handleEmailEnabledChange"
                  :active-text="t('settings.form.notifications.email.enabled')"
                  :inactive-text="t('settings.form.notifications.email.disabled')"
                  :disabled="!isEditMode.notification"
                />
              </el-form-item>
              
              <template v-if="emailEnabled">
                <el-form ref="emailFormRef" :model="settings.emailConfig" :rules="emailRules" label-width="166px" class="notification-config-form">
                  <el-form-item :label="t('settings.form.notifications.email.smtp.host')" prop="smtpServer">
                    <el-input 
                      v-model="settings.emailConfig.smtpServer" 
                      :placeholder="t('settings.form.notifications.email.smtp.host')"
                      :disabled="!isEditMode.notification"
                    >
                      <template #prefix>
                        <el-icon><Connection /></el-icon>
                      </template>
                    </el-input>
                  </el-form-item>
                  
                  <el-form-item :label="t('settings.form.notifications.email.smtp.port')" prop="smtpPort">
                    <el-input-number 
                      v-model="settings.emailConfig.smtpPort" 
                      :min="1" 
                      :max="65535" 
                      class="w-full"
                      :disabled="!isEditMode.notification"
                    />
                  </el-form-item>
                  
                  <el-form-item :label="t('settings.form.notifications.email.smtp.username')" prop="smtpUsername">
                    <el-input 
                      v-model="settings.emailConfig.smtpUsername" 
                      :placeholder="t('settings.form.notifications.email.smtp.username')"
                      :disabled="!isEditMode.notification"
                    >
                      <template #prefix>
                        <el-icon><User /></el-icon>
                      </template>
                    </el-input>
                  </el-form-item>
                  
                  <el-form-item :label="t('settings.form.notifications.email.smtp.password')" prop="smtpPassword">
                    <el-input
                      v-model="settings.emailConfig.smtpPassword"
                      type="password"
                      :placeholder="t('settings.form.notifications.email.smtp.password')"
                      show-password
                      :disabled="!isEditMode.notification"
                    >
                      <template #prefix>
                        <el-icon><Lock /></el-icon>
                      </template>
                    </el-input>
                  </el-form-item>
                  
                  <el-form-item :label="t('settings.form.notifications.email.smtp.from')" prop="smtpFrom">
                    <el-input 
                      v-model="settings.emailConfig.smtpFrom" 
                      :placeholder="t('settings.form.notifications.email.smtp.from')"
                      :disabled="!isEditMode.notification"
                    >
                      <template #prefix>
                        <el-icon><Position /></el-icon>
                      </template>
                    </el-input>
                  </el-form-item>
                  
                  <el-form-item class="text-right" label-width="70px" v-if="isEditMode.notification">
                    <el-button
                      type="primary"
                      @click="testEmailConfig"
                      :loading="testingEmail"
                    >
                      <el-icon><Check /></el-icon>
                      {{ t('settings.form.notifications.email.smtp.test') }}
                    </el-button>
                  </el-form-item>
                </el-form>
              </template>

              <el-divider />

              <div class="notification-section-title">{{ t('settings.form.notifications.wechat.title') }}</div>
              <el-form-item class="notification-toggle-item" label-width="60px">
                <el-switch
                  v-model="wechatEnabled"
                  @change="handleWechatEnabledChange"
                  :active-text="t('settings.form.notifications.wechat.enabled')"
                  :inactive-text="t('settings.form.notifications.wechat.disabled')"
                  :disabled="!isEditMode.notification"
                />
              </el-form-item>
              
              <template v-if="wechatEnabled">
                <el-form ref="wechatFormRef" :model="settings.wechatConfig" :rules="wechatRules" label-width="120px" class="notification-config-form">
                  <el-form-item :label="t('settings.form.notifications.wechat.config.title')" label-width="166px" prop="webhookUrl">
                    <el-input
                      v-model="settings.wechatConfig.webhookUrl"
                      :placeholder="t('settings.form.notifications.wechat.config.appId')"
                      :disabled="!isEditMode.notification"
                    >
                      <template #prefix>
                        <el-icon><Link /></el-icon>
                      </template>
                    </el-input>
                  </el-form-item>
                  
                  <el-form-item class="text-right" label-width="70px" v-if="isEditMode.notification">
                    <el-button
                      type="primary"
                      @click="testWechatConfig"
                      :loading="testingWechat"
                    >
                      <el-icon><Check /></el-icon>
                      {{ t('settings.form.notifications.wechat.config.test') }}
                    </el-button>
                  </el-form-item>
                </el-form>
              </template>

              <el-divider />

              <div class="notification-section-title">{{ t('settings.form.notifications.events.title') }}</div>
              <div class="event-category-wrapper">
                <div class="event-category">
                  <h4>{{ t('settings.form.notifications.events.scan.title') }}</h4>
                  <div class="event-settings-grid">
                    <div class="grid-item">
                      <label>{{ t('settings.form.notifications.events.scan.complete') }}</label>
                      <el-switch 
                        v-model="scanCompleted" 
                        :disabled="!isEditMode.notification"
                      />
                    </div>
                    
                    <div class="grid-item">
                      <label>{{ t('settings.form.notifications.events.scan.error') }}</label>
                      <el-switch 
                        v-model="scanFailed" 
                        :disabled="!isEditMode.notification"
                      />
                    </div>
                  </div>
                </div>
                
                <el-divider v-if="t('settings.form.notifications.events.ip.title')" />

                <div class="event-category">
                  <h4>{{ t('settings.form.notifications.events.ip.title') }}</h4>
                  <div class="event-settings-grid">
                    <div class="grid-item">
                      <label>{{ t('settings.form.notifications.events.ip.claim') }}</label>
                      <el-switch 
                        v-model="ipClaimed" 
                        :disabled="!isEditMode.notification"
                      />
                    </div>
                    
                    <div class="grid-item">
                      <label>{{ t('settings.form.notifications.events.ip.release') }}</label>
                      <el-switch 
                        v-model="ipReleased" 
                        :disabled="!isEditMode.notification"
                      />
                    </div>
                  </div>
                </div>

                <el-divider v-if="t('settings.form.notifications.events.system.title')" />

                <div class="event-category">
                  <h4>{{ t('settings.form.notifications.events.system.title') }}</h4>
                  <div class="event-settings-grid">
                    <div class="grid-item">
                      <label>{{ t('settings.form.notifications.events.system.info') }}</label>
                      <el-switch 
                        v-model="policyCreated" 
                        :disabled="!isEditMode.notification"
                      />
                    </div>
                    
                    <div class="grid-item">
                      <label>{{ t('settings.form.notifications.events.system.warning') }}</label>
                      <el-switch 
                        v-model="policyUpdated" 
                        :disabled="!isEditMode.notification"
                      />
                    </div>
                    
                    <div class="grid-item">
                      <label>{{ t('settings.form.notifications.events.system.error') }}</label>
                      <el-switch 
                        v-model="policyDeleted" 
                        :disabled="!isEditMode.notification"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
          <el-button type="primary" @click="saveSettings" class="save-button" v-if="Object.values(isEditMode).some(v => v)">
            {{ t('settings.buttons.save') }}
          </el-button>
        </el-form>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useI18n } from 'vue-i18n';
import { useTheme } from '../composables/useTheme';
import { useSettingsStore } from '../stores/settings';
import type { FormInstance, FormRules } from 'element-plus';
import { Link, Connection, User, Lock, Position, Check  } from '@element-plus/icons-vue';

const { t } = useI18n();
const { toggleTheme } = useTheme();
const settingsStore = useSettingsStore();

// 表单验证规则
const emailRules: FormRules = {
  smtpServer: [
    { required: true, message: t('settings.form.notifications.email.smtp.host'), trigger: 'blur' }
  ],
  smtpPort: [
    { required: true, message: t('settings.form.notifications.email.smtp.port'), trigger: 'blur' }
  ],
  smtpUsername: [
    { required: true, message: t('settings.form.notifications.email.smtp.username'), trigger: 'blur' }
  ],
  smtpPassword: [
    { required: true, message: t('settings.form.notifications.email.smtp.password'), trigger: 'blur' }
  ],
  smtpFrom: [
    { required: true, message: t('settings.form.notifications.email.smtp.from'), trigger: 'blur' },
    { type: 'email', message: t('settings.form.notifications.email.smtp.from'), trigger: 'blur' }
  ]
};

const wechatRules: FormRules = {
  webhookUrl: [
    { required: true, message: t('settings.form.notifications.wechat.config.appId'), trigger: 'blur' }
  ]
};

// 系统设置的数据模型
const settings = ref({
  language: 'zh',
  theme: 'light',
  notificationsEnabled: false,
  timeFormat: '24h',
  emailConfig: {
    enabled: false,
    smtpServer: '',
    smtpPort: 587,
    smtpUsername: '',
    smtpPassword: '',
    smtpFrom: ''
  },
  wechatConfig: {
    enabled: false,
    webhookUrl: ''
  },
  eventConfig: {
    scanCompleted: true,
    scanFailed: true,
    ipClaimed: true,
    ipReleased: true,
    policyCreated: true,
    policyUpdated: true,
    policyDeleted: true
  }
});

// 计算属性用于处理双向绑定
const emailEnabled = computed({
  get: () => settings.value.emailConfig?.enabled ?? false,
  set: (value) => {
    if (!settings.value.emailConfig) {
      settings.value.emailConfig = {
        enabled: false,
        smtpServer: '',
        smtpPort: 587,
        smtpUsername: '',
        smtpPassword: '',
        smtpFrom: ''
      };
    }
    settings.value.emailConfig.enabled = value;
  }
});

const wechatEnabled = computed({
  get: () => settings.value.wechatConfig?.enabled ?? false,
  set: (value) => {
    if (!settings.value.wechatConfig) {
      settings.value.wechatConfig = {
        enabled: false,
        webhookUrl: ''
      };
    }
    settings.value.wechatConfig.enabled = value;
  }
});

// 事件配置的计算属性
const scanCompleted = computed({
  get: () => settings.value.eventConfig?.scanCompleted ?? false,
  set: (value) => {
    if (!settings.value.eventConfig) {
      settings.value.eventConfig = {
        scanCompleted: false,
        scanFailed: false,
        ipClaimed: false,
        ipReleased: false,
        policyCreated: false,
        policyUpdated: false,
        policyDeleted: false
      };
    }
    settings.value.eventConfig.scanCompleted = value;
  }
});

const scanFailed = computed({
  get: () => settings.value.eventConfig?.scanFailed ?? false,
  set: (value) => {
    if (!settings.value.eventConfig) {
      settings.value.eventConfig = {
        scanCompleted: false,
        scanFailed: false,
        ipClaimed: false,
        ipReleased: false,
        policyCreated: false,
        policyUpdated: false,
        policyDeleted: false
      };
    }
    settings.value.eventConfig.scanFailed = value;
  }
});

const ipClaimed = computed({
  get: () => settings.value.eventConfig?.ipClaimed ?? false,
  set: (value) => {
    if (!settings.value.eventConfig) {
      settings.value.eventConfig = {
        scanCompleted: false,
        scanFailed: false,
        ipClaimed: false,
        ipReleased: false,
        policyCreated: false,
        policyUpdated: false,
        policyDeleted: false
      };
    }
    settings.value.eventConfig.ipClaimed = value;
  }
});

const ipReleased = computed({
  get: () => settings.value.eventConfig?.ipReleased ?? false,
  set: (value) => {
    if (!settings.value.eventConfig) {
      settings.value.eventConfig = {
        scanCompleted: false,
        scanFailed: false,
        ipClaimed: false,
        ipReleased: false,
        policyCreated: false,
        policyUpdated: false,
        policyDeleted: false
      };
    }
    settings.value.eventConfig.ipReleased = value;
  }
});

const policyCreated = computed({
  get: () => settings.value.eventConfig?.policyCreated ?? false,
  set: (value) => {
    if (!settings.value.eventConfig) {
      settings.value.eventConfig = {
        scanCompleted: false,
        scanFailed: false,
        ipClaimed: false,
        ipReleased: false,
        policyCreated: false,
        policyUpdated: false,
        policyDeleted: false
      };
    }
    settings.value.eventConfig.policyCreated = value;
  }
});

const policyUpdated = computed({
  get: () => settings.value.eventConfig?.policyUpdated ?? false,
  set: (value) => {
    if (!settings.value.eventConfig) {
      settings.value.eventConfig = {
        scanCompleted: false,
        scanFailed: false,
        ipClaimed: false,
        ipReleased: false,
        policyCreated: false,
        policyUpdated: false,
        policyDeleted: false
      };
    }
    settings.value.eventConfig.policyUpdated = value;
  }
});

const policyDeleted = computed({
  get: () => settings.value.eventConfig?.policyDeleted ?? false,
  set: (value) => {
    if (!settings.value.eventConfig) {
      settings.value.eventConfig = {
        scanCompleted: false,
        scanFailed: false,
        ipClaimed: false,
        ipReleased: false,
        policyCreated: false,
        policyUpdated: false,
        policyDeleted: false
      };
    }
    settings.value.eventConfig.policyDeleted = value;
  }
});

// 测试状态
const testingEmail = ref(false);
const testingWechat = ref(false);

// 添加原始数据存储
const originalSettings = ref({
  language: '',
  theme: '',
  notificationsEnabled: false,
  timeFormat: '',
  emailConfig: {
    enabled: false,
    smtpServer: '',
    smtpPort: 587,
    smtpUsername: '',
    smtpPassword: '',
    smtpFrom: ''
  },
  wechatConfig: {
    enabled: false,
    webhookUrl: ''
  },
  eventConfig: {
    scanCompleted: false,
    scanFailed: false,
    ipClaimed: false,
    ipReleased: false,
    policyCreated: false,
    policyUpdated: false,
    policyDeleted: false
  }
});

// 检查数据是否有修改
const hasChanges = (section: keyof EditModeState) => {
  switch (section) {
    case 'basic':
      return settings.value.language !== originalSettings.value.language ||
             settings.value.theme !== originalSettings.value.theme;
    case 'interface':
      return settings.value.notificationsEnabled !== originalSettings.value.notificationsEnabled ||
             settings.value.timeFormat !== originalSettings.value.timeFormat;
    case 'notification':
      return JSON.stringify(settings.value.emailConfig) !== JSON.stringify(originalSettings.value.emailConfig) ||
             JSON.stringify(settings.value.wechatConfig) !== JSON.stringify(originalSettings.value.wechatConfig) ||
             JSON.stringify(settings.value.eventConfig) !== JSON.stringify(originalSettings.value.eventConfig);
    default:
      return false;
  }
};

// 保存原始数据
const saveOriginalSettings = () => {
  originalSettings.value = JSON.parse(JSON.stringify(settings.value));
};

// 重置为原始数据
const resetToOriginal = (section: keyof EditModeState) => {
  switch (section) {
    case 'basic':
      settings.value.language = originalSettings.value.language;
      settings.value.theme = originalSettings.value.theme;
      break;
    case 'interface':
      settings.value.notificationsEnabled = originalSettings.value.notificationsEnabled;
      settings.value.timeFormat = originalSettings.value.timeFormat;
      break;
    case 'notification':
      settings.value.emailConfig = JSON.parse(JSON.stringify(originalSettings.value.emailConfig));
      settings.value.wechatConfig = JSON.parse(JSON.stringify(originalSettings.value.wechatConfig));
      settings.value.eventConfig = JSON.parse(JSON.stringify(originalSettings.value.eventConfig));
      break;
  }
};

// 监听设置变化
watch(() => settings.value.language, (newLang) => {
  settingsStore.setLanguage(newLang);
});

watch(() => settings.value.theme, (newTheme) => {
  toggleTheme(newTheme as 'light' | 'dark');
  settingsStore.setTheme(newTheme as 'light' | 'dark');
});

watch(() => settings.value.notificationsEnabled, (value) => {
  settingsStore.setNotificationsEnabled(value);
});

watch(() => settings.value.timeFormat, (value) => {
  settingsStore.setTimeFormat(value as '12h' | '24h');
});

// 初始化加载设置
onMounted(async () => {
  try {
    await settingsStore.fetchConfig();
    
    settings.value = {
      language: settingsStore.language,
      theme: settingsStore.theme,
      notificationsEnabled: settingsStore.notificationsEnabled,
      timeFormat: settingsStore.timeFormat,
      emailConfig: settingsStore.emailConfig || {
        enabled: false,
        smtpServer: '',
        smtpPort: 587,
        smtpUsername: '',
        smtpPassword: '',
        smtpFrom: ''
      },
      wechatConfig: settingsStore.wechatConfig || {
        enabled: false,
        webhookUrl: ''
      },
      eventConfig: settingsStore.eventConfig || {
        scanCompleted: false,
        scanFailed: false,
        ipClaimed: false,
        ipReleased: false,
        policyCreated: false,
        policyUpdated: false,
        policyDeleted: false
      }
    };
    
    // 保存初始数据
    saveOriginalSettings();
  } catch (error) {
    console.error('加载设置失败:', error);
    ElMessage.error(t('settings.messages.loadFailed'));
  }
});

// 控制折叠面板的展开项
const activeNames = ref(['1', '2', '3', '4']);

// 表单引用
const emailFormRef = ref<FormInstance>();
const wechatFormRef = ref<FormInstance>();

// 处理邮件配置启用状态变化
const handleEmailEnabledChange = (value: boolean) => {
  emailEnabled.value = value;
  if (!value) {
    settings.value.emailConfig = {
      enabled: false,
      smtpServer: '',
      smtpPort: 587,
      smtpUsername: '',
      smtpPassword: '',
      smtpFrom: ''
    };
  }
};

// 处理微信配置启用状态变化
const handleWechatEnabledChange = (value: boolean) => {
  wechatEnabled.value = value;
  if (!value) {
    settings.value.wechatConfig = {
      enabled: false,
      webhookUrl: ''
    };
  }
};

// 测试邮件配置
const testEmailConfig = async () => {
  if (!emailFormRef.value) return;
  await emailFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        testingEmail.value = true;
        const success = await settingsStore.testConfig('email', settings.value.emailConfig);
        if (success) {
          ElMessage.success(t('settings.messages.notification.testEmailSuccess'));
        } else {
          ElMessage.error(t('settings.messages.notification.testEmailFailed'));
        }
      } catch (error) {
        // 理论上这里不会捕获到错误，因为 testConfig 已经内部处理并返回布尔值
        console.error('测试发送时发生意外错误:', error);
        ElMessage.error(t('common.error')); // 通用错误消息
      } finally {
        testingEmail.value = false;
      }
    }
  });
};

// 测试微信配置
const testWechatConfig = async () => {
  if (!wechatFormRef.value) return;
  await wechatFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        testingWechat.value = true;
        const success = await settingsStore.testConfig('wechat', settings.value.wechatConfig);
        if (success) {
          ElMessage.success(t('settings.form.notifications.wechat.config.testSuccess'));
        } else {
          ElMessage.error(t('settings.form.notifications.wechat.config.testFailed'));
        }
      } catch (error) {
        console.error('测试发送时发生意外错误:', error);
        ElMessage.error(t('common.error')); // 通用错误消息
      } finally {
        testingWechat.value = false;
      }
    }
  });
};

// 修改切换编辑模式的函数
const toggleEditMode = async (section: keyof EditModeState) => {
  if (isEditMode.value[section]) {
    // 如果当前是编辑模式，检查是否有未保存的修改
    if (hasChanges(section)) {
      try {
        await ElMessageBox.confirm(
          t('settings.messages.unsavedChanges'),
          t('common.warning'),
          {
            confirmButtonText: t('common.confirm'),
            cancelButtonText: t('common.cancel'),
            type: 'warning'
          }
        );
        // 用户确认取消，先重置数据，再关闭编辑模式
        resetToOriginal(section);
        isEditMode.value[section] = false;
      } catch {
        // 用户取消操作，保持编辑状态
        return;
      }
    } else {
      // 没有修改，直接关闭编辑模式
      isEditMode.value[section] = false;
    }
  } else {
    // 进入编辑模式时，保存当前数据作为原始数据
    saveOriginalSettings();
    isEditMode.value[section] = true;
  }
};

// 修改保存设置函数
const saveSettings = async () => {
  try {
    // 添加保存确认对话框
    await ElMessageBox.confirm(
      t('settings.messages.confirmSave'),
      t('common.confirm'),
      {
        confirmButtonText: t('common.save'),
        cancelButtonText: t('common.cancel'),
        type: 'info'
      }
    );

    await settingsStore.updateConfig({
      emailConfig: settings.value.emailConfig,
      wechatConfig: settings.value.wechatConfig,
      eventConfig: settings.value.eventConfig
    });
    ElMessage.success(t('settings.messages.notification.saveSuccess'));
    
    // 保存成功后更新原始数据
    saveOriginalSettings();
    
    // 重置所有编辑状态
    isEditMode.value = {
      basic: false,
      interface: false,
      notification: false
    };
  } catch (error) {
    // 如果是用户取消保存，不显示错误消息
    if (error !== 'cancel') {
      ElMessage.error(t('settings.messages.notification.saveFailed'));
    }
  }
};

// 编辑模式状态
interface EditModeState {
  basic: boolean;
  interface: boolean;
  notification: boolean;
}

const isEditMode = ref<EditModeState>({
  basic: false,
  interface: false,
  notification: false
});
</script>

<style scoped>
.settings {
  padding: 20px;
}

.main-settings-card {
  margin-bottom: 20px;
  box-shadow: var(--el-box-shadow-light); /* 更明显的阴影 */
}

.page-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-header h2 {
  font-size: 24px;
  margin: 0;
  color: var(--el-text-color-primary);
}

.page-header .subtitle {
  color: var(--el-text-color-regular);
  margin: 5px 0 0;
  font-size: 14px;
}

.page-content {
  max-height: 85%;
  overflow: auto;
}

:deep(.el-collapse-item__header) {
  font-size: 16px;
  font-weight: 500;
  padding: 12px 0;
  color: var(--el-text-color-primary);
}

:deep(.el-collapse-item__content) {
  padding: 20px;
}

.save-button {
  margin-top: 20px;
  margin-left: auto;
  margin-right: auto; /* 居中 */
  display: block;
  min-width: 150px; /* 增加按钮最小宽度 */
  text-align: center;
}

/* 通知部分容器 */
.notification-section {
  margin-bottom: 25px; /* 增加部分间距 */
  padding: 20px;
  border-radius: var(--el-border-radius-base);
  background-color: var(--el-fill-color-extra-light); /* 轻微背景色 */
  box-shadow: var(--el-box-shadow-lighter);
  transition: all 0.2s ease-in-out;
  &:hover {
    box-shadow: var(--el-box-shadow-light); /* 鼠标悬停时阴影加深 */
  }
}

/* 通知部分标题 */
.notification-section-title {
  font-size: 16px;
  font-weight: 600;
  margin-top: 25px; /* 与上一部分有更大间距 */
  margin-bottom: 20px;
  color: var(--el-text-color-primary);
  padding-left: 10px;
  border-left: 4px solid var(--el-color-primary); /* 增加左侧主色边框 */
}

/* 通知开关项样式 */
.notification-toggle-item {
  margin-bottom: 20px;
  padding-left: 10px; /* 与标题对齐 */
  :deep(.el-form-item__content) {
    justify-content: flex-end; /* 使开关靠右 */
    width: 100%;
  }
}

/* 通知配置表单样式 */
.notification-config-form {
  padding: 0;
  border: none;
  margin-bottom: 0;
}

/* 事件分类包裹器 */
.event-category-wrapper {
  padding-top: 10px;
}

/* 事件分类标题和内容块 */
.event-category {
  margin-bottom: 25px; /* 增加分类间距 */
  &:last-child {
    margin-bottom: 0;
  }
  h4 {
    font-size: 16px; /* 稍大一些 */
    font-weight: 600;
    color: var(--el-text-color-regular);
    margin-top: 0;
    margin-bottom: 15px;
    padding-left: 10px;
    border-left: 3px solid var(--el-color-info-light-3); /* 稍浅的边框色 */
  }
}

/* 事件设置网格布局 */
.event-settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); /* 调整列宽，适应更多列 */
  gap: 15px;
  padding: 0;
  border: none;
}

.grid-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: var(--el-color-white); /* 保持白色背景 */
  border: 1px solid var(--el-border-color-lighter); /* 细边框 */
  padding: 12px 18px;
  border-radius: var(--el-border-radius-base);
  box-shadow: var(--el-box-shadow-light); /* 增加轻微阴影 */
  transition: all 0.2s ease-in-out; /* 添加过渡效果 */
  cursor: pointer;
  label {
    color: var(--el-text-color-regular);
    font-size: 14px;
    margin-right: 10px; /* 标签和开关之间的距离 */
    flex-grow: 1; /* 标签占据更多空间 */
  }
  &:hover {
    box-shadow: var(--el-box-shadow-hover); /* 鼠标悬停时的阴影效果 */
    transform: translateY(-3px); /* 轻微上浮效果 */
  }
}

.text-right {
  display: flex;
  justify-content: flex-end;
  width: 100%;
  margin-top: 20px;
  padding-right: 0;
}

/* 确保表单项内部开关对齐 */
:deep(.el-form-item) {
  margin-bottom: 18px;
  align-items: center;
  .el-form-item__label {
    justify-content: flex-end;
    padding-right: 12px;
    line-height: 1.5;
    align-items: center;
    width: 166px!important;
  }
  .el-form-item__content {
    display: flex;
    align-items: center;
    line-height: 15px;
  }
}

/* 其他通用 Element Plus 样式 */
:deep(.el-input-number) {
  width: 100%;
}

:deep(.el-switch__label) {
  color: var(--el-text-color-regular);
}

:deep(.el-switch__label.is-active) {
  color: var(--el-color-primary);
}

:deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px var(--el-border-color) inset;
  &:hover {
    box-shadow: 0 0 0 1px var(--el-color-primary) inset;
  }
  &.is-focus {
    box-shadow: 0 0 0 1px var(--el-color-primary) inset;
  }
}

:deep(.el-button) {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

:deep(.el-button .el-icon) {
  margin-right: 4px;
}

/* 新增样式 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.section-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.section-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.readonly-value {
  color: var(--el-text-color-regular);
  font-size: 14px;
  padding: 8px 12px;
  background-color: var(--el-fill-color-light);
  border-radius: var(--el-border-radius-base);
  display: inline-block;
  min-width: 120px;
}

/* 编辑按钮样式 */
:deep(.el-button--primary.is-link) {
  font-size: 14px;
  padding: 0;
  height: auto;
  &:hover {
    opacity: 0.8;
  }
}

/* 表单项在只读模式下的样式 */
:deep(.el-form-item.is-readonly) {
  .el-form-item__content {
    background-color: var(--el-fill-color-light);
    border-radius: var(--el-border-radius-base);
    padding: 8px 12px;
  }
}

/* 修改禁用状态的样式 */
:deep(.el-input.is-disabled .el-input__wrapper),
:deep(.el-select.is-disabled .el-input__wrapper),
:deep(.el-input-number.is-disabled .el-input__wrapper) {
  background-color: var(--el-fill-color-light);
  box-shadow: 0 0 0 1px var(--el-border-color) inset;
}

:deep(.el-switch.is-disabled) {
  opacity: 0.8;
}

:deep(.el-switch.is-disabled .el-switch__core) {
  border-color: var(--el-border-color) !important;
  background-color: var(--el-fill-color-light) !important;
}

:deep(.el-switch.is-disabled .el-switch__action) {
  background-color: var(--el-color-white) !important;
}

:deep(.el-switch.is-disabled.is-checked .el-switch__core) {
  background-color: var(--el-color-primary-light-3) !important;
}

:deep(.el-switch.is-disabled.is-checked .el-switch__action) {
  background-color: var(--el-color-white) !important;
}
</style>
