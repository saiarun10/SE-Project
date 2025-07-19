<template>
  <Navbar />
  <div class="pdf-viewer-container">
    <button class="back-btn" @click="goBack">
      <i class="fas fa-arrow-left"></i> Back To Module
    </button>

    <h2 class="topic-title">Topic: {{ topicTitle }}</h2>

   

    <div v-if="topicContent" class="topic-content" v-html="topicContent">
      </div>

    <iframe
      v-if="pdfPath"
      :src="pdfPath"
      class="pdf-frame"
      frameborder="0"
      @load="onPdfLoad" @error="onPdfError" ></iframe>

    <div v-if="!topicContent && !pdfPath" class="no-content-message">
      Content for this topic is not yet available.
    </div>

    <Alert :visible="alert.visible" :message="alert.message" :type="alert.type" @update:visible="alert.visible = $event" />
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
      currentLessonId: null, 
      currentModuleId: null,
      currentTopicId: null,
      alert: { visible: false, message: '', type: '' },
      
      // Progress tracking states
      currentProgress: 0, // Stores the actual percentage from backend
      isTrackingProgress: false, // Flag to prevent multiple concurrent API calls
      lastTrackedAction: null, // To prevent redundant calls for same action (e.g., multiple 'paused')
      progressTracked: false, // Flag to ensure 'started' is only sent once per topic load
      
      // Debounce and visibility handling
      lastProgressCallTime: 0, // Timestamp of the last trackProgress call
      progressCallDebounceMs: 500, // Minimum delay between non-critical progress calls
      visibilityTimeout: null, // For debouncing visibility changes
      pageVisibilityHandler: null, // Storing ref for removing event listener
    };
  },

  computed: {
    ...mapState(['user', 'token']),
    isAuthenticated() {
      return this.$store.getters.isAuthenticated;
    },
    // Ensure user_id from Vuex is numeric if it's stored as string
    currentUserId() {
        return this.user ? parseInt(this.user.user_id) : null;
    }
  },

  methods: {
    showAlert(message, type = 'info') {
      this.alert = { visible: true, message, type };
    },
    hideAlert() {
      this.alert = { visible: false, message: '', type: '' };
    },

    async loadTopicContent() {
      this.loading = true;
      this.error = null;
      this.hideAlert(); // Clear previous alerts

      if (!this.isAuthenticated) {
        this.error = 'Please log in to view topic content.';
        this.showAlert(this.error, 'error');
        this.loading = false;
        return;
      }

      if (!this.currentLessonId || !this.currentModuleId || !this.currentTopicId) {
        this.error = 'Missing required parameters (lessonId, moduleId, or topicId).';
        this.showAlert(this.error, 'error');
        this.loading = false;
        console.error('Missing parameters:', {
          lessonId: this.currentLessonId,
          moduleId: this.currentModuleId,
          topicId: this.currentTopicId
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

        const response = await axios.get(
          `${import.meta.env.VITE_BASE_URL}/api/lesson/${this.currentLessonId}/module/${this.currentModuleId}/topic/${this.currentTopicId}`,
          config
        );
        const topicData = response.data;
        this.topicTitle = topicData.topic_title || 'Untitled Topic';
        this.topicContent = topicData.topic_content || ''; // Assuming topic_content is HTML string

        if (topicData.has_pdf) {
          this.pdfPath = `${import.meta.env.VITE_BASE_URL}/api/lesson/${this.currentLessonId}/module/${this.currentModuleId}/topic/${this.currentTopicId}/pdf?token=${this.token}`;
          // The @load and @error on the iframe will handle tracking 'content_loaded' for PDFs
        } else {
          this.pdfPath = '';
          // If no PDF, and there is content, track content_loaded immediately
          if (this.topicContent) {
            await this.trackProgress('content_loaded');
          }
        }

        console.log('Topic loaded successfully:', {
          title: this.topicTitle,
          hasContent: !!this.topicContent, // Ensure it's boolean
          hasPdf: !!this.pdfPath, // Ensure it's boolean
          topicId: topicData.topic_id
        });

        // Track 'started' only once per topic load
        if (!this.progressTracked) {
          await this.trackProgress('started');
          this.progressTracked = true; // Mark as started for this topic
        }

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
        
        this.showAlert(this.error, 'error');
      } finally {
        this.loading = false;
      }
    },

    async trackProgress(action) {
      console.log('trackProgress called with action:', action);
      
      const now = Date.now();
      // Define actions that should always go through without debounce or flag checks
      // 'completed' is critical, 'started' should always be initial, 'exited' is final
      const criticalActions = ['completed', 'started', 'exited']; 
      
      // Prevent multiple concurrent API calls
      if (this.isTrackingProgress && !criticalActions.includes(action)) {
          console.log(`Skipping trackProgress for action: ${action}. API call already in progress.`);
          return;
      }
      
      // Debounce non-critical actions
      if (!criticalActions.includes(action) && (now - this.lastProgressCallTime < this.progressCallDebounceMs)) {
            console.log(`Skipping progress call for action: ${action} - too soon after last call.`);
            return;
      }

      // Prevent redundant same-action calls unless it's an 'accessed' or 'content_loaded' (which can update periodically)
      if (this.lastTrackedAction === action && !['accessed', 'content_loaded'].includes(action) && !criticalActions.includes(action)) {
          console.log(`Skipping duplicate trackProgress for action: ${action}.`);
          return;
      }

      this.lastProgressCallTime = now;
      this.isTrackingProgress = true; // Set flag when starting an API call
      this.lastTrackedAction = action; // Remember the last action requested

      if (!this.isAuthenticated) {
        console.error('Not authenticated - cannot track progress');
        this.isTrackingProgress = false;
        return;
      }
      
      if (!this.currentUserId || !this.currentModuleId || !this.currentTopicId) {
        console.error('Missing required IDs for tracking progress:', {
          userId: this.currentUserId,
          moduleId: this.currentModuleId,
          topicId: this.currentTopicId
        });
        this.isTrackingProgress = false;
        return;
      }

      try {
        const config = {
          headers: {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
          }
        };

        const progressData = {
          user_id: this.currentUserId, // Already parsed as int in computed property
          module_id: parseInt(this.currentModuleId), 
          topic_id: parseInt(this.currentTopicId),
          action: action
        };

        // Frontend provides percentage only for specific, explicit actions
        // Let backend determine default percentages for general access actions
        if (action === 'started') {
          progressData.progress_percentage = 25;
        } else if (action === 'completed') {
          progressData.progress_percentage = 100;
        } else if (action === 'accessed') {
          progressData.progress_percentage = 50; // Explicitly set if frontend drives this logic
        } else if (action === 'content_loaded') {
          progressData.progress_percentage = 75; // Explicitly set if frontend drives this logic
        }

        console.log('Sending progress data:', progressData);
        console.log('API URL:', `${import.meta.env.VITE_BASE_URL}/api/user/progress`);

        const response = await axios.post(
          `${import.meta.env.VITE_BASE_URL}/api/user/progress`,
          progressData,
          config
        );

        console.log('Progress tracking response:', response.data);
        console.log('Response status:', response.status);

        if (response.data && response.data.message) {
          console.log('Progress tracking successful:', response.data.message);
          this.currentProgress = response.data.progress_percentage; // Update local progress state from backend
        }

      } catch (err) {
        console.error('Error tracking progress:', err);
        
        if (err.response) {
          console.error('Error response status:', err.response.status);
          console.error('Error response data:', err.response.data);
          
          let errorMessage = 'Failed to track progress. Please try again.';
          if (err.response.status === 409) {
              errorMessage = 'Progress already recorded for this action or there was a conflict.';
          } else if (err.response.data && err.response.data.error) {
              errorMessage = err.response.data.error;
          }
          this.showAlert(errorMessage, 'error');
        } else if (err.request) {
          console.error('Error request:', err.request);
          this.showAlert('Network error. Please check your connection.', 'error');
        } else {
          console.error('An unexpected error occurred:', err.message);
          this.showAlert('An unexpected error occurred.', 'error');
        }
      } finally {
        this.isTrackingProgress = false; // Reset flag regardless of success or failure
      }
    },

    // *** REMOVED markAsCompleted() method ***
    // The logic is now integrated into goBack()

    handleVisibilityChange() {
      // Clear previous timeout to prevent multiple calls if visibility changes rapidly
      if (this.visibilityTimeout) {
        clearTimeout(this.visibilityTimeout);
      }
      
      // Debounce the visibility change events to avoid too many API calls
      this.visibilityTimeout = setTimeout(() => {
        if (document.hidden) {
          this.trackProgress('paused');
        } else {
          this.trackProgress('resumed');
        }
      }, 1000); // 1 second debounce
    },

    onPdfLoad() {
      console.log('PDF loaded successfully - tracking content_loaded');
      // This will now correctly trigger 'content_loaded' for PDFs.
      this.trackProgress('content_loaded');
    },

    onPdfError() {
      console.error('Failed to load PDF');
      this.showAlert('Failed to load PDF content.', 'error');
    },

    async goBack() {
      console.log("Back button clicked. Attempting to mark topic as complete before navigating.");
      
      // Mark the topic as 100% complete if it's not already
      if (this.currentProgress < 100) {
        await this.trackProgress('completed'); // Directly call trackProgress with 'completed' action
        if (this.currentProgress === 100) { // Check if progress actually updated to 100
            this.showAlert('Topic completed! Well done!', 'success');
        } else {
            this.showAlert('Failed to mark topic as complete. Please try again.', 'error');
        }
      } else {
          this.showAlert('Topic is already marked as complete!', 'info');
      }

      // Track 'exited' as a final action before navigating
      await this.trackProgress('exited'); 

      console.log("Navigating back to previous module.");
      this.$router.go(-1); // Navigates back one step in history
    },

    // Optional: Auto-completion logic (adjust timing as needed)
    setupAutoComplete() {
      // Example: Mark as complete after 5 minutes if not already completed and visible
      // This is a basic example and might need more sophisticated logic for real apps
      setTimeout(async () => { // Make async to await trackProgress
        if (!document.hidden && this.currentProgress < 100) { // Check if not hidden AND not already 100%
          console.log('Attempting auto-completion after timeout.');
          await this.trackProgress('completed'); // Directly call trackProgress with 'completed'
          if (this.currentProgress === 100) {
            this.showAlert('Topic auto-completed! Well done!', 'success');
          } else {
            this.showAlert('Failed to auto-complete topic.', 'error');
          }
        }
      }, 5 * 60 * 1000); // 5 minutes = 300000 ms
    },

    async fetchInitialProgress() {
        if (!this.isAuthenticated || !this.currentUserId || !this.currentModuleId || !this.currentTopicId) {
            return;
        }
        try {
            const config = {
                headers: { 'Authorization': `Bearer ${this.token}` }
            };
            // Fetch specific topic progress for this user
            const response = await axios.get(
                `${import.meta.env.VITE_BASE_URL}/api/user/${this.currentUserId}/module/${this.currentModuleId}/topic/${this.currentTopicId}/progress`,
                config
            );
            if (response.data && response.data.progress_percentage !== undefined) {
                this.currentProgress = response.data.progress_percentage;
                this.progressTracked = true; // Assume if we fetched progress, it's already 'started'
                console.log(`Fetched initial progress: ${this.currentProgress}%`);
            }
        } catch (error) {
            console.error('Error fetching initial progress:', error);
            // If 404, it means no record, which is fine, progress remains 0.
        }
    }
  },

  async mounted() {
    // Assign route params to component's data properties
    this.currentLessonId = this.lessonId || this.$route.params.lessonId;
    this.currentModuleId = this.moduleId || this.$route.params.moduleId;
    this.currentTopicId = this.topicId || this.$route.params.topicId;

    console.log('Topic component mounted with params:', {
      lessonId: this.currentLessonId,
      moduleId: this.currentModuleId,
      topicId: this.currentTopicId
    });

    // Setup visibility listener
    this.pageVisibilityHandler = this.handleVisibilityChange.bind(this);
    document.addEventListener('visibilitychange', this.pageVisibilityHandler);

    // Fetch topic content and also current progress
    await this.fetchInitialProgress(); // Fetch existing progress first
    await this.loadTopicContent(); // This will call 'started' if no progress was found
    
    this.setupAutoComplete(); // Set up the auto-completion timer
  },

  async beforeUnmount() {
    // Clear any pending visibility timeout
    if (this.visibilityTimeout) {
      clearTimeout(this.visibilityTimeout);
    }
    
    // Track 'exited' when leaving the topic
    try {
      await this.trackProgress('exited');
    } catch (error) {
      console.error('Error tracking exit:', error);
    }
    
    // Remove the event listener
    if (this.pageVisibilityHandler) {
      document.removeEventListener('visibilitychange', this.pageVisibilityHandler);
    }
  },

  watch: {
    async '$route.params'(newParams, oldParams) {
      // Only re-trigger if the topic itself has changed
      if (newParams.topicId !== oldParams.topicId || newParams.moduleId !== oldParams.moduleId || newParams.lessonId !== oldParams.lessonId) {
        if (this.progressTracked) {
          // Track 'exited' for the old topic before loading the new one
          await this.trackProgress('exited');
        }

        // Update component's data properties for the new route
        this.currentLessonId = newParams.lessonId;
        this.currentModuleId = newParams.moduleId;
        this.currentTopicId = newParams.topicId;
        
        // Reset state for the new topic
        this.topicTitle = '';
        this.topicContent = '';
        this.pdfPath = '';
        this.currentProgress = 0;
        this.progressTracked = false; // Reset for new topic
        this.lastTrackedAction = null;
        this.lastProgressCallTime = 0;
        
        console.log('Route params changed - loading new topic:', {
          lessonId: this.currentLessonId,
          moduleId: this.currentModuleId,
          topicId: this.currentTopicId
        });
        
        // Load content and setup for the new topic
        await this.fetchInitialProgress(); // Fetch progress for new topic
        await this.loadTopicContent();
        this.setupAutoComplete();
      }
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

.back-btn {
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
}

.back-btn:hover {
  background: #3d4145;
}
</style>
