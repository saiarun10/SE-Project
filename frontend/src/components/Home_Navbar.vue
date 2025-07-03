<template>
  <nav class="navbar navbar-expand-lg bg-light shadow-sm px-4 py-3 sticky-top border-bottom">
    <div class="container-fluid">
      <!-- Brand -->
      <router-link to="/" class="navbar-brand fw-bold fs-3 text-brand">
        GrowUp Richie
      </router-link>

      <!-- Mobile toggle -->
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarContent"
        aria-controls="navbarContent"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <!-- Nav items -->
      <div class="collapse navbar-collapse" id="navbarContent">
        <ul class="navbar-nav ms-auto mb-2 mb-lg-0 d-flex gap-4">
          <li class="nav-item">
            <router-link to="/" class="nav-link" exact-active-class="active-link">Home</router-link>
          </li>
          <li class="nav-item">
            <router-link to="/login" class="nav-link" exact-active-class="active-link">Login</router-link>
          </li>
          <li class="nav-item">
            <router-link to="/signup" class="nav-link" exact-active-class="active-link">Register</router-link>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'AppNavbar'
}
</script>

<style scoped>
/* Custom styles for professional, minimalist design with solid colors */
.navbar {
  background-color: #f8f9fa; /* Light gray background */
}

.text-brand {
  color: #4b5efc; /* Professional blue */
}

.nav-link {
  color: #212529; /* Dark gray */
  font-weight: 500;
  font-size: 1.1rem;
  padding: 0.75rem 1rem;
  transition: all 0.3s ease;
  border-radius: 0.5rem;
}

.nav-link:hover {
  color: #2f22a5 !important; /* Coral hover */
  background-color: rgba(51, 128, 41, 0.1);
}

.active-link {
  color: #4b5efc !important; /* Professional blue */
  font-weight: 600;
  border-bottom: 2px solid #4b5efc;
}

@media (max-width: 768px) {
  .navbar-nav {
    gap: 0.5rem !important;
  }
  .nav-link {
    font-size: 1rem;
    padding: 0.5rem 1rem;
  }
}
</style>