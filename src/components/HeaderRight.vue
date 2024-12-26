<template>
  <div class="header-right">
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
import { ref, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import UserMenu from './UserMenu.vue';
import { Moon, Sunny, ArrowDown } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

const { t, locale } = useI18n();

// 主题状态
const isDarkTheme = ref(localStorage.getItem('theme') === 'dark');

// 初始化主题
onMounted(() => {
  const savedTheme = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
  isDarkTheme.value = savedTheme === 'dark';
});

// 当前语言显示
const currentLanguageLabel = computed(() => {
  return locale.value === 'zh' ? '中文' : 'English';
});

// 切换语言
const handleLanguageChange = (lang: string) => {
  locale.value = lang;
  localStorage.setItem('language', lang);
  ElMessage.success(t('common.success'));
};

// 主题切换
const toggleTheme = () => {
  isDarkTheme.value = !isDarkTheme.value;
  const newTheme = isDarkTheme.value ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
};
</script>

<style scoped>
.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.theme-toggle {
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