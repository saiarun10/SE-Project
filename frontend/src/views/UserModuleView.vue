<template>
  <Navbar />
  <div class="modules-container bg-white">
    
    <!-- Back Button -->
    <div class="back-section">
      <button @click="goBack" class="back-btn">
        <i class="fas fa-arrow-left"></i> Back to Lessons
      </button>
    </div>

    
    <div class="container main-content">

      <!-- Header Section -->
      <div class="header-section">
        
        <h1 class="page-title">Learn {{ currentLesson?.title }}, {{ userName }}</h1>

       
        <div class="topic-icon-header" @click="openCalculator">
          <img src="@/assets/calculator.png" alt="Calculator" class="calculator-icon" />
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        Loading modules...
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-message">
        <i class="fas fa-exclamation-triangle"></i>
        <p>{{ error }}</p>
        <button @click="fetchModules" class="btn btn-primary">Try Again</button>
      </div>

      <!-- Modules List -->
      <div v-else class="modules-list">
        <div 
          v-for="(module, index) in currentLesson.modules"

          :key="module.id"
          class="module-item"
          :class="{ 
            'completed': module.completed, 
            'in-progress': module.inProgress,
            'locked': module.locked,
            'expanded': expandedModule === module.id
          }"
        >
          <!-- Module Header -->
          <div class="module-header" @click="toggleModule(module)">
            <div class="module-number">
              <span v-if="module.completed" class="status-icon completed">
                <i class="fas fa-check"></i>
              </span>
              <span v-else-if="module.inProgress" class="status-icon in-progress">
                <i class="fas fa-play"></i>
              </span>
              <span v-else class="status-icon locked">
                <i class="fas fa-lock"></i>
              </span>
            </div>

            <div class="module-content">
              <h3 class="module-title">{{ module.title }}</h3>
              <p class="module-description">{{ module.description }}</p>
            </div>

            <div class="module-action">
              <i class="fas fa-chevron-down" :class="{ 'rotated': expandedModule === module.id }"></i>
            </div>
          </div>

          <!-- Topics Dropdown -->
          <div 
            v-if="expandedModule === module.id" 
            class="topics-dropdown"
            :class="{ 'show': expandedModule === module.id }"
          >
            <div class="topics-header">
              <h4>Topics in this module:</h4>
            </div>
            <div class="topics-list">
              <div 
                v-for="(topic, topicIndex) in module.topics" 
                :key="topic.id"
                class="topic-item"
                @click.stop="selectTopic(module, topic)"
                :class="{ 

                }"
              >
                <div class="topic-icon">
                  <i v-if="topic.completed" class="fas fa-check-circle text-success"></i>
                  <i v-else-if="topic.inProgress" class="fas fa-play-circle text-warning"></i>
                  <i v-else class="fas fa-circle text-muted"></i>
                </div>
                <div class="topic-content">
                  <h5 class="topic-title">{{ topic.title }}</h5>
                  <p class="topic-description">{{ topic.description }}</p>
                  <div class="topic-meta">
                    <span class="topic-duration">
                      <i class="fas fa-clock"></i>
                      {{ topic.duration }}
                    </span>
                    <span class="topic-type">
                      <i class="fas fa-file-alt"></i>
                      {{ topic.type }}
                    </span>
                  </div>
                </div>
                <div class="topic-action">
                  <i class="fas fa-arrow-right"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Floating Calculator Window -->
    <div v-if="showCalculator" class="floating-calculator-overlay" @click="closeCalculator">
      <div class="floating-calculator-window" @click.stop>
        <div class="floating-calculator-header">
          <h3>Calculator</h3>
          <button @click="closeCalculator" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="floating-calculator-content">
          <Calculator />
        </div>
      </div>
    </div>

    
  </div>
  <AppFooter />
</template>

<script>
import Navbar from '@/components/Navbar.vue'
import AppFooter from '@/components/Footer.vue'
import Alert from '@/components/Alert.vue'
import Calculator from '@/views/CalculatorView.vue' 
import axios from 'axios'
import { mapState } from 'vuex'

