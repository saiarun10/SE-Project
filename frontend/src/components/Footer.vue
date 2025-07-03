<template>
  <footer class="bg-light text-dark pt-5 pb-4 border-top mt-5 w-100">
    <div class="container-fluid px-5">
      <div class="row gx-5 gy-4">
        <!-- Company Info -->
        <div class="col-12 col-md-3">
          <h5 class="fw-bold text-uppercase mb-3">GrowUp Richie</h5>
          <p class="text-muted">
            Empowering your digital journey with smart and scalable solutions for the future.
          </p>
        </div>

        <!-- About Links -->
        <div class="col-6 col-md-2">
          <h6 class="text-uppercase fw-bold mb-3">About</h6>
          <ul class="list-unstyled">
            <li><a href="/about" class="footer-link">Our Team</a></li>
            <li><a href="/about" class="footer-link">Careers</a></li>
            <li><a href="/about" class="footer-link">Blog</a></li>
            <li><a href="/about" class="footer-link">Press</a></li>
          </ul>
        </div>

        <!-- Support Links -->
        <div class="col-6 col-md-2">
          <h6 class="text-uppercase fw-bold mb-3">Support</h6>
          <ul class="list-unstyled">
            <li><a href="#" class="footer-link">Help Center</a></li>
            <li><a href="#" class="footer-link">FAQs</a></li>
            <li><a href="/contact" class="footer-link">Contact Us</a></li>
            <li><a href="#" class="footer-link">Feedback</a></li>
          </ul>
        </div>

        <!-- Legal -->
        <div class="col-6 col-md-2">
          <h6 class="text-uppercase fw-bold mb-3">Legal</h6>
          <ul class="list-unstyled">
            <li><a href="#" class="footer-link">Privacy Policy</a></li>
            <li><a href="#" class="footer-link">Terms of Service</a></li>
            <li><a href="#" class="footer-link">Cookie Policy</a></li>
            <li><a href="#" class="footer-link">Licenses</a></li>
          </ul>
        </div>

        <!-- Social Media: 3 Icons per Row -->
        <div class="col-6 col-md-3">
          <h6 class="text-uppercase-center fw-bold mb-3">Connect with Us</h6>
          <div class="row g-1">
            <div class="col-4 text-center">
              <a href="#" class="footer-social d-block"><i class="fab fa-facebook-f"></i></a>
            </div>
            <div class="col-4 text-center">
              <a href="#" class="footer-social d-block"><i class="fab fa-twitter"></i></a>
            </div>
            <div class="col-4 text-center">
              <a href="#" class="footer-social d-block"><i class="fab fa-instagram"></i></a>
            </div>
            <div class="col-4 text-center">
              <a href="#" class="footer-social d-block"><i class="fab fa-linkedin-in"></i></a>
            </div>
            <div class="col-4 text-center">
              <a href="#" class="footer-social d-block"><i class="fab fa-github"></i></a>
            </div>
            <div class="col-4 text-center">
              <a href="#" class="footer-social d-block"><i class="fab fa-youtube"></i></a>
            </div>
          </div>
        </div>
      </div>

      <hr class="my-4"/>

      <!-- Copyright -->
      <div class="text-center small text-muted">
        &copy; 2025 <strong>GrowUp Richie</strong>. All rights reserved.
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'AppFooter'
}
</script>

<style scoped>
footer {
  background-color: #f8f9fa; /* off-white */
}

.footer-link {
  display: block;
  color: #6c757d;
  text-decoration: none;
  margin-bottom: 0.5rem;
  transition: all 0.2s ease-in-out;
}

.footer-link:hover {
  color: #0000CD;
  text-decoration: underline;
}

.footer-social {
  color: #343a40;
  font-size: 1.25rem;
  transition: all 0.3s ease;
}

.footer-social:hover {
  color: #0000CD;
  transform: scale(1.2);
}
</style>
