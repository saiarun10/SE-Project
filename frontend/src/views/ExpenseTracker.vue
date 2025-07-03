<template>
  <Navbar />
  <div class="container mt-5" style="font-family: var(--bs-body-font-family);">
    <h2 class="text-center mb-4">Welcome Richie, Start Tracking your Expenses</h2>

    <!-- Enter Passcode Form -->
    <div class="card mx-auto p-4" style="max-width: 400px;">
      <form @submit.prevent="submitPasscode">
        <div class="mb-3">
          <label for="passcode" class="form-label">Enter your Passcode</label>
          <input type="password" class="form-control" id="passcode" v-model="passcode" placeholder="Enter your passcode" required>
        </div>
        <button type="submit" class="btn btn-primary w-100">Submit</button>
      </form>

      <!-- Set Up Passcode Section -->
      <div class="mt-4 text-center">
        <button class="btn btn-secondary" @click="checkPasscodeStatus">Set Up Passcode</button>
        <div class="mt-3" v-if="passcodeStatus === true">
          <p class="text-danger">Passcode already exists</p>
        </div>
        <div class="mt-3" v-else-if="passcodeStatus === false">
          <form @submit.prevent="createPasscode">
            <div class="mb-3">
              <label for="newPasscode" class="form-label">Create New Passcode</label>
              <input type="password" class="form-control" id="newPasscode" v-model="newPasscode" placeholder="Enter new passcode" required>
            </div>
            <button type="submit" class="btn btn-success w-100">Create Passcode</button>
          </form>
        </div>
      </div>
    </div>
  </div>
<Footer/>
</template>

<script>
import { ref } from 'vue';
import Navbar from '@/components/Navbar.vue'
import Footer from '@/components/Footer.vue'
import { useRouter } from 'vue-router'


export default {
  name: 'ExpenseTracker',
  components: {
    Navbar,
    Footer
  },
  setup() {
    const router = useRouter()
    const passcode = ref('');
    const newPasscode = ref('');
    const passcodeStatus = ref(null); // null = not checked, true = exists, false = does not exist
    const errorMessage={"value":""}
    const submitPasscode = async () => {
        try {
            // const response = await fetch('/api/submit_passcode', {
            // method: 'POST',
            // headers: { 'Content-Type': 'application/json' },
            // body: JSON.stringify({ passcode: passcode.value })
            // });
            // const data = await response.json();
            const data = {"success":true}

            if (data.success === true) {
            router.push('/expense-interface'); // Adjust route name as defined in your router
            } else {
            errorMessage.value = 'Wrong passcode';
            }
        } catch (err) {
            console.error('Submit error:', err);
            errorMessage.value = 'An error occurred. Please try again.';
        }
        };

    const checkPasscodeStatus = async () => {
      try {
        // const response = await fetch('/api/get_passcode_status');
        // const data = await response.json();
        const data={"exists":true}
        passcodeStatus.value = data.exists; // expects: { exists: true/false }
      } catch (err) {
        console.error('Status check error:', err);
      }
    };

    const createPasscode = async () => {
      try {
        await fetch('/api/create_passcode', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ passcode: newPasscode.value })
        });
        window.location.reload(); // refresh page to reset state
      } catch (err) {
        console.error('Create error:', err);
      }
    };

    return {
      passcode,
      newPasscode,
      passcodeStatus,
      submitPasscode,
      checkPasscodeStatus,
      createPasscode
    };
  }
};
</script>

<style scoped>
/* Optional styles for cleaner UI */
</style>
