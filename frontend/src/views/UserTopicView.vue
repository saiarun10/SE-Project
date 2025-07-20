<template>
  <Navbar />
  <div class="pdf-viewer-container">
    <button class="back-btn" @click="$router.go(-1)">
      <i class="fas fa-arrow-left"></i> Back To Module
    </button>

    <h2 class="topic-title">Topic: {{ topicTitle }}</h2>

    <!-- Show topic content if available -->
    <div v-if="topicContent" class="topic-content">
      {{ topicContent }}
    </div>

    <!-- Show PDF if available -->
    <iframe
      v-if="pdfPath"
      :src="pdfPath"
      class="pdf-frame"
      frameborder="0"
    ></iframe>

    <!-- Show message when no content is available -->
    <div v-if="!topicContent && !pdfPath" class="no-content-message">
      Content for this topic is not yet available.
    </div>

    <!-- Mark as Complete button -->
    <button
      v-if="isAuthenticated"
      class="complete-btn"
      @click="markAsComplete"
      :disabled="loading"
    >
      Mark as Complete
    </button>
  </div>
  <AppFooter />
</template>

<script>
import Navbar from '@/components/Navbar.vue'
import AppFooter from '@/components/Footer.vue'
import Alert from '@/components/Alert.vue'
import axios from 'axios'
import { mapState } from 'vuex'

