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
    <div class="shadow-lg p-3 p-md-4 mx-auto rounded-4 border" style="max-width: 720px;">
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
      <div class="form-group mb-3">
        <label class="form-label text-black fw-semibold">Select Topic</label>
        <select v-model="selectedTopic" class="form-select" @change="updateSelectedTopicName" :disabled="!selectedModule || isSubmitting">
          <option value="">-- Select Topic --</option>
          <option v-for="topic in topics" :key="topic.topic_id" :value="topic.topic_id">{{ topic.topic_title }}</option>
        </select>
      </div>
      <div v-if="selectedTopic" class="mb-4">
        <h4 class="text-black fw-semibold mb-3">Manage Content for {{ selectedTopicName }}</h4>
        <div class="form-group mb-3">
          <label class="form-label text-black">{{ editingContent ? 'Update Content File' : 'Upload Content File' }}</label>
          <input type="file" class="form-control" ref="fileInput" @change="handleFileChange" :disabled="isSubmitting" accept="application/pdf" />
        </div>
        <div class="text-center">
          <button class="btn btn-primary text-white" @click="uploadContent" :disabled="!selectedTopic || !file || isSubmitting">
            <i class="fas fa-upload me-2"></i>{{ editingContent ? 'Update Content' : 'Upload Content' }}
          </button>
        </div>
      </div>
      <div v-if="selectedModule && topics.length" class="mb-4">
        <h4 class="text-black fw-semibold mb-3">Topics for {{ selectedModuleName }}</h4>
        <ul class="list-group">
          <li v-for="topic in topics" :key="topic.topic_id" class="list-group-item d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center">
            <div>
              <strong>{{ topic.topic_title }}</strong>
              <p class="mb-0 text-muted" v-if="topic.has_content">
                <a href="#" @click.prevent="viewPdf(topic.topic_id)" class="text-primary">View PDF Content</a>
              </p>
              <p class="mb-0 text-muted" v-else>No content uploaded</p>
            </div>
            <div class="mt-2 mt-md-0">
              <button v-if="topic.has_content" class="btn btn-warning btn-sm me-2 text-white" @click="editContent(topic)" :disabled="isSubmitting">
                <i class="fas fa-edit me-1"></i>Edit Content
              </button>
            </div>
          </li>
        </ul>
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
      selectedTopic: '',
      selectedModuleName: '',
      selectedTopicName: '',
      file: null,
      isSubmitting: false,
      editingContent: false,
      alert: { visible: false, message: '', type: 'notification' },
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
        this.selectedTopic = '';
        this.selectedModuleName = '';
        this.selectedTopicName = '';
        return;
      }
      try {
        const response = await axios.get(`${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/modules`, {
          headers: { Authorization: `Bearer ${this.$store.state.token}` }
        });
        this.modules = response.data;
        const module = this.modules.find(m => m.module_id === parseInt(this.selectedModule));
        this.selectedModuleName = module ? module.module_title : '';
        this.selectedModule = '';
        this.topics = [];
        this.selectedTopic = '';
        this.selectedTopicName = '';
      } catch (err) {
        this.alert = { visible: true, message: 'Failed to load modules', type: 'error' };
      }
    },
    async fetchTopics() {
      if (!this.selectedModule) {
        this.topics = [];
        this.selectedTopic = '';
        this.selectedTopicName = '';
        return;
      }
      try {
        const response = await axios.get(`${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.selectedModule}/topics`, {
          headers: { Authorization: `Bearer ${this.$store.state.token}` }
        });
        this.topics = response.data;
        const module = this.modules.find(m => m.module_id === parseInt(this.selectedModule));
        this.selectedModuleName = module ? module.module_title : '';
        this.selectedTopic = '';
        this.selectedTopicName = '';
      } catch (err) {
        this.alert = { visible: true, message: 'Failed to load topics', type: 'error' };
      }
    },
    handleFileChange(event) {
      this.file = event.target.files[0];
    },
    async uploadContent() {
      if (!this.file || !this.selectedLesson || !this.selectedModule || !this.selectedTopic) {
        this.alert = { visible: true, message: 'Please select a lesson, module, topic, and upload a PDF file', type: 'error' };
        return;
      }
      if (!this.file.type.includes('application/pdf')) {
        this.alert = { visible: true, message: 'Only PDF files are allowed', type: 'error' };
        return;
      }
      this.isSubmitting = true;
      const formData = new FormData();
      formData.append('content_file', this.file);
      try {
        const endpoint = this.editingContent
          ? `${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.selectedModule}/topic/${this.selectedTopic}/update_content`
          : `${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.selectedModule}/topic/${this.selectedTopic}/upload_content`;
        await axios.post(endpoint, formData, {
          headers: { Authorization: `Bearer ${this.$store.state.token}`, 'Content-Type': 'multipart/form-data' }
        });
        this.alert = { visible: true, message: this.editingContent ? 'Content updated successfully' : 'Content uploaded successfully', type: 'success' };
        this.file = null;
        this.$refs.fileInput.value = '';
        this.editingContent = false;
        await this.fetchTopics();
        this.updateSelectedTopicName();
      } catch (err) {
        this.alert = { visible: true, message: this.editingContent ? 'Failed to update content' : 'Failed to upload content', type: 'error' };
      } finally {
        this.isSubmitting = false;
      }
    },
    async viewPdf(topicId) {
      try {
        const response = await axios.get(
          `${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.selectedModule}/topic/${topicId}/download_content`,
          {
            headers: { Authorization: `Bearer ${this.$store.state.token}` },
            responseType: 'blob'
          }
        );
        const blob = new Blob([response.data], { type: 'application/pdf' });
        const url = window.URL.createObjectURL(blob);
        window.open(url, '_blank');
      } catch (err) {
        this.alert = { visible: true, message: 'Failed to load PDF content', type: 'error' };
      }
    },
    editContent(topic) {
      this.selectedTopic = topic.topic_id;
      this.updateSelectedTopicName();
      this.editingContent = true;
      this.file = null;
      this.$refs.fileInput.value = '';
    },
    updateSelectedTopicName() {
      const topic = this.topics.find(t => t.topic_id === parseInt(this.selectedTopic));
      this.selectedTopicName = topic ? topic.topic_title : '';
    },
  },
  watch: {
    selectedTopic(newTopicId) {
      if (newTopicId) {
        this.updateSelectedTopicName();
        this.editingContent = false;
        this.file = null;
        this.$refs.fileInput.value = '';
      } else {
        this.selectedTopicName = '';
      }
    },
    selectedModule() {
      this.topics = [];
      this.selectedTopic = '';
      this.selectedTopicName = '';
      this.editingContent = false;
      this.file = null;
      if (this.$refs.fileInput) this.$refs.fileInput.value = '';
    }
  },
  mounted() {
    this.fetchLessons();
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
}
@media (max-width: 576px) {
  .container {
    padding-left: 12px;
    padding-right: 12px;
  }
  h2 {
    font-size: 1.5rem;
  }
  h4 {
    font-size: 1.2rem;
  }
  .btn-sm {
    font-size: 0.8rem;
    padding: 0.4rem 0.8rem;
  }
}
</style>