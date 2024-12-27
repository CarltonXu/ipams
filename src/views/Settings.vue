<template>
  <div class="settings">
    <el-card>
      <div class="page-title">
        <div class="page-header">
          <h2>{{ t('settings.title') }}</h2>
          <p class="subtitle">{{ t('settings.subtitle') }}</p>
        </div>
      </div>

      <el-form :model="settings" label-width="128px" @submit.prevent="saveSettings">
        <!-- 基本设置 -->
        <el-collapse v-model="activeNames">
          <el-collapse-item :title="t('settings.sections.basic')" name="1">
            <el-form-item :label="t('settings.form.language.label')" :rules="[{ required: true, message: t('settings.validation.language') }]">
              <el-select v-model="settings.language" :placeholder="t('settings.form.language.placeholder')">
                <el-option :label="t('settings.form.language.options.zh')" value="zh"></el-option>
                <el-option :label="t('settings.form.language.options.en')" value="en"></el-option>
              </el-select>
            </el-form-item>

            <el-form-item :label="t('settings.form.theme.label')" :rules="[{ required: true, message: t('settings.validation.theme') }]">
              <el-select v-model="settings.theme" :placeholder="t('settings.form.theme.placeholder')">
                <el-option :label="t('settings.form.theme.options.light')" value="light"></el-option>
                <el-option :label="t('settings.form.theme.options.dark')" value="dark"></el-option>
              </el-select>
            </el-form-item>
          </el-collapse-item>

          <!-- 界面设置 -->
          <el-collapse-item :title="t('settings.sections.interface')" name="2">
            <el-form-item :label="t('settings.form.notifications.label')">
              <el-switch 
                v-model="settings.notifications" 
                :active-text="t('settings.form.notifications.on')" 
                :inactive-text="t('settings.form.notifications.off')"
              ></el-switch>
            </el-form-item>

            <el-form-item :label="t('settings.form.timeFormat.label')">
              <el-select v-model="settings.timeFormat" :placeholder="t('settings.form.timeFormat.placeholder')">
                <el-option :label="t('settings.form.timeFormat.options.12h')" value="12h"></el-option>
                <el-option :label="t('settings.form.timeFormat.options.24h')" value="24h"></el-option>
              </el-select>
            </el-form-item>
          </el-collapse-item>

          <!-- 账户设置 -->
          <el-collapse-item :title="t('settings.sections.account')" name="3">
            <el-form-item :label="t('settings.form.password.label')">
              <el-button @click="showChangePasswordDialog" type="primary">
                {{ t('settings.form.password.button') }}
              </el-button>
            </el-form-item>
          </el-collapse-item>
        </el-collapse>

        <el-button type="primary" @click="saveSettings" class="save-button">
          {{ t('settings.buttons.save') }}
        </el-button>
      </el-form>

      <!-- 修改密码对话框 -->
      <el-dialog 
        v-model="changePasswordDialogVisible"
        :title="t('settings.form.password.dialog.title')" 
        width="600px"
      >
        <el-form :model="passwordForm" label-width="160px">
          <el-form-item 
            :label="t('settings.form.password.dialog.old')"
            :rules="[{ required: true, message: t('settings.validation.oldPassword') }]"
          >
            <el-input 
              v-model="passwordForm.oldPassword" 
              type="password"
              style="width: 360px;"
              :show-password="true"
            />
          </el-form-item>
          <el-form-item 
            :label="t('settings.form.password.dialog.new')"
            :rules="[{ required: true, message: t('settings.validation.newPassword') }]"
          >
            <el-input 
              v-model="passwordForm.newPassword" 
              type="password"
              style="width: 360px;"
              :show-password="true"
            />
          </el-form-item>
          <el-form-item 
            :label="t('settings.form.password.dialog.confirm')"
            :rules="[{ required: true, message: t('settings.validation.confirmPassword') }]"
          >
            <el-input 
              v-model="passwordForm.confirmPassword" 
              type="password"
              style="width: 360px;"
              :show-password="true"
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <div class="dialog-footer">
            <el-button @click="changePasswordDialogVisible = false">
              {{ t('settings.buttons.cancel') }}
            </el-button>
            <el-button type="primary" @click="changePassword">
              {{ t('settings.buttons.confirm') }}
            </el-button>
          </div>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { useI18n } from 'vue-i18n';
