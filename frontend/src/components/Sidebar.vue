<template>
  <el-menu
    default-active="1"
    background-color="#ffffff"
    text-color="#333333"
    active-text-color="#409eff">
    <router-link to="/ips">
      <el-menu-item index="1">
        <el-icon><Setting /></el-icon>
        <span>{{ $t('menu.ipManagement') }}</span>
      </el-menu-item>
    </router-link>
    <!-- 仅管理员可见 -->
    <template v-if="authStore.user?.is_admin">
      <router-link to="/users">
        <el-menu-item index="2">
          <el-icon><User /></el-icon>
          <span>{{ $t('menu.userManagement') }}</span>
        </el-menu-item>
      </router-link>
      <router-link to="/scans">
        <el-menu-item index="3">
          <el-icon><Operation /></el-icon>
          <span>{{ $t('menu.scanConfig') }}</span>
        </el-menu-item>
      </router-link>
      <router-link to="/tasks">
        <el-menu-item index="4">
          <el-icon><Clock /></el-icon>
          <span>{{ $t('menu.task') }}</span>
        </el-menu-item>
      </router-link>
      <router-link to="/notifications">
        <el-menu-item index="5">
          <el-icon><Bell /></el-icon>
          <span>{{ $t('menu.notifications') }}</span>
        </el-menu-item>
      </router-link>
    </template>
    <router-link to="/settings">
      <el-menu-item index="6">
        <el-icon><Setting /></el-icon>
        <span>{{ $t('menu.settings') }}</span>
      </el-menu-item>
    </router-link>
    <router-link to="/monitor">
      <el-menu-item index="7">
        <el-icon><Monitor /></el-icon>
        <span>{{ $t('menu.monitor') }}</span>
      </el-menu-item>
    </router-link>
  </el-menu>
</template>

<script setup lang="ts">
import { useAuthStore } from "../stores/auth"
import { ElMenu, ElMenuItem, ElIcon } from 'element-plus';
import { Setting, User, Bell, Operation, Clock, Monitor } from '@element-plus/icons-vue';  // 引入 Element Plus 的图标

const authStore = useAuthStore();
</script>

<style scoped>
.el-menu {
  border-right: none;
  margin: 0;
  padding: 1.5rem 0;
}

.el-menu a {
  text-decoration: none;
}

.el-menu-item {
  padding: 0; /* 去掉默认内边距 */
  font-size: 16px;
  height: 35px;
  margin: 10px;
}

.el-menu-item:hover {
  background-color: #f5f7fa;  /* 悬停背景色 */
}

.el-menu-item.is-active {
  background: #ff009526;
  color: #902362;
  font-weight: 500;
}
</style>