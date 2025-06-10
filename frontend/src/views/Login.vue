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
  background-image: url('/src/assets/login-bg.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.login-box {
  background: #ffffffe0;
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

.register-link {
  color: var(--el-color-primary);
  text-decoration: none;
  margin-left: 0.5rem;
}

.register-link:hover {
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