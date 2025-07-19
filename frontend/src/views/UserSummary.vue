<template>
  <div class="bg-light min-vh-100">
    <Navbar />

    <div class="container py-4 py-md-5">
      <Alert v-if="alert.visible" :message="alert.message" :type="alert.type" @close="alert.visible = false" class="z-3 position-sticky top-0" />

      <!-- Header Section -->
      <header class="text-center mb-5">
        <h1 class="display-6 fw-bold mb-1">Welcome Back, {{ username }}!</h1>
        <p class="lead text-muted">Here is a summary of your progress.</p>
      </header>

      <!-- Main Stats Grid -->
      <div class="row g-4">
        <!-- Overall Stats Column -->
        <div class="col-lg-4">
          <div class="card h-100 shadow-sm border-0">
            <div class="card-body d-flex flex-column">
              <h5 class="card-title text-muted mb-4"><i class="bi bi-person-check-fill me-2 text-primary"></i>Overall Stats</h5>
              <div class="stat-item" v-for="(item, key) in overallDisplay" :key="key">
                <div class="d-flex justify-content-between align-items-center">
                  <span class="fw-medium text-dark">{{ item.label }}</span>
                  <span class="fs-5 fw-bold text-primary">{{ item.value }}</span>
                </div>
                <hr class="my-3">
              </div>
              <div class="mt-auto">
                <h6 class="text-muted text-center mb-3">Time Allocation (min)</h6>
                <canvas ref="doughnutCanvas" class="chart-canvas"></canvas>
              </div>
            </div>
          </div>
        </div>

        <!-- Quiz and Learning Stats Column -->
        <div class="col-lg-8">
          <!-- Quiz Stats Card -->
          <div class="card shadow-sm border-0 mb-4">
            <div class="card-body">
              <h5 class="card-title text-muted mb-4"><i class="bi bi-patch-question-fill me-2 text-success"></i>Quiz Performance</h5>
              <div class="row g-3 text-center">
                <div class="col-sm-4" v-for="(item, key) in quizDisplay" :key="key">
                  <div class="p-3 bg-light rounded-3">
                    <div class="fs-2 fw-bold text-success">{{ item.value }}</div>
                    <div class="text-muted small">{{ item.label }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Learning Stats Card -->
          <div class="card shadow-sm border-0">
             <div class="card-body">
              <h5 class="card-title text-muted mb-4"><i class="bi bi-book-half me-2 text-info"></i>Learning Progress</h5>
              <div class="row g-3 text-center">
                <div class="col-sm-4" v-for="(item, key) in learningDisplay" :key="key">
                  <div class="p-3 bg-light rounded-3">
                    <div class="fs-2 fw-bold text-info">{{ item.value }}</div>
                    <div class="text-muted small">{{ item.label }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Parental Reports Section -->
      <div v-if="isPremium" class="card shadow-sm border-0 mt-5">
        <div class="card-body p-4 p-md-5 text-center">
          <div class="row justify-content-center align-items-center">
            <div class="col-md-4">
              <h4 class="fw-bold">Parental Reports</h4>
              <p class="text-muted">Download detailed progress reports.</p>
            </div>
            <div class="col-md-8">
              <div class="d-flex flex-column flex-sm-row justify-content-center align-items-center gap-3 mt-3 mt-md-0">
                <select v-model="reportPeriod" class="form-select w-auto">
                    <option value="1d">Last Day</option>
                    <option value="7d">Last 7 Days</option>
                    <option value="30d">Last 30 Days</option>
                    <option value="all">All Time</option>
                </select>
                <button class="btn btn-primary w-100 w-sm-auto" @click="requestReport('analytics')" :disabled="isDownloading">
                    <span v-if="isDownloading && reportTypeToDownload === 'analytics'" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    <i v-else class="bi bi-file-earmark-bar-graph-fill me-2"></i>
                    Analytics
                </button>
                <button v-if="hasParentEmail" class="btn btn-secondary w-100 w-sm-auto" @click="requestReport('chatbot')" :disabled="isDownloading">
                    <span v-if="isDownloading && reportTypeToDownload === 'chatbot'" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    <i v-else class="bi bi-chat-left-text-fill me-2"></i>
                    Chat History
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Session History Table -->
      <div class="card shadow-sm border-0 mt-5">
        <div class="card-header bg-white border-0 pt-3">
          <h5 class="card-title text-muted"><i class="bi bi-clock-history me-2"></i>Recent Sessions</h5>
        </div>
        <div class="card-body">
          <div v-if="sessions.length === 0" class="text-center text-muted py-5">
            <i class="bi bi-emoji-frown fs-1"></i>
            <p class="mt-2">No session history available.</p>
          </div>
          <div v-else class="table-responsive">
            <table class="table table-hover align-middle">
              <thead>
                <tr>
                  <th>Login Time</th>
                  <th>Logout Time</th>
                  <th class="text-end">Duration (min)</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="session in sessions" :key="session.session_id">
                  <td>{{ new Date(session.login_at).toLocaleString() }}</td>
                  <td>{{ session.logout_at ? new Date(session.logout_at).toLocaleString() : 'Active' }}</td>
                  <td class="text-end fw-bold">{{ session.session_duration_seconds ? (session.session_duration_seconds / 60).toFixed(1) : 'N/A' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Parent Password Modal -->
    <div class="modal fade" id="passwordModal" tabindex="-1" aria-labelledby="passwordModalLabel" aria-hidden="true" ref="passwordModal">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="passwordModalLabel">Parental Verification Required</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <p class="text-muted">Please enter the parent password to download this report.</p>
                    <form @submit.prevent="verifyPasswordAndDownload">
                        <div class="mb-3">
                            <input type="password" class="form-control" v-model="parentPassword" placeholder="Enter Password" required>
                        </div>
                         <div v-if="passwordError" class="alert alert-danger p-2 small">{{ passwordError }}</div>
                        <div class="d-flex justify-content-end">
                             <button type="button" class="btn btn-secondary me-2" data-bs-dismiss="modal">Cancel</button>
                             <button type="submit" class="btn btn-primary" :disabled="isVerifying">
                                <span v-if="isVerifying" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                                Verify & Download
                             </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <AppFooter />
  </div>
</template>

<script>
import axios from 'axios';
import { mapState } from 'vuex';
import { Modal } from 'bootstrap';
import Alert from '@/components/Alert.vue';
import Navbar from '../components/Navbar.vue';
import AppFooter from '../components/Footer.vue';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, DoughnutController } from 'chart.js';

// Register the necessary components for Chart.js
ChartJS.register(ArcElement, Tooltip, Legend, DoughnutController);

export default {
  name: 'UserSummaryView',
  components: { Alert, Navbar, AppFooter },
  data() {
    return {
      // User and session data
      username: 'User',
      sessions: [],
      
      // Statistics
      quizStats: { attempted: 0, averageScore: 0, totalTime: 0 },
      learningStats: { modulesCompleted: 0, topicsLearned: 0, totalTime: 0 },
      overallStats: { dailyAverage: 0, streak: 0 },
      
      // Chart.js data
      chartData: { labels: [], datasets: [{ data: [], backgroundColor: ['#0d6efd', '#198754', '#0dcaf0'] }] },
      doughnutChartInstance: null,

      // Report download state
      isPremium: false,
      hasParentEmail: false,
      isDownloading: false,
      reportPeriod: '30d',
      reportTypeToDownload: null,
      
      // UI state
      alert: { visible: false, message: '', type: 'notification' },
      
      // Modal and password verification state
      passwordModalInstance: null,
      parentPassword: '',
      passwordError: '',
      isVerifying: false,
    };
  },
  computed: {
    ...mapState(['token']),
    BASE_URL() { 
      // Access environment variables for the backend URL
      return import.meta.env.VITE_BASE_URL; 
    },
    chartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '70%',
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (context) => `${context.label}: ${context.parsed} min`
            }
          }
        }
      };
    },
    // Computed properties for displaying stats in the template
    quizDisplay() {
      return {
        attempted: { label: 'Quizzes Attempted', value: this.quizStats.attempted },
        avgScore: { label: 'Average Score (%)', value: this.quizStats.averageScore },
        totalTime: { label: 'Total Time (min)', value: this.quizStats.totalTime }
      };
    },
    learningDisplay() {
      return {
        modules: { label: 'Modules Completed', value: this.learningStats.modulesCompleted },
        topics: { label: 'Topics Learned', value: this.learningStats.topicsLearned },
        time: { label: 'Time Spent (min)', value: this.learningStats.totalTime }
      };
    },
    overallDisplay() {
      return {
        dailyAvg: { label: 'Daily Average (min)', value: this.overallStats.dailyAverage },
        streak: { label: 'Streak (days)', value: this.overallStats.streak }
      };
    }
  },
  watch: {
    // Re-render the chart whenever its data changes
    chartData(newData) {
      if (newData && newData.datasets[0].data.length) {
        this.renderDoughnutChart();
      }
    }
  },
  async mounted() {
    // Fetch user data when the component is mounted
    await this.fetchUserStats();
    // Initialize the Bootstrap modal instance
    if (this.$refs.passwordModal) {
        this.passwordModalInstance = new Modal(this.$refs.passwordModal);
    }
  },
  beforeUnmount() {
    // Clean up instances to prevent memory leaks
    if (this.doughnutChartInstance) this.doughnutChartInstance.destroy();
    if (this.passwordModalInstance) this.passwordModalInstance.dispose();
  },
  methods: {
    // Fetch all summary data from the backend
    async fetchUserStats() {
      if (!this.token) return;
      try {
        const res = await axios.get(`${this.BASE_URL}/api/user-summary`, {
          headers: { Authorization: `Bearer ${this.token}` }
        });
        const data = res.data;
        if (data) {
          this.username = data.username;
          this.quizStats = data.quiz;
          this.learningStats = data.learning;
          this.overallStats = data.overall;
          this.sessions = data.sessions;
          this.chartData = data.dailyUsageData;
          this.isPremium = data.isPremium;
          this.hasParentEmail = data.hasParentEmail;
        }
      } catch (error) {
        this.showAlert('Failed to load user statistics. Please try again.', 'error');
        console.error("Error fetching user stats:", error);
      }
    },
    // Render or update the doughnut chart
    renderDoughnutChart() {
      if (this.doughnutChartInstance) {
        this.doughnutChartInstance.destroy();
      }
      const canvas = this.$refs.doughnutCanvas;
      if (canvas) {
        this.doughnutChartInstance = new ChartJS(canvas.getContext('2d'), {
          type: 'doughnut',
          data: this.chartData,
          options: this.chartOptions
        });
      }
    },
    // Show the password modal before downloading
    requestReport(reportType) {
        this.reportTypeToDownload = reportType;
        this.parentPassword = '';
        this.passwordError = '';
        this.passwordModalInstance.show();
    },
    // Verify the password with the backend
    async verifyPasswordAndDownload() {
        if (!this.parentPassword || this.isVerifying) return;
        this.isVerifying = true;
        this.passwordError = '';
        try {
            const response = await axios.post(`${this.BASE_URL}/api/verify-parent-password`, 
                { password: this.parentPassword },
                { headers: { Authorization: `Bearer ${this.token}` } }
            );
            if (response.data.verified) {
                this.passwordModalInstance.hide();
                await this.downloadReport(this.reportTypeToDownload);
            } else {
                 this.passwordError = 'Incorrect password. Please try again.';
            }
        } catch (error) {
            this.passwordError = error.response?.data?.message || 'Verification failed. Please try again.';
        } finally {
            this.isVerifying = false;
        }
    },
    // Download the report after successful verification
    async downloadReport(reportType) {
        if (!this.token || this.isDownloading) return;
        this.isDownloading = true;
        this.showAlert('Generating your report...', 'info');
        try {
            const response = await axios.get(`${this.BASE_URL}/api/user-reports/${reportType}`, {
                headers: { Authorization: `Bearer ${this.token}` },
                params: { period: this.reportPeriod },
                responseType: 'blob' // Important for handling file downloads
            });
            
            const contentDisposition = response.headers['content-disposition'];
            let fileName = `${reportType}_report_${this.reportPeriod}.csv`;
            if (contentDisposition) {
                const fileNameMatch = contentDisposition.match(/filename="(.+)"/);
                if (fileNameMatch && fileNameMatch.length === 2) fileName = fileNameMatch[1];
            }

            this.triggerCsvDownload(response.data, fileName);
            this.showAlert('Report downloaded successfully!', 'success');
        } catch (error) {
            this.showAlert(`Failed to download ${reportType} report. Ensure you have access.`, 'error');
        } finally {
            this.isDownloading = false;
            this.reportTypeToDownload = null;
        }
    },
    // Create a temporary link to trigger the browser's download functionality
    triggerCsvDownload(blobContent, fileName) {
        const link = document.createElement('a');
        const url = URL.createObjectURL(blobContent);
        link.setAttribute('href', url);
        link.setAttribute('download', fileName);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url); // Free up memory
    },
    // Utility method to display alerts to the user
    showAlert(message, type) {
      this.alert = { visible: true, message, type };
    }
  }
};
</script>

<style scoped>
.card {
  border-radius: 0.75rem;
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}
.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.1) !important;
}
.card-title i {
  vertical-align: middle;
}
.chart-canvas {
  max-height: 180px;
  margin: 0 auto;
}
.table thead th {
  font-weight: 600;
  color: #6c757d;
  border: 0;
}
.table tbody tr:last-child td {
  border-bottom: 0;
}
.btn {
  font-weight: 500;
}

/* Mobile Responsive Styles */
@media (max-width: 767.98px) {
  .display-6 {
    font-size: 2rem;
  }
  .card-body {
    padding: 1.25rem;
  }
  .chart-canvas {
    max-height: 160px;
  }
}
</style>
