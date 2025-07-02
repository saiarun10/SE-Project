<template>
  <Navbar />
  <div class="container py-5">
    <Alert
      v-if="alert.visible"
      :message="alert.message"
      :type="alert.type"
      @close="alert.visible = false"
    />

    <h2 class="mb-4 text-center text-primary fw-bold">Your Profile</h2>

    <div
      class="shadow-lg p-4 mx-auto rounded-4 bg-gradient"
      style="max-width: 720px; background: linear-gradient(to right, #f0f8ff, #ffe6f0); border: none;"
    >
      <!-- Avatar -->
      <div class="d-flex justify-content-center mb-4">
        <div
          class="rounded-circle shadow d-flex align-items-center justify-content-center"
          :style="avatarStyle"
        >
          <i :class="avatarIconClass" class="text-white" style="font-size: 48px;"></i>
        </div>
      </div>

      <!-- Username -->
      <div class="form-group mb-3">
        <label class="form-label text-primary"><i class="fas fa-user"></i> Username</label>
        <input type="text" class="form-control" :value="profile.username" disabled />
      </div>

      <!-- Email -->
      <div class="form-group mb-3">
        <label class="form-label text-primary"><i class="fas fa-envelope"></i> Email</label>
        <input type="email" class="form-control" :value="profile.email" disabled />
      </div>

      <!-- Full Name -->
      <div class="form-group mb-3">
        <label class="form-label text-primary"><i class="fas fa-id-badge"></i> Full Name</label>
        <input v-model="profile.full_name" type="text" class="form-control" :disabled="!isEditing" />
        <small v-if="errors.full_name" class="text-danger">{{ errors.full_name }}</small>
      </div>

      <!-- Gender & Birth Date -->
      <div class="row mb-3">
        <div class="col-md-6">
          <label class="form-label text-primary"><i class="fas fa-venus-mars"></i> Gender</label>
          <select v-model="profile.gender" class="form-select" :disabled="!isEditing">
            <option value="">-- Select Gender --</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>
          <small v-if="errors.gender" class="text-danger">{{ errors.gender }}</small>
        </div>
        <div class="col-md-6">
          <label class="form-label text-primary"><i class="fas fa-calendar-alt"></i> Birth Date</label>
          <input v-model="profile.birth_date" type="date" class="form-control" :disabled="!isEditing" />
          <small v-if="errors.birth_date" class="text-danger">{{ errors.birth_date }}</small>
          <div v-if="profile.birth_date && !isEditing" class="text-muted small mt-1">
            <i class="fas fa-hourglass-half"></i> Age: {{ age }}
          </div>
        </div>
      </div>

      <!-- Parent Email -->
      <div class="form-group mb-3">
        <label class="form-label text-primary"><i class="fas fa-user-shield"></i> Parent Email</label>
        <div v-if="profile.parent_email">
          <input type="email" class="form-control" :value="profile.parent_email" disabled />
        </div>
        <div v-else>
          <button class="btn btn-outline-primary w-100" @click="openParentEmailModal">
            <i class="fas fa-plus-circle"></i> Set Parent Email
          </button>
        </div>
      </div>

      <!-- Date of Joining -->
      <div class="form-group mb-3">
        <label class="form-label text-primary"><i class="fas fa-calendar-check"></i> Date of Joining</label>
        <input
          type="text"
          class="form-control"
          :value="formatJoinDate(profile.created_at)"
          disabled
        />
      </div>

      <!-- Membership Status -->
      <div class="form-group mb-4">
        <label class="form-label text-primary me-3">
          <i class="fas fa-star"></i> Membership Status
        </label>
        <span
          class="badge fs-6 px-3 py-2"
          :class="profile.is_premium_user ? 'bg-success' : 'bg-secondary'"
        >
          {{ profile.is_premium_user ? 'Premium User' : 'Free User' }}
        </span>
        <router-link
          v-if="!profile.is_premium_user"
          to="/buy-premium"
          class="btn btn-warning ms-3 shadow-sm"
        >
          <i class="fas fa-crown"></i> Buy Premium
        </router-link>
      </div>

      <!-- Buttons -->
      <div class="text-center mt-4">
        <button
          v-if="isEditing"
          class="btn btn-success me-2"
          @click="saveProfile"
        >
          <i class="fas fa-save"></i> Save
        </button>
        <button
          v-if="isEditing"
          class="btn btn-secondary"
          @click="cancelEdit"
        >
          <i class="fas fa-times"></i> Cancel
        </button>
        <button
          v-else
          class="btn btn-primary"
          @click="isEditing = true"
        >
          <i class="fas fa-edit"></i> Edit Profile
        </button>
      </div>
    </div>
  </div>
  <AppFooter />
