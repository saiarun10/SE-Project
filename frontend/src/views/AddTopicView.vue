<template>
  <Navbar />
  <div class="container py-4 px-3 px-md-4">
    <Alert
      v-if="alert.visible"
      :message="alert.message"
      :type="alert.type"
      @close="alert.visible = false"
    />
    <h2 class="mb-4 text-center text-black fw-bold">Admin, Please Manage Topics</h2>
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
      <div v-if="selectedModule" class="mb-4">
        <h4 class="text-black fw-semibold mb-3">Create New Topic for {{ selectedModuleName }}</h4>
        <div class="form-group mb-3">
          <label class="form-label text-black">Topic Title</label>
          <input v-model="newTopicName" type="text" class="form-control" :disabled="isSubmitting" placeholder="Enter topic title" />
        </div>
        <div class="text-center">
          <button class="btn btn-primary text-white" @click="createOrUpdateTopic" :disabled="!selectedLesson || !selectedModule || !newTopicName || isSubmitting">
            <i class="fas fa-plus me-2"></i>{{ editingTopicId ? 'Update Topic' : 'Add Topic' }}
          </button>
        </div>
      </div>
      <div v-if="topics.length" class="mb-4">
        <h4 class="text-black fw-semibold mb-3">Existing Topics for {{ selectedModuleName }}</h4>
        <ul class="list-group">
          <li v-for="topic in topics" :key="topic.topic_id" class="list-group-item d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center">
            <div>
              <strong>{{ topic.topic_title }}</strong>
              <p class="mb-0 text-muted" v-if="topic.topic_content">{{ topic.topic_content }}</p>
            </div>
            <div class="mt-2 mt-md-0">
              <button class="btn btn-warning btn-sm me-2 text-white" @click="editTopic(topic)" :disabled="isSubmitting">
                <i class="fas fa-edit me-1"></i>Edit
              </button>
              <button class="btn btn-danger btn-sm text-white" @click="deleteTopic(topic.topic_id)" :disabled="isSubmitting">
                <i class="fas fa-trash me-1"></i>Delete
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
  name: 'AddTopic',
  components: { Alert, Navbar, AppFooter },
  data() {
    return {
      lessons: [],
      modules: [],
      topics: [],
      selectedLesson: '',
      selectedModule: '',
      selectedLessonName: '',
      selectedModuleName: '',
      newTopicName: '',
      isSubmitting: false,
      alert: { visible: false, message: '', type: 'notification' },
      editingTopicId: null,
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
        this.selectedLessonName = '';
        this.selectedModule = '';
        this.topics = [];
        return;
      }
      try {
        const response = await axios.get(`${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/modules`, {
          headers: { Authorization: `Bearer ${this.$store.state.token}` }
        });
        this.modules = response.data;
        const lesson = this.lessons.find(l => l.lesson_id === parseInt(this.selectedLesson));
        this.selectedLessonName = lesson ? lesson.lesson_name : '';
        this.selectedModule = '';
        this.topics = [];
      } catch (err) {
        this.alert = { visible: true, message: 'Failed to load modules', type: 'error' };
      }
    },
    async fetchTopics() {
      if (!this.selectedModule) {
        this.topics = [];
        this.selectedModuleName = '';
        return;
      }
      try {
        const response = await axios.get(`${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.selectedModule}/topics`, {
          headers: { Authorization: `Bearer ${this.$store.state.token}` }
        });
        this.topics = response.data;
        const module = this.modules.find(m => m.module_id === parseInt(this.selectedModule));
        this.selectedModuleName = module ? module.module_title : '';
      } catch (err) {
        this.alert = { visible: true, message: 'Failed to load topics', type: 'error' };
      }
    },
    async createOrUpdateTopic() {
      if (!this.newTopicName || !this.selectedLesson || !this.selectedModule) {
        this.alert = { visible: true, message: 'Please provide a topic title and select both a lesson and module', type: 'error' };
        return;
      }
      this.isSubmitting = true;
      try {
        if (this.editingTopicId) {
          // Update existing topic
          const payload = { topic_title: this.newTopicName };
          const response = await axios.put(
            `${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.selectedModule}/topic/${this.editingTopicId}/update`,
            payload,
            { headers: { Authorization: `Bearer ${this.$store.state.token}` } }
          );
          const index = this.topics.findIndex(t => t.topic_id === this.editingTopicId);
          if (index !== -1) this.topics[index] = response.data;
          this.alert = { visible: true, message: 'Topic updated successfully', type: 'success' };
        } else {
          // Create new topic
          const payload = { topic_title: this.newTopicName, topic_content: '' }; // Content is empty as per requirement
          const response = await axios.post(
            `${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.selectedModule}/topic/create`,
            payload,
            { headers: { Authorization: `Bearer ${this.$store.state.token}` } }
          );
          this.topics.push(response.data);
          this.alert = { visible: true, message: 'Topic created successfully', type: 'success' };
        }
        this.newTopicName = '';
        this.editingTopicId = null;
      } catch (err) {
        this.alert = {
          visible: true,
          message: this.editingTopicId ? 'Failed to update topic' : 'Failed to create topic',
          type: 'error'
        };
      } finally {
        this.isSubmitting = false;
      }
    },
    editTopic(topic) {
      this.editingTopicId = topic.topic_id;
      this.newTopicName = topic.topic_title;
    },
    async deleteTopic(topicId) {
      if (!confirm('Are you sure you want to delete this topic?')) return;
      this.isSubmitting = true;
      try {
        await axios.delete(
          `${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.selectedModule}/topic/${topicId}/delete`,
          { headers: { Authorization: `Bearer ${this.$store.state.token}` } }
        );
        this.topics = this.topics.filter(t => t.topic_id !== topicId);
        this.alert = { visible: true, message: 'Topic deleted successfully', type: 'success' };
      } catch (err) {
        this.alert = { visible: true, message: 'Failed to delete topic', type: 'error' };
      } finally {
        this.isSubmitting = false;
      }
    },
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
button.btn {
  transition: all 0.2s ease;
}
button.btn:hover {
  filter: brightness(1.15);
  transform: translateY(-1px);
}
button.btn:active {
  transform: translateY(0);
}
input:disabled,
select:disabled,
textarea:disabled {
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