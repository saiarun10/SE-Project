<template>
<Navbar />
  <div class="container py-5">
    <Alert v-if="alert.visible" :message="alert.message" :type="alert.type" @close="alert.visible = false" />
    
    <h2 class="mb-4 text-center">Upgrade to Premium</h2>
    
    <div class="card shadow-sm p-4 mx-auto" style="max-width: 600px;">
      <h4 class="mb-3">Premium Membership Benefits</h4>
      <ul class="list-group list-group-flush mb-4">
        <li class="list-group-item">Access to exclusive content</li>
        <li class="list-group-item">Priority support</li>
        <li class="list-group-item">Ad-free experience</li>
        <li class="list-group-item">Advanced analytics</li>
      </ul>
      <div class="text-center">
        <p class="mb-3">Unlock all features for just $9.99/month!</p>
        <button class="btn btn-primary" @click="buyPremium">Proceed to Payment</button>
      </div>
    </div>
  </div>
    <AppFooter />
</template>


<script>
import Alert from '@/components/Alert.vue';
import Navbar from '../components/Navbar.vue';
import AppFooter from '../components/Footer.vue';
export default {
  name: 'BuyPremiumView',
  components: { Alert, Navbar, AppFooter },
  data() {
    return {
      alert: {
        visible: false,
        message: '',
        type: 'notification'
      }
    };
  },
  methods: {
    buyPremium() {
      // Placeholder for payment integration (e.g., Stripe, PayPal)
      this.showAlert('Payment processing is not yet implemented', 'alert');
      // Example: Redirect to payment gateway or call backend API
    },
    showAlert(message, type) {
      this.alert = { visible: true, message, type };
    }
  }
};
</script>

<style scoped>
.card {
  background-color: #f8f9fa;
  border-radius: 0.5rem;
  border: 1px solid rgba(75, 94, 252, 0.2);
}

.list-group-item {
  background-color: #ffffff;
  border: none;
  padding: 0.75rem 1rem;
  transition: all 0.3s ease;
}

.list-group-item:hover {
  background-color: rgba(75, 94, 252, 0.1);
}

.btn-primary {
  background-color: #4b5efc;
  border-color: #4b5efc;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  background-color: #2f22a5;
  border-color: #2f22a5;
}

@media (max-width: 576px) {
  .card {
    padding: 1.5rem;
  }

  h2, h4 {
    font-size: 1.5rem;
  }

  .btn-primary {
    font-size: 0.9rem;
  }
}
</style>