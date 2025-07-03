<template>
  <div class="min-vh-100 d-flex flex-column">
    <AppNavbar />
    <main class="flex-grow-1 d-flex align-items-center justify-content-center py-5 px-3">
      <div class="container">
        <div class="row justify-content-center">
          <div class="col-12 col-md-8 col-lg-5">
            <div class="card shadow-lg border-0 rounded-4 p-5 p-md-6" style="background-color: #f8f9fa;">
              <h2 class="text-center mb-5 fw-bold text-dark" style="font-size: 2rem;">Log In to Your Account</h2>
              <form @submit.prevent="handleLogin">
                <div class="row g-4">
                  <div class="col-12">
                    <label for="username" class="form-label fw-medium text-dark" style="font-size: 1.1rem;">Username <span class="text-danger">*</span></label>
                    <input
                      id="username"
                      v-model="form.username"
                      type="text"
                      class="form-control rounded-3 hover-input"
                      placeholder="Enter your username"
                      required
                      style="font-size: 1.1rem; padding: 0.75rem;"
                      @input="validateUsername"
                    />
                    <div v-if="errors.username" class="text-danger small mt-2">{{ errors.username }}</div>
                  </div>
                  <div class="col-12">
                    <label for="password" class="form-label fw-medium text-dark" style="font-size: 1.1rem;">Password <span class="text-danger">*</span></label>
                    <input
                      id="password"
                      v-model="form.password"
                      type="password"
                      class="form-control rounded-3 hover-input"
                      placeholder="Enter your password"
                      required
                      style="font-size: 1.1rem; padding: 0.75rem;"
                      @input="validatePassword"
                    />
                    <div v-if="errors.password" class="text-danger small mt-2">{{ errors.password }}</div>
                  </div>
                </div>

                <Alert v-if="alert.message" :message="alert.message" :type="alert.type" @close="alert.message = ''" />

                <div class="d-grid mt-5">
                  <button
                    type="submit"
                    class="btn btn-primary rounded-3 hover-button"
                    :disabled="loading || hasErrors"
                    style="font-size: 1.2rem; padding: 0.75rem; background-color: #4b5efc; border-color: #4b5efc;"
                  >
                    <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Sign In
                  </button>
                </div>
              </form>
              <div class="text-center mt-4">
                <p class="mb-0 small text-muted" style="font-size: 1rem;">
                  Don't have an account? 
                  <router-link to="/signup" class="text-primary hover-link">Sign up</router-link>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
    <AppFooter />
  </div>
</template>

<script>
import axios from 'axios';
import { useStore } from 'vuex';
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import AppNavbar from '../components/Home_Navbar.vue';
import AppFooter from '../components/Footer.vue';
import Alert from '@/components/Alert.vue';

const BASE_URL = `${import.meta.env.VITE_BASE_URL}/api`;

export default {
  name: 'LoginView',
  components: {
    AppNavbar,
    AppFooter,
    Alert,
  },
  setup() {
    const store = useStore();
    const router = useRouter();
    const form = ref({
      username: '',
      password: '',
    });
    const alert = ref({
      message: '',
      type: 'error',
    });
    const loading = ref(false);
    const errors = ref({
      username: '',
      password: '',
    });

    const validateUsername = () => {
      errors.value.username = form.value.username.length < 3 ? 'Username must be at least 3 characters long' : '';
    };

    const validatePassword = () => {
      errors.value.password = form.value.password.length < 6 ? 'Password must be at least 6 characters long' : '';
    };

    const hasErrors = computed(() => {
      return Object.values(errors.value).some(error => error !== '') || !form.value.username || !form.value.password;
    });

    const handleLogin = async () => {
      validateUsername();
      validatePassword();

      if (hasErrors.value) {
        alert.value.message = 'Please fix the errors in the form';
        alert.value.type = 'error';
        return;
      }

      loading.value = true;
      alert.value.message = '';
      try {
        const response = await axios.post(`${BASE_URL}/login`, form.value);
        await store.dispatch('login', {
          token: response.data.access_token,
          user: response.data.user,
        });
        alert.value = { message: 'Login successful', type: 'success' };
        setTimeout(() => {
          const route = response.data.user.user_role === 'admin' ? '/admin-dashboard' : '/user-dashboard';
          router.push(route);
        }, 1500);
      } catch (error) {
        alert.value.message = error.response?.data?.error || 'An unexpected error occurred';
        alert.value.type = 'error';
      } finally {
        loading.value = false;
      }
    };

    return {
      form,
      alert,
      loading,
      errors,
      validateUsername,
      validatePassword,
      handleLogin,
    };
  },
};
</script>

<style scoped>
/* Custom styles for professional, minimalist design with solid colors */
.card {
  background-color: #f8f9fa; /* Light gray background */
  border-radius: 1.2rem;
}

.form-control, .form-select {
  transition: all 0.3s ease;
}

.hover-input:hover {
  border-color: #ff6f61 !important; /* Coral hover */
  box-shadow: 0 0 15px rgba(255, 111, 97, 0.4);
  transform: scale(1.02);
}

.hover-input:focus {
  border-color: #ff6f61 !important;
  box-shadow: 0 0 15px rgba(255, 111, 97, 0.6);
  transform: scale(1.02);
}

.btn-primary {
  background-color: #4b5efc; /* Professional blue */
  border-color: #4b5efc;
}

.hover-button:hover:not(:disabled) {
  background-color: #0ed44a !important; /* Coral hover */
  border-color: #0ed44a !important;
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.hover-link:hover {
  color: #0ed44a !important; /* Coral hover */
  text-decoration: underline;
  transition: color 0.3s ease;
}

@media (max-width: 768px) {
  .container {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }
  .card {
    padding: 2rem;
  }
  .form-label {
    font-size: 1rem !important;
  }
  .form-control, .form-select {
    font-size: 1rem !important;
    padding: 0.65rem !important;
  }
  .btn-primary {
    font-size: 1.1rem !important;
    padding: 0.65rem !important;
  }
}
</style>