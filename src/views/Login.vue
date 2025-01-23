<template>
  <div class="login-container">
    <div class="login-box">
      <div class="header">
        <h2>{{ t('auth.title') }}</h2>
        <p class="subtitle">{{ t('auth.subtitle') }}</p>
      </div>

      <el-form 
        :model="form" 
        @submit.prevent="handleSubmit"
        label-position="top"
        class="login-form"
      >
        <el-form-item :label="t('auth.username')" required>
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
        
        <el-form-item :label="t('auth.password')" required>
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

        <el-form-item :label="t('auth.captcha')" required>
          <div class="captcha-container">
            <el-input 
            v-model="form.captcha"
            :placeholder="t('auth.captchaPlaceholder')"
            class="captcha-input">
            <template #prefix>
              <el-icon><Picture /></el-icon>
            </template>
          </el-input>
          <img 
            :src="captchaUrl" 
            alt="验证码"
            class="captcha-image"
            @click="refreshCaptcha"
          />
        </div>
      </el-form-item>
       
        <el-button 
          type="primary" 
          native-type="submit"
          :loading="loading"
          class="submit-btn"
        >
          {{ t('auth.login') }}
        </el-button>

        <!-- 注册链接 -->
        
        <div class="additional-links">
          <span>{{ t('auth.noAccount') }}</span>
          <router-link to="/register" class="register-link">{{ t('auth.register') }}</router-link>
        </div>

        <!-- 语言切换放在登录按钮下方 -->
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
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { ElMessage } from 'element-plus';
import { useI18n } from 'vue-i18n';
import { User, Lock } from '@element-plus/icons-vue';
import { useSettingsStore } from '../stores/settings';
import type { LoginCredentials } from '../types/user';
import { Picture } from '@element-plus/icons-vue';

const { t, locale } = useI18n();
const router = useRouter();
const authStore = useAuthStore();
const settingsStore = useSettingsStore();
const loading = ref(false);

const currentLanguage = computed(() => locale.value);


// 添加验证码相关状态
const captchaUrl = ref('');
const captchaKey = ref('');

const form = ref<LoginCredentials>({
  username: '',
  password: '',
  captcha: '',
  captchaKey: '',
});

// 获取验证码
const getCaptcha = async () => {
  try {
    const { data } = await authStore.getCaptcha();
    captchaUrl.value = data.captchaImage;
    captchaKey.value = data.captchaKey;
  } catch (error) {
    ElMessage.error(t('auth.captchaError'));
  }
};

// 刷新验证码
const refreshCaptcha = () => {
  getCaptcha();
};

const changeLanguage = (lang: string) => {
  settingsStore.setLanguage(lang);
  locale.value = lang;
};

// 修改登录处理函数
const handleSubmit = async () => {
  if (!form.value.captcha) {
    ElMessage.error(t('auth.validation.captchaRequired'));
    return;
  }

  loading.value = true;
  try {
    await authStore.login({
      ...form.value,
      captchaKey: captchaKey.value
    });
    ElMessage.success(t('auth.loginSuccess'));
    router.push('/dashboard');
  } catch (error: any) {
    ElMessage.error(error.message || t('auth.loginError'));
    // 登录失败刷新验证码
    refreshCaptcha();
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  getCaptcha();
});

</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.login-box {
  background: var(--el-bg-color);
  padding: 2.5rem;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
  width: 405px;
  transition: all 0.3s ease;
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
  height: 42px;
  border-radius: 4px;
  cursor: pointer;
  transition: opacity 0.3s;
}

.captcha-image:hover {
  opacity: 0.8;
}

/* 新增样式 */
.additional-links {
  text-align: right;
  color: var(--el-text-color-secondary);
  font-size: 0.9rem;
}

.register-link {
  color: var(--el-color-primary);
  font-weight: bold;
  text-decoration: none;
}

.register-link:hover {
  text-decoration: underline;
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

.login-form {
  .el-form-item {
    margin-bottom: 1.5rem;
  }
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
:root[data-theme='dark'] .login-container {
  background: linear-gradient(135deg, #1a1c1e 0%, #2d3436 100%);
}
</style>