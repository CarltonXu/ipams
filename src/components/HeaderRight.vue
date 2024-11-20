<template>
  <div class="header-right">
    <!-- 主题切换按钮 -->
    <el-button
      icon="el-icon-sunrise"
      circle
      @click="toggleTheme"
      class="theme-toggle"
    />
  
    <!-- 语言切换下拉菜单 -->
    <el-dropdown trigger="click" class="language-dropdown">
      <span class="el-dropdown-link">
        {{ currentLanguage === 'zh' ? '中' : 'EN' }}
      </span>
      <template #dropdown>
        <el-dropdown-menu slot="dropdown">
          <el-dropdown-item @click="setLanguage('zh')">中文</el-dropdown-item>
          <el-dropdown-item @click="setLanguage('en')">English</el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  
    <!-- 用户菜单 -->
    <user-menu />
  </div>
</template>
  
<script setup lang="ts">
import { ref } from 'vue';
import UserMenu from './UserMenu.vue'; // 引入自定义用户菜单组件

// 当前语言状态
const currentLanguage = ref('zh');

// 切换语言
const setLanguage = (lang: string) => {
  currentLanguage.value = lang;
  // 在这里可以加入国际化逻辑，例如 vue-i18n
  console.log(`语言切换到: ${lang}`);
};

// 主题切换
const toggleTheme = () => {
  const currentTheme = document.body.getAttribute('data-theme');
  const newTheme = currentTheme === 'light' ? 'dark' : 'light';
  document.body.setAttribute('data-theme', newTheme);
  console.log(`主题切换到: ${newTheme}`);
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
  font-size: 14px;
  color: #333;
  padding: 5px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #fff;
}

.el-dropdown-link:hover {
  background-color: #f5f5f5;
}
</style>