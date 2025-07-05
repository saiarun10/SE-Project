<template>
  <Navbar />
  <div class="container py-4 px-3 px-md-4">
    <Alert
      v-if="alert.visible"
      :message="alert.message"
      :type="alert.type"
      @close="alert.visible = false"
    />
    <h2 class="mb-4 text-center text-black fw-bold">Admin Please , Manage Modules</h2>
    <div class="shadow-lg p-3 p-md-4 mx-auto rounded-4 border" style="max-width: 720px;">
      <div class="form-group mb-3">
        <label class="form-label text-black fw-semibold">Select Lesson</label>
        <select v-model="selectedLesson" class="form-select" @change="fetchModules" :disabled="isSubmitting">
          <option value="">-- Select Lesson --</option>
          <option v-for="lesson in lessons" :key="lesson.lesson_id" :value="lesson.lesson_id">{{ lesson.lesson_name }}</option>
        </select>
      </div>
      <div v-if="selectedLesson" class="mb-4">
        <h4 class="text-black fw-semibold mb-3">Create New Module for {{ selectedLessonName }}</h4>
        <div class="form-group mb-3">
          <label class="form-label text-black">Module Title</label>
          <input v-model="newModuleName" type="text" class="form-control" :disabled="isSubmitting" placeholder="Enter module title" />
        </div>
        <div class="form-group mb-3">
          <label class="form-label text-black">Module Description</label>
          <textarea v-model="newModuleDescription" class="form-control" :disabled="isSubmitting" placeholder="Enter module description" rows="4"></textarea>
        </div>
        <div class="text-center">
          <button class="btn btn-primary text-white" @click="createModule" :disabled="!selectedLesson || !newModuleName || isSubmitting">
            <i class="fas fa-plus me-2"></i>{{ editingModuleId ? 'Update Module' : 'Add Module' }}
          </button>
        </div>
      </div>
      <div v-if="modules.length" class="mb-4">
        <h4 class="text-black fw-semibold mb-3">Existing Modules for {{ selectedLessonName }}</h4>
        <ul class="list-group">
          <li v-for="module in modules" :key="module.module_id" class="list-group-item d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center">
            <div>
              <strong>{{ module.module_title }}</strong>
              <p class="mb-0 text-muted" v-if="module.module_description">{{ module.module_description }}</p>
            </div>
            <div class="mt-2 mt-md-0">
              <button class="btn btn-warning btn-sm me-2 text-white" @click="editModule(module)" :disabled="isSubmitting">
                <i class="fas fa-edit me-1"></i>Edit
              </button>
              <button class="btn btn-danger btn-sm text-white" @click="deleteModule(module.module_id)" :disabled="isSubmitting">
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
  name: 'AddModule',
  components: { Alert, Navbar, AppFooter },
  data() {
    return {
      lessons: [],
      modules: [],
      selectedLesson: '',
      selectedLessonName: '',
      newModuleName: '',
      newModuleDescription: '',
      isSubmitting: false,
      alert: { visible: false, message: '', type: 'notification' },
      editingModuleId: null,
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
        return;
      }
      try {
        const response = await axios.get(`${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/modules`, {
          headers: { Authorization: `Bearer ${this.$store.state.token}` }
        });
        this.modules = response.data;
        const lesson = this.lessons.find(l => l.lesson_id === parseInt(this.selectedLesson));
        this.selectedLessonName = lesson ? lesson.lesson_name : '';
      } catch (err) {
        this.alert = { visible: true, message: 'Failed to load modules', type: 'error' };
      }
    },
    async createModule() {
      if (!this.newModuleName || !this.selectedLesson) {
        this.alert = { visible: true, message: 'Please provide a module title and select a lesson', type: 'error' };
        return;
      }
      this.isSubmitting = true;
      try {
        const payload = {
          module_title: this.newModuleName,
          module_description: this.newModuleDescription || '',
        };
        let response;
        if (this.editingModuleId) {
          // Update existing module
          response = await axios.put(
            `${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.editingModuleId}/update`,
            payload,
            { headers: { Authorization: `Bearer ${this.$store.state.token}` } }
          );
          const index = this.modules.findIndex(m => m.module_id === this.editingModuleId);
          if (index !== -1) this.modules[index] = response.data;
          this.alert = { visible: true, message: 'Module updated successfully', type: 'success' };
        } else {
          // Create new module
          response = await axios.post(
            `${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/create`,
            payload,
            { headers: { Authorization: `Bearer ${this.$store.state.token}` } }
          );
          this.modules.push(response.data);
          this.alert = { visible: true, message: 'Module created successfully', type: 'success' };
        }
        this.newModuleName = '';
        this.newModuleDescription = '';
        this.editingModuleId = null;
      } catch (err) {
        this.alert = {
          visible: true,
          message: this.editingModuleId ? 'Failed to update module' : 'Failed to create module',
          type: 'error'
        };
      } finally {
        this.isSubmitting = false;
      }
    },
    editModule(module) {
      this.editingModuleId = module.module_id;
      this.newModuleName = module.module_title;
      this.newModuleDescription = module.module_description || '';
    },
    async deleteModule(moduleId) {
      if (!confirm('Are you sure you want to delete this module?')) return;
      this.isSubmitting = true;
      try {
        await axios.delete(
          `${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${moduleId}/delete`,
          { headers: { Authorization: `Bearer ${this.$store.state.token}` } }
        );
        this.modules = this.modules.filter(m => m.module_id !== moduleId);
        this.alert = { visible: true, message: 'Module deleted successfully', type: 'success' };
      } catch (err) {
        this.alert = { visible: true, message: 'Failed to delete module', type: 'error' };
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