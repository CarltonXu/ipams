import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import MainLayout from '../components/MainLayout.vue';
import IPList from '../components/IPList.vue';
import Profile from '../components/Profile.vue';
import UserManagement from '../views/UserManagement.vue';
import Settings from '../views/Settings.vue';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import ScanPolicyList from '../components/ScanPolicyList.vue';
import JobResults from '../components/JobResults.vue';

const routes = [
    {
        path: '/',
        component: MainLayout,
        children: [
          { path: 'ips', name: 'ShowIPs', component: IPList, meta: { requiresAuth: true } },
          { path: 'users', name: 'UserManagement', component: UserManagement, meta: { requiresAuth: true } },
          { path: 'scans', name: 'scan', component: ScanPolicyList, meta: { requiresAuth: true } },
          { path: 'settings', name: 'Settings', component: Settings, meta: { requiresAuth: true } },
          { path: 'profile', name: 'Profile', component: Profile, meta: { requiresAuth: true } },
          { path: 'jobs/:jobId/results', name: 'JobResults', component: JobResults, meta: { requiresAuth: true } },
        ],
    },
    {
        path: '/login',
        name: 'Login',
        component: Login,
        meta: { requiresAuth: true }
    },
    {
        path: '/register',
        name: 'Register',
        component: Register
    },
    {
        path: '/:pathMatch(.*)*',
        redirect: '/login'
    },
];

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes,
});

// 添加导航守卫，检查用户是否已登录
router.beforeEach((to, from, next) => {
    const authStore = useAuthStore();
    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        // 如果用户未认证并且访问的是需要认证的页面
        if (to.path !== '/login') {  // 如果目标页面不是登录页
            next('/login');  // 重定向到登录页
        } else {
            next();  // 如果已经在登录页，继续执行
        }
    } else {
        next();  // 否则继续执行
    }
});

export default router;