export default {
  name: 'Topic',
  components: {
    Navbar,
    AppFooter,
    Alert
  },
 
  props: {
    lessonId: String,
    moduleId: String,
    topicId: String
  },
  
  data() {
    return {
      loading: true,
      error: null,
      topicTitle: '',
      topicContent: '',
      pdfPath: '',
      lessonId: null,
      moduleId: null,
      topicId: null,
      alert: { visible: false, message: '', type: '' }
    };
  },

  computed: {
    ...mapState(['user', 'token']),
    isAuthenticated() {
      return this.$store.getters.isAuthenticated;
    }
  },

  methods: {
    async loadTopicContent() {
      this.loading = true;
      this.error = null;
      this.alert = { visible: false, message: '', type: '' };

      if (!this.isAuthenticated) {
        this.error = 'Please log in to view topic content.';
        this.alert = { visible: true, message: this.error, type: 'error' };
        this.loading = false;
        return;
      }

      if (!this.lessonId || !this.moduleId || !this.topicId) {
        this.error = 'Missing required parameters (lessonId, moduleId, or topicId).';
        this.alert = { visible: true, message: this.error, type: 'error' };
        this.loading = false;
        console.error('Missing parameters:', {
          lessonId: this.lessonId,
          moduleId: this.moduleId,
          topicId: this.topicId
        });
        return;
      }

      try {
        const config = {
          headers: {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
          }
        };

        // Fetch topic details from database
        const response = await axios.get(
          `${import.meta.env.VITE_BASE_URL}/api/lesson/${this.lessonId}/module/${this.moduleId}/topic/${this.topicId}`,
          config
        );

        const topicData = response.data;
        this.topicTitle = topicData.topic_title || 'Untitled Topic';
        this.topicContent = topicData.topic_content || '';

        if (topicData.has_pdf) {
          this.pdfPath = `${import.meta.env.VITE_BASE_URL}/api/lesson/${this.lessonId}/module/${this.moduleId}/topic/${this.topicId}/pdf?token=${this.token}`;
        } else {
          this.pdfPath = '';
        }

        console.log('Topic loaded successfully:', {
          title: this.topicTitle,
          hasContent: !!this.topicContent,
          hasPdf: !!this.pdfPath
        });

        // Mark topic as started
        await this.markAsStarted();

      } catch (err) {
        console.error('Error loading topic content:', err);
        
        if (err.response) {
          const status = err.response.status;
          if (status === 404) {
            this.error = 'Topic not found.';
          } else if (status === 403) {
            this.error = 'Access denied. Please check your permissions.';
          } else {
            this.error = err.response.data?.error || `Server error: ${status}`;
          }
        } else if (err.request) {
          this.error = 'Network error. Please check your connection and try again.';
        } else {
          this.error = 'Failed to load topic content. Please try again.';
        }
        
        this.alert = { visible: true, message: this.error, type: 'error' };
      } finally {
        this.loading = false;
      }
    },

    async markAsStarted() {
      try {
        const config = {
          headers: {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
          }
        };

        await axios.post(
          `${import.meta.env.VITE_BASE_URL}/api/progress/lesson/${this.lessonId}/module/${this.moduleId}/topic/${this.topicId}/start`,
          {},
          config
        );

        console.log('Topic marked as started');
      } catch (err) {
        console.error('Error marking topic as started:', err);
        // Don't show error to user, as this is a background operation
      }
    },

    async markAsComplete() {
      if (!this.isAuthenticated) {
        this.alert = { visible: true, message: 'Please log in to mark topic as complete.', type: 'error' };
        return;
      }

      try {
        this.loading = true;
        const config = {
          headers: {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
          }
        };

        const response = await axios.post(
          `${import.meta.env.VITE_BASE_URL}/api/progress/lesson/${this.lessonId}/module/${this.moduleId}/topic/${this.topicId}/complete`,
          {},
          config
        );

        this.alert = { visible: true, message: 'Topic marked as complete!', type: 'success' };
        console.log('Topic marked as complete:', response.data);
      } catch (err) {
        console.error('Error marking topic as complete:', err);
        let errorMessage = 'Failed to mark topic as complete. Please try again.';
        if (err.response) {
          const status = err.response.status;
          if (status === 404) {
            errorMessage = 'Topic not found.';
          } else if (status === 403) {
            errorMessage = 'Access denied. Please check your permissions.';
          } else {
            errorMessage = err.response.data?.error || `Server error: ${status}`;
          }
        } else if (err.request) {
          errorMessage = 'Network error. Please check your connection and try again.';
        }
        this.alert = { visible: true, message: errorMessage, type: 'error' };
      } finally {
        this.loading = false;
      }
    },

    onPdfLoad() {
      console.log('PDF loaded successfully');
    },

    onPdfError() {
      console.error('Failed to load PDF');
      this.alert = { visible: true, message: 'Failed to load PDF content.', type: 'error' };
    },

    goBack() {
      this.$router.push({
        name: 'ModuleView',
        params: {
          id: this.lessonId
        }
      });
    },

    loadStaticContent() {
      const topicMap = {
        1: { title: 'What is a Stock?', file: 'stock-intro.pdf' },
        2: { title: 'How Stock Market Works', file: 'stock-market-works.pdf' },
        3: { title: 'Stock Types', file: 'stock-types.pdf' },
        4: { title: 'Investment Strategies', file: 'investment-strategies.pdf' }
      };

      const topic = topicMap[this.topicId];
      if (topic) {
        this.topicTitle = topic.title;
        this.pdfPath = `/pdfs/${topic.file}`;
      } else {
        this.topicTitle = `Topic ${this.topicId}`;
        this.error = 'Topic content not found.';
      }
      this.loading = false;
    }
  },

  async mounted() {
    this.lessonId = this.lessonId || this.$route.params.lessonId;
    this.moduleId = this.moduleId || this.$route.params.moduleId;
    this.topicId = this.topicId || this.$route.params.topicId;

    console.log('Topic component mounted with params:', {
      lessonId: this.lessonId,
      moduleId: this.moduleId,
      topicId: this.topicId
    });

    await this.loadTopicContent();
  },

  watch: {
    async '$route.params'(newParams) {
      this.lessonId = newParams.lessonId;
      this.moduleId = newParams.moduleId;
      this.topicId = newParams.topicId;
      
      console.log('Route params changed:', {
        lessonId: this.lessonId,
        moduleId: this.moduleId,
        topicId: this.topicId
      });
      
      await this.loadTopicContent();
    }
  }
};
</script>

<style scoped>
.pdf-viewer-container {
  padding: 20px;
  background: #fff;
}
.back-btn {
  margin-bottom: 10px;
}
.topic-title {
  font-size: 24px;
  margin-bottom: 20px;
}
.pdf-frame {
  width: 100%;
  height: 80vh;
  border: 1px solid #ccc;
}

.back-btn, .complete-btn {
  background: #52575b;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.3s ease;
  margin-bottom: 10px;
}

.back-btn:hover, .complete-btn:hover {
  background: #3d4145;
}

.complete-btn:disabled {
  background: #cccccc;
  cursor: not-allowed;
}
</style>