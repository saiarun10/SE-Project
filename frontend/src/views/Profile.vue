<template>
  <Navbar />
  <div class="container py-4 py-md-5">
    <Alert
      v-if="alert.visible"
      :message="alert.message"
      :type="alert.type"
      @close="alert.visible = false"
    />

    <h2 class="mb-4 text-center text-primary fw-bold">Your Profile</h2>

    <div
      class="shadow-lg p-3 p-md-4 mx-auto rounded-4 bg-gradient"
      style="max-width: 720px; background: linear-gradient(to right, #f0f8ff, #ffe6f0); border: none;"
    >
      <div class="d-flex justify-content-center mb-4">
        <div
          class="avatar-wrapper rounded-circle shadow d-flex align-items-center justify-content-center"
          :style="avatarBgStyle"
        >
          <i :class="avatarIconClass" class="avatar-icon text-white"></i>
        </div>
      </div>

      <div class="form-group mb-3">
        <label class="form-label text-primary"><i class="fas fa-user"></i> Username</label>
        <input type="text" class="form-control" :value="profile.username" disabled />
      </div>

      <div class="form-group mb-3">
        <label class="form-label text-primary"><i class="fas fa-envelope"></i> Email</label>
        <input type="email" class="form-control" :value="profile.email" disabled />
      </div>

      <div class="form-group mb-3">
        <label class="form-label text-primary"><i class="fas fa-id-badge"></i> Full Name</label>
        <input v-model="profile.full_name" type="text" class="form-control" :disabled="!isEditing" />
        <small v-if="errors.full_name" class="text-danger">{{ errors.full_name }}</small>
      </div>

      <div class="row mb-3">
        <div class="col-md-6 mb-3 mb-md-0">
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

      <div class="form-group mb-3">
        <label class="form-label text-primary"><i class="fas fa-calendar-check"></i> Date of Joining</label>
        <input
          type="text"
          class="form-control"
          :value="formatJoinDate(profile.created_at)"
          disabled
        />
      </div>

      <div class="form-group mb-4">
        <div class="d-flex flex-column flex-sm-row align-items-start align-items-sm-center gap-2">
          <label class="form-label text-primary m-0 fw-normal">
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
            class="btn btn-warning shadow-sm"
          >
            <i class="fas fa-crown"></i> Buy Premium
          </router-link>
        </div>
      </div>

      <div class="text-center mt-4">
        <div class="d-grid gap-2 d-sm-flex justify-content-sm-center">
            <button v-if="isEditing" class="btn btn-success" @click="saveProfile"><i class="fas fa-save"></i> Save</button>
            <button v-if="isEditing" class="btn btn-secondary" @click="cancelEdit"><i class="fas fa-times"></i> Cancel</button>
            <button v-else class="btn btn-primary" @click="isEditing = true"><i class="fas fa-edit"></i> Edit Profile</button>
        </div>
      </div>
    </div>

    <div v-if="showParentModal" class="modal fade show" style="display: block; background-color: rgba(0,0,0,0.5);" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title fw-bold text-primary"><i class="fas fa-user-shield"></i> Set Parent/Guardian Information</h5>
            <button type="button" class="btn-close" @click="closeParentEmailModal" :disabled="isSubmittingParent"></button>
          </div>
          <div class="modal-body">
            <Alert v-if="modalAlert.visible" :message="modalAlert.message" :type="modalAlert.type" @close="modalAlert.visible = false"/>
            
            <form @submit.prevent="handleSetParentEmail">
              <div class="mb-3">
                <label for="parentName" class="form-label">Your Full Name</label>
                <input type="text" class="form-control" id="parentName" v-model="parentData.name" :disabled="isSubmittingParent">
                <small v-if="modalErrors.name" class="text-danger">{{ modalErrors.name }}</small>
              </div>
              <div class="mb-3">
                <label for="parentRelationship" class="form-label">Relationship with Child</label>
                <input type="text" class="form-control" id="parentRelationship" v-model="parentData.relationship" :disabled="isSubmittingParent">
                <small v-if="modalErrors.relationship" class="text-danger">{{ modalErrors.relationship }}</small>
              </div>
              <div class="mb-3">
                <label for="parentProof" class="form-label">Upload Proof of Guardianship</label>
                <input type="file" class="form-control" id="parentProof" @change="handleFileUpload" :disabled="isSubmittingParent">
                 <small v-if="modalErrors.proof" class="text-danger">{{ modalErrors.proof }}</small>
              </div>
              <div class="mb-3">
                <label for="parentEmail" class="form-label">Parent's Email Address</label>
                <input type="email" class="form-control" id="parentEmail" v-model="parentData.email" :disabled="isSubmittingParent">
                <small v-if="modalErrors.email" class="text-danger">{{ modalErrors.email }}</small>
              </div>
              <div class="mb-3">
                <label for="parentPassword" class="form-label">Create Password</label>
                <input type="password" class="form-control" id="parentPassword" v-model="parentData.password" :disabled="isSubmittingParent">
                <small v-if="modalErrors.password" class="text-danger">{{ modalErrors.password }}</small>
              </div>
              <div class="mb-3">
                <label for="parentConfirmPassword" class="form-label">Confirm Password</label>
                <input type="password" class="form-control" id="parentConfirmPassword" v-model="parentData.confirmPassword" :disabled="isSubmittingParent">
                <small v-if="modalErrors.confirmPassword" class="text-danger">{{ modalErrors.confirmPassword }}</small>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeParentEmailModal" :disabled="isSubmittingParent">Close</button>
            <button type="button" class="btn btn-primary" @click="handleSetParentEmail" :disabled="isSubmittingParent">
              <span v-if="isSubmittingParent" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
              <i v-else class="fas fa-paper-plane"></i>
              Submit
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
  <AppFooter />