import { useTheme } from '../composables/useTheme';
import { useSettingsStore } from '../stores/settings';
import { useAuthStore } from '../stores/auth';
import { useUserStore } from '../stores/user';
import { useRouter } from 'vue-router';
import { useGlobalConfig } from 'element-plus';
// 导入 Element Plus 的语言包
import zhCn from 'element-plus/dist/locale/zh-cn.mjs';
import en from 'element-plus/dist/locale/en.mjs';

const { t, locale } = useI18n();
const { theme, toggleTheme } = useTheme();
const settingsStore = useSettingsStore();
const authStore = useAuthStore();
const userStore = useUserStore();
const router = useRouter();
const globalConfig = useGlobalConfig();
// 系统设置的数据模型
const settings = ref({
  language: locale.value,
  theme: theme.value,
  notifications: settingsStore.notifications,
  timeFormat: settingsStore.timeFormat
});

// 监听设置变化
watch(() => settings.value.language, (newLang) => {
  locale.value = newLang;
  // 更新 Element Plus 的语言
  globalConfig.locale = newLang === 'zh' ? zhCn : en;
  settingsStore.setLanguage(newLang);
});

watch(() => settings.value.theme, (newTheme) => {
  toggleTheme(newTheme);
  settingsStore.setTheme(newTheme);
});

watch(() => settings.value.notifications, (value) => {
  settingsStore.setNotifications(value);
});

watch(() => settings.value.timeFormat, (value) => {
  settingsStore.setTimeFormat(value);
});

// 初始化加载设置
onMounted(() => {
  settings.value = {
    language: settingsStore.language,
    theme: settingsStore.theme,
    notifications: settingsStore.notifications,
    timeFormat: settingsStore.timeFormat
  };
});

// 修改密码的表单数据
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
});

// 控制修改密码对话框显示
const changePasswordDialogVisible = ref(false);

// 控制折叠面板的展开项
const activeNames = ref(['1', '2', '3']);

// 保存系统设置
const saveSettings = () => {
  ElMessage.success(t('settings.messages.saveSuccess'));
};

// 显示修改密码对话框
const showChangePasswordDialog = () => {
  changePasswordDialogVisible.value = true;
  // 重置密码表单
  passwordForm.value = {
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  };
};

// 执行修改密码操作
const changePassword = async () => {
  // 获取表单数据
  const { oldPassword, newPassword, confirmPassword } = passwordForm.value;
  
  // 检查所有字段是否为空
  if (!oldPassword.trim()) {
    ElMessage.error(t('settings.validation.oldPassword'));
    return;
  }
  
  if (!newPassword.trim()) {
    ElMessage.error(t('settings.validation.newPassword'));
    return;
  }
  
  if (!confirmPassword.trim()) {
    ElMessage.error(t('settings.validation.confirmPassword'));
    return;
  }

  // 验证新密码和确认密码是否一致
  if (newPassword !== confirmPassword) {
    ElMessage.error(t('settings.messages.passwordMismatch'));
    return;
  }

  try {
    // 从 auth store 获取当前用户 ID
    const currentUserId = authStore.user?.id;
    
    if (!currentUserId) {
      throw new Error('未找到用户信息');
    }

    // 调用 store 的修改密码方法
    await userStore.updatePassword(
      currentUserId,
      oldPassword,
      newPassword
    );

    // 修改成功后的处理
    ElMessage.success(t('settings.messages.passwordSuccess'));
    changePasswordDialogVisible.value = false;
    
    // 重置表单
    passwordForm.value = {
      oldPassword: '',
      newPassword: '', 
      confirmPassword: ''
    };

    // 显示提示信息并倒计时
    ElMessage({
      type: 'success',
      message: t('settings.messages.passwordSuccessRedirect'),
      duration: 5000  // 显示5秒
    });

    // 5秒后登出并跳转到登录页
    setTimeout(async () => {
      await authStore.logout();  // 调用登出方法
      router.push('/login');     // 跳转到登录页
    }, 5000);

  } catch (error: any) {
    // 错误处理
    ElMessage.error(error.message || t('settings.messages.passwordError'));
  }
};
</script>

<style scoped>
:deep(.el-collapse-item__header) {
  font-size: 16px;
  font-weight: 500;
  padding: 12px 0;
}

:deep(.el-collapse-item__content) {
  padding: 20px;
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
  color: #333;
}

.page-header .subtitle {
  color: #666;
  margin: 5px 0 0;
  font-size: 14px;
}

.settings {
  padding: 20px;
}

.save-button {
  margin-top: 20px;
  margin-left: auto;
}

.dialog-footer {
  text-align: right;
}

.el-form-item {
  margin-bottom: 20px;
}
</style>
