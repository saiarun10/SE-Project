<template>
  <Navbar />
  <div class="lesson-container bg-white">
    
    <div class="container main-content">
      <!-- Header Section -->
      <div class="header-section">
        <h1 class="welcome-title text-center">Let's Learn Richie, {{ userName }}</h1>
        <div class="subtitle">Choose a Topic to learn today</div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        Loading lessons...
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-message">
        <i class="fas fa-exclamation-triangle"></i>
        <p>{{ error }}</p>
        <button @click="fetchLessons" class="btn btn-primary">Try Again</button>
      </div>

      <!-- Lessons Grid -->
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
        </div>
      </div>
    </div>
    
  </div>
  <AppFooter />
</template>

<script>
import Navbar from '@/components/Navbar.vue'
import AppFooter from '@/components/Footer.vue'

export default {
  name: 'Lesson',
  components: {
    Navbar,
    AppFooter
  }, 
  
  data() {
    return {
      loading: true,
      error: null,
      userName: 'User Name',
      lessons: []
    }
  },
  
  methods: {
    async fetchLessons() {
      this.loading = true;
      this.error = null;
      
      try {
        await new Promise(resolve => setTimeout(resolve, 1500));
        this.lessons = [
          { id: 1, title: 'Stock Market', description: 'Learn the basics of stock market investing and trading strategies.', icon: 'fas fa-chart-line', completed: false, inProgress: true },
          { id: 2, title: 'Banking Sector', description: 'Understand banking services, loans, and financial institutions.', icon: 'fas fa-university', completed: true, inProgress: false },
          { id: 3, title: 'Budget', description: 'Master personal budgeting and expense management techniques.', icon: 'fas fa-calculator', completed: false, inProgress: true },
          { id: 4, title: 'Tax', description: 'Navigate tax planning, deductions, and filing requirements.', icon: 'fas fa-file-invoice-dollar', completed: false, inProgress: false },
          { id: 5, title: 'Credit & Interest', description: 'Understand credit scores, interest rates, and loan management.', icon: 'fas fa-credit-card', completed: false, inProgress: true },
          { id: 6, title: 'Financial Planning', description: 'Develop comprehensive financial planning and investment strategies.', icon: 'fas fa-chart-pie', completed: false, inProgress: false }
        ];
      } catch (err) {
        this.error = 'Failed to load lessons. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    selectLesson(lesson) {
      console.log('Selected:', lesson.title);
      
      // Navigate to the lesson detail page
      this.$router.push(`/lesson/${lesson.id}`);
    }
  },
  
  mounted() {
    this.fetchLessons();
  }
}
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