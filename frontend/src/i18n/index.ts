import { createI18n } from 'vue-i18n';
import messagesEn from './locales/en';
import messagesZh from './locales/zh';
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'; // 导入中文语言包
import enLocale from 'element-plus/dist/locale/en.mjs'; // 导入英文语言包并重命名

const i18n = createI18n({
  legacy: false, // 使用 Composition API 模式
  locale: localStorage.getItem('language') || 'zh', // 默认语言
  fallbackLocale: 'en', // 备用语言
  messages: {
    en: messagesEn,
    zh: messagesZh,
  },
  globalInjection: true, // 全局注入 $t
});

export { enLocale, zhCn }; // 导出 Element Plus 的语言包
export default i18n; 