export default {
  name: 'Module',
  components: {
    Navbar,
    AppFooter,
    Alert,
    Calculator
  },
  props: ['id'],
  
  data() {
    return {
      loading: true,
      error: null,
      currentLesson: null,
      lessonId: null,
      expandedModule: null,
      showCalculator: false,
      modules: [],
      topics: {}, // This should be reactive in Vue 3
      alert: { visible: false, message: '', type: '' }
    }
  },

  computed: {
    ...mapState(['user', 'token']),
    userName() {
      return this.user?.username || 'Student';
    },
    isAuthenticated() {
      return this.$store.getters.isAuthenticated;
    }
  },
  
  methods: {
    async loadLessonContent() {
      this.loading = true;
      this.error = null;
      this.alert = { visible: false, message: '', type: '' };
      
      if (!this.isAuthenticated) {
        this.error = 'Please log in to view lesson content.';
        this.alert = { visible: true, message: this.error, type: 'error' };
        this.loading = false;
        return;
      }

      try {
        const config = {
          headers: {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
          }
        };

        // Fetch modules for this lesson
        const modulesResponse = await axios.get(
          `${import.meta.env.VITE_BASE_URL}/api/${this.lessonId}/modules`,
          config
        );

        this.modules = modulesResponse.data;

        if (this.modules.length === 0) {
          this.alert = { visible: true, message: 'No modules found for this lesson.', type: 'info' };
        }

        // Fetch topics for each module
        for (const module of this.modules) {
          try {
            const topicsResponse = await axios.get(
              `${import.meta.env.VITE_BASE_URL}/api/${this.lessonId}/module/${module.module_id}/topics`,
              config
            );
            
            // Store topics with module_id as key (Vue 3 way)
            this.topics[module.module_id] = topicsResponse.data;
          } catch (topicError) {
            console.error(`Error fetching topics for module ${module.module_id}:`, topicError);
            this.topics[module.module_id] = [];
          }
        }   

        // Create currentLesson object to maintain compatibility with existing template
        this.currentLesson = {
          id: parseInt(this.lessonId),
          title: this.getLessonTitle(this.lessonId),
          modules: this.modules.map(module => ({
            id: module.module_id,
            title: module.module_title,
            description: module.module_description,
            topics: (this.topics[module.module_id] || []).map(topic => ({
              id: topic.topic_id,
              title: topic.topic_title,
              description: topic.topic_title,
              hasContent: topic.has_content
            }))
          }))
        };

        console.log('Loaded lesson content:', {
          lessonId: this.lessonId,
          modulesCount: this.modules.length,
          currentLesson: this.currentLesson
        });

      } catch (err) {
        console.error('Error loading lesson content:', err);
        this.error = err.response?.data?.error || 'Failed to load lesson content. Please try again.';
        this.alert = { visible: true, message: this.error, type: 'error' };
      } finally {
        this.loading = false;
      }
    },

    // Helper method to get lesson title (you can customize this based on your needs)
    getLessonTitle(lessonId) {
      const lessonTitles = {
        1: 'Stock Market',
        2: 'Banking Sector',
        3: 'Budget',
        4: 'Tax',
        5: 'Credit & Interest',
        6: 'Financial Planning'
      };
      return lessonTitles[lessonId] || `Lesson ${lessonId}`;
    },

    openCalculator() {
      this.showCalculator = true;
    },
    
    closeCalculator() {
      this.showCalculator = false;
    },

      selectTopic(module, topic) {
      // Handle both raw database objects and mapped objects
      const moduleId = module.id || module.module_id;
      const topicId = topic.id || topic.topic_id;
      
      // If moduleId is still undefined, try to find it from the expanded module
      const finalModuleId = moduleId || this.expandedModule;
      
      // Debug logging to see what we're working with
      console.log('selectTopic called with:', {
        module: module,
        topic: topic,
        moduleId: moduleId,
        topicId: topicId
      });

      // Make sure we have all required parameters
      if (!this.lessonId || !moduleId || !topicId) {
        console.error('Missing required parameters for topic navigation:', {
          lessonId: this.lessonId,
          moduleId: finalModuleId,
          topicId: topicId
        });
        this.alert = { visible: true, message: 'Missing required parameters for navigation.', type: 'error' };
        return;
      }

      this.$router.push({
        name: 'LearnTopic',
        params: {
          lessonId: this.lessonId,
          moduleId: finalModuleId,
          topicId: topicId
        }
      });
          },

    selectModule(module) {
      if (module.locked) {
        this.alert = { visible: true, message: 'This module is locked. Complete previous modules first.', type: 'warning' };
        return;
      }
      
      console.log('Selected module:', module.title);
      // Navigate to the specific module content
      this.$router.push({
        name: 'ModuleContent',
        params: {
          lessonId: this.lessonId,
          moduleId: module.id
        }
      });
    },

    toggleModule(module) {
      if (this.expandedModule === module.id) {
        this.expandedModule = null; // collapse
      } else {
        this.expandedModule = module.id; // expand
      }
    },

    goBack() {
      this.$router.push('/lesson');
    }
  },
  
  async mounted() {
    this.lessonId = this.$route.params.id;
    console.log('Module component mounted with Lesson ID:', this.lessonId);
    await this.loadLessonContent();
  },
  
  watch: {
    async '$route.params.id'(newId) {
      this.lessonId = newId;
      await this.loadLessonContent();
    }
  }
}
</script>

<style scoped>
.modules-container {
  width: 100vw;
  min-height: 100vh;
  padding: 20px;
  background-color: white;
  overflow-x: hidden;
}

