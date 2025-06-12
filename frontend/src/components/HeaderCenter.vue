<template>
  <nav class="header-nav">
    <router-link 
      v-for="item in filteredNavItems"
      :key="item.path"
      :to="item.path"
      class="nav-link"
      :class="{'clicked': item.clicked}" 
      @click="handleClick(item)"
      active-class="active">
      <el-icon>
        <component :is="item.icon" />
      </el-icon>
      {{ item.label }}
    </router-link>
   </nav>
</template>

<script setup lang="ts">
import { ref, markRaw, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { Setting, User, Operation, Bell, Clock } from '@element-plus/icons-vue';
import { useAuthStore } from '../stores/auth'; // 引入认证存储

const { t } = useI18n();

const navItems = ref([
  { label: computed(() => t('menu.ipManagement')), path: '/ips', icon: markRaw(Setting), clicked: false, is_admin_only: false },
  { label: computed(() => t('menu.userManagement')), path: '/users', icon: markRaw(User), clicked: false, is_admin_only: true },
  { label: computed(() => t('menu.scanConfig')), path: '/scans', icon: markRaw(Operation), clicked: false, is_admin_only: true },
  { label: computed(() => t('menu.task')), path: '/tasks', icon: markRaw(Clock), clicked: false, is_admin_only: false },
  { label: computed(() => t('menu.notifications')), path: '/notifications', icon: markRaw(Bell), clicked: false, is_admin_only: false },
  { label: computed(() => t('menu.settings')), path: '/settings', icon: markRaw(Setting), clicked: false, is_admin_only: false },
]);

// 获取用户权限状态
const authStore = useAuthStore();
const isAdmin = computed(() => authStore.user?.is_admin); // 从存储中获取是否为管理员

// 过滤后的导航项
const filteredNavItems = computed(() =>
  navItems.value.filter(item => !item.is_admin_only || isAdmin.value)
);

// 点击事件处理，设置 clicked 为 true，并将其他按钮的 clicked 设置为 false
const handleClick = (clickedItem: any) => {
  // 清除所有按钮的点击状态
  navItems.value.forEach(item => {
    item.clicked = false;
  });
  // 设置当前点击按钮为选中状态
  clickedItem.clicked = true;
};
</script>

<style scoped>
.header-nav {
  flex-grow: 1;
  display: flex;
  justify-content: center;
  gap: 10px;
}

.nav-link {
  font-weight: 500;
  font-size: .875rem;
  color: #333;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  position: relative;
  transition: all 0.3s;
  border-bottom: 2px solid transparent;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;    /* 定位到中间 */
  width: 0;
  height: 2px;
  background-color: #912363;
  transition: width 0.3s ease, transform 0.3s ease;
  transform: translateX(-50%) scaleX(0);  /* 从中间开始，缩放效果 */
}

.nav-link:hover::after {
  width: 100%;         /* 鼠标悬停时，边框宽度变为100% */
  transform: translateX(-50%) scaleX(1); /* 鼠标悬停时，从中间扩展 */
  border-radius: 3px;
}

.nav-link.active {
  font-weight: 500;
  color: #912363;
}

.nav-link.clicked::after {
  width: 100%;
  transform: translateX(-50%) scaleX(1);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}
</style>