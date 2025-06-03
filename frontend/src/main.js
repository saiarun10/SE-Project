// main.js
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import store from './store';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import bootstrap from 'bootstrap/dist/js/bootstrap.bundle.min.js';
import 'bootstrap';
import 'chart.js';


const BASE_URL = `${import.meta.env.VITE_BASE_URL}/api`;

axios.interceptors.request.use(config => {
  const token = config.url.includes('/refresh') ? store.state.refresh_token : store.state.access_token;
  console.log('Interceptor - Request URL:', config.url);
//   console.log('Interceptor - Adding token:', token);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  } else {
    console.warn('Interceptor - No token available for:', config.url);
  }
  return config;
}, error => {
  console.error('Interceptor - Request error:', error);
  return Promise.reject(error);
});

axios.interceptors.response.use(
  response => {
    return response;
  },
  async error => {
    console.error('Interceptor - Error:', error.response?.status, error.response?.data);
    const originalRequest = error.config;

    // Skip refresh for login endpoints or if already retried
    if (error.response?.status === 401 && 
        !originalRequest._retry && 
        !originalRequest.url.includes('/login/user') && 
        !originalRequest.url.includes('/login/admin')) {
      originalRequest._retry = true;
      try {
        const newToken = await store.dispatch('refreshToken');
        console.log('Interceptor - New token:', newToken);
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return axios(originalRequest);
      } catch (refreshError) {
        console.error('Interceptor - Refresh failed:', refreshError);
        store.commit('clearAuth');
        router.push('/login');
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

const app = createApp(App);
app.use(router);
app.use(store);
app.mount('#app');