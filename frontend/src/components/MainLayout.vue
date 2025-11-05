<!-- src/layouts/MainLayout.vue -->
<template>
  <n-message-provider>
  <el-container>
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-content">
        <!-- 左侧 Logo 和描述 -->
        <div class="header-left">
          <img class="logo" src="/src/assets/IPAM.png" alt="Logo" />
          <span class="platform-description">IPAM System</span>
        </div>

        <!-- 中间功能按钮 -->
        <div class="header-center">
          <header-center />
        </div>
        <!-- 右边功能按钮 -->
        <header-right />
      </div>
    </el-header>

    <!-- 左侧导航栏 -->
    <el-aside :class="['sidebar', { 'sidebar-collapsed': sidebarCollapsed }]">
      <sidebar />
    </el-aside>

    <!-- 主体内容 -->
    <el-main :class="['content', { 'content-expanded': sidebarCollapsed }]">
      <router-view />
    </el-main>
    <el-footer class="footer">
      <footer-nav />
    </el-footer>
  </el-container>
  </n-message-provider>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import HeaderRight from '../components/HeaderRight.vue';
import HeaderCenter from '../components/HeaderCenter.vue';
import FooterNav from '../components/FooterNav.vue';
import Sidebar from '../components/Sidebar.vue';
import { NMessageProvider } from 'naive-ui';

const sidebarCollapsed = ref(false);

const handleSidebarToggle = (event: CustomEvent) => {
  sidebarCollapsed.value = event.detail.collapsed;
};

onMounted(() => {
  window.addEventListener('sidebar-toggle', handleSidebarToggle as EventListener);
  // 从localStorage读取初始状态
  const saved = localStorage.getItem('sidebarCollapsed');
  if (saved !== null) {
    sidebarCollapsed.value = saved === 'true';
  }
});

onUnmounted(() => {
  window.removeEventListener('sidebar-toggle', handleSidebarToggle as EventListener);
});
</script>

<style scoped>
.el-container {
  margin-top: 30px; /* 预留顶部导航栏高度 */
  height: calc(100vh - 36px); /* 减去导航栏高度 */
  overflow: hidden;
}

.header {
  background-color: #fff;
  padding: 0 20px;
  position: fixed;
  top: 0;
  width: 100%;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
}

.header-content {
  display: flex;
  width: 100%;
  align-items: center;
  justify-content: space-between;
}

.sidebar {
  background-color: #fff;
  width: 240px;
  height: 100%;
  position: fixed;
  margin: 0;
  overflow-y: auto;
  z-index: 1;
  top: 3.75rem;
  left: 0;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
  scrollbar-color: rgb(184.875, 44.625, 126.225) #c2c2c4;
  scrollbar-width: thin;
  transition: width 0.3s;
}

.sidebar-collapsed {
  width: 64px;
}

.content {
  margin-left: 240px;
  padding: 32px;
  height: calc(100vh - 64px - 36px);
  background-color: #fff;
  transition: margin-left 0.3s;
}

.content-expanded {
  margin-left: 64px;
}

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  height: 40px;
  margin-right: 10px;
}

.platform-description {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}
</style>