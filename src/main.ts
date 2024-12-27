import { createApp } from 'vue';
import App from './App.vue';
import router from './routers';
import { createPinia } from 'pinia';
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';
import i18n from './i18n';
// 导入 Element Plus 的语言包
import zhCn from 'element-plus/dist/locale/zh-cn.mjs';
import en from 'element-plus/dist/locale/en.mjs';
import './style.css'

const app = createApp(App);
const pinia = createPinia();

// 根据当前语言设置 Element Plus 的语言
const currentLocale = localStorage.getItem('language') || 'zh';
const elementLocale = currentLocale === 'zh' ? zhCn : en;

app.use(ElementPlus, {
  locale: elementLocale, // 设置 Element Plus 的语言
});
app.use(i18n);
app.use(pinia);
app.use(router);

app.mount('#app');