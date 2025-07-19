<template>
  <div>
    <Navbar />
    <div class="container py-5">
      <Alert v-if="alert.visible" :message="alert.message" :type="alert.type" @close="alert.visible = false" />
      <div v-if="isPremiumUser" class="card shadow-sm p-4 mx-auto text-center" style="max-width: 600px;">
        <h2 class="text-success">🎉 You are a Premium Member!</h2>
        <p class="mt-3">Thank you for being a Super Richie. You have access to all exclusive features.</p>
      </div>
      <div v-else>
        <h2 class="mb-4 text-center">Upgrade to Premium</h2>
        <div class="card shadow-sm p-4 mx-auto" style="max-width: 600px;">
          <h4 class="mb-3">Premium Membership Benefits</h4>
          <ul class="list-group list-group-flush mb-4">
            <li class="list-group-item">Unlimited Chat with AI Tutor</li>
            <li class="list-group-item">Detailed Progress Analytics</li>
            <li class="list-group-item">Report Download for Parents</li>
            <li class="list-group-item">Ad-free Experience</li>
          </ul>
          <div class="text-center">
            <p class="mb-3">Unlock all features for a one-time payment of <strong>₹1000</strong>!</p>
            <button class="btn btn-primary" @click="handleBuyPremium" :disabled="isLoading">
              {{ isLoading ? 'Processing...' : 'Proceed to Payment' }}
            </button>
          </div>
        </div>
      </div>
    </div>
    <AppFooter />
  </div>
</template>

<script>
import axios from 'axios';
import { mapGetters, mapState } from 'vuex';
import Alert from '@/components/Alert.vue';
import Navbar from '../components/Navbar.vue';
import AppFooter from '../components/Footer.vue';

export default {
  name: 'BuyPremium',
  components: { Alert, Navbar, AppFooter },
  data() {
    return {
      isLoading: false,
      alert: { visible: false, message: '', type: 'alert-info' },
      BASE_URL: import.meta.env.VITE_BASE_URL + '/api',
    };
  },
  computed: {
    ...mapGetters(['isPremiumUser']),
    ...mapState(['user', 'token']),
  },
  methods: {
    async handleBuyPremium() {
      this.isLoading = true;
      try {
        const response = await axios.post(`${this.BASE_URL}/payment-create-checkout-session`, {});
        
        // 1. Store the session_id from the backend response in localStorage
        localStorage.setItem('stripe_session_id', response.data.session_id);

        // 2. Redirect to Stripe's payment page
        window.location.href = response.data.url;
      } catch (error) {
        const message = error.response?.data?.message || 'Failed to initiate payment. Please try again.';
        this.showAlert(message, 'alert-danger');
        this.isLoading = false;
      }
    },
    
    // NEW: Method to verify payment with the backend
    async verifyPayment(sessionId) {
        try {
            const response = await axios.post(`${this.BASE_URL}/verify-payment`, {
                session_id: sessionId
            });

            // If verification is successful, update the Vuex store
            if (response.data.is_premium) {
                this.showAlert('Payment successful! Welcome to Premium.', 'alert-success');
                const updatedUser = { ...this.user, is_premium_user: true };
                this.$store.commit('SET_USER', { user: updatedUser, token: this.token });
            }
        } catch (error) {
            const message = error.response?.data?.message || 'Could not verify payment. Please contact support.';
            this.showAlert(message, 'alert-danger');
        } finally {
            // Clean up the stored session ID regardless of outcome
            localStorage.removeItem('stripe_session_id');
        }
    },

    handlePaymentRedirect() {
      const urlParams = new URLSearchParams(window.location.search);
      const sessionId = localStorage.getItem('stripe_session_id');

      // Check for the success parameter and if a session ID is stored
      if (urlParams.get('success') && sessionId) {
        this.verifyPayment(sessionId);
      } else if (urlParams.get('canceled')) {
        this.showAlert('Payment was canceled. You can try again anytime.', 'alert-warning');
        // Clean up if canceled
        localStorage.removeItem('stripe_session_id');
      }

      // Clean up the URL
      if (urlParams.has('success') || urlParams.has('canceled')) {
          window.history.replaceState(null, null, window.location.pathname);
      }
    },

    showAlert(message, type) {
      this.alert = { visible: true, message, type };
    },
  },
  mounted() {
    this.handlePaymentRedirect();
  }
};
</script>

<style scoped>
.card {
  background-color: #f8f9fa;
  border-radius: 0.5rem;
  border: 1px solid rgba(75, 94, 252, 0.1);
}
.list-group-item {
  background-color: #f8f9fa;
  border: none;
  padding: 0.75rem 1rem;
}
.btn-primary {
  background-color: #4b5efc;
  border-color: #4b5efc;
  transition: all 0.3s ease;
  padding: 0.6rem 1.5rem;
  font-size: 1rem;
}
.btn-primary:hover:not(:disabled) {
  background-color: #2f22a5;
  border-color: #2f22a5;
}
.btn-primary:disabled {
    cursor: not-allowed;
    opacity: 0.65;
}
@media (max-width: 576px) {
  .card { padding: 1.5rem; }
  h2, h4 { font-size: 1.5rem; }
}
</style>