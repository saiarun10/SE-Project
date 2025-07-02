<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-offwhite px-3">
    <div class="container-fluid">
      <!-- Brand -->
      <router-link class="navbar-brand fw-bold text-dark" :to="homeRoute">GrowUp Riche</router-link>

      <!-- Toggler for mobile -->
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNavDropdown"
        aria-controls="navbarNavDropdown"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <!-- Right-side items -->
      <div class="collapse navbar-collapse justify-content-end" id="navbarNavDropdown">
        <ul class="navbar-nav align-items-lg-center">
          <!-- Home button (redirects based on role) -->
          <li class="nav-item">
            <router-link
              class="nav-link text-dark"
              :to="homeRoute"
            >Home</router-link>
          </li>

          <!-- For admin: show direct Logout button -->
          <li class="nav-item" v-if="isAuthenticated && userRole === 'admin'">
            <button
              class="btn btn-outline-danger btn-sm ms-2"
              @click="logout"
            >Logout</button>
          </li>

          <!-- For non-admin authenticated users: show profile icon with dropdown -->
          <li class="nav-item dropdown" v-if="isAuthenticated && userRole !== 'admin'">
            <a
              class="nav-link dropdown-toggle d-flex align-items-center text-dark"
              href="#"
              id="profileDropdown"
              role="button"
              data-bs-toggle="dropdown"
              aria-expanded="false"
            >
              <i class="bi bi-person-circle fs-5"></i>
            </a>
            <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="profileDropdown">
              <li>
                <router-link class="dropdown-item" to="/profile">View Profile</router-link>
              </li>
              <li>
                <router-link class="dropdown-item" to="/user-summary">View Summary</router-link>
              </li>
              <li>
                <router-link class="dropdown-item" to="/buy-premium">Buy Premium</router-link>
              </li>
              <li>
                <hr class="dropdown-divider" />
              </li>
              <li>
                <a class="dropdown-item text-danger" href="#" @click.prevent="logout">Logout</a>
              </li>
            </ul>
          </li>

          <!-- If not authenticated: show Login / Signup -->
          <template v-else-if="!isAuthenticated">
            <li class="nav-item">
              <router-link class="nav-link text-dark" to="/login">Login</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link text-dark" to="/signup">Signup</router-link>
            </li>
          </template>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: 'Navbar',
  computed: {
    ...mapGetters(['isAuthenticated', 'userRole']),
    homeRoute() {
      if (!this.isAuthenticated) {
        return '/';
      }
      return this.userRole === 'admin' ? '/admin-dashboard' : '/user-dashboard';
    },
  },
  methods: {
    logout() {
      this.$store.dispatch('logout').finally(() => {
        this.$router.push('/');
      });
    },
  },
};
</script>

<style scoped>
/* Light gray background for navbar */
.bg-offwhite {
  background-color: #f8f9fa !important; /* Inspired light gray */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Navbar link styles */
.nav-link {
  color: #212529 !important; /* Dark gray */
  font-weight: 500;
  padding: 0.75rem 1rem;
  transition: all 0.3s ease;
  border-radius: 0.5rem;
  font-size: 1rem;
}

/* Hover effect for nav links */
.nav-link:hover {
  color: #2f22a5 !important; /* Coral hover */
  background-color: rgba(75, 94, 252, 0.1); /* Light blue background on hover */
}

/* Active link state */
.nav-link.active {
  color: #4b5efc !important; /* Professional blue */
  font-weight: 600;
  border-bottom: 2px solid #4b5efc; /* Inspired active underline */
}

/* Logout button styles for admin */
.btn-outline-danger {
  border-color: #dc3545;
  color: #dc3545;
  padding: 0.25rem 0.75rem;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.btn-outline-danger:hover {
  background-color: #dc3545;
  color: #ffffff;
  border-color: #dc3545;
}

/* Dropdown menu styles */
.dropdown-menu {
  min-width: 12rem;
  border: 1px solid rgba(75, 94, 252, 0.2); /* Light blue border */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-radius: 0.5rem;
  margin-top: 0.5rem;
  background-color: #f8f9fa; /* Light gray background */
}

/* Dropdown item styles */
.dropdown-item {
  padding: 0.5rem 1rem;
  color: #212529; /* Dark gray */
  transition: all 0.3s ease;
  font-size: 0.95rem;
}

/* Dropdown item hover effect */
.dropdown-item:hover {
  background-color: rgba(75, 94, 252, 0.1); /* Light blue background */
  color: #2f22a5; /* Coral hover */
}

/* Dropdown logout item */
.dropdown-item.text-danger {
  color: #dc3545 !important;
}

.dropdown-item.text-danger:hover {
  background-color: rgba(75, 94, 252, 0.1); /* Light blue background */
  color: #c82333 !important;
}

/* Navbar brand styling */
.navbar-brand {
  font-size: 1.5rem;
  color: #4b5efc !important; /* Professional blue */
  font-weight: 600;
  transition: all 0.3s ease;
}

.navbar-brand:hover {
  color: #2f22a5 !important; /* Coral hover */
}

/* Mobile responsive styles */
@media (max-width: 991.98px) {
  .navbar-nav {
    padding: 1rem 0;
    text-align: center;
    gap: 0.5rem !important; /* Inspired gap */
  }

  .nav-item {
    margin: 0.5rem 0;
  }

  .nav-link {
    padding: 0.75rem 1rem;
    font-size: 1.1rem;
  }

  .btn-outline-danger {
    width: 100%;
    margin: 0.5rem 0;
    padding: 0.5rem 1rem;
    font-size: 1.1rem;
  }

  .dropdown-menu {
    width: 100%;
    border: none;
    box-shadow: none;
    background-color: #f8f9fa; /* Light gray */
    text-align: center;
  }

  .dropdown-item {
    padding: 0.75rem 1.5rem;
    font-size: 1.1rem;
  }

  .dropdown-toggle {
    justify-content: center;
    padding: 0.75rem 1rem;
  }

  .bi-person-circle {
    font-size: 1.5rem;
  }
}

/* Smaller screens (e.g., phones) */
@media (max-width: 576px) {
  .navbar-brand {
    font-size: 1.25rem;
  }

  .nav-link {
    font-size: 1rem;
  }

  .btn-outline-danger {
    font-size: 1rem;
  }

  .dropdown-item {
    font-size: 1rem;
  }

  .bi-person-circle {
    font-size: 1.25rem;
  }
}

/* Ensure navbar toggler is styled */
.navbar-toggler {
  border: 1px solid rgba(75, 94, 252, 0.2); /* Light blue border */
  padding: 0.35rem 0.75rem;
}

.navbar-toggler-icon {
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 30'%3e%3cpath stroke='%234b5efc' stroke-width='2' stroke-linecap='round' stroke-miterlimit='10' d='M4 7h22M4 15h22M4 23h22'/%3e%3c/svg%3e"); /* Professional blue */
}
</style>