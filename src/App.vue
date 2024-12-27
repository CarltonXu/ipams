<script setup lang="ts">
import { useAuthStore } from './stores/auth';
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { ElMessage } from 'element-plus';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const authStore = useAuthStore();
const router = useRouter();

// 添加响应拦截器
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    // 处理 token 过期的情况
    if (error.response?.data?.message === 'Token has expired') {
      // 清除认证状态
      authStore.logout();
      
      // 显示提示信息

      ElMessage.error(t('auth.tokenExpired'));
      
      // 跳转到登录页
      router.push('/login');
    }
    return Promise.reject(error);
  }
);

// 在挂载后检查身份认证状态
onMounted(() => {
  // 如果有 token 和 user，恢复用户状态
  if (localStorage.getItem('token') && localStorage.getItem('user')) {
    authStore.token = localStorage.getItem('token')!;
    authStore.user = JSON.parse(localStorage.getItem('user')!);
    axios.defaults.headers.common['Authorization'] = `Bearer ${authStore.token}`;
  }

  // 如果用户已登录，跳转到主页；如果没有登录，跳转到登录页面
  if (authStore.isAuthenticated) {
    router.push('/');
  } else {
    router.push('/login');
  }
});
</script>

<template>
  <div class="app">
    <router-view />
  </div>
</template>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

body {
  margin: 0;
  padding: 0;
  font-family: Arial, sans-serif;
}

.el-container {
  display: flex;
}

.el-main {
  flex-grow: 1;
  padding: 20px;
}
</style>
