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
import BuyPremiumView from '../views/UserBuyPremiumView.vue';
import AddContent from '../views/AddContentView.vue';
import AddModule from '../views/AddModuleView.vue';
import AddTopic from '../views/AddTopicView.vue';
import GenerateQuiz from '../views/GenerateQuizView.vue';
import Lesson from '../views/UserLessonView.vue';
import Module from '../views/UserModuleView.vue';
import Topic from '../views/UserTopicView.vue';
import Awareness from '../views/UserAwarenessView.vue';
import AddExpense from '../views/UserAddExpenseView.vue';
import ExpenseInterface from '../views/USerExpenseInterfaceView.vue';
import ExpenseTracker from '../views/UserExpenseTrackerView.vue';
import store from '../store';
import UserQuizView from '../views/UserQuizView.vue';
import ExamInterface from '../views/UserExamInterface.vue';
import ChatBotPage from '../views/ChatBotPage.vue';
import Calculator from '../views/CalculatorView.vue'
import RegularCalculator from '../views/RegularCalculatorView.vue'
import CustomCalculatorInterest from '../views/CustomCalculatorInterestView.vue'
import CustomCalculatorLoancompare from '../views/CustomCalculatorLoancompareView.vue'

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
  { path: '/quiz', name: 'UserQuizView', component: UserQuizView, meta: { requiresAuth: true, role: 'user' }},
  { path: '/exam/:quizId/:accessToken', name: 'UserExamInterface', component: ExamInterface, meta: { requiresAuth: true, role: 'user' } },
  { path: '/chatbot', name: 'ChatBotPage', component: ChatBotPage, meta: { requiresAuth: true, role: 'user' } },
  { path: '/calculator', name: 'Calculator', component: Calculator, meta: { requiresAuth: true, role: 'user' } }, 
  { path: '/regular-calculator', name: 'RegularCalculator', component: RegularCalculator, meta: { requiresAuth: true, role: 'user' } },   
  { path: '/custom-calculator-interest', name: 'CustomCalculatorInterest', component: CustomCalculatorInterest, meta: { requiresAuth: true, role: 'user' } }, 
  { path: '/custom-calculator-loancompare', name: 'CustomCalculatorLoancompare', component: CustomCalculatorLoancompare, meta: { requiresAuth: true, role: 'user' } },    
  



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