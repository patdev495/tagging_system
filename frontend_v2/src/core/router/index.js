import { createRouter, createWebHistory } from 'vue-router';
import PackingPage from '../../views/PackingPage.vue';
import AdminLayout from '../layouts/AdminLayout.vue';

const routes = [
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
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
