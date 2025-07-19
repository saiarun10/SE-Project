
<template>
      <Navbar />
  <div class="container py-4 px-3 px-md-4">
    <Alert
      v-if="alert.visible"
      :message="alert.message"
      :type="alert.type"
      @close="alert.visible = false"
    />
    <h2 class="mb-4 text-center text-black fw-bold">Take a Quiz</h2>
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
        <select v-model="selectedTopic" class="form-select" @change="fetchQuizzes" :disabled="!selectedModule || isSubmitting">
          <option value="">-- Select Topic --</option>
          <option v-for="topic in topics" :key="topic.topic_id" :value="topic.topic_id">{{ topic.topic_title }}</option>
        </select>
      </div>
      <div class="text-center mb-4">
        <button class="btn btn-primary text-white" @click="fetchQuizzes" :disabled="!selectedTopic || isSubmitting">
          <i class="fas fa-search me-2"></i>Load Quizzes
        </button>
      </div>
      <div v-if="quizzes.length" class="mb-4">
        <h4 class="text-black fw-semibold mb-3">Available Quizzes</h4>
        <ul class="list-group">
          <li v-for="quiz in quizzes" :key="quiz.quiz_id" class="list-group-item d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center">
            <div>
              <strong>{{ quiz.quiz_title }}</strong>
              <p class="mb-0 text-muted small">
                Duration: {{ quiz.duration_minutes }} min | Questions: {{ quiz.total_questions }} | Max Score: {{ quiz.total_score }}
              </p>

            </div>
            <div class="mt-2 mt-md-0">
              <button class="btn btn-success btn-sm text-white" @click="startQuiz(quiz.quiz_id)" :disabled="isSubmitting">
                <i class="fas fa-play me-1"></i>Start Quiz
              </button>
            </div>
          </li>
        </ul>
      </div>
      <div v-if="recentScore !== null" class="mt-4 text-center">
        <p class="text-lg text-black fw-semibold">Your Recent Score: {{ recentScore }}</p>
      </div>
      <ExamInterface
        v-if="showExam"
        :lesson-id="selectedLesson"
        :module-id="selectedModule"
        :topic-id="selectedTopic"
        :quiz-id="selectedQuizId"
        :access-token="quizAccessToken"
        @close="closeExam"
      />
    </div>
  </div>
      <AppFooter />
</template>

<script>
import { ref, onMounted } from 'vue';
import { useStore } from 'vuex';
import axios from 'axios';
import Navbar from '@/components/Navbar.vue';
import AppFooter from '@/components/Footer.vue';
import ExamInterface from '@/views/UserExamInterface.vue';
import Alert from '@/components/Alert.vue';

