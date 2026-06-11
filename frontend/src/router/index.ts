import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    // Admin routes
    {
      path: '/admin/login',
      name: 'admin-login',
      component: () => import('../views/admin/AdminLoginView.vue'),
    },
    {
      path: '/admin',
      component: () => import('../views/admin/AdminLayout.vue'),
      meta: { requiresAdminAuth: true },
      children: [
        {
          path: '',
          redirect: '/admin/posts',
        },
        {
          path: 'posts',
          name: 'admin-posts',
          component: () => import('../views/admin/AdminPostsView.vue'),
        },
        {
          path: 'reports',
          name: 'admin-reports',
          component: () => import('../views/admin/AdminReportsView.vue'),
        },
        {
          path: 'statistics',
          name: 'admin-statistics',
          component: () => import('../views/admin/AdminStatisticsView.vue'),
        },
        {
          path: 'nlp-feedback',
          name: 'admin-nlp-feedback',
          component: () => import('../views/admin/AdminNlpFeedbackView.vue'),
        },
      ],
    },
  ],
});

// Navigation guard for admin auth
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('admin_token');

  if (to.name === 'admin-login') {
    if (token) {
      next({ name: 'admin-posts' });
      return;
    }
    next();
    return;
  }

  if (to.meta.requiresAdminAuth || to.path.startsWith('/admin')) {
    if (!token) {
      next({ name: 'admin-login' });
      return;
    }
  }
  next();
});
