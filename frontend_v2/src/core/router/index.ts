import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';
import PackingPage from '../../views/PackingPage.vue';
import AdminLayout from '../layouts/AdminLayout.vue';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Packing',
    component: PackingPage,
  },
  {
    path: '/admin',
    component: AdminLayout,
    children: [
      {
        path: '',
        name: 'AdminDashboard',
        component: () => import('../../views/admin/DashboardPage.vue'),
      },
      {
        path: 'customers',
        name: 'CustomerManagement',
        component: () => import('../../views/admin/CustomerManagementPage.vue'),
      },
      {
        path: 'products',
        name: 'ProductManagement',
        component: () => import('../../views/admin/ProductManagementPage.vue'),
      },
      {
        path: 'history',
        name: 'CartonHistory',
        component: () => import('../../views/admin/CartonHistoryPage.vue'),
      },
      {
        path: 'stats',
        name: 'SNLookup',
        component: () => import('../../views/admin/SNLookupPage.vue'),
      },
    ]
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('../../views/admin/LoginPage.vue'),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, _from, next) => {
  // Check for admin routes
  if (to.path.startsWith('/admin')) {
    // Allow access to login page
    if (to.name === 'AdminLogin') {
      next();
      return;
    }

    const isAuthenticated = sessionStorage.getItem('admin_session') === 'true';
    if (isAuthenticated) {
      next();
    } else {
      // Redirect to login with the original target path
      next({ name: 'AdminLogin', query: { redirect: to.fullPath } });
    }
  } else {
    // If navigating back to packing (root), clear admin session
    if (to.path === '/') {
      sessionStorage.removeItem('admin_session');
    }
    next();
  }
});

export default router;
