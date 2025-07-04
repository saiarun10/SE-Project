import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import AboutView from '../views/AboutView.vue'
import ContactView from '../views/ContactView.vue'
import AdminDashboard from '../views/AdminDashboard.vue';
import UserDashboard from '../views/UserDashboard.vue';
import LoginView from '../views/Login.vue';
import SignupView from '../views/Signup.vue';
import ProfileView from '../views/Profile.vue';
import UserSummaryView from '../views/UserSummary.vue';
import BuyPremiumView from '../views/BuyPremium.vue';
import AddContent from '../views/AddContent.vue';
import AddModule from '../views/AddModule.vue';
import AddTopic from '../views/AddTopic.vue';
import GenerateQuiz from '../views/GenerateQuiz.vue';
import Lesson from '../views/Lesson.vue';
import Module from '../views/Module.vue';
import Topic from '../views/Topic.vue';
import Awareness from '../views/Awareness.vue';
import AddExpense from '../views/AddExpense.vue';
import ExpenseInterface from '../views/ExpenseInterface.vue';
import ExpenseTracker from '../views/ExpenseTracker.vue';
import store from '../store';
import QuizView from '../views/QuizView.vue';
import ExamInterface from '../views/ExamInterface.vue';

const routes = [
  { path: '/', name: 'Home', component: HomeView },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: HomeView },
  { path: '/about', name: 'About', component: AboutView },
  { path: '/contact', name: 'Contact', component: ContactView },
  { path: '/login', name: 'Login', component: LoginView },
  { path: '/signup', name: 'Signup', component: SignupView },


  { path: '/user-dashboard',name: 'UserDashboard',component: UserDashboard,meta: { requiresAuth: true, role: 'user' },},
  { path: '/admin-dashboard',name: 'AdminDashboard',component: AdminDashboard,meta: { requiresAuth: true, role: 'admin' },},

  { path: '/profile',name: 'Profile',component: ProfileView,meta: { requiresAuth: true},},
  { path: '/buy-premium',name: 'BuyPremium', component: BuyPremiumView,meta: { requiresAuth: true, role: 'user' },},
  { path: '/user-summary',name: 'UserSummary',component: UserSummaryView,meta: { requiresAuth: true, role: 'user' },},
  { path: '/lesson',  name: 'Lesson', component: Lesson, meta: { requiresAuth: true, role: 'user' }},
  { path: '/lesson/:id',name: 'Module',  component: Module, meta: { requiresAuth: true, role: 'user' }, props: true },
  { path: '/lessons/:lessonId/:topicId/learn_topic',name: 'LearnTopic', component: Topic, meta: { requiresAuth: true, role: 'user' }, props: true },
  { path: '/awareness', name: 'Awareness', component: Awareness, meta: { requiresAuth: true, role: 'user' } },
  { path: '/add-expense', name: 'AddExpense', component: AddExpense, meta: { requiresAuth: true, role: 'user' } },
  { path: '/expense-interface', name: 'ExpenseInterface', component: ExpenseInterface, meta: { requiresAuth: true, role: 'user' } },
  { path: '/expense-tracker', name: 'ExpenseTracker', component: ExpenseTracker, meta: { requiresAuth: true, role: 'user' } },

  { path: '/add-module', name: 'AddModule', component: AddModule, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/add-topic', name: 'AddTopic', component: AddTopic, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/add-content', name: 'AddContent', component: AddContent, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/generate-quiz', name: 'GenerateQuiz', component: GenerateQuiz, meta: { requiresAuth: true, role: 'admin' } },

];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters.isAuthenticated;
  const userRole = store.getters.userRole;

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'Home' });
  } else if (to.meta.role && to.meta.role !== userRole) {
    next({ name: 'Home' });
  } else {
    next();
  }
});

export default router;