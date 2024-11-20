<template>
  <div class="login-container">
    <div class="login-box">
      <div class="header">
        <h2>IPAM System Platform</h2>
        <p class="subtitle">Monitor and manage your network with ease</p>
      </div>
      <el-form 
        :model="form" 
        @submit.prevent="handleSubmit"
        label-position="top"
        class="login-form"
      >
        <el-form-item label="Username" required>
          <el-input 
            v-model="form.username"
            placeholder="Enter your username"
            class="input-field"
          />
        </el-form-item>
        
        <el-form-item label="Password" required>
          <el-input 
            v-model="form.password"
            type="password"
            placeholder="Enter your password"
            show-password
            class="input-field"
          />
        </el-form-item>
        
        <el-button 
          type="primary" 
          native-type="submit"
          :loading="loading"
          class="submit-btn"
        >
          Login
        </el-button>
        <!--
        <div class="additional-links">
          <span>Don't have an account?</span>
          <router-link to="/register" class="register-link">Register here</router-link>
        </div>
        -->
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { ElMessage } from 'element-plus';
import type { LoginCredentials } from '../types/user';

const router = useRouter();
const authStore = useAuthStore();
const loading = ref(false);

const form = ref<LoginCredentials>({
  username: '',
  password: '',
});

const handleSubmit = async () => {
  loading.value = true;
  try {
    await authStore.login(form.value);
    ElMessage.success('Login successful');
    // 登录成功后跳转到主页
    router.push('/ips'); // 跳转到主页或用户想去的页面
  } catch (error: any) {
    ElMessage.error(error.message);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: url('/assets/background.jpg') no-repeat center center fixed;
  background-size: cover;
}

.login-box {
  background: rgba(255, 255, 255, 0.85);
  padding: 2rem 3rem;
  border-radius: 2px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  max-width: 400px;
  width: 100%;
}

.header {
  text-align: center;
  margin-bottom: 2rem;
}

.header h2 {
  font-size: 1.8rem;
  font-weight: 600;
  color: #333;
}

.subtitle {
  font-size: 1rem;
  color: #666;
  margin-top: 0.3rem;
}

.input-field {
  border-radius: 8px;
  padding: 12px;
}

.submit-btn {
  width: 100%;
  height: 45px;
  border-radius: 8px;
  margin-top: 1.5rem;
  font-size: 1.1rem;
}

.additional-links {
  text-align: center;
  margin-top: 1rem;
  font-size: 14px;
}

.register-link {
  color: #1d4ed8;
  font-weight: bold;
  text-decoration: none;
}

.register-link:hover {
  text-decoration: underline;
}
</style>
