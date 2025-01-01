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
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.register-box {
  background: var(--el-bg-color);
  padding: 2.5rem;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
  width: 450px;
  transition: all 0.3s ease;
}

.header {
  text-align: center;
  margin-bottom: 2rem;
}

.header h2 {
  font-size: 2rem;
  font-weight: 600;
  color: #333;
}

.subtitle {
  font-size: 1rem;
  color: #666;
  margin-top: 0.5rem;
}


.additional-links {
  text-align: right;
  color: var(--el-text-color-secondary);
  font-size: 0.9rem;
}

.login-link {
  color: var(--el-color-primary);
  font-weight: bold;
  text-decoration: none;
}

.login-link:hover {
  text-decoration: underline;
}

.input-field {
  --el-input-height: 42px;
  
  :deep(.el-input__wrapper) {
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
    
    &:hover {
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    &.is-focus {
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    }
  }

  :deep(.el-input__prefix) {
    color: var(--el-text-color-secondary);
  }
}

.submit-btn {
  width: 100%;
  height: 42px;
  font-size: 1rem;
  font-weight: 500;
  margin: 1rem 0;
  letter-spacing: 1px;
}

.language-switch {
  text-align: center;
  margin-top: 1.5rem;
  color: var(--el-text-color-secondary);
  font-size: 0.9rem;

  span {
    cursor: pointer;
    padding: 0.3rem 0.5rem;
    transition: all 0.3s ease;

    &:hover {
      color: var(--el-color-primary);
    }

    &.active {
      color: var(--el-color-primary);
      font-weight: 500;
    }
  }

  .divider {
    margin: 0 0.5rem;
    cursor: default;
    
    &:hover {
      color: var(--el-text-color-secondary);
    }
  }
}

/* 暗色模式适配 */
:root[data-theme='dark'] .register-container {
  background: linear-gradient(135deg, #1a1c1e 0%, #2d3436 100%);
}
</style>