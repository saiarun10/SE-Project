<template>
  <div class="quiz-container bg-light min-vh-100 d-flex align-items-center py-4">
    <div class="container" style="max-width: 1140px;">
      <div class="row justify-content-center">
        <div class="col-lg-10 col-md-12">
          <div class="card shadow-lg border-0 rounded-4">
            <div class="card-body p-4 p-md-5">

              <!-- Alert Component -->
              <Alert
                v-if="alert.visible"
                :message="alert.message"
                :type="alert.type"
                @close="alert.visible = false"
                class="mb-4"
              />

              <!-- Quiz Header -->
              <div class="text-center mb-4">
                <h1 class="h3 fw-bold text-primary">{{ quizTitle }}</h1>
              </div>

              <div v-if="currentQuestion">
                <!-- Quiz Info Bar -->
                <div class="d-flex flex-column flex-sm-row justify-content-between align-items-center bg-light p-3 rounded-3 mb-4 border">
                  <div class="fw-bold text-dark mb-2 mb-sm-0">
                    Question {{ currentIndex + 1 }} of {{ questions.length }}
                  </div>
                  <div class="fw-bold text-danger w-50">
                    <div class="d-flex justify-content-end align-items-center">
                       <i class="far fa-clock me-2"></i>Time Remaining: {{ formatTime(timeLeft) }}
                    </div>
                    <div class="progress mt-1" style="height: 6px;">
                        <div class="progress-bar bg-danger" role="progressbar" :style="{ width: timeProgressPercentage + '%' }" :aria-valuenow="timeProgressPercentage" aria-valuemin="0" aria-valuemax="100"></div>
                    </div>
                  </div>
                </div>

                <!-- Question -->
                <div class="question-area mb-4">
                  <p class="h5 fw-bold mb-4" style="line-height: 1.6;">{{ currentQuestion.question_text }}</p>
                  <div class="options-list d-grid gap-3">
                    <div v-for="(option, index) in options" :key="index">
                      <input
                        type="radio"
                        class="btn-check"
                        :id="`option${index}`"
                        :value="option"
                        v-model="selectedOption"
                      />
                      <label :for="`option${index}`" class="btn btn-outline-primary w-100 text-start p-3 rounded-3">
                        <span class="fw-bold me-2">{{ String.fromCharCode(65 + index) }}.</span> {{ option }}
                      </label>
                    </div>
                  </div>
                </div>

                <!-- Navigation Buttons -->
                <div class="d-flex justify-content-between mt-5">
                  <button
                    @click="prevQuestion"
                    :disabled="currentIndex === 0"
                    class="btn btn-secondary px-4 py-2 rounded-pill"
                  >
                    <i class="fas fa-arrow-left me-2"></i>Previous
                  </button>
                  <button
                    @click="nextQuestion"
                    :disabled="currentIndex >= questions.length - 1"
                    class="btn btn-primary px-4 py-2 rounded-pill"
                  >
                    Next<i class="fas fa-arrow-right ms-2"></i>
                  </button>
                </div>
                
                <hr class="my-4">

                <!-- Action Buttons -->
                <div class="text-center">
                    <div class="d-inline-flex flex-wrap justify-content-center gap-3">
                        <button @click="handleSaveClick" :disabled="!selectedOption" class="btn btn-info text-white px-4 py-2 rounded-pill">
                            <i class="fas fa-save me-2"></i>Save Answer
                        </button>
                        <button @click="openSubmitModal" class="btn btn-danger px-4 py-2 rounded-pill">
                            <i class="fas fa-check-circle me-2"></i>Submit Quiz
                        </button>
                    </div>
                </div>
              </div>
              
              <div v-else class="text-center p-5">
                  <div class="spinner-border text-primary" role="status">
                      <span class="visually-hidden">Loading Quiz...</span>
                  </div>
                  <p class="mt-3">Loading Quiz...</p>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Submit Confirmation Modal -->
    <div v-if="showSubmitModal" class="modal-backdrop">
      <div class="modal-dialog">
        <div class="modal-content shadow-lg">
          <div class="modal-header">
            <h5 class="modal-title">Confirm Submission</h5>
            <button type="button" class="btn-close" @click="showSubmitModal = false"></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to submit the quiz?</p>
          </div>
          <div class="modal-footer">
            <button @click="showSubmitModal = false" class="btn btn-secondary">No, go back</button>
            <button @click="submitQuiz" class="btn btn-success">Yes, Submit</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Time's Up Modal -->
    <div v-if="showTimeUpModal" class="modal-backdrop">
      <div class="modal-dialog">
        <div class="modal-content shadow-lg">
          <div class="modal-header bg-danger text-white">
            <h5 class="modal-title">Time's Up!</h5>
          </div>
          <div class="modal-body">
            <p>Your time has expired. The quiz will be submitted automatically.</p>
          </div>
          <div class="modal-footer">
            <button @click="goToHome" class="btn btn-primary">Go to Home</button>
          </div>
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
  name: 'QuizInterface',
  components: { Alert },
  props: {
    accessToken: { type: String, required: true },
  },
  // CHANGED: Declare the event the component will emit
  emits: ['close'],
  setup(props, { emit }) {
    const store = useStore();
    const router = useRouter();
    
    // ... (no other changes needed in reactive state or computed properties)
    const questions = ref([]);
    const currentIndex = ref(0);
    const selectedOption = ref(null);
    const userAnswers = ref(new Map());
    const showSubmitModal = ref(false);
    const showTimeUpModal = ref(false);
    const timeLeft = ref(0);
    const totalTime = ref(0);
    const timer = ref(null);
    const alert = ref({ visible: false, message: '', type: '' });
    const quizTitle = ref('Loading Quiz...');

    const currentQuestion = computed(() => questions.value[currentIndex.value]);
    const options = computed(() => {
      if (!currentQuestion.value) return [];
      return [
        currentQuestion.value.option1,
        currentQuestion.value.option2,
        currentQuestion.value.option3,
        currentQuestion.value.option4,
      ].filter(Boolean);
    });
    const timeProgressPercentage = computed(() => {
        if (totalTime.value <= 0) return 100;
        return Math.max(0, (timeLeft.value / totalTime.value) * 100);
    });
    // ... (no other changes needed in hooks or other methods)

    onMounted(async () => {
      if (!store.getters.isAuthenticated) {
        router.push('/login');
        return;
      }
      if (!props.accessToken) {
        showAlert('Invalid quiz session. No access token provided.', 'error');
        return;
      }
      await fetchQuizDetails();
    });

    onUnmounted(() => {
      if (timer.value) clearInterval(timer.value);
    });

    const showAlert = (message, type = 'error', duration = 3000) => {
        alert.value = { visible: true, message, type };
        setTimeout(() => { alert.value.visible = false; }, duration);
    };

    const fetchQuizDetails = async () => {
      try {
        const response = await axios.get(
          `${import.meta.env.VITE_BASE_URL}/api/quiz_details/${props.accessToken}`,
          { headers: { Authorization: `Bearer ${store.state.token}` } }
        );
        
        const data = response.data;
        if (data && data.questions && data.questions.length > 0) {
            quizTitle.value = data.quiz_title;
            totalTime.value = (data.duration_minutes || 0) * 60;
            timeLeft.value = totalTime.value;
            questions.value = data.questions;

            data.questions.forEach(q => {
                if (q.selected_answer) {
                    userAnswers.value.set(q.question_id, q.selected_answer);
                }
            });
            
            loadAnswerForCurrentQuestion();
            startTimer();
        } else {
            showAlert('No questions found for this quiz.', 'warning');
        }
      } catch (error) {
        console.error('Error fetching quiz details:', error);
        showAlert(error.response?.data?.message || 'Failed to load quiz details.', 'error');
        if (error.response?.status === 404 || error.response?.status === 403) {
            setTimeout(() => emit('close'), 3000); // Also close on error
        }
      }
    };

    const startTimer = () => {
      if (timeLeft.value > 0 && !timer.value) {
        timer.value = setInterval(() => {
          timeLeft.value--;
          if (timeLeft.value <= 0) {
            handleTimeUp();
          }
        }, 1000);
      }
    };
    
    const handleTimeUp = () => {
        clearInterval(timer.value);
        timer.value = null;
        showTimeUpModal.value = true;
        submitQuiz();
    };

    const formatTime = (seconds) => {
      if (seconds < 0) return '00:00';
      const minutes = Math.floor(seconds / 60);
      const secs = seconds % 60;
      return `${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    };

    const saveAnswer = async () => {
      if (!selectedOption.value || !currentQuestion.value) return;
      
      userAnswers.value.set(currentQuestion.value.question_id, selectedOption.value);

      try {
        await axios.post(
          `${import.meta.env.VITE_BASE_URL}/api/save_answer`,
          {
            quiz_attempt_access_token: props.accessToken,
            question_id: currentQuestion.value.question_id,
            selected_answer: selectedOption.value,
          },
          { headers: { Authorization: `Bearer ${store.state.token}` } }
        );
      } catch (error) {
        console.error('Error saving answer:', error);
        showAlert(error.response?.data?.message || 'Could not save answer.', 'error');
      }
    };
    
    const handleSaveClick = async () => {
        if (!selectedOption.value) {
            showAlert('Please select an option before saving.', 'warning');
            return;
        }
        await saveAnswer();
        showAlert('Answer saved!', 'success');
    };

    const loadAnswerForCurrentQuestion = () => {
        if (currentQuestion.value) {
            selectedOption.value = userAnswers.value.get(currentQuestion.value.question_id) || null;
        }
    };

    const nextQuestion = async () => {
      await saveAnswer();
      if (currentIndex.value < questions.value.length - 1) {
        currentIndex.value++;
        loadAnswerForCurrentQuestion();
      }
    };

    const prevQuestion = () => {
      if (currentIndex.value > 0) {
        currentIndex.value--;
        loadAnswerForCurrentQuestion();
      }
    };
    
    const openSubmitModal = () => {
      showSubmitModal.value = true;
    };

    const submitQuiz = async () => {
      showSubmitModal.value = false;
      if (timer.value) clearInterval(timer.value);

      await saveAnswer();

      try {
        const responses = Array.from(userAnswers.value.entries()).map(([question_id, selected_option]) => ({
            question_id,
            selected_option,
        }));

        const response = await axios.post(
          `${import.meta.env.VITE_BASE_URL}/api/evaluate_quiz`,
          {
            quiz_attempt_access_token: props.accessToken,
            responses,
          },
          { headers: { Authorization: `Bearer ${store.state.token}` } }
        );
        const scoreData = response.data;

        if (!showTimeUpModal.value) {
            showAlert('Quiz submitted successfully!', 'success');
            // CHANGED: Emit the 'close' event with the score data.
            emit('close', scoreData.score, scoreData.total_possible_score);
        }

      } catch (error) {
        console.error('Error submitting quiz:', error);
        showAlert(error.response?.data?.message || 'Failed to submit quiz.', 'error');
      }
    };
    
    const goToHome = () => {
        // CHANGED: Emit the 'close' event to hide the exam interface.
        emit('close');
    };

    return {
      questions,
      currentIndex,
      selectedOption,
      currentQuestion,
      options,
      nextQuestion,
      prevQuestion,
      openSubmitModal,
      submitQuiz,
      showSubmitModal,
      showTimeUpModal,
      timeLeft,
      formatTime,
      alert,
      quizTitle,
      goToHome,
      timeProgressPercentage,
      handleSaveClick,
    };
  },
};
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');

.quiz-container {
  font-family: 'Inter', sans-serif;
}

.card {
  transition: all 0.3s ease;
}

.btn {
  transition: all 0.2s ease;
  font-weight: 600;
}

.btn-check:checked + .btn-outline-primary {
    background-color: var(--bs-primary);
    color: white;
    border-color: var(--bs-primary);
    box-shadow: 0 4px 15px rgba(0, 123, 255, 0.2);
}

.btn-outline-primary {
    border-width: 2px;
}

.btn-outline-primary:hover {
    background-color: rgba(0, 123, 255, 0.1);
    color: var(--bs-primary);
}

.modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1050;
}

.modal-dialog {
    max-width: 500px;
    margin: 1.75rem auto;
}

.btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.progress-bar {
    transition: width 0.5s ease-in-out;
}
</style>
