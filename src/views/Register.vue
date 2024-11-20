<template>
  <div class="register-container">
    <div class="register-box">
      <div class="header">
        <h2>IP Management System</h2>
        <p class="subtitle">Create an account to manage your network</p>
      </div>
      <el-form 
        :model="form" 
        @submit.prevent="handleSubmit"
        label-position="top"
        class="register-form"
      >
        <el-form-item label="Username" required>
          <el-input 
            v-model="form.username"
            placeholder="Enter your username"
            class="input-field"
          />
        </el-form-item>
        
        <el-form-item label="Email" required>
          <el-input 
            v-model="form.email"
            placeholder="Enter your email"
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

        <el-form-item label="Confirm Password" required>
          <el-input 
            v-model="form.confirmPassword"
            type="password"
            placeholder="Confirm your password"
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
          Register
        </el-button>
        
        <div class="additional-links">
          <span>Already have an account?</span>
          <router-link to="/login" class="login-link">Login</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { ElMessage } from 'element-plus';
import type { RegisterCredentials } from '../types/user';

const router = useRouter();
const authStore = useAuthStore();
const loading = ref(false);

const form = ref<RegisterCredentials>({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
});

const handleSubmit = async () => {
  if (form.value.password !== form.value.confirmPassword) {
    ElMessage.error('Passwords do not match!');
    return;
  }

  loading.value = true;
  try {
    await authStore.register(form.value);
    ElMessage.success('Registration successful');
    // 注册成功后跳转到登录页面
    router.push('/login');
  } catch (error: any) {
    ElMessage.error(error.message);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: url('/assets/background.jpg') no-repeat center center fixed;
  background-size: cover;
}

.register-box {
  background: rgba(255, 255, 255, 0.85);
  padding: 2rem 3rem;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  max-width: 400px;
  width: 100%;
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

.login-link {
  color: #1d4ed8;
  font-weight: bold;
  text-decoration: none;
}

.login-link:hover {
  text-decoration: underline;
}
</style>