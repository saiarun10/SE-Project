<template>
 <Navbar />
  <div class="container py-5">
    <Alert v-if="alert.visible" :message="alert.message" :type="alert.type" @close="alert.visible = false" />

    <h2 class="mb-4 text-center">Your Profile</h2>

    <div class="card shadow p-4 mx-auto animated fadeIn" style="max-width: 640px;">
      <!-- Avatar with Bootstrap Icon -->
      <div class="text-center mb-4">
        <div
          class="rounded-circle d-flex align-items-center justify-content-center bg-light border border-primary border-3 shadow"
          style="width: 120px; height: 120px; font-size: 48px; color: #4b5efc;"
        >
          <i :class="avatarIconClass"></i>
        </div>
      </div>

      <!-- Profile Fields -->
      <div class="form-group mb-3">
        <label class="form-label"><i class="fas fa-user"></i> Username</label>
        <input type="text" class="form-control" :value="profile.username" disabled />
      </div>

      <div class="form-group mb-3">
        <label class="form-label"><i class="fas fa-envelope"></i> Email</label>
        <input type="email" class="form-control" :value="profile.email" disabled />
      </div>

      <div class="form-group mb-3">
        <label class="form-label"><i class="fas fa-id-badge"></i> Full Name</label>
        <input v-model="profile.full_name" type="text" class="form-control" :disabled="!isEditing" />
        <small v-if="errors.full_name" class="text-danger">{{ errors.full_name }}</small>
      </div>

      <div class="form-group mb-3">
        <label class="form-label"><i class="fas fa-venus-mars"></i> Gender</label>
        <select v-model="profile.gender" class="form-select" :disabled="!isEditing">
          <option value="">-- Select Gender --</option>
          <option value="male">Male</option>
          <option value="female">Female</option>
          <option value="other">Other</option>
        </select>
        <small v-if="errors.gender" class="text-danger">{{ errors.gender }}</small>
      </div>

      <div class="form-group mb-3">
        <label class="form-label"><i class="fas fa-calendar-alt"></i> Birth Date</label>
        <input v-model="profile.birth_date" type="date" class="form-control" :disabled="!isEditing" />
        <small v-if="errors.birth_date" class="text-danger">{{ errors.birth_date }}</small>
      </div>

      <div class="form-group mb-3">
        <label class="form-label"><i class="fas fa-user-shield"></i> Parent Email</label>
        <div v-if="profile.parent_email">
          <input type="email" class="form-control" :value="profile.parent_email" disabled />
        </div>
        <div v-else>
          <button class="btn btn-outline-primary w-100" @click="openParentEmailModal">
            <i class="fas fa-plus-circle"></i> Set Parent Email
          </button>
        </div>
      </div>

      <div class="form-group mb-3">
        <label class="form-label"><i class="fas fa-calendar-check"></i> Date of Joining</label>
        <input type="text" class="form-control" :value="new Date(profile.created_at).toLocaleDateString()" disabled />
      </div>

      <div class="form-group mb-3">
        <label class="form-label"><i class="fas fa-star"></i> Membership Status</label>
        <div>
          <span v-if="profile.is_premium_user" class="badge bg-success">Premium User</span>
          <router-link v-else to="/buy-premium" class="btn btn-warning btn-sm">
            <i class="fas fa-crown"></i> Buy Premium
          </router-link>
        </div>
      </div>

      <!-- Action Buttons -->
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

    <!-- Parent Email Modal -->
    <div v-if="showParentEmailModal" class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Set Parent Email</h5>
            <button type="button" class="btn-close" @click="closeParentEmailModal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Parent Email</label>
              <input v-model="parentEmailForm.parent_email" type="email" class="form-control" />
              <small v-if="errors.parent_email" class="text-danger">{{ errors.parent_email }}</small>
            </div>
            <div class="mb-3">
              <label class="form-label">Parent Password</label>
              <input v-model="parentEmailForm.parent_password" type="password" class="form-control" />
              <small v-if="errors.parent_password" class="text-danger">{{ errors.parent_password }}</small>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeParentEmailModal">Cancel</button>
            <button class="btn btn-primary" @click="setParentEmail">Confirm</button>
          </div>
        </div>
      </div>
    </div>
    </div>
    <AppFooter />
</template>

<script>
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
      showParentEmailModal: false,
      parentEmailForm: {
        parent_email: '',
        parent_password: ''
      },
      errors: {},
      alert: {
        visible: false,
        message: '',
        type: 'notification'
      }
    };
  },
  computed: {
    avatarIconClass() {
      const gender = this.profile.gender;
      if (gender === 'male') return 'bi bi-person-fill';
      if (gender === 'female') return 'bi bi-person-fill';
      return 'bi bi-person-circle';
    }
  },
  async mounted() {
    await this.fetchProfile();
  },
  methods: {
    validateProfile() {
      this.errors = {};
      if (!this.profile.full_name.trim()) {
        this.errors.full_name = 'Full name is required';
      }
      if (!['male', 'female', 'other'].includes(this.profile.gender)) {
        this.errors.gender = 'Gender must be selected';
      }
      if (!this.profile.birth_date) {
        this.errors.birth_date = 'Birth date is required';
      }
      return Object.keys(this.errors).length === 0;
    },
    async fetchProfile() {
      try {
        const response = await axios.get(`${import.meta.env.VITE_BASE_URL}/api/get_user_profile`, {
          headers: { Authorization: `Bearer ${this.$store.state.token}` }
        });
        this.profile = response.data;
        this.originalProfile = { ...response.data };
      } catch (error) {
        this.showAlert('Failed to load profile', 'error');
      }
    },
    async saveProfile() {
      if (!this.validateProfile()) return;
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
        this.showAlert('Profile updated successfully', 'success');
      } catch (error) {
        this.showAlert(error.response?.data?.error || 'Failed to update profile', 'error');
      }
    },
    cancelEdit() {
      this.profile = { ...this.originalProfile };
      this.isEditing = false;
    },
    openParentEmailModal() {
      this.showParentEmailModal = true;
    },
    closeParentEmailModal() {
      this.showParentEmailModal = false;
      this.parentEmailForm = { parent_email: '', parent_password: '' };
      this.errors = {};
    },
    async setParentEmail() {
      this.errors = {};
      if (!this.parentEmailForm.parent_email) this.errors.parent_email = 'Parent email is required';
      if (!this.parentEmailForm.parent_password) this.errors.parent_password = 'Parent password is required';
      if (Object.keys(this.errors).length > 0) return;
      try {
        await axios.post(
          `${import.meta.env.VITE_BASE_URL}/api/set_parent_email`,
          this.parentEmailForm,
          { headers: { Authorization: `Bearer ${this.$store.state.token}` } }
        );
        this.closeParentEmailModal();
        await this.fetchProfile();
        this.showAlert('Parent email set successfully', 'success');
      } catch (error) {
        this.showAlert(error.response?.data?.error || 'Failed to set parent email', 'error');
      }
    },
    showAlert(message, type) {
      this.alert = { visible: true, message, type };
    }
  }
};
</script>

