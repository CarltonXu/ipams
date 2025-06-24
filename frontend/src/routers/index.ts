import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
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
import Dashboard from '../components/Dashboard.vue';
import NotificationHistory from '../views/NotificationHistory.vue';
import Tasks from '../views/Tasks.vue';
import Monitor from '../views/Monitor.vue';

const routes: RouteRecordRaw[] = [
    {
        path: '/',
        component: MainLayout,
        children: [
          { path: 'ips', name: 'ShowIPs', component: IPList, meta: { requiresAuth: true } },
          { path: 'users', name: 'UserManagement', component: UserManagement, meta: { requiresAuth: true } },
          { path: 'scans', name: 'scan', component: ScanPolicyList, meta: { requiresAuth: true } },
          { path: 'tasks', name: 'task', component: Tasks, meta: { requiresAuth: true } },
          { path: 'settings', name: 'Settings', component: Settings, meta: { requiresAuth: true } },
          { path: 'profile', name: 'Profile', component: Profile, meta: { requiresAuth: true } },
          { path: 'jobs/:jobId/results', name: 'JobResults', component: JobResults, meta: { requiresAuth: true } },
          { path: 'dashboard', name: 'Dashboard', component: Dashboard, meta: { requiresAuth: true } },
          {
              path: 'monitor',
              name: 'Monitor',
              component: Monitor,
              meta: { requiresAuth: true },
          },
          // 通知相关路由
          { 
            path: 'notifications', 
            name: 'Notifications', 
            component: NotificationHistory, 
            meta: { requiresAuth: true, title: '通知历史'}
          },
        ],
    },
    {
        path: '/login',
        name: 'Login',
        component: Login,
        meta: { requiresAuth: false }
    },
    {
        path: '/register',
        name: 'Register',
        component: Register,
        meta: { requiresAuth: false }
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

// 路由守卫
router.beforeEach((to, _from, next) => {
    const authStore = useAuthStore();
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth);

    if (requiresAuth && !authStore.isAuthenticated) {
        next('/login');
    } else {
        next();
    }
});

export default router;