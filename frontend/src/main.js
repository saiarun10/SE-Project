import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import store from './store';

// Optimized imports for Bootstrap, Bootstrap Icons, Font Awesome, and Chart.js
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import 'bootstrap-icons/font/bootstrap-icons.css';
import '@fortawesome/fontawesome-free/css/all.min.css';
import 'chart.js/auto';

const app = createApp(App);

// Initialize authentication state before mounting
store.dispatch('initializeAuth').then(() => {
  app.use(store).use(router).mount('#app');
});