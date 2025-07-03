<template>
  <div>
    <Navbar />
    
    <div class="container py-5">
      <Alert v-if="alert.visible" :message="alert.message" :type="alert.type" @close="alert.visible = false" class="z-3" />
      
      <!-- Header Section -->
      <div class="text-center mb-5">
        <h1 class="display-5 fw-bold mb-3">Hey Richie Track Your Progress</h1>
      </div>

      <!-- Quiz Section -->
      <div class="card shadow-sm mb-4">
        <div class="card-body">
          <h4 class="card-title text-muted mb-4">Quiz Section</h4>
          <div class="row g-4">
            <div class="col-md-4">
              <div class="d-flex justify-content-between align-items-center py-2">
                <span class="fw-medium">Number Of Quiz Attempted:</span>
                <span class="fs-4 fw-bold text-primary">{{ quizStats.attempted }}</span>
              </div>
            </div>
            <div class="col-md-4">
              <div class="d-flex justify-content-between align-items-center py-2">
                <span class="fw-medium">Average Time of Quiz:</span>
                <span class="fs-4 fw-bold text-primary">{{ quizStats.averageTime }} Minutes</span>
              </div>
            </div>
            <div class="col-md-4">
              <div class="d-flex justify-content-between align-items-center py-2">
                <span class="fw-medium">Average Score:</span>
                <span class="fs-4 fw-bold text-primary">{{ quizStats.averageScore }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Learning Section -->
      <div class="card shadow-sm mb-4">
        <div class="card-body">
          <h4 class="card-title text-muted mb-4">Learning Section</h4>
          <div class="row g-4">
            <div class="col-md-3">
              <div class="d-flex justify-content-between align-items-center py-2">
                <span class="fw-medium">Sections Chosen:</span>
                <span class="fs-4 fw-bold text-success">{{ learningStats.sectionsChosen }}</span>
              </div>
            </div>
            <div class="col-md-3">
              <div class="d-flex justify-content-between align-items-center py-2">
                <span class="fw-medium">Modules Completed:</span>
                <span class="fs-4 fw-bold text-success">{{ learningStats.modulesCompleted }}</span>
              </div>
            </div>
            <div class="col-md-3">
              <div class="d-flex justify-content-between align-items-center py-2">
                <span class="fw-medium">Topics Learned:</span>
                <span class="fs-4 fw-bold text-success">{{ learningStats.topicsLearned }}</span>
              </div>
            </div>
            <div class="col-md-3">
              <div class="d-flex justify-content-between align-items-center py-2">
                <span class="fw-medium">Total Learning Time:</span>
                <span class="fs-4 fw-bold text-success">{{ learningStats.totalTime }} Hours</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Overall Summary -->
      <div class="card shadow-sm mb-4">
        <div class="card-body">
          <h4 class="card-title text-muted mb-4">Overall Summary</h4>
          <div class="row">
            <div class="col-md-6">
              <div class="d-flex justify-content-between align-items-center py-2 mb-3">
                <span class="fw-medium">Your Rank:</span>
                <span class="fs-4 fw-bold text-warning">{{ overallStats.rank }}</span>
              </div>
              <div class="d-flex justify-content-between align-items-center py-2 mb-3">
                <span class="fw-medium">Daily Average Time:</span>
                <span class="fs-4 fw-bold text-warning">{{ overallStats.dailyAverage }}Minutes</span>
              </div>
              <div class="d-flex justify-content-between align-items-center py-2 mb-3">
                <span class="fw-medium">Streak:</span>
                <span class="fs-4 fw-bold text-warning">{{ overallStats.streak }} days</span>
              </div>
            </div>
            <div class="col-md-6">
              <div class="text-center">
                <h6 class="text-muted mb-3">Daily Usage Distribution</h6>
                <canvas ref="chartCanvas" width="300" height="300" class="mx-auto"></canvas>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Email Summary Section -->
      <div class="card shadow-sm mb-4">
        <div class="card-body text-center py-5">
          <h4 class="mb-3">Get Summary On Your Email</h4>
          <button class="btn btn-primary btn-lg px-5" @click="generateReport">
            Generate Report
          </button>
        </div>
      </div>

      <!-- Session History (Original Content) -->
      <div class="card shadow-sm">
        <div class="card-body">
          <h4 class="card-title mb-4">Session History</h4>
          <div v-if="sessions.length === 0" class="text-center text-muted py-4">
            No session history available.
          </div>
          <div v-else class="table-responsive">
            <table class="table table-hover">
              <thead class="table-light">
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
    </div>

    <AppFooter />
  </div>
</template>

<script>
import axios from 'axios';
import Alert from '@/components/Alert.vue';
import Navbar from '../components/Navbar.vue';
import AppFooter from '../components/Footer.vue';

export default {
  name: 'UserSummaryView',
  components: { Alert, Navbar, AppFooter },
  data() {
    return {
      sessions: [],
      quizStats: {
        attempted: 10,
        averageTime: 15,
        averageScore: 40
      },
      learningStats: {
        sectionsChosen: 3,
        modulesCompleted: 8,
        topicsLearned: 22,
        totalTime: 3
      },
      overallStats: {
        rank: 343,
        dailyAverage: 20,
        streak: 7
      },
      alert: {
        visible: false,
        message: '',
        type: 'notification'
      }
    };
  },
  async mounted() {
    await this.fetchSessions();
    await this.fetchUserStats();
    this.drawPieChart();
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
    async fetchUserStats() {
      try {
        // Replace with your actual API endpoints
        const response = await axios.get(`${import.meta.env.VITE_BASE_URL}/api/user-stats`, {
          headers: { Authorization: `Bearer ${this.$store.state.token}` }
        });
        
        // Update stats with real data
        if (response.data) {
          this.quizStats = { ...this.quizStats, ...response.data.quiz };
          this.learningStats = { ...this.learningStats, ...response.data.learning };
          this.overallStats = { ...this.overallStats, ...response.data.overall };
        }
      } catch (error) {
        console.log('Using default stats data');
      }
    },
    drawPieChart() {
      const canvas = this.$refs.chartCanvas;
      const ctx = canvas.getContext('2d');
      
      // Chart data
      const data = [
        { label: 'Learning', value: 45, color: '#4CAF50' },
        { label: 'Quiz', value: 30, color: '#2196F3' },
        { label: 'Reading', value: 15, color: '#FF9800' },
        { label: 'Practice', value: 10, color: '#9C27B0' }
      ];
      
      const total = data.reduce((sum, item) => sum + item.value, 0);
      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;
      const radius = Math.min(centerX, centerY) - 20;
      
      let currentAngle = -Math.PI / 2;
      
      // Draw pie slices
      data.forEach(item => {
        const sliceAngle = (item.value / total) * 2 * Math.PI;
        
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
        ctx.closePath();
        ctx.fillStyle = item.color;
        ctx.fill();
        
        // Draw labels
        const labelAngle = currentAngle + sliceAngle / 2;
        const labelX = centerX + Math.cos(labelAngle) * (radius * 0.7);
        const labelY = centerY + Math.sin(labelAngle) * (radius * 0.7);
        
        ctx.fillStyle = '#fff';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(`${item.value}%`, labelX, labelY);
        
        currentAngle += sliceAngle;
      });
      
      // Draw legend
      const legendY = canvas.height - 60;
      data.forEach((item, index) => {
        const legendX = 20 + (index * 70);
        
        ctx.fillStyle = item.color;
        ctx.fillRect(legendX, legendY, 12, 12);
        
        ctx.fillStyle = '#333';
        ctx.font = '10px Arial';
        ctx.textAlign = 'left';
        ctx.fillText(item.label, legendX + 16, legendY + 10);
      });
    },
    generateReport() {
      this.showAlert('Report generation started! You will receive an email shortly.', 'success');
    },
    showAlert(message, type) {
      this.alert = { visible: true, message, type };
    }
  }
};
</script>

<style scoped>
.card {
  background-color: #ffffff;
  border-radius: 0.75rem;
  border: 1px solid rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.15s ease-in-out;
}

.card:hover {
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
}

.card-title {
  font-weight: 600;
  color: #6c757d;
  border-bottom: 2px solid #e9ecef;
  padding-bottom: 0.5rem;
}

.text-primary {
  color: #4285f4 !important;
}

.text-success {
  color: #34a853 !important;
}

.text-warning {
  color: #fbbc04 !important;
}

.btn-primary {
  background-color: #4285f4;
  border-color: #4285f4;
  font-weight: 500;
  border-radius: 0.5rem;
}

.btn-primary:hover {
  background-color: #3367d6;
  border-color: #3367d6;
}

.table {
  background-color: #ffffff;
  border-radius: 0.5rem;
}

.table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #495057;
  border-top: none;
}

.table td, .table th {
  vertical-align: middle;
  padding: 0.75rem;
  border-color: #e9ecef;
}

.table-hover tbody tr:hover {
  background-color: rgba(66, 133, 244, 0.1);
}

@media (max-width: 768px) {
  .display-5 {
    font-size: 2rem;
  }
  
  .fs-4 {
    font-size: 1.1rem !important;
  }
  
  .card-body {
    padding: 1rem;
  }
  
  .row.g-4 > * {
    margin-bottom: 1rem;
  }
  
  canvas {
    max-width: 100%;
    height: auto;
  }
}

@media (max-width: 576px) {
  .container {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  
  .d-flex.justify-content-between {
    flex-direction: column;
    align-items: flex-start !important;
  }
  
  .d-flex.justify-content-between span:last-child {
    margin-top: 0.25rem;
    font-size: 1.2rem !important;
  }
}
</style>