</template>

<script>
// ... (The entire <script> section remains unchanged from the previous version)
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
      errors: {},
      // State for Parent Email Modal
      showParentModal: false,
      isSubmittingParent: false,
      parentData: {
        name: '',
        relationship: '',
        proof: null,
        email: '',
        password: '',
        confirmPassword: ''
      },
      modalErrors: {},
      modalAlert: {
        visible: false,
        message: '',
        type: 'danger'
      }
    };
  },
  computed: {
    avatarIconClass() {
      const gender = this.profile.gender;
      if (gender === 'male') return 'bi bi-person-fill';
      if (gender === 'female') return 'bi bi-person-fill';
      return 'bi bi-person-circle';
    },
    avatarBgStyle() {
      if (this.profile.gender === 'male') return { 'background-color': '#003f8a' };
      if (this.profile.gender === 'female') return { 'background-color': '#a30566' };
      return { 'background-color': '#343a40' };
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
      if (this.profile.parent_email) {
        this.alert = {
          visible: true,
          message: 'Parent email is already set and cannot be changed.',
          type: 'warning'
        };
        return;
      }
      this.showParentModal = true;
    },
    closeParentEmailModal() {
      this.showParentModal = false;
      this.parentData = { name: '', relationship: '', proof: null, email: '', password: '', confirmPassword: '' };
      this.modalErrors = {};
      this.modalAlert.visible = false;
    },
    handleFileUpload(event) {
        this.parentData.proof = event.target.files[0];
        if (this.parentData.proof) {
          this.modalErrors.proof = ''; // Clear error on file selection
        }
    },
    validateParentForm() {
      this.modalErrors = {};
      let isValid = true;
      if (!this.parentData.name.trim()) {
        this.modalErrors.name = 'Your name is required.';
        isValid = false;
      }
      if (!this.parentData.relationship.trim()) {
        this.modalErrors.relationship = 'Your relationship to the child is required.';
        isValid = false;
      }
      if (!this.parentData.proof) {
        this.modalErrors.proof = 'Proof of guardianship is required.';
        isValid = false;
      }
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!this.parentData.email) {
        this.modalErrors.email = 'Parent email is required.';
        isValid = false;
      } else if (!emailRegex.test(this.parentData.email)) {
        this.modalErrors.email = 'Please enter a valid email address.';
        isValid = false;
      }
      if (this.parentData.password.length < 6) { // Common minimum password length
        this.modalErrors.password = 'Password must be at least 6 characters long.';
        isValid = false;
      }
      if (this.parentData.password !== this.parentData.confirmPassword) {
        this.modalErrors.confirmPassword = 'Passwords do not match.';
        isValid = false;
      }
      return isValid;
    },
    async handleSetParentEmail() {
      this.modalAlert.visible = false;
      if (!this.validateParentForm()) return;

      this.isSubmittingParent = true;
      try {
        await axios.post(
          `${import.meta.env.VITE_BASE_URL}/api/set_parent_email`,
          {
            parent_email: this.parentData.email,
            parent_password: this.parentData.password
          },
          { headers: { Authorization: `Bearer ${this.$store.state.token}` } }
        );

        this.closeParentEmailModal();
        await this.fetchProfile(); // Refresh profile to show new parent email
        this.alert = { visible: true, message: 'Parent email set successfully!', type: 'success' };
      } catch (err) {
        const defaultError = 'An unexpected error occurred. Please try again.';
        this.modalAlert = {
          visible: true,
          message: err.response?.data?.message || defaultError,
          type: 'danger'
        };
      } finally {
        this.isSubmittingParent = false;
      }
    }
  },
  mounted() {
    this.fetchProfile();
  }
};
</script>

<style scoped>
.avatar-wrapper {
  width: 120px;
  height: 120px;
  transition: all 0.3s ease;
}
.avatar-icon {
  font-size: 48px;
  transition: all 0.3s ease;
}

/* Media query for smaller screens */
@media (max-width: 576px) {
  .avatar-wrapper {
    width: 90px;
    height: 90px;
  }
  .avatar-icon {
    font-size: 36px;
  }
}

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
.modal {
  z-index: 1055;
}
</style>