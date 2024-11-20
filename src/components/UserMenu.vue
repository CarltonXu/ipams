<template>
  <el-dropdown @command="handleCommand" trigger="click">
    <span class="el-dropdown-link">
      <el-avatar size="small" :src="user.avatar" alt="Avatar" />
      <span class="username">{{ user.username }}</span>
    </span>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item command="profile">个人中心</el-dropdown-item>
        <el-dropdown-item command="logout">退出登录</el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup lang="ts">
import { useAuthStore } from '../stores/auth';  // 引入 Pinia store
import { useRouter } from 'vue-router';
import { computed } from 'vue';

// 获取用户数据
const authStore = useAuthStore();
const user = computed(() => authStore.user);
const router = useRouter();

// 处理下拉菜单命令
const handleCommand = (command: string) => {
  if (command === 'logout') {
    authStore.logout();  // 执行登出操作
    router.push('/login')
  } else if (command === 'profile') {
    router.push('/profile')
  }
};
</script>

<style scoped>
.el-dropdown-link {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 14px;
  gap: 0.5rem;
}

.el-dropdown-menu {
  z-index: 9999;
}

.username {
  font-weight: 500;
}

.el-dropdown-menu {
  width: 150px;
  text-align: center;
}

.el-dropdown-item {
  font-size: 14px;
}

/* 鼠标悬停时的效果 */
.el-dropdown-item:hover {
  background-color: #f5f5f5;
  color: #409eff;
}
</style>