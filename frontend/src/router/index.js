import { createRouter, createWebHistory } from 'vue-router'
import UserDashboard from '@/components/UserDashboard.vue'
import CustomCalculatorPage from '@/components/CustomCalculatorPage.vue'
import LoanComparisonPage from '@/components/LoanComparisonPage.vue' 

const routes = [
  {
    path: '/',
    component: {
      template: '<div>Welcome! Click the button above to go to the dashboard.</div>'
    }
  },
  {
    path: '/user-dashboard',
    component: UserDashboard
  },
  { path: '/calculator', 
    component: CustomCalculatorPage 
  },
  { path: '/loan-comparison', 
    component: LoanComparisonPage 
  }

]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router




// import { createRouter, createWebHistory } from 'vue-router';
// import store from '@/store';
// import UserDashboard from '@/UserDashboard.vue'
// //import LoginPage from '@/components/LoginPage.vue' // assuming you have one
// //import AdminDashboard from '@/components/AdminDashboard.vue' // optional

// const routes = [
  
//   {
//     path: '/user-dashboard',
//     component: UserDashboard,
//     meta: { requiresAuth: true, role: 'user' }
//   },
//   {
//     path: '/',
//     redirect: '/user-dashboard'
//   }
// ]


// const router = createRouter({
//   history: createWebHistory(),
//   routes
// });

// router.beforeEach((to, from, next) => {
//   const isAuthenticated = !!store.state.access_token;
//   const userRole = store.state.role;

//   if (to.meta.requiresAuth) {
//     if (!isAuthenticated) {
//       next('/login');
//     } else if (to.meta.role && to.meta.role !== userRole) {
//       next(userRole === 'admin' ? '/admin-dashboard' : '/user-dashboard');
//     } else {
//       next();
//     }
//   } else {
//     next();
//   }
// });

// export default router;