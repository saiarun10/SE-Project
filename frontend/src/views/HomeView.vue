<template>
  <div>
    <!-- Navbar -->
    <AppNavbar />

    <!-- Heading Section (Above Image) -->
    <div class="text-center py-5">
      <h2 class="display-4 fw-bold text-dark">Welcome to <span class="text-primary">GrowUp Richie</span></h2>
      <p class="lead text-muted">
        A place where you learn to manage the money, save the money,
        and ultimately mind your money.
      </p>
    </div>

    <!-- Fullscreen Image Section -->
    <section class="w-100 position-relative">
      <img
        src="@/assets/Home_page.png"
        alt="GrowUp Richie Slide"
        class="w-100"
        style="height: 100vh; object-fit: cover;"
      />
    </section>

    <!-- Features -->
    <section class="container mt-5">
      <FeatureSection />
    </section>

    <!-- Reviews -->
    <section class="container my-5">
      <UserReviews />
    </section>

    <!-- Footer -->
    <AppFooter />
  </div>
</template>

<script>
import AppNavbar from '../components/Home_Navbar.vue'
import FeatureSection from '../components/Home_Features.vue'
import UserReviews from '../components/Home_Reviews.vue'
import AppFooter from '../components/Footer.vue'

export default {
  name: 'HomeView',
  components: {
    AppNavbar,
    FeatureSection,
    UserReviews,
    AppFooter
  }
}
</script>

<style scoped>
@media (max-width: 768px) {
  h2.display-4 {
    font-size: 2rem;
  }
  p.lead {
    font-size: 1rem;
  }
}
</style>