export default {
  components: { Navbar, AppFooter, ExamInterface, Alert },
  setup() {
    const store = useStore();
    const lessons = ref([]);
    const modules = ref([]);
    const topics = ref([]);
    const quizzes = ref([]);
    const selectedLesson = ref('');
    const selectedModule = ref('');
    const selectedTopic = ref('');
    const isSubmitting = ref(false);
    const alert = ref({ visible: false, message: '', type: '' });
    const showExam = ref(false);
    const selectedQuizId = ref(null);
    const quizAccessToken = ref('');
    const recentScore = ref(null);
    const totalScorePossible = ref(null);

    onMounted(async () => {
      if (!store.getters.isAuthenticated) {
        alert.value = { visible: true, message: 'Please log in to access quizzes', type: 'error' };
        return;
      }
      await fetchLessons();
    });

    const fetchLessons = async () => {
      try {
        isSubmitting.value = true;
        const response = await axios.get(`${import.meta.env.VITE_BASE_URL}/api/get_all_lessons`, {
          headers: { Authorization: `Bearer ${store.state.token}` },
        });
        lessons.value = response.data;
      } catch (err) {
        alert.value = { visible: true, message: err.response?.data?.error || 'Failed to load lessons', type: 'error' };
      } finally {
        isSubmitting.value = false;
      }
    };

    const fetchModules = async () => {
      if (!selectedLesson.value) {
        modules.value = [];
        selectedModule.value = '';
        topics.value = [];
        selectedTopic.value = '';
        quizzes.value = [];
        return;
      }
      try {
        isSubmitting.value = true;
        const response = await axios.get(`${import.meta.env.VITE_BASE_URL}/api/${selectedLesson.value}/modules`, {
          headers: { Authorization: `Bearer ${store.state.token}` },
        });
        modules.value = response.data;
        selectedModule.value = '';
        topics.value = [];
        selectedTopic.value = '';
        quizzes.value = [];
      } catch (err) {
        alert.value = { visible: true, message: err.response?.data?.error || 'Failed to load modules', type: 'error' };
      } finally {
        isSubmitting.value = false;
      }
    };

    const fetchTopics = async () => {
      if (!selectedLesson.value || !selectedModule.value) {
        topics.value = [];
        selectedTopic.value = '';
        quizzes.value = [];
        return;
      }
      try {
        isSubmitting.value = true;
        const response = await axios.get(`${import.meta.env.VITE_BASE_URL}/api/${selectedLesson.value}/module/${selectedModule.value}/topics`, {
          headers: { Authorization: `Bearer ${store.state.token}` },
        });
        topics.value = response.data;
        selectedTopic.value = '';
        quizzes.value = [];
      } catch (err) {
        alert.value = { visible: true, message: err.response?.data?.error || 'Failed to load topics', type: 'error' };
      } finally {
        isSubmitting.value = false;
      }
    };

    const fetchQuizzes = async () => {
      if (!selectedLesson.value || !selectedModule.value || !selectedTopic.value) {
        quizzes.value = [];
        return;
      }
      try {
        isSubmitting.value = true;
        const response = await axios.get(
          `${import.meta.env.VITE_BASE_URL}/api/${selectedLesson.value}/module/${selectedModule.value}/topic/${selectedTopic.value}/quizzes`,
          {
            headers: { Authorization: `Bearer ${store.state.token}` },
          }
        );
        console.log('Quizzes fetched:', response.data);
        quizzes.value = Array.isArray(response.data) ? response.data.filter(quiz => quiz.is_visible) : [];
        console.log('Filtered quizzes:', quizzes.value);
        recentScore.value = null;
        totalScorePossible.value = null;
      } catch (err) {
        alert.value = { visible: true, message: err.response?.data?.error || 'Failed to load quizzes', type: 'error' };
      } finally {
        isSubmitting.value = false;
      }
    };

    const startQuiz = async (quizId) => {
      try {
        isSubmitting.value = true;
        const response = await axios.post(
          `${import.meta.env.VITE_BASE_URL}/api/start_quiz`,
          { quiz_id: quizId },
          {
            headers: { Authorization: `Bearer ${store.state.token}` },
          }
        );
        selectedQuizId.value = quizId;
        quizAccessToken.value = response.data.quiz_attempt_access_token;
        showExam.value = true;
      } catch (err) {
        alert.value = { visible: true, message: err.response?.data?.error || 'Failed to start quiz', type: 'error' };
      } finally {
        isSubmitting.value = false;
      }
    };

    const closeExam = (score, total) => {
      showExam.value = false;
      selectedQuizId.value = null;
      quizAccessToken.value = '';
      recentScore.value = score;
      totalScorePossible.value = total;
    };

    return {
      lessons,
      modules,
      topics,
      quizzes,
      selectedLesson,
      selectedModule,
      selectedTopic,
      isSubmitting,
      alert,
      fetchLessons,
      fetchModules,
      fetchTopics,
      fetchQuizzes,
      startQuiz,
      showExam,
      selectedQuizId,
      quizAccessToken,
      closeExam,
      recentScore,
      totalScorePossible,
    };
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
select:disabled,
button:disabled {
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