import { createApp } from 'vue';
import App from './App.vue';
import router from './routers';
import { createPinia } from 'pinia';
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';
// 从你的 i18n/index.ts 导入 i18n 实例以及 Element Plus 的语言包
import i18n, { enLocale, zhCn } from './i18n';
import './style.css'

const app = createApp(App);
const pinia = createPinia();

// 根据当前语言动态选择 Element Plus 的语言包
const getElementPlusLocale = (locale: string) => {
  if (locale === 'zh') {
    return zhCn;
  } else {
    return enLocale;
  }
};

app.use(ElementPlus, {
  locale: getElementPlusLocale(i18n.global.locale.value), // 动态设置 Element Plus 的语言
});
app.use(i18n);
app.use(pinia);
app.use(router);

app.mount('#app');