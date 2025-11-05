<template>
  <div class="sidebar-container">
    <!-- 折叠/展开按钮 -->
    <div class="collapse-button-container">
      <div class="collapse-button" @click="toggleCollapse">
        <el-icon>
          <component :is="isCollapsed ? Expand : Fold" />
        </el-icon>
      </div>
    </div>

  <el-menu
      :default-active="activeIndex"
      :collapse="isCollapsed"
    background-color="#ffffff"
    text-color="#333333"
      active-text-color="#409eff"
      :unique-opened="true"
      @select="handleMenuSelect">
      
      <!-- 资源管理 -->
      <el-sub-menu index="resource">
        <template #title>
          <el-icon><Grid /></el-icon>
          <span>{{ $t('menu.category.resourceManagement') }}</span>
        </template>
        <el-menu-item index="resource-ip" @click="router.push('/ips')">
          <el-icon><Connection /></el-icon>
          <template #title>{{ $t('menu.ipAddressManagement') }}</template>
      </el-menu-item>
        <el-menu-item index="resource-credential" @click="router.push('/credentials')">
        <el-icon><Key /></el-icon>
          <template #title>{{ $t('menu.credentials') }}</template>
      </el-menu-item>
      </el-sub-menu>

      <!-- 主机采集 -->
      <el-menu-item index="host" @click="router.push('/hosts')">
        <el-icon><DataAnalysis /></el-icon>
        <template #title>{{ $t('menu.hostCollection') }}</template>
      </el-menu-item>

      <!-- 系统监控 -->
      <el-menu-item index="monitor" @click="router.push('/monitor')">
        <el-icon><Monitor /></el-icon>
        <template #title>{{ $t('menu.monitor') }}</template>
      </el-menu-item>

      <!-- 网络扫描（仅管理员可见） -->
    <template v-if="authStore.user?.is_admin">
        <el-sub-menu index="scan">
          <template #title>
          <el-icon><Operation /></el-icon>
            <span>{{ $t('menu.category.networkScan') }}</span>
          </template>
          <el-menu-item index="scan-config" @click="router.push('/scans')">
            <el-icon><Setting /></el-icon>
            <template #title>{{ $t('menu.scanConfig') }}</template>
        </el-menu-item>
          <el-menu-item index="scan-task" @click="router.push('/tasks')">
          <el-icon><Clock /></el-icon>
            <template #title>{{ $t('menu.task') }}</template>
          </el-menu-item>
        </el-sub-menu>
      </template>

      <!-- 系统管理（仅管理员可见） -->
      <template v-if="authStore.user?.is_admin">
        <el-sub-menu index="admin">
          <template #title>
            <el-icon><UserFilled /></el-icon>
            <span>{{ $t('menu.category.systemManagement') }}</span>
          </template>
          <el-menu-item index="admin-user" @click="router.push('/users')">
            <el-icon><User /></el-icon>
            <template #title>{{ $t('menu.userManagement') }}</template>
        </el-menu-item>
          <el-menu-item index="admin-notification" @click="router.push('/notifications')">
          <el-icon><Bell /></el-icon>
            <template #title>{{ $t('menu.notifications') }}</template>
        </el-menu-item>
        </el-sub-menu>
    </template>

      <!-- 系统设置 -->
      <el-menu-item index="settings" @click="router.push('/settings')">
        <el-icon><Tools /></el-icon>
        <template #title>{{ $t('menu.settings') }}</template>
      </el-menu-item>
  </el-menu>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from "../stores/auth";
import { useRoute, useRouter } from 'vue-router';
import { 
  ElMenu, 
  ElMenuItem, 
  ElSubMenu,
  ElIcon 
} from 'element-plus';
import { 
  Setting, 
  User, 
  UserFilled,
  Bell, 
  Operation, 
  Clock, 
  Monitor, 
  Key, 
  DataAnalysis,
  Grid,
  Connection,
  Tools,
  Expand,
  Fold
} from '@element-plus/icons-vue';

const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();

// 折叠状态
const isCollapsed = ref(false);

// 从localStorage读取折叠状态
onMounted(() => {
  const saved = localStorage.getItem('sidebarCollapsed');
  if (saved !== null) {
    isCollapsed.value = saved === 'true';
  }
});

// 切换折叠状态
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value;
  localStorage.setItem('sidebarCollapsed', String(isCollapsed.value));
  // 触发自定义事件，通知MainLayout更新宽度
  window.dispatchEvent(new CustomEvent('sidebar-toggle', { 
    detail: { collapsed: isCollapsed.value } 
  }));
};

// 根据路由计算当前激活的菜单项
const activeIndex = computed(() => {
  const path = route.path;
  if (path === '/ips') return 'resource-ip';
  if (path === '/credentials') return 'resource-credential';
  if (path === '/hosts') return 'host';
  if (path === '/monitor') return 'monitor';
  if (path === '/users') return 'admin-user';
  if (path === '/scans') return 'scan-config';
  if (path === '/tasks') return 'scan-task';
  if (path === '/notifications') return 'admin-notification';
  if (path === '/settings') return 'settings';
  return '';
});

const handleMenuSelect = (index: string) => {
  // 菜单选择处理
  console.log('Selected menu:', index);
};
</script>

<style scoped>
.sidebar-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.collapse-button-container {
  padding: 16px 10px 8px;
  display: flex;
  justify-content: flex-end;
  flex-shrink: 0;
}

.collapse-button {
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  background-color: #f5f7fa;
  transition: background-color 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.collapse-button:hover {
  background-color: #f0f2f5;
}

.collapse-button .el-icon {
  font-size: 18px;
  color: #606266;
}

.el-menu {
  border-right: none;
  margin: 0;
  height: 100%;
}

.el-menu:not(.el-menu--collapse) {
  width: 240px;
}

.el-menu--collapse {
  width: 64px;
}

.el-menu a {
  text-decoration: none;
}

.el-menu-item,
.el-sub-menu__title {
  padding: 0 20px !important;
  font-size: 14px;
  height: 48px;
  line-height: 48px;
}

:deep(.el-menu-item:hover),
:deep(.el-sub-menu__title:hover) {
  background-color: #f5f7fa;
}

.el-menu-item.is-active {
  background: #ff009526;
  color: #902362;
  font-weight: 500;
}

.el-sub-menu {
  margin-bottom: 4px;
}

.el-sub-menu .el-menu-item {
  padding-left: 50px !important;
  height: 44px;
  line-height: 44px;
}

.el-icon {
  margin-right: 8px;
  font-size: 18px;
}

/* 折叠状态下的样式调整 */
.el-menu--collapse .el-menu-item,
.el-menu--collapse .el-sub-menu__title {
  padding: 0 20px !important;
  text-align: center;
}

.el-menu--collapse .el-icon {
  margin-right: 0;
}

/* 确保折叠时菜单项文本隐藏 */
.el-menu--collapse .el-menu-item span,
.el-menu--collapse .el-menu-item .el-menu-tooltip__trigger {
  display: none;
}
</style>