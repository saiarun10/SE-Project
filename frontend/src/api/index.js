import axios from 'axios';
import store from '@/store';

const BASE_URL = `${import.meta.env.VITE_BASE_URL}/api`;

const apiClient = axios.create({
  baseURL: BASE_URL || 'http://localhost:5000/api', // Fallback URL
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to include the JWT token
apiClient.interceptors.request.use(
  (config) => {
    const token = store.state.access_token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default apiClient;