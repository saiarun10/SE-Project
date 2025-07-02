<template>
  <AppNavbar />
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-lg-8">
        <h2 class="text-center fw-bold mb-4 text-primary">Get in Touch</h2>
        <p class="lead text-muted text-center mb-4">
          We’d love to hear from you! Whether it's a question, suggestion, or opportunity — let's connect.
        </p>

        <div class="card shadow-sm">
          <div class="card-body">
            <h5 class="card-title fw-bold text-dark mb-3">Contact Details</h5>
            <ul class="list-unstyled">
              <li class="mb-2">
                <i class="fas fa-envelope text-primary me-2"></i>
                <strong>Email:</strong> <a href="mailto:support@growuprichie.com">support@growuprichie.com</a>
              </li>
              <li class="mb-2">
                <i class="fas fa-phone text-primary me-2"></i>
                <strong>Phone:</strong> +91-7001486011
              </li>
              <li class="mb-2">
                <i class="fab fa-instagram text-primary me-2"></i>
                <strong>Instagram:</strong> <a href="#" target="_blank">@growuprichie</a>
              </li>
            </ul>
            <hr>
            <p class="mb-0 text-muted">We usually respond within 1-2 business days.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
  <AppFooter />
</template>

<script>

import App from '../App.vue';
import AppNavbar from '../components/Navbar.vue';
import AppFooter from '../components/Footer.vue';
import Alert from '@/components/Alert.vue';
export default {
  name: 'ContactView',
  components: {
    AppNavbar,
    AppFooter,
    Alert
  }
}
</script>

<style scoped>
h2 {
  color: #0000CD;
}
a {
  color: #0000CD;
}
a:hover {
  text-decoration: underline;
}
</style>
