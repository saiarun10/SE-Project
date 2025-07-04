<template>
  <Navbar />

  <div class="container mt-4" v-if="questions.length">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4 px-2">
      <h4 class="text-primary fw-bold">Max Score: {{ maxScore }}</h4>
      <h5 class="text-danger fw-semibold">Time Left: {{ formattedTime }}</h5>
    </div>

    <!-- Question Display -->
    <div class="quiz-box mx-auto p-5 shadow rounded bg-white">
      <h5 class="mb-4 fw-bold text-center">
        Q{{ currentIndex + 1 }}. {{ currentQuestion.question_text }}
      </h5>

      <div class="row g-3 justify-content-center">
        <div class="col-md-6" v-for="n in 4" :key="n">
          <div
            class="form-check option-pill"
            :class="{ selected: answers[currentQuestion.question_id] === n }"
            @click="answers[currentQuestion.question_id] = n"
          >
            <input
              class="form-check-input d-none"
              type="radio"
              :id="'option' + n"
              :value="n"
              v-model="answers[currentQuestion.question_id]"
            />
            <label
              class="form-check-label w-100 text-center"
              :for="'option' + n"
            >
              {{ currentQuestion['option' + n] }}
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- Navigation Buttons -->
    <div class="d-flex justify-content-between mt-4">
      <button
        class="btn btn-outline-secondary"
        :disabled="currentIndex === 0"
        @click="prevQuestion"
      >
        Previous
      </button>

      <button
        v-if="currentIndex < questions.length - 1"
        class="btn btn-primary"
        @click="nextQuestion"
      >
        Next
      </button>

      <button
        v-else
        class="btn btn-success"
        @click="submitQuiz"
      >
        Submit Quiz
      </button>
    </div>
  </div>

  <div v-else class="text-center mt-5">
    <div class="text-danger fs-4 fw-semibold">No questions available for this quiz.</div>
  </div>

  <Footer />
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import Navbar from '@/components/Navbar.vue';
import Footer from '@/components/Footer.vue';

const route = useRoute();

const questions = ref(route.state?.questions ?? []);
const duration = ref(route.state?.duration_minutes ?? 120); 
const quizId = ref(null);
const maxScore = ref(0);
const timeLeft = ref(0);
const timerInterval = ref(null);

const currentIndex = ref(0);
const answers = ref({});

const currentQuestion = computed(() => questions.value[currentIndex.value]);


const formattedTime = computed(() => {
  const min = String(Math.floor(timeLeft.value / 60)).padStart(2, '0');
  const sec = String(timeLeft.value % 60).padStart(2, '0');
  return `${min}:${sec}`;
});


const startTimer = () => {
  timerInterval.value = setInterval(() => {
    timeLeft.value--;
    if (timeLeft.value <= 0) {
      clearInterval(timerInterval.value);
      submitQuiz();
    }
  }, 1000);
};


onMounted(() => {
  if (!questions.value.length) return;

  quizId.value = questions.value[0]?.quiz_id ?? null;
  maxScore.value = questions.value.reduce((sum, q) => sum + (q.score_points || 0), 0);
  timeLeft.value = duration.value;
  startTimer();
});


const nextQuestion = () => {
  if (currentIndex.value < questions.value.length - 1) {
    currentIndex.value++;
  }
};

const prevQuestion = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--;
  }
};


const submitQuiz = async () => {
  clearInterval(timerInterval.value);

  const payload = {
    quiz_id: quizId.value,
    responses: questions.value.map(q => ({
      question_id: q.question_id,
      selected_option: answers.value[q.question_id] || 0
    }))
  };

  try {
    const result = await axios.post('/api/evaluate_quiz', payload);
    alert('Quiz Submitted Successfully!\nScore: ' + result.data.score);
  } catch (error) {
    alert('Error submitting quiz');
    console.error(error);
  }
};
</script>

<style scoped>
.quiz-box {
  max-width: 700px;
  background: #ffffff;
  border: 1px solid #dee2e6;
}

.option-pill {
  cursor: pointer;
  border: 2px solid #dee2e6;
  border-radius: 30px;
  padding: 10px 20px;
  background-color: #f8f9fa;
  transition: all 0.3s ease;
}

.option-pill:hover {
  background-color: #e9ecef;
  border-color: #0d6efd;
}

.option-pill.selected {
  background-color: #0d6efd;
  color: white;
  border-color: #0d6efd;
  font-weight: bold;
  box-shadow: 0 0 10px rgba(13, 110, 253, 0.4);
}

.form-check-label {
  padding: 10px;
  display: inline-block;
  width: 100%;
  border-radius: 30px;
}
</style>
