<template>
  <Navbar />
  <div class="container py-4 px-3 px-md-4">
    <Alert
      v-if="alert.visible"
      :message="alert.message"
      :type="alert.type"
      @close="alert.visible = false"
    />
    <h2 class="mb-4 text-center text-black fw-bold">Admin, Please Manage Topic Content</h2>
    <div class="shadow-lg p-3 p-md-4 mx-auto rounded-4 border" style="max-width: 800px;">
      <div class="form-group mb-3">
        <label class="form-label text-black fw-semibold">Select Lesson</label>
        <select v-model="selectedLesson" class="form-select" @change="fetchModules" :disabled="isSubmitting">
          <option value="">-- Select Lesson --</option>
          <option v-for="lesson in lessons" :key="lesson.lesson_id" :value="lesson.lesson_id">{{ lesson.lesson_name }}</option>
        </select>
      </div>
      <div class="form-group mb-3">
        <label class="form-label text-black fw-semibold">Select Module</label>
        <select v-model="selectedModule" class="form-select" @change="fetchTopics" :disabled="!selectedLesson || isSubmitting">
          <option value="">-- Select Module --</option>
          <option v-for="module in modules" :key="module.module_id" :value="module.module_id">{{ module.module_title }}</option>
        </select>
      </div>

      <div v-if="selectedModule && topics.length" class="mb-4">
        <h4 class="text-black fw-semibold mb-3">Topics for {{ selectedModuleName }}</h4>
        <ul class="list-group">
          <li v-for="topic in topics" :key="topic.topic_id" class="list-group-item d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-2">
            <div class="flex-grow-1">
              <strong>{{ topic.topic_title }}</strong>
              <p v-if="!topic.has_content" class="mb-0 text-muted small">No content uploaded</p>
            </div>
            
            <div class="d-flex align-items-center flex-shrink-0">
              <template v-if="!topic.has_content">
                <input
                  type="file"
                  :ref="'fileInput-' + topic.topic_id"
                  class="form-control form-control-sm w-auto me-2"
                  @change="handleFileChange($event, topic.topic_id)"
                  :disabled="isSubmitting"
                  accept="application/pdf"
                />
                <button
                  class="btn btn-primary btn-sm text-white"
                  @click="uploadContent(topic.topic_id)"
                  :disabled="!files[topic.topic_id] || isSubmitting"
                >
                  <i class="fas fa-upload me-1"></i>Upload
                </button>
              </template>

              <template v-if="topic.has_content">
                <button class="btn btn-success btn-sm me-2 text-white" @click="viewPdf(topic)" :disabled="isSubmitting">
                  <i class="fas fa-eye me-1"></i>View
                </button>
                <button class="btn btn-primary btn-sm me-2 text-white" @click="editContent(topic)" :disabled="isSubmitting">
                  <i class="fas fa-edit me-1"></i>Edit
                </button>
                <button class="btn btn-danger btn-sm text-white" @click="deleteContent(topic.topic_id)" :disabled="isSubmitting">
                  <i class="fas fa-trash-alt me-1"></i>Delete
                </button>
              </template>
            </div>
          </li>
        </ul>
      </div>
    </div>

    <div class="modal fade" id="editContentModal" tabindex="-1" aria-labelledby="editContentModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title text-black fw-semibold" id="editContentModalLabel">
              Update Content for {{ editingTopic?.topic_title }}
            </h5>
            <button type="button" class="btn-close" @click="cancelEdit" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p>Select a new PDF file to replace the existing content.</p>
            <input
              type="file"
              class="form-control"
              ref="editFileInput"
              @change="handleFileChange($event, editingTopic?.topic_id)"
              :disabled="isSubmitting"
              accept="application/pdf"
            />
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="cancelEdit" :disabled="isSubmitting">Cancel</button>
            <button
              type="button"
              class="btn btn-primary text-white"
              @click="updateContent(editingTopic?.topic_id)"
              :disabled="!files[editingTopic?.topic_id] || isSubmitting"
            >
              <i class="fas fa-upload me-2"></i>Submit
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="viewPdfModal" tabindex="-1" aria-labelledby="viewPdfModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-xl">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title text-black fw-semibold" id="viewPdfModalLabel">
              Viewing: {{ viewingTopicTitle }}
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body p-0" style="height: 80vh;">
            <iframe v-if="pdfUrl" :src="pdfUrl" width="100%" height="100%" frameborder="0"></iframe>
            <div v-else class="d-flex justify-content-center align-items-center h-100">
              <p>Loading PDF...</p>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
  <AppFooter />
