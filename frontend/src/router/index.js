import { createRouter, createWebHistory } from 'vue-router';
import store from '@/store';


const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to, from, next) => {
  const isAuthenticated = !!store.state.access_token;
  const userRole = store.state.role;

  if (to.meta.requiresAuth) {
    if (!isAuthenticated) {
      next('/login');
    } else if (to.meta.role && to.meta.role !== userRole) {
      next(userRole === 'admin' ? '/admin-dashboard' : '/user-dashboard');
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;