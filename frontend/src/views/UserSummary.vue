<template>
  <div class="container py-5">
    <Alert v-if="alert.visible" :message="alert.message" :type="alert.type" @close="alert.visible = false" />
    
    <h2 class="mb-4 text-center">Your Activity Summary</h2>
    
    <div class="card shadow-sm p-4 mx-auto" style="max-width: 800px;">
      <h4 class="mb-3">Session History</h4>
      <div v-if="sessions.length === 0" class="text-center text-muted">
        No session history available.
      </div>
      <div v-else class="table-responsive">
        <table class="table table-hover">
          <thead>
            <tr>
              <th>Login Time</th>
              <th>Logout Time</th>
              <th>Duration (minutes)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="session in sessions" :key="session.session_id">
              <td>{{ new Date(session.login_at).toLocaleString() }}</td>
              <td>{{ session.logout_at ? new Date(session.logout_at).toLocaleString() : 'Active' }}</td>
              <td>{{ session.session_duration_seconds ? (session.session_duration_seconds / 60).toFixed(2) : 'N/A' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Alert from '@/components/Alert.vue';

export default {
  name: 'UserSummaryView',
  components: { Alert },
  data() {
    return {
      sessions: [],
      alert: {
        visible: false,
        message: '',
        type: 'notification'
      }
    };
  },
  async mounted() {
    await this.fetchSessions();
  },
  methods: {
    async fetchSessions() {
      try {
        const response = await axios.get(`${import.meta.env.VITE_BASE_URL}/api/sessions`, {
          headers: { Authorization: `Bearer ${this.$store.state.token}` }
        });
        this.sessions = response.data;
      } catch (error) {
        this.showAlert('Failed to load session history', 'error');
      }
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

.table {
  background-color: #ffffff;
  border-radius: 0.5rem;
}

.table th, .table td {
  vertical-align: middle;
  padding: 0.75rem;
}

.table-hover tbody tr:hover {
  background-color: rgba(75, 94, 252, 0.1);
}

@media (max-width: 576px) {
  .card {
    padding: 1.5rem;
  }

  h2, h4 {
    font-size: 1.5rem;
  }

  .table {
    font-size: 0.9rem;
  }
}
</style>