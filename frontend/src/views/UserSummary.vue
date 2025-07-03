<template>
  <div>
    <Navbar />

    <div class="container py-4">
      <Alert v-if="alert.visible" :message="alert.message" :type="alert.type" @close="alert.visible = false" class="z-3" />

      <!-- Header Section -->
      <div class="text-center mb-4">
        <h1 class="h3 fw-bold mb-2">Hey Richie, Track Your Progress</h1>
      </div>

      <!-- Quiz Section -->
      <div class="card shadow-sm mb-3">
        <div class="card-body">
          <h5 class="card-title text-muted mb-3">Quiz Stats</h5>
          <div class="row g-3">
            <div class="col-md-4" v-for="(val, label) in quizDisplay" :key="label">
              <div class="d-flex justify-content-between align-items-center py-1">
                <span class="fw-medium">{{ label }}</span>
                <span class="fs-6 fw-bold text-primary">{{ val }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Learning Section -->
      <div class="card shadow-sm mb-3">
        <div class="card-body">
          <h5 class="card-title text-muted mb-3">Learning Stats</h5>
          <div class="row g-3">
            <div class="col-md-3" v-for="(val, label) in learningDisplay" :key="label">
              <div class="d-flex justify-content-between align-items-center py-1">
                <span class="fw-medium">{{ label }}</span>
                <span class="fs-6 fw-bold text-success">{{ val }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Overall Summary -->
      <div class="card shadow-sm mb-3">
        <div class="card-body">
          <h5 class="card-title text-muted mb-3">Overall Summary</h5>
          <div class="row">
            <div class="col-md-6">
              <div v-for="(val, label) in overallDisplay" :key="label" class="d-flex justify-content-between align-items-center py-1 mb-2">
                <span class="fw-medium">{{ label }}</span>
                <span class="fs-6 fw-bold text-warning">{{ val }}</span>
              </div>
            </div>
            <div class="col-md-6 text-center">
              <h6 class="text-muted mb-2">Daily Usage Chart</h6>
              <canvas ref="chartCanvas" width="240" height="240" class="mx-auto"></canvas>
            </div>
          </div>
        </div>
      </div>

      <!-- Email Summary -->
      <div class="card shadow-sm mb-3">
        <div class="card-body text-center py-4">
          <h5 class="mb-2">Email Your Summary</h5>
          <button class="btn btn-primary btn-sm px-4" @click="generateReport">Generate Report</button>
        </div>
      </div>

      <!-- Session History -->
      <div class="card shadow-sm">
        <div class="card-body">
          <h5 class="card-title mb-3">Session History</h5>
          <div v-if="sessions.length === 0" class="text-center text-muted py-3">
            No session history available.
          </div>
          <div v-else class="table-responsive">
            <table class="table table-sm table-hover">
              <thead class="table-light">
                <tr>
                  <th>Login</th>
                  <th>Logout</th>
                  <th>Duration (min)</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="session in sessions" :key="session.session_id">
                  <td>{{ new Date(session.login_at).toLocaleString() }}</td>
                  <td>{{ session.logout_at ? new Date(session.logout_at).toLocaleString() : 'Active' }}</td>
                  <td>{{ session.session_duration_seconds ? (session.session_duration_seconds / 60).toFixed(1) : 'N/A' }}</td>
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
      quizStats: { attempted: 10, averageTime: 15, averageScore: 40 },
      learningStats: { sectionsChosen: 3, modulesCompleted: 8, topicsLearned: 22, totalTime: 3 },
      overallStats: { rank: 343, dailyAverage: 20, streak: 7 },
      alert: { visible: false, message: '', type: 'notification' }
    };
  },
  computed: {
    quizDisplay() {
      return {
        'Attempted': this.quizStats.attempted,
        'Avg Time (min)': this.quizStats.averageTime,
        'Avg Score': this.quizStats.averageScore
      };
    },
    learningDisplay() {
      return {
        'Sections': this.learningStats.sectionsChosen,
        'Modules': this.learningStats.modulesCompleted,
        'Topics': this.learningStats.topicsLearned,
        'Hours': this.learningStats.totalTime
      };
    },
    overallDisplay() {
      return {
        'Rank': this.overallStats.rank,
        'Daily Avg (min)': this.overallStats.dailyAverage,
        'Streak (days)': this.overallStats.streak
      };
    }
  },
  async mounted() {
    await this.fetchSessions();
    await this.fetchUserStats();
    this.drawPieChart();
  },
  methods: {
    async fetchSessions() {
      try {
        const res = await axios.get(`${import.meta.env.VITE_BASE_URL}/api/sessions`, {
          headers: { Authorization: `Bearer ${this.$store.state.token}` }
        });
        this.sessions = res.data;
      } catch {
        this.showAlert('Failed to load session history', 'error');
      }
    },
    async fetchUserStats() {
      try {
        const res = await axios.get(`${import.meta.env.VITE_BASE_URL}/api/user-stats`, {
          headers: { Authorization: `Bearer ${this.$store.state.token}` }
        });
        if (res.data) {
          this.quizStats = { ...this.quizStats, ...res.data.quiz };
          this.learningStats = { ...this.learningStats, ...res.data.learning };
          this.overallStats = { ...this.overallStats, ...res.data.overall };
        }
      } catch {
        console.log('Using default stats');
      }
    },
    drawPieChart() {
      const canvas = this.$refs.chartCanvas;
      const ctx = canvas.getContext('2d');
      const data = [
        { label: 'Learning', value: 45, color: '#4CAF50' },
        { label: 'Quiz', value: 30, color: '#2196F3' },
        { label: 'Reading', value: 15, color: '#FF9800' },
        { label: 'Practice', value: 10, color: '#9C27B0' }
      ];
      const total = data.reduce((sum, item) => sum + item.value, 0);
      const [cx, cy] = [canvas.width / 2, canvas.height / 2];
      const radius = Math.min(cx, cy) - 15;
      let start = -Math.PI / 2;
      data.forEach(item => {
        const angle = (item.value / total) * 2 * Math.PI;
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.arc(cx, cy, radius, start, start + angle);
        ctx.closePath();
        ctx.fillStyle = item.color;
        ctx.fill();
        const mid = start + angle / 2;
        ctx.fillStyle = '#fff';
        ctx.font = '10px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(`${item.value}%`, cx + Math.cos(mid) * radius * 0.65, cy + Math.sin(mid) * radius * 0.65);
        start += angle;
      });
    },
    generateReport() {
      this.showAlert('Report generation started! Check your email soon.', 'success');
    },
    showAlert(message, type) {
      this.alert = { visible: true, message, type };
    }
  }
};
</script>

<style scoped>
.card { border-radius: 0.5rem; }
.card-title { font-weight: 600; border-bottom: 1px solid #eaeaea; padding-bottom: 0.4rem; }
.fs-6 { font-size: 1rem !important; }

.text-primary { color: #4285f4 !important; }
.text-success { color: #34a853 !important; }
.text-warning { color: #fbbc04 !important; }

.btn-primary {
  background-color: #4285f4;
  border-color: #4285f4;
  font-weight: 500;
  border-radius: 0.4rem;
}
.btn-primary:hover {
  background-color: #3367d6;
  border-color: #3367d6;
}

.table th, .table td {
  padding: 0.5rem;
  vertical-align: middle;
  border-color: #e9ecef;
}
.table-sm th, .table-sm td { font-size: 0.85rem; }

@media (max-width: 768px) {
  h1.h3 { font-size: 1.5rem; }
  .fs-6 { font-size: 0.95rem !important; }
  canvas { width: 100% !important; height: auto !important; }
}
</style>