</template>

<script>
import 'bootstrap-icons/font/bootstrap-icons.css';
import '@fortawesome/fontawesome-free/css/all.min.css';

import axios from 'axios';
import Alert from '@/components/Alert.vue';
import Navbar from '@/components/Navbar.vue';
import AppFooter from '@/components/Footer.vue';

export default {
  name: 'ProfileView',
  components: { Alert, Navbar, AppFooter },
  data() {
    return {
      profile: {
        user_id: null,
        email: '',
        username: '',
        full_name: '',
        gender: '',
        birth_date: '',
        parent_email: null,
        is_premium_user: false,
        created_at: ''
      },
      originalProfile: {},
      isEditing: false,
      alert: {
        visible: false,
        message: '',
        type: 'notification'
      },
      errors: {}
    };
  },
  computed: {
    avatarIconClass() {
      const gender = this.profile.gender;
      if (gender === 'male') return 'bi bi-person-fill';
      if (gender === 'female') return 'bi bi-person-fill';
      return 'bi bi-person-circle';
    },
    avatarStyle() {
      const base = 'width: 120px; height: 120px;';
      if (this.profile.gender === 'male') return base + ' background-color: #003f8a;';
      if (this.profile.gender === 'female') return base + ' background-color: #a30566;';
      return base + ' background-color: #343a40;';
    },
    age() {
      if (!this.profile.birth_date) return '';
      const birth = new Date(this.profile.birth_date);
      const today = new Date();

      let years = today.getFullYear() - birth.getFullYear();
      let months = today.getMonth() - birth.getMonth();
      let days = today.getDate() - birth.getDate();

      if (days < 0) {
        months--;
        days += new Date(today.getFullYear(), today.getMonth(), 0).getDate();
      }
      if (months < 0) {
        years--;
        months += 12;
      }

      return `${years}y ${months}m ${days}d`;
    }
  },
  methods: {
    formatJoinDate(dateStr) {
      const options = { day: 'numeric', month: 'long', year: 'numeric' };
      return new Date(dateStr).toLocaleDateString('en-IN', options);
    },
    async fetchProfile() {
      try {
        const response = await axios.get(`${import.meta.env.VITE_BASE_URL}/api/get_user_profile`, {
          headers: { Authorization: `Bearer ${this.$store.state.token}` }
        });
        this.profile = response.data;
        this.originalProfile = { ...response.data };
      } catch (err) {
        this.alert = { visible: true, message: 'Failed to load profile', type: 'error' };
      }
    },
    async saveProfile() {
      this.errors = {};
      if (!this.profile.full_name) this.errors.full_name = 'Full name is required';
      if (!this.profile.gender) this.errors.gender = 'Gender is required';
      if (!this.profile.birth_date) this.errors.birth_date = 'Birth date is required';
      if (Object.keys(this.errors).length > 0) return;

      try {
        const response = await axios.put(
          `${import.meta.env.VITE_BASE_URL}/api/get_user_profile`,
          {
            full_name: this.profile.full_name,
            gender: this.profile.gender,
            birth_date: this.profile.birth_date
          },
          { headers: { Authorization: `Bearer ${this.$store.state.token}` } }
        );
        this.profile = response.data;
        this.originalProfile = { ...response.data };
        this.isEditing = false;
        this.alert = { visible: true, message: 'Profile updated successfully', type: 'success' };
      } catch (err) {
        this.alert = { visible: true, message: 'Update failed', type: 'error' };
      }
    },
    cancelEdit() {
      this.profile = { ...this.originalProfile };
      this.isEditing = false;
    },
    openParentEmailModal() {
      // Placeholder: modal open logic
    }
  },
  mounted() {
    this.fetchProfile();
  }
};
</script>

<style scoped>
button.btn:hover {
  filter: brightness(1.1);
}
.bg-gradient {
  background: linear-gradient(135deg, #f0f8ff, #ffe6f0);
  border-radius: 1rem;
}
input:disabled,
select:disabled {
  background-color: #f8f9fa;
  cursor: not-allowed;
}
</style>
