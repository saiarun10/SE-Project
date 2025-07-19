<template>
  <Navbar />
  <div class="lesson-container bg-white">
    <Alert
      v-if="alert.visible"
      :message="alert.message"
      :type="alert.type"
      @close="alert.visible = false"
    />

    <div class="container main-content">
      <div class="header-section">
        <h1 class="welcome-title text-center">Let's Learn Richie, {{ userName }}</h1>
        <div class="subtitle">Choose a Topic to learn today</div>
      </div>

      <div v-if="loading" class="loading">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="text-black mt-2">Loading lessons...</p>
      </div>

      <div v-else-if="error" class="error-message text-center">
        <i class="fas fa-exclamation-triangle text-danger fs-3 mb-2"></i>
        <p class="text-danger">{{ error }}</p>
        <button @click="fetchLessons" class="btn btn-primary">Try Again</button>
      </div>

      <div v-else class="topics-grid">
        <div
          v-for="lesson in lessons"
          :key="lesson.id"
          class="topic-card"
          @click="selectLesson(lesson)"
          :class="{ 'completed': lesson.completed, 'in-progress': lesson.inProgress }"
        >
          <div class="topic-icon">
            <i :class="lesson.icon"></i>
          </div>
          <h3 class="topic-title">{{ lesson.title }}</h3>
          <p class="topic-description">{{ lesson.description }}</p>
          <div v-if="lesson.inProgress" class="progress mt-2">
            <div class="progress-bar bg-warning" role="progressbar" style="width: 50%;" aria-valuenow="50" aria-valuemin="0" aria-valuemax="100"></div>
          </div>
          <span v-if="lesson.completed" class="badge bg-success mt-2">Completed</span>
          <span v-else-if="lesson.inProgress" class="badge bg-info mt-2">In Progress</span>
        </div>
      </div>
    </div>
  </div>
  <AppFooter />
</template>

<script>
import Navbar from '@/components/Navbar.vue';
import AppFooter from '@/components/Footer.vue';
import Alert from '@/components/Alert.vue'; // Assuming you have this component
import axios from 'axios'; // Import axios for API calls
import { mapState } from 'vuex'; // To easily map state from Vuex store

export default {
  name: 'UserLessonView', // Renamed from 'Lesson' for clarity with file name
  components: {
    Navbar,
    AppFooter,
    Alert
  },

  data() {
    return {
      loading: true, // Controls loading spinner visibility
      error: null,   // Holds error message if any
      // userName will be derived from Vuex store via computed property
      lessons: [],   // Stores fetched lesson data
      alert: { visible: false, message: '', type: '' } // For the Alert component
    };
  },

  computed: {
    // Maps the 'user' state from your Vuex store to a local computed property
    // Assumes your Vuex store has a 'user' object in its state and a 'token'
    // e.g., store.state.user = { username: 'John Doe' }
    ...mapState(['user', 'token']),
    userName() {
      return this.user?.username || 'Learner'; // Use user.username if available, otherwise default
    },
    isAuthenticated() {
      // Assuming your Vuex store has a getter for isAuthenticated
      return this.$store.getters.isAuthenticated;
    }
  },

  methods: {
    // Helper to map lesson names to FontAwesome icons (adjust as needed)
    getLessonIcon(lessonName) {
      const iconMap = {
        'Stock Market': 'fas fa-chart-line',
        'Banking Sector': 'fas fa-university',
        'Budget': 'fas fa-calculator',
        'Tax': 'fas fa-file-invoice-dollar',
        'Credit & Interest': 'fas fa-credit-card',
        'Financial Planning': 'fas fa-chart-pie',
        // Add more mappings for your lesson names here
      };
      return iconMap[lessonName] || 'fas fa-book'; // Default icon if no match
    },

    async fetchLessons() {
      this.loading = true; // Show loading indicator
      this.error = null;   // Clear previous errors
      this.alert = { visible: false, message: '', type: '' }; // Clear previous alerts

      if (!this.isAuthenticated) {
        this.error = 'Please log in to view lessons.';
        this.alert = { visible: true, message: this.error, type: 'error' };
        this.loading = false;
        return;
      }

      try {
        // Use the token from Vuex store for authentication
        const response = await axios.get(`${import.meta.env.VITE_BASE_URL}/api/get_all_lessons`, {
          headers: { Authorization: `Bearer ${this.token}` },
        });

        // Transform backend data to match frontend UI requirements
        this.lessons = response.data.map(lesson => ({
          id: lesson.lesson_id,
          title: lesson.lesson_name,
          description: lesson.lesson_description,
          icon: this.getLessonIcon(lesson.lesson_name), // Dynamically assign icon
          completed: false, // Default or fetch from user progress if available
          inProgress: false // Default or fetch from user progress if available
        }));

        if (this.lessons.length === 0) {
          this.alert = { visible: true, message: 'No lessons found.', type: 'info' };
        }

      } catch (err) {
        console.error("Error fetching lessons:", err);
        this.error = err.response?.data?.error || 'Failed to load lessons. Please try again.';
        this.alert = { visible: true, message: this.error, type: 'error' };
      } finally {
        this.loading = false; // Hide loading indicator
      }
    },

    selectLesson(lesson) {
      console.log('Selected:', lesson.title);
      // Navigate to the lesson detail page (ensure your Vue Router is set up for this)
      this.$router.push(`/lesson/${lesson.id}`);
    }
  },

  mounted() {
    // Fetch lessons when the component is mounted
    this.fetchLessons();
  }
};
</script>

<style scoped>

  .lesson-container {
    width: 100vw;
    min-height: 100vh;
    padding: 20px;
    background-color: white;
    overflow-x: hidden; /* Hide horizontal overflow */
  }

  .main-content {
    width: 100%;
    max-width: 1300px;
    margin: 0 auto;
    padding: 0 2rem;
  }

.header-section {
  text-align: center;
  margin-bottom: 3rem;
}

.welcome-title {
  font-size: 2.5rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 1rem;
}

.subtitle {
  background-color: #e9ecef;
  padding: 1rem 2rem;
  border-radius: 25px;
  display: inline-block;
  font-size: 1.1rem;
  color: #666;
}

.topics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2rem;
  margin-bottom: 3rem;
}

.topic-card {
  background: white;
  border-radius: 20px;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.topic-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0,0,0,0.15);
}


.topic-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 1rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.topic-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.5rem;
}

.topic-description {
  color: #666;
  font-size: 0.9rem;
  line-height: 1.4;
  margin-bottom: 1rem;
}

.error-message {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.error-message i {
  font-size: 3rem;
  color: #dc3545;
  margin-bottom: 1rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-primary {
  background-color: #667eea;
  color: white;
}

.btn-primary:hover {
  background-color: #5a6fd8;
}

</style>