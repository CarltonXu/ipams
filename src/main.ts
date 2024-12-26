import { createApp } from 'vue';
import { createPinia } from 'pinia';
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';
import App from './App.vue';
import router from './routers';
import i18n from './i18n';
import './style.css';

const app = createApp(App);
app.use(createPinia());
app.use(ElementPlus);
app.use(i18n);
app.use(router);
app.mount('#app');