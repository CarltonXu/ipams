<template>
  <div class="register-container">
    <div class="register-box">
      <div class="header">
        <h2>{{ t('auth.title') }}</h2>
        <p class="subtitle">{{ t('auth.registerSubtitle') }}</p>
      </div>

      <el-form 
        :model="form" 
        @submit.prevent="handleSubmit"
        label-position="top"
        class="register-form"
        :rules="rules"
        ref="formRef"
      >
        <el-form-item :label="t('auth.username')" prop="username">
          <el-input 
            v-model="form.username"
            :placeholder="t('user.management.dialog.placeholders.username')"
            class="input-field"
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item :label="t('auth.email')" prop="email">
          <el-input 
            v-model="form.email"
            :placeholder="t('user.management.dialog.placeholders.email')"
            class="input-field"
          >
            <template #prefix>
              <el-icon><Message /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item :label="t('auth.password')" prop="password">
          <el-input 
            v-model="form.password"
            type="password"
            :placeholder="t('user.management.dialog.placeholders.password')"
            show-password
            class="input-field"
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item :label="t('auth.confirmPassword')" prop="confirmPassword">
          <el-input 
            v-model="form.confirmPassword"
            type="password"
            :placeholder="t('auth.confirmPasswordPlaceholder')"
            show-password
            class="input-field"
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-button 
          type="primary" 
          native-type="submit"
          :loading="loading"
          class="submit-btn"
        >
          {{ t('auth.register') }}
        </el-button>
        
        <div class="additional-links">
          <span>{{ t('auth.hasAccount') }}</span>
          <router-link to="/login" class="login-link">
            {{ t('auth.login') }}
          </router-link>
        </div>

        <!-- 语言切换 -->
        <div class="language-switch">
          <span 
            :class="{ active: currentLanguage === 'zh' }"
            @click="changeLanguage('zh')"
          >
            中文
          </span>
          <span class="divider">|</span>
          <span 
            :class="{ active: currentLanguage === 'en' }"
            @click="changeLanguage('en')"
          >
            English
          </span>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useSettingsStore } from '../stores/settings';
import { ElMessage } from 'element-plus';
import { useI18n } from 'vue-i18n';
import { User, Lock, Message } from '@element-plus/icons-vue';
import type { FormInstance } from 'element-plus';
import type { RegisterCredentials } from '../types/user';

const { t, locale } = useI18n();
const router = useRouter();
const authStore = useAuthStore();
const settingsStore = useSettingsStore();
const loading = ref(false);
const formRef = ref<FormInstance>();
const currentLanguage = computed(() => locale.value);

const form = ref<RegisterCredentials>({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
});

const rules = {
  username: [
    { required: true, message: t('auth.validation.username'), trigger: 'blur' },
    { min: 3, message: t('auth.validation.usernameLength'), trigger: 'blur' }
  ],
  email: [
    { required: true, message: t('auth.validation.email.required'), trigger: 'blur' },
    { type: 'email', message: t('auth.validation.email.invalid'), trigger: 'blur' }
  ],
  password: [
    { required: true, message: t('auth.validation.password'), trigger: 'blur' },
    { min: 6, message: t('auth.validation.passwordLength'), trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: t('auth.validation.confirmPassword'), trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: Function) => {
        if (value !== form.value.password) {
          callback(new Error(t('auth.validation.passwordMismatch')));
        } else {
          callback();
        }
      },
      trigger: 'blur'
    }
  ]
};

const changeLanguage = (lang: string) => {
  settingsStore.setLanguage(lang);
  locale.value = lang;
};

const handleSubmit = async () => {
  if (!formRef.value) return;
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        await authStore.register(form.value);
        ElMessage.success(t('auth.registerSuccess'));
        router.push('/login');
      } catch (error: any) {
        ElMessage.error(error.message || t('auth.registerError'));
      } finally {
        loading.value = false;
      }
    }
  });
};
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-image: url('/src/assets/login-bg.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.register-box {
  background: #ffffffe0;;
  padding: 2.5rem;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
  width: 405px;
  transition: all 0.3s ease;
  border-radius: 8px;
}

.header {
  text-align: center;
  margin-bottom: 2rem;
}

.header h2 {
  font-size: 1.8rem;
  color: var(--el-text-color-primary);
  margin-bottom: 0.5rem;
}

.subtitle {
  color: var(--el-text-color-secondary);
  font-size: 0.9rem;
}

.captcha-container {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.captcha-input {
  flex: 1;
}

.captcha-image {
  height: 40px;
  border-radius: 4px;
  cursor: pointer;
}

.submit-btn {
  width: 100%;
  margin-top: 1rem;
}

.additional-links {
  margin-top: 1rem;
  text-align: center;
  color: var(--el-text-color-secondary);
}

.login-link {
  color: var(--el-color-primary);
  text-decoration: none;
  margin-left: 0.5rem;
}

.login-link:hover {
  text-decoration: underline;
}

.language-switch {
  margin-top: 1.5rem;
  text-align: center;
  color: var(--el-text-color-secondary);
}

.language-switch span {
  cursor: pointer;
  padding: 0 0.5rem;
}

.language-switch span.active {
  color: var(--el-color-primary);
  font-weight: 500;
}

.language-switch .divider {
  cursor: default;
  color: var(--el-border-color);
}

.input-field {
  width: 100%;
}
</style>