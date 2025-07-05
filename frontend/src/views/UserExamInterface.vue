<template>
  <div class="shadow-lg p-3 p-md-4 mx-auto rounded-4 border" style="max-width: 720px;">
    <Alert
      v-if="alert.visible"
      :message="alert.message"
      :type="alert.type"
      @close="alert.visible = false"
    />
    <h2 class="mb-4 text-center fw-bold">Quiz Interface</h2>
    <div class="mb-4 d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center">
      <p class="mb-2 mb-md-0">Time Remaining: {{ formatTime(timeLeft) }}</p>
      <p>Score: {{ currentScore }} / {{ totalScorePossible }}</p>
    </div>
    <div v-if="currentQuestion" class="border p-4 mb-4 rounded-3">
      <p class="font-semibold mb-3">{{ currentQuestion.question_text }}</p>
      <div v-for="(option, index) in options" :key="index" class="mb-2">
        <input
          type="radio"
          :id="`option${index}`"
          :value="option"
          v-model="selectedOption"
          @change="saveAnswer"
          class="me-2"
        />
        <label :for="`option${index}`">{{ option }}</label>
      </div>
      <div class="d-flex justify-content-between mt-4">
        <button
          @click="prevQuestion"
          :disabled="currentIndex === 0"
          class="btn btn-secondary text-white"
        >
          Previous
        </button>
        <button
          @click="saveAnswer"
          :disabled="!selectedOption"
          class="btn btn-primary text-white"
        >
          Save Answer
        </button>
        <button
          @click="nextQuestion"
          :disabled="currentIndex === questions.length - 1"
          class="btn btn-secondary text-white"
        >
          Next
        </button>
      </div>
      <div class="mt-4 d-flex flex-wrap gap-2">
        <button
          v-for="q in questions"
          :key="q.question_id"
          @click="goToQuestion(q.question_id)"
          class="btn btn-sm"
          :class="answeredQuestions.includes(q.question_id) ? 'btn-success' : 'btn-primary'"
        >
          {{ q.question_id }}
        </button>
      </div>
    </div>
    <div class="text-center">
      <button @click="openSubmitModal" class="btn btn-danger text-white">
        <i class="fas fa-check me-2"></i>Submit Quiz
      </button>
    </div>
    <!-- Submit Confirmation Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 d-flex align-items-center justify-content-center">
      <div class="bg-white p-4 rounded shadow-lg">
        <p class="mb-3">Are you sure you want to submit the quiz?</p>
        <div class="d-flex justify-content-center gap-2">
          <button @click="submitQuiz" class="btn btn-success text-white">Yes</button>
          <button @click="showModal = false" class="btn btn-danger text-white">No</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import axios from 'axios';
import Alert from '@/components/Alert.vue';

