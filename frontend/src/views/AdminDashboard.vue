<template>
  <div class="d-flex flex-column min-vh-100">
    <Navbar />
    <main class="flex-grow-1">
      <div class="container px-3 py-5">
        <!-- Header -->
        <h2 class="h1 fw-bold mb-5 text-brown-900">Welcome, Admin</h2>
        
        <!-- Summary Section -->
        <section class="mb-5">
          <h2 class="h3 fw-semibold mb-4 text-brown-900">Overview</h2>
          <div class="row g-4">
            <!-- Loading State -->
            <div v-if="isLoading" class="col-12 text-center text-brown-900">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <p class="mt-2">Fetching latest statistics...</p>
            </div>
            
            <!-- Data Display -->
            <div v-else class="col-12 col-sm-6 col-md-4" v-for="(item, index) in summaryData" :key="index">
              <div class="card text-center p-4 transition-all hover-scale-110 hover-shadow-lg text-brown-100 bg-brown-600">
                <div class="fw-medium">{{ item.label }}</div>
                <div class="h2 fw-bold mt-3">{{ item.value }}</div>
              </div>
            </div>
          </div>
        </section>

        <!-- Manage Section -->
        <section>
          <h2 class="h3 fw-semibold mb-4 text-brown-900">Manage Learning Content</h2>
          <div class="d-flex flex-wrap justify-content-center gap-4">
            <router-link to="/add-module" class="text-decoration-none">
              <button class="btn btn-outline-brown rounded-circle d-flex flex-column align-items-center justify-content-center transition-all hover-scale-105 hover-shadow hover-bg-brown-100">
                <span class="fs-5 text-brown-900 fw-medium">Add Modules</span>
                <span class="mt-2"><i class="fas fa-hand-pointer"></i></span>
              </button>
            </router-link>

            <router-link to="/add-topic" class="text-decoration-none">
              <button class="btn btn-outline-brown rounded-circle d-flex flex-column align-items-center justify-content-center transition-all hover-scale-105 hover-shadow hover-bg-brown-100">
                <span class="fs-5 text-brown-900 fw-medium">Add Topics</span>
                <span class="mt-2"><i class="fas fa-hand-pointer"></i></span>
              </button>
            </router-link>

            <router-link to="/add-content" class="text-decoration-none">
              <button class="btn btn-outline-brown rounded-circle d-flex flex-column align-items-center justify-content-center transition-all hover-scale-105 hover-shadow hover-bg-brown-100">
                <span class="fs-5 text-brown-900 fw-medium">Add Content</span>
                <span class="mt-2"><i class="fas fa-hand-pointer"></i></span>
              </button>
            </router-link>

            <router-link to="/generate-quiz" class="text-decoration-none">
              <button class="btn btn-outline-brown rounded-circle d-flex flex-column align-items-center justify-content-center transition-all hover-scale-105 hover-shadow hover-bg-brown-100">
                <span class="fs-5 text-brown-900 fw-medium">Generate Quiz</span>
                <span class="mt-2"><i class="fas fa-hand-pointer"></i></span>
              </button>
            </router-link>
          </div>
        </section>
      </div>
    </main>
    <AppFooter />
  </div>
</template>

<script>
import AppFooter from '../components/Footer.vue';
import Navbar from '../components/Navbar.vue';
import axios from 'axios';

export default {
  name: 'AdminDashboard',
  components: {
    AppFooter,
    Navbar
  },
  data() {
    return {
      isLoading: true,
      summaryData: []
    };
  },
  methods: {
    async fetchSummaryData() {
      this.isLoading = true;
      try {
        // Updated API endpoint to match the backend
        const response = await axios.get(`${import.meta.env.VITE_BASE_URL}/api/admin_dashboard_summary`, {
          headers: { Authorization: `Bearer ${this.$store.state.token}` }
        });
        
        const data = response.data;
        
        // Map API response to the data structure required by the template
        this.summaryData = [
          { label: 'Total Registered Users', value: data.total_users },
          { label: 'Daily Active Users', value: data.daily_active_users },
          { label: 'Avg. Session Duration', value: data.avg_session_duration },
          { label: 'Average Quiz Score', value: data.avg_quiz_score },
          { label: 'Average Quiz Time', value: data.avg_quiz_time },
          { label: 'Total Quizzes', value: data.total_quizzes },
        ];
      } catch (error) {
        console.error("Failed to fetch dashboard summary:", error.response?.data || error.message);
        // Provide fallback data on error for a better user experience
        this.summaryData = [
          { label: 'Total Registered Users', value: 'N/A' },
          { label: 'Daily Active Users', value: 'N/A' },
          { label: 'Avg. Session Duration', value: 'N/A' },
          { label: 'Average Quiz Score', value: 'N/A' },
          { label: 'Average Quiz Time', value: 'N/A' },
          { label: 'Total Quizzes', value: 'N/A' },
        ];
        // You could also add an alert here to notify the admin of the failure
      } finally {
        this.isLoading = false;
      }
    }
  },
  mounted() {
    this.fetchSummaryData();
  }
};
</script>

<style scoped>
/* Original color palette */
.bg-brown-600 {
  background-color: #6B4B4B;
}
.bg-brown-100 {
  background-color: #F5E8E4;
}
.text-brown-900 {
  color: #3C2F2F;
}
.text-brown-100 {
  color: #F5E8E4;
}
.btn-outline-brown {
  border-color: #6B4B4B;
  color: #6B4B4B;
}
.hover-bg-brown-100:hover {
  background-color: #F5E8E4;
}

/* Smooth transitions and hover effects */
.transition-all {
  transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out, background-color 0.3s ease-in-out;
}
.hover-scale-105:hover {
  transform: scale(1.05);
}
.hover-scale-110:hover {
  transform: scale(1.10);
}
.hover-shadow:hover {
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}
.hover-shadow-lg:hover {
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.3);
}

/* Card styling */
.card {
  border: none;
  border-radius: 0.5rem;
  min-height: 180px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

/* Button styling */
.btn {
  width: 160px;
  height: 160px;
  padding: 1rem;
}

/* Font Awesome icon styling */
.fas {
  font-size: 1.75rem;
  color: #3C2F2F;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .container {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  .h1 { font-size: 2.25rem; }
  .h3 { font-size: 1.5rem; }
  .h2 { font-size: 1.75rem; }
  .btn {
    width: 140px;
    height: 140px;
    font-size: 0.9rem;
  }
}

@media (max-width: 576px) {
  .h1 { font-size: 1.75rem; }
  .h3 { font-size: 1.25rem; }
  .h2 { font-size: 1.5rem; }
  .btn {
    width: 120px;
    height: 120px;
    font-size: 0.85rem;
  }
}

/* Ensure content is centered and responsive */
.container {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
