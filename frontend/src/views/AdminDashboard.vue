<template>
  <Navbar />
  <div>
    <div class="container py-5">
      <!-- Header -->
      <h1 class="fs-4 fw-bold mb-4">Hey Admin, Welcome</h1>

      <!-- Summary Section -->
      <section class="bg-light p-4 rounded shadow-sm mb-5">
        <h2 class="fs-5 fw-semibold mb-4">Summary</h2>
        <div class="row g-4">
          <div class="col-12 col-sm-6 col-md-4" v-for="(item, index) in summaryData" :key="index">
            <div class="text-white text-center p-3 rounded shadow-sm" :style="{ backgroundColor: '#6B4B4B' }">
              <div class="small">{{ item.label }}</div>
              <div class="fs-5 fw-bold mt-2">{{ item.value }}</div>
            </div>
          </div>
        </div>
      </section>

      <!-- Manage Section -->
      <section class="bg-light p-4 rounded shadow-sm">
        <h2 class="fs-5 fw-semibold mb-4">Manage Learning and Content Section</h2>
        <div class="d-flex flex-wrap justify-content-center gap-3">
          <router-link to="/NewModule" class="text-decoration-none">
            <button class="btn btn-outline-secondary rounded-circle d-flex align-items-center justify-content-center shadow-sm" style="width: 130px; height: 130px;">
              ADD Modules
            </button>
          </router-link>

          <router-link to="/new_topics" class="text-decoration-none">
            <button class="btn btn-outline-secondary rounded-circle d-flex align-items-center justify-content-center shadow-sm" style="width: 130px; height: 130px;">
              ADD Topics in Module
            </button>
          </router-link>

          <router-link to="/add_content" class="text-decoration-none">
            <button class="btn btn-outline-secondary rounded-circle d-flex align-items-center justify-content-center shadow-sm" style="width: 130px; height: 130px;">
              ADD Content
            </button>
          </router-link>

          <router-link to="/generate_quiz" class="text-decoration-none">
            <button class="btn btn-outline-secondary rounded-circle d-flex align-items-center justify-content-center shadow-sm" style="width: 130px; height: 130px;">
              Generate Quiz
            </button>
          </router-link>
        </div>
      </section>
    </div>

    <AppFooter />
  </div>
</template>

<script>
import AppFooter from '../components/Footer.vue'
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
        { label: 'Total Registered Users', value: 550 },
        { label: 'Daily Active Users', value: 220 },
        { label: 'Average Daily Time Spent', value: '30 Minutes' },
        { label: 'Average Quiz Score', value: 50 },
        { label: 'Average Quiz Time', value: '30 Min' },
        { label: 'Number of Quiz on App', value: 35 },
      ]
    }
  }
}
</script>

<style scoped>
/* Optional hover effect for buttons */
.btn:hover {
  background-color: #e2e6ea;
}
</style>
