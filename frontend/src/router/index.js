import { createRouter, createWebHistory } from 'vue-router';
import store from '@/store';
import Home from '@/components/Home.vue';
import About from '@/components/About.vue';
// import Login from '@/components/Login.vue';
// import Signup from '@/components/Signup.vue';
// import AdminDashboard from '@/components/AdminDashboard.vue';
// import UserDashboard from '@/components/UserDashboard.vue';

const routes = [
  { path: '/', component: Home, name: 'Home' },
  { path: '/about', component: About, name: 'About' },
  // { path: '/login', component: Login, name: 'Login' },
  // { path: '/signup', component: Signup, name: 'Signup' },
  // {
  //   path: '/admin-dashboard',
  //   component: AdminDashboard,
  //   meta: { requiresAuth: true, role: 'admin' },
  //   name: 'AdminDashboard',
  // },
  // {
  //   path: '/user-dashboard',
  //   component: UserDashboard,
  //   meta: { requiresAuth: true, role: 'user' },
  //   name: 'UserDashboard',
  // },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// router.beforeEach((to, from, next) => {
//   const isAuthenticated = store.state.access_token;
//   const userRole = store.state.user.user_role || 'user';

//   // Prevent authenticated users from accessing public routes
//   if (isAuthenticated && (to.name === 'Login' || to.name === 'Signup' || to.name === 'Home')) {
//     const redirectPath = userRole === 'admin' ? '/admin-dashboard' : '/user-dashboard';
//     if (to.path !== redirectPath) {
//       next(redirectPath);
//     } else {
//       next();
//     }
//   }
//   // Handle protected routes
//   else if (to.meta.requiresAuth) {
//     if (!isAuthenticated) {
//       next({ path: '/login', query: { redirect: to.fullPath } });
//     } else if (to.meta.role && to.meta.role !== userRole) {
//       next(userRole === 'admin' ? '/admin-dashboard' : '/user-dashboard');
//     } else {
//       next();
//     }
//   }
//   // Allow public routes
//   else {
//     next();
//   }
// });

export default router;