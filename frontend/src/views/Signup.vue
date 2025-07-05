<template>
  <div class="min-vh-100 d-flex flex-column">
    <AppNavbar />
    <main class="flex-grow-1 d-flex align-items-center justify-content-center py-5 px-3">
      <div class="container">
        <div class="row justify-content-center">
          <div class="col-12 col-md-10 col-lg-7">
            <div class="card shadow-lg border-0 rounded-4 p-5 p-md-6" style="background-color: #f8f9fa;">
              <h2 class="text-center mb-5 fw-bold text-dark" style="font-size: 2rem;">Create Your Account</h2>
              <form @submit.prevent="handleSignup">
                <div class="row g-4">
                  <div class="col-12 col-md-6">
                    <label for="email" class="form-label fw-medium text-dark" style="font-size: 1.1rem;">Email Address <span class="text-danger">*</span></label>
                    <input
                      id="email"
                      v-model="form.email"
                      type="email"
                      class="form-control rounded-3 hover-input"
                      placeholder="Enter your email"
                      required
                      style="font-size: 1.1rem; padding: 0.75rem;"
                      @input="validateEmail"
                    />
                    <div v-if="errors.email" class="text-danger small mt-2">{{ errors.email }}</div>
                  </div>
                  <div class="col-12 col-md-6">
                    <label for="username" class="form-label fw-medium text-dark" style="font-size: 1.1rem;">Username <span class="text-danger">*</span></label>
                    <input
                      id="username"
                      v-model="form.username"
                      type="text"
                      class="form-control rounded-3 hover-input"
                      placeholder="Choose a username"
                      required
                      style="font-size: 1.1rem; padding: 0.75rem;"
                      @input="validateUsername"
                    />
                    <div v-if="errors.username" class="text-danger small mt-2">{{ errors.username }}</div>
                  </div>
                </div>
                <div class="row g-4 mt-3">
                  <div class="col-12 col-md-6">
                    <label for="password" class="form-label fw-medium text-dark" style="font-size: 1.1rem;">Password <span class="text-danger">*</span></label>
                    <div class="position-relative">
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
                      <span v-if="passwordsMatch" class="position-absolute top-50 end-0 translate-middle-y me-3 text-success" style="font-size: 1.2rem;">
                        ✔
                      </span>
                    </div>
                    <div v-if="errors.password" class="text-danger small mt-2">{{ errors.password }}</div>
                  </div>
                  <div class="col-12 col-md-6">
                    <label for="confirm_password" class="form-label fw-medium text-dark" style="font-size: 1.1rem;">Confirm Password <span class="text-danger">*</span></label>
                    <div class="position-relative">
                      <input
                        id="confirm_password"
                        v-model="form.confirm_password"
                        type="password"
                        class="form-control rounded-3 hover-input"
                        placeholder="Confirm your password"
                        required
                        style="font-size: 1.1rem; padding: 0.75rem;"
                        @input="validateConfirmPassword"
                      />
                      <span v-if="passwordsMatch" class="position-absolute top-50 end-0 translate-middle-y me-3 text-success" style="font-size: 1.2rem;">
                        ✔
                      </span>
                    </div>
                    <div v-if="errors.confirm_password" class="text-danger small mt-2">{{ errors.confirm_password }}</div>
                  </div>
                </div>
                <div class="row g-4 mt-3">
                  <div class="col-12 col-md-6">
                    <label for="full_name" class="form-label fw-medium text-dark" style="font-size: 1.1rem;">Full Name</label>
                    <input
                      id="full_name"
                      v-model="form.full_name"
                      type="text"
                      class="form-control rounded-3 hover-input"
                      placeholder="Enter your full name (optional)"
                      style="font-size: 1.1rem; padding: 0.75rem;"
                    />
                  </div>
                  <div class="col-12 col-md-6">
                    <label for="birth_date" class="form-label fw-medium text-dark" style="font-size: 1.1rem;">Birth Date <span class="text-danger">*</span></label>
                    <input
                      id="birth_date"
                      v-model="form.birth_date"
                      type="date"
                      class="form-control rounded-3 hover-input"
                      required
                      style="font-size: 1.1rem; padding: 0.75rem;"
                      @change="validateBirthDate"
                    />
                    <div v-if="errors.birth_date" class="text-danger small mt-2">{{ errors.birth_date }}</div>
                    <p v-if="age !== null" class="small text-muted mt-2" style="font-size: 1rem;">
                      Age: {{ age }} {{ age === 1 ? 'year' : 'years' }} 
                    </p>
                  </div>
                </div>
                <div class="row g-4 mt-3">
                  <div class="col-12 col-md-6">
                    <label for="gender" class="form-label fw-medium text-dark" style="font-size: 1.1rem;">Gender <span class="text-danger">*</span></label>
                    <select
                      id="gender"
                      v-model="form.gender"
                      class="form-select rounded-3 hover-input"
                      required
                      style="font-size: 1.1rem; padding: 0.75rem;"
                      @change="validateGender"
                    >
                      <option value="" disabled>Select Gender</option>
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                      <option value="other">Other</option>
                    </select>
                    <div v-if="errors.gender" class="text-danger small mt-2">{{ errors.gender }}</div>
                  </div>
                  <div class="col-12 col-md-6">
                    <label for="parent_email" class="form-label fw-medium text-dark" style="font-size: 1.1rem;">Parent Email</label>
                    <input
                      id="parent_email"
                      v-model="form.parent_email"
                      type="email"
                      class="form-control rounded-3 hover-input"
                      placeholder="Enter parent email (optional)"
                      style="font-size: 1.1rem; padding: 0.75rem;"
                      @input="validateParentEmail"
                    />
                    <div v-if="errors.parent_email" class="text-danger small mt-2">{{ errors.parent_email }}</div>
                  </div>
                </div>

                <Alert v-if="alert.message" :message="alert.message" :type="alert.type" @close="alert.message = ''" />

                <div class="d-grid mt-5">
                  <button
                    type="submit"
                    class="btn btn-primary rounded-3 hover-button"
                    :disabled="loading || hasErrors || form.password !== form.confirm_password"
                    style="font-size: 1.2rem; padding: 0.75rem; background-color: #4b5efc; border-color: #4b5efc;"
                  >
                    <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Sign Up
                  </button>
                </div>
              </form>
              <div class="text-center mt-4">
                <p class="mb-0 small text-muted" style="font-size: 1rem;">
                  Already have an account? 
                  <router-link to="/login" class="text-primary hover-link">log in</router-link>
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
  name: 'SignupView',
  components: {
    AppNavbar,
    AppFooter,
    Alert,
  },
  setup() {
    const store = useStore();
    const router = useRouter();
    const form = ref({
      email: '',
      username: '',
      password: '',
      confirm_password: '',
      full_name: '',
      birth_date: '',
      gender: '',
      parent_email: '',
    });
    const alert = ref({
      message: '',
      type: 'error',
    });
    const loading = ref(false);
    const age = ref(null);
    const errors = ref({
      email: '',
      username: '',
      password: '',
      confirm_password: '',
      birth_date: '',
      gender: '',
      parent_email: '',
    });

    const passwordsMatch = computed(() => {
      return form.value.password && form.value.password === form.value.confirm_password && form.value.password.length >= 6;
    });

    const validateEmail = () => {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      errors.value.email = form.value.email && !emailRegex.test(form.value.email) ? 'Please enter a valid email address' : '';
    };

    const validateUsername = () => {
      errors.value.username = form.value.username.length < 3 ? 'Username must be at least 3 characters long' : '';
    };

    const validatePassword = () => {
      errors.value.password = form.value.password.length < 6 ? 'Password must be at least 6 characters long' : '';
      validateConfirmPassword();
    };

    const validateConfirmPassword = () => {
      errors.value.confirm_password = form.value.confirm_password && form.value.confirm_password !== form.value.password ? 'Passwords do not match' : '';
    };

    const validateBirthDate = () => {
      if (form.value.birth_date) {
        const birthDate = new Date(form.value.birth_date);
        const today = new Date();
        errors.value.birth_date = birthDate > today ? 'Birth date cannot be in the future' : '';
        calculateAge();
      } else {
        errors.value.birth_date = 'Birth date is required';
        age.value = null;
      }
    };

    const validateGender = () => {
      errors.value.gender = !form.value.gender ? 'Please select a gender' : '';
    };

    const validateParentEmail = () => {
      if (form.value.parent_email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        errors.value.parent_email = !emailRegex.test(form.value.parent_email) ? 'Please enter a valid email address' : '';
      } else {
        errors.value.parent_email = '';
      }
    };

    const calculateAge = () => {
      if (form.value.birth_date && !errors.value.birth_date) {
        const today = new Date();
        const birthDate = new Date(form.value.birth_date);
        let calculatedAge = today.getFullYear() - birthDate.getFullYear();
        const monthDiff = today.getMonth() - birthDate.getMonth();
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
          calculatedAge--;
        }
        age.value = calculatedAge;
      } else {
        age.value = null;
      }
    };

    const hasErrors = computed(() => {
      return Object.values(errors.value).some(error => error !== '') || !form.value.email || !form.value.username || !form.value.password || !form.value.confirm_password || !form.value.birth_date || !form.value.gender;
    });

    const handleSignup = async () => {
      validateEmail();
      validateUsername();
      validatePassword();
      validateConfirmPassword();
      validateBirthDate();
      validateGender();
      validateParentEmail();

      if (hasErrors.value) {
        alert.value.message = 'Please fix the errors in the form';
        alert.value.type = 'error';
        return;
      }

      loading.value = true;
      alert.value.message = '';
      try {
        await axios.post(`${BASE_URL}/signup`, {
          email: form.value.email,
          username: form.value.username,
          password: form.value.password,
          full_name: form.value.full_name,
          birth_date: form.value.birth_date,
          gender: form.value.gender,
          parent_email: form.value.parent_email,
        });
        alert.value = { message: 'Signup successful! Please log in.', type: 'success' };
        setTimeout(() => {
          router.push('/login');
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
      age,
      errors,
      passwordsMatch,
      calculateAge,
      validateEmail,
      validateUsername,
      validatePassword,
      validateConfirmPassword,
      validateBirthDate,
      validateGender,
      validateParentEmail,
      handleSignup,
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