.main-content {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.header-section {
  margin-bottom: 2rem;
}

.breadcrumb {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.back-btn {
  background: #52575b;
  border: none;
  font-size: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  Color: white;
  cursor: pointer;
  margin-right: 1rem;
  padding: 10px 20px;
  border-radius: 8px;
  transition: background-color 0.3s ease;
}

.back-btn:hover {
  background: #3d4145;
}

.page-title {
  font-size: 2rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 1rem;
}

.topic-icon-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 2rem;
}

.topic-icon-header i {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.modules-list {
  margin-bottom: 3rem;
}

.module-item {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  margin-bottom: 1rem;
  transition: all 0.3s ease;
  overflow: hidden;
}

.module-item:hover:not(.locked) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  border-color: #667eea;
}

.module-item.locked {
  opacity: 0.6;
}

.module-item.expanded {
  border-color: #667eea;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.module-header {
  display: flex;
  align-items: center;
  padding: 1.5rem;
  cursor: pointer;
}

.module-header.locked {
  cursor: not-allowed;
}

.module-number {
  margin-right: 1.5rem;
}

.status-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
}

.status-icon.completed {
  background-color: #28a745;
  color: white;
}

.status-icon.in-progress {
  background-color: #ffc107;
  color: white;
}

.status-icon.locked {
  background-color: #6c757d;
  color: white;
}

.module-content {
  flex: 1;
}

.module-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.5rem;
}

.module-description {
  color: #666;
  font-size: 0.9rem;
  line-height: 1.4;
  margin: 0;
}

.module-action {
  color: #666;
  font-size: 1rem;
  transition: transform 0.3s ease;
}

.module-action .fa-chevron-down.rotated {
  transform: rotate(180deg);
}

/* Topics Dropdown Styles */
.topics-dropdown {
  background: #f8f9fa;
  border-top: 1px solid #e9ecef;
  padding: 0;
  max-height: 0;
  overflow: hidden;
  transition: all 0.3s ease;
}

.topics-dropdown.show {
  max-height: 1000px;
  padding: 1rem 1.5rem;
}

.topics-header {
  margin-bottom: 1rem;
}

.topics-header h4 {
  color: #333;
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
}

.topics-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.topic-item {
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.topic-item:hover:not(.topic-locked) {
  border-color: #667eea;
  transform: translateX(5px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.topic-item.topic-locked {
  opacity: 0.6;
  cursor: not-allowed;
}

.topic-icon {
  margin-right: 1rem;
  font-size: 1.2rem;
}

.text-success {
  color: #28a745 !important;
}

.text-warning {
  color: #ffc107 !important;
}

.text-muted {
  color: #6c757d !important;
}

.topic-content {
  flex: 1;
}

.topic-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 0.25rem 0;
}

.topic-description {
  font-size: 0.85rem;
  color: #666;
  margin: 0 0 0.5rem 0;
  line-height: 1.3;
}

.topic-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: #999;
}

.topic-duration, .topic-type {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.topic-action {
  color: #666;
  font-size: 0.9rem;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.topic-item:hover .topic-action {
  opacity: 1;
}

.loading {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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
.button-container {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  padding: 10px;
}

.topic-icon-header {
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  padding: 8px;
  border-radius: 8px;
  border: 1px solid #ddd;
  background-color: #fff;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-left: 1000px;
}

.topic-icon-header:hover {
  background-color: #f8f9fa;
  border-color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.calculator-icon {
  width: 48px;
  height: 48px;
  object-fit: cover;
  border-radius: 4px;
}

/* Floating Calculator Styles */
.floating-calculator-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

.floating-calculator-window {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  max-width: 400px;
  width: 90%;
  max-height: 80vh;
  overflow: hidden;
  animation: slideIn 0.3s ease;
}

.floating-calculator-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.floating-calculator-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.2rem;
}

.close-btn {
  background: #dc3545;
  border: none;
  font-size: 1.4rem;
  color: white;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.2s ease;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(220, 53, 69, 0.2);
}

.close-btn:hover {
  background-color: #c82333;
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(220, 53, 69, 0.3);
}

.floating-calculator-content {
  padding: 0;
  max-height: calc(80vh - 70px);
  overflow-y: auto;
}

/* Responsive Design */
@media (max-width: 768px) {
  .main-content {
    padding: 0 1rem;
  }

  .page-title {
    font-size: 1.5rem;
  }

  .module-header {
    padding: 1rem;
  }

  .module-number {
    margin-right: 1rem;
  }

  .topic-item {
    padding: 0.75rem;
  }

  .topic-meta {
    flex-direction: column;
    gap: 0.25rem;
  }

  .topics-dropdown.show {
    padding: 1rem;
  }

 



}
</style>