export default {
  components: { Alert },
  props: {
    lessonId: { type: [Number, String], required: true },
    moduleId: { type: [Number, String], required: true },
    topicId: { type: [Number, String], required: true },
    quizId: { type: [Number, String], required: true },
    accessToken: { type: String, required: true },
  },
  setup(props) {
    const store = useStore();
    const router = useRouter();
    const questions = ref([]);
    const currentIndex = ref(0);
    const selectedOption = ref(null);
    const currentScore = ref(0);
    const totalScorePossible = ref(0);
    const answeredQuestions = ref([]);
    const showModal = ref(false);
    const timeLeft = ref(0);
    const timer = ref(null);
    const alert = ref({ visible: false, message: '', type: '' });

    onMounted(async () => {
      if (!store.getters.isAuthenticated) {
        alert.value = { visible: true, message: 'Please log in to access the quiz', type: 'error' };
        router.push('/login');
        return;
      }
      if (!props.quizId || !props.accessToken || !props.lessonId || !props.moduleId || !props.topicId) {
        alert.value = { visible: true, message: 'Invalid quiz, lesson, module, topic, or access token', type: 'error' };
        return;
      }
      await fetchQuestions();
      startTimer();
    });

    onUnmounted(() => {
      if (timer.value) clearInterval(timer.value);
    });

    const fetchQuestions = async () => {
      try {
        const response = await axios.get(
          `${import.meta.env.VITE_BASE_URL}/api/${props.lessonId}/module/${props.moduleId}/topic/${props.topicId}/quizzes/${props.quizId}/questions`,
          {
            headers: { Authorization: `Bearer ${store.state.token}` },
          }
        );
        questions.value = response.data;
        totalScorePossible.value = questions.value.reduce((sum, q) => sum + (q.score_points || 0), 0);
        timeLeft.value = questions.value[0]?.quiz?.duration_minutes * 60 || 0;
      } catch (error) {
        console.error('Error fetching questions:', error);
        alert.value = { visible: true, message: error.response?.data?.error || 'Failed to load questions', type: 'error' };
      }
    };

    const startTimer = () => {
      if (timeLeft.value > 0) {
        timer.value = setInterval(() => {
          timeLeft.value -= 1;
          if (timeLeft.value <= 0) {
            clearInterval(timer.value);
            submitQuiz();
          }
        }, 1000);
      }
    };

    const formatTime = (seconds) => {
      const minutes = Math.floor(seconds / 60);
      const secs = seconds % 60;
      return `${minutes}:${secs < 10 ? '0' : ''}${secs}`;
    };

    const currentQuestion = computed(() => questions.value[currentIndex.value]);
    const options = computed(() => {
      if (!currentQuestion.value) return [];
      return [
        currentQuestion.value.option1,
        currentQuestion.value.option2,
        currentQuestion.value.option3,
        currentQuestion.value.option4,
      ].filter(option => option);
    });

    const saveAnswer = async () => {
      if (!selectedOption.value || !currentQuestion.value) {
        alert.value = { visible: true, message: 'Please select an answer', type: 'warning' };
        return;
      }
      try {
        await axios.post(
          `${import.meta.env.VITE_BASE_URL}/api/save_answer`,
          {
            quiz_attempt_access_token: props.accessToken,
            question_id: currentQuestion.value.question_id,
            selected_answer: selectedOption.value,
          },
          {
            headers: { Authorization: `Bearer ${store.state.token}` },
          }
        );
        if (!answeredQuestions.value.includes(currentQuestion.value.question_id)) {
          answeredQuestions.value.push(currentQuestion.value.question_id);
          currentQuestion.value.selected_answer = selectedOption.value;
        }
        alert.value = { visible: true, message: 'Answer saved successfully', type: 'success' };
      } catch (error) {
        console.error('Error saving answer:', error);
        alert.value = { visible: true, message: error.response?.data?.error || 'Failed to save answer', type: 'error' };
      }
    };

    const nextQuestion = async () => {
      if (currentIndex.value < questions.value.length - 1) {
        currentIndex.value += 1;
        selectedOption.value = questions.value[currentIndex.value]?.selected_answer || null;
      }
    };

    const prevQuestion = async () => {
      if (currentIndex.value > 0) {
        currentIndex.value -= 1;
        selectedOption.value = questions.value[currentIndex.value]?.selected_answer || null;
      }
    };

    const goToQuestion = async (questionId) => {
      const index = questions.value.findIndex(q => q.question_id === questionId);
      if (index !== -1) {
        currentIndex.value = index;
        selectedOption.value = questions.value[currentIndex.value]?.selected_answer || null;
      }
    };

    const openSubmitModal = () => {
      if (answeredQuestions.value.length < questions.value.length) {
        alert.value = { visible: true, message: 'Please answer all questions before submitting', type: 'warning' };
        return;
      }
      showModal.value = true;
    };

    const submitQuiz = async () => {
      try {
        const responses = questions.value.map(q => ({
          question_id: q.question_id,
          selected_option: q.selected_answer || null,
        }));
        const response = await axios.post(
          `${import.meta.env.VITE_BASE_URL}/api/evaluate_quiz`,
          {
            quiz_attempt_access_token: props.accessToken,
            responses,
          },
          {
            headers: { Authorization: `Bearer ${store.state.token}` },
          }
        );
        currentScore.value = response.data.score;
        totalScorePossible.value = response.data.total_score_possible;
        showModal.value = false;
        alert.value = { visible: true, message: 'Quiz submitted successfully', type: 'success' };
        router.push('/quiz');
        setTimeout(() => {
          this.$emit('close', currentScore.value, totalScorePossible.value);
        }, 0);
      } catch (error) {
        console.error('Error submitting quiz:', error);
        alert.value = { visible: true, message: error.response?.data?.error || 'Failed to submit quiz', type: 'error' };
      } finally {
        if (timer.value) clearInterval(timer.value);
      }
    };

    return {
      questions,
      currentIndex,
      selectedOption,
      currentQuestion,
      options,
      saveAnswer,
      nextQuestion,
      prevQuestion,
      goToQuestion,
      openSubmitModal,
      submitQuiz,
      showModal,
      timeLeft,
      formatTime,
      currentScore,
      totalScorePossible,
      answeredQuestions,
      alert,
    };
  },
};
</script>

<style scoped>
h2, p, label {
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
button:disabled {
  background-color: #f8f9fa;
  cursor: not-allowed;
}
.border {
  border-color: #dee2e6;
}
@media (max-width: 576px) {
  .shadow-lg {
    padding: 12px;
  }
  h2 {
    font-size: 1.5rem;
  }
  .btn-sm {
    font-size: 0.8rem;
    padding: 0.4rem 0.8rem;
  }
}
</style>