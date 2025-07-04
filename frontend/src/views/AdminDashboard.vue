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
            <div class="col-12 col-sm-6 col-md-4" v-for="(item, index) in summaryData" :key="index">
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

export default {
  name: 'AdminDashboard',
  components: {
    AppFooter,
    Navbar
  },
  data() {
    return {
      summaryData: [
        { label: 'Total Registered Users', value: '550' },
        { label: 'Daily Active Users', value: '220' },
        { label: 'Average Daily Time Spent', value: '30 Minutes' },
        { label: 'Average Quiz Score', value: '50' },
        { label: 'Average Quiz Time', value: '30 Min' },
        { label: 'Number of Quizzes', value: '35' },
      ]
    };
  },
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
  .display-4 {
    font-size: 2rem;
  }
  .h3 {
    font-size: 1.5rem;
  }
  .h2 {
    font-size: 1.75rem;
  }
  .btn {
    width: 140px;
    height: 140px;
    font-size: 0.9rem;
  }
}

@media (max-width: 576px) {
  .display-4 {
    font-size: 1.5rem;
  }
  .h3 {
    font-size: 1.25rem;
  }
  .h2 {
    font-size: 1.5rem;
  }
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