</template>

<script>
import axios from 'axios';
import Alert from '@/components/Alert.vue';
import Navbar from '@/components/Navbar.vue';
import AppFooter from '@/components/Footer.vue';
import { Modal } from 'bootstrap';

export default {
  name: 'AddContent',
  components: { Alert, Navbar, AppFooter },
  data() {
    return {
      lessons: [],
      modules: [],
      topics: [],
      selectedLesson: '',
      selectedModule: '',
      selectedModuleName: '',
      files: {},
      editingTopic: null,
      isSubmitting: false,
      alert: { visible: false, message: '', type: 'notification' },
      editModal: null,
      viewPdfModal: null, // Modal instance for PDF viewer
      pdfUrl: '',         // URL for the PDF blob
      viewingTopicTitle: '', // Title for the PDF viewer modal
    };
  },
  methods: {
    async fetchLessons() {
      try {
        const response = await axios.get(`${import.meta.env.VITE_BASE_URL}/api/get_all_lessons`, {
          headers: { Authorization: `Bearer ${this.$store.state.token}` }
        });
        this.lessons = response.data;
      } catch (err) {
        this.alert = { visible: true, message: 'Failed to load lessons', type: 'error' };
      }
    },
    async fetchModules() {
      if (!this.selectedLesson) {
        this.modules = [];
        this.selectedModule = '';
        this.topics = [];
        return;
      }
      this.topics = [];
      this.selectedModule = '';
      try {
        const response = await axios.get(`${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/modules`, {
          headers: { Authorization: `Bearer ${this.$store.state.token}` }
        });
        this.modules = response.data;
      } catch (err) {
        this.alert = { visible: true, message: 'Failed to load modules', type: 'error' };
      }
    },
    async fetchTopics() {
      if (!this.selectedModule) {
        this.topics = [];
        return;
      }
      try {
        const response = await axios.get(`${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.selectedModule}/topics`, {
          headers: { Authorization: `Bearer ${this.$store.state.token}` }
        });
        this.topics = response.data;
        const module = this.modules.find(m => m.module_id === parseInt(this.selectedModule));
        this.selectedModuleName = module ? module.module_title : '';
        if (this.topics.length === 0) {
          this.alert = { visible: true, message: 'No topics available for this module', type: 'warning' };
        }
      } catch (err) {
        this.alert = { visible: true, message: 'Failed to load topics', type: 'error' };
      }
    },
    handleFileChange(event, topicId) {
      const file = event.target.files[0];
      if (file) {
        this.files[topicId] = file;
      }
    },
    async uploadContent(topicId) {
      const file = this.files[topicId];
      if (!file) {
        this.alert = { visible: true, message: 'Please select a PDF file to upload', type: 'error' };
        return;
      }
      if (file.type !== 'application/pdf') {
        this.alert = { visible: true, message: 'Only PDF files are allowed', type: 'error' };
        return;
      }
      this.isSubmitting = true;
      const formData = new FormData();
      formData.append('content_file', file);
      try {
        await axios.post(
          `${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.selectedModule}/topic/${topicId}/upload_content`,
          formData,
          { headers: { Authorization: `Bearer ${this.$store.state.token}`, 'Content-Type': 'multipart/form-data' } }
        );
        this.alert = { visible: true, message: 'Content uploaded successfully!', type: 'success' };
        this.files[topicId] = null;
        this.$refs[`fileInput-${topicId}`][0].value = '';
        await this.fetchTopics();
      } catch (err) {
        this.alert = { visible: true, message: `Failed to upload content: ${err.response?.data?.error || err.message}`, type: 'error' };
      } finally {
        this.isSubmitting = false;
      }
    },
    async updateContent(topicId) {
      const file = this.files[topicId];
      if (!file) {
        this.alert = { visible: true, message: 'Please select a new PDF file to upload', type: 'error' };
        return;
      }
       if (file.type !== 'application/pdf') {
        this.alert = { visible: true, message: 'Only PDF files are allowed', type: 'error' };
        return;
      }
      this.isSubmitting = true;
      const formData = new FormData();
      formData.append('content_file', file);
      try {
        await axios.post(
          `${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.selectedModule}/topic/${topicId}/update_content`,
          formData,
          { headers: { Authorization: `Bearer ${this.$store.state.token}`, 'Content-Type': 'multipart/form-data' } }
        );
        this.alert = { visible: true, message: 'Content updated successfully!', type: 'success' };
        this.cancelEdit();
        await this.fetchTopics();
      } catch (err) {
        this.alert = { visible: true, message: `Failed to update content: ${err.response?.data?.error || err.message}`, type: 'error' };
      } finally {
        this.isSubmitting = false;
      }
    },
    async viewPdf(topic) {
      this.pdfUrl = '';
      this.viewingTopicTitle = topic.topic_title;
      this.viewPdfModal.show(); // Show modal with loading indicator

      try {
        const response = await axios.get(
          `${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.selectedModule}/topic/${topic.topic_id}/download_content`,
          {
            headers: { Authorization: `Bearer ${this.$store.state.token}` },
            responseType: 'blob'
          }
        );
        const blob = new Blob([response.data], { type: 'application/pdf' });
        this.pdfUrl = window.URL.createObjectURL(blob);
      } catch (err) {
        this.alert = { visible: true, message: 'Failed to load PDF content', type: 'error' };
        this.viewPdfModal.hide(); // Hide modal on error
      }
    },
    async deleteContent(topicId) {
      if (!confirm('Are you sure you want to delete this content? This action cannot be undone.')) {
        return;
      }
      this.isSubmitting = true;
      try {
        await axios.delete(
          `${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.selectedModule}/topic/${topicId}/delete_content`,
          { headers: { Authorization: `Bearer ${this.$store.state.token}` } }
        );
        this.alert = { visible: true, message: 'Content deleted successfully!', type: 'success' };
        await this.fetchTopics();
      } catch (err) {
        this.alert = { visible: true, message: `Failed to delete content: ${err.response?.data?.error || err.message}`, type: 'error' };
      } finally {
        this.isSubmitting = false;
      }
    },
    editContent(topic) {
      this.editingTopic = topic;
      this.files[topic.topic_id] = null; // Clear any previously selected file for this topic
      this.$nextTick(() => {
        this.editModal.show();
      });
    },
    cancelEdit() {
      if (this.editModal) this.editModal.hide();
      this.editingTopic = null;
      if (this.$refs.editFileInput) this.$refs.editFileInput.value = '';
    },
  },
  mounted() {
    this.fetchLessons();
    
    // Initialize modals
    const editModalEl = document.getElementById('editContentModal');
    if (editModalEl) this.editModal = new Modal(editModalEl);

    const viewPdfModalEl = document.getElementById('viewPdfModal');
    if (viewPdfModalEl) {
      this.viewPdfModal = new Modal(viewPdfModalEl);
      // Cleanup blob URL to prevent memory leaks
      viewPdfModalEl.addEventListener('hidden.bs.modal', () => {
        if (this.pdfUrl) {
          window.URL.revokeObjectURL(this.pdfUrl);
          this.pdfUrl = '';
          this.viewingTopicTitle = '';
        }
      });
    }
  },
};
</script>

<style scoped>
h2, h4, label {
  color: #000000;
}
button.btn, a.text-primary {
  transition: all 0.2s ease;
}
button.btn:hover, a.text-primary:hover {
  filter: brightness(1.15);
  transform: translateY(-1px);
}
button.btn:active, a.text-primary:active {
  transform: translateY(0);
}
input:disabled, select:disabled {
  background-color: #f8f9fa;
  cursor: not-allowed;
}
.list-group-item {
  border-color: #dee2e6;
  padding-top: 1rem;
  padding-bottom: 1rem;
}
@media (max-width: 767px) {
  .list-group-item .d-flex.align-items-center {
    width: 100%;
    justify-content: flex-start;
    margin-top: 0.5rem;
  }
}
</style>