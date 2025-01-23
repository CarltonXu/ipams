<template>
  <div class="header-right">
    <el-button
      circle
      @click="goHome"
      class="home-button"
    >
      <el-icon><HomeFilled /></el-icon>
    </el-button>
    <!-- 主题切换按钮 -->
    <el-button
      circle
      @click="toggleTheme"
      class="theme-toggle"
    >
      <el-icon>
        <component :is="isDarkTheme ? Sunny : Moon" />
      </el-icon>
    </el-button>
  
    <!-- 语言切换下拉菜单 -->
    <el-dropdown trigger="click" class="language-dropdown" @command="handleLanguageChange">
      <span class="el-dropdown-link">
        {{ currentLanguageLabel }}
        <el-icon class="el-icon--right"><arrow-down /></el-icon>
      </span>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item command="zh">中文</el-dropdown-item>
          <el-dropdown-item command="en">English</el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  
    <!-- 用户菜单 -->
    <user-menu />
  </div>
</template>
  
<script setup lang="ts">
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import UserMenu from './UserMenu.vue';
import { useSettingsStore } from '../stores/settings';
import { Moon, Sunny, ArrowDown, HomeFilled } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import { useRouter } from 'vue-router';

const { t, locale } = useI18n();
const settingsStore = useSettingsStore();
const router = useRouter();

// 主题状态
const isDarkTheme = ref(settingsStore.theme === 'dark');

// 当前语言显示
const currentLanguageLabel = computed(() => {
  return settingsStore.language === 'zh' ? '中文' : 'English';
});

// 返回首页
const goHome = () => {
  router.push('/dashboard');
};

// 切换语言
const handleLanguageChange = (lang: string) => {
  locale.value = lang;
  settingsStore.setLanguage(lang);
  ElMessage.success(t('common.success'));
};

// 主题切换
const toggleTheme = () => {
  isDarkTheme.value = !isDarkTheme.value;
  const newTheme = isDarkTheme.value ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', newTheme);
  settingsStore.setTheme(newTheme);
};
</script>

<style scoped>
.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.theme-toggle, .home-button {
  font-size: 18px;
}

.language-dropdown {
  cursor: pointer;
}

.el-dropdown-link {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: var(--el-text-color-primary);
  padding: 5px 10px;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  background-color: var(--el-bg-color);
}

.el-dropdown-link:hover {
  background-color: var(--el-bg-color-hover);
}

/* 暗色主题适配 */
:deep(.el-button) {
  --el-button-bg-color: var(--el-bg-color);
  --el-button-text-color: var(--el-text-color-primary);
  --el-button-border-color: var(--el-border-color);
}
</style>