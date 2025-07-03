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
      <h5 class="mb-4 fw-bold text-center">Q{{ currentIndex + 1 }}. {{ currentQuestion.question_content }}</h5>

      <div class="row g-3 justify-content-center">
        <div
          class="col-md-6"
          v-for="n in 4"
          :key="n"
        >
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
              {{ currentQuestion['question_option' + n] }}
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
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
    <p class="mt-3">Loading questions...</p>
  </div>
  <Footer />
</template>


<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import Navbar from '@/components/Navbar.vue';
import Footer from '@/components/Footer.vue';
import axios from 'axios';

const route = useRoute();
// const quizData = ref(route.state?.quiz);
const questions = ref([]);
const quizId = ref(null);
const maxScore = ref(0);
const timeLeft = ref(0);
const timerInterval = ref(null);

const currentIndex = ref(0);
const answers = ref({});
const quizData = {"value":
  {quiz_id: "sample_quiz_001",
  time_limit: 90,  // in seconds
  max_score: 10,
  questions: [
    {
      question_id: 1,
      question_content: "What is the capital of France?",
      question_option1: "Berlin",
      question_option2: "Madrid",
      question_option3: "Paris",
      question_option4: "Rome"
    },
    {
      question_id: 2,
      question_content: "Which planet is known as the Red Planet?",
      question_option1: "Earth",
      question_option2: "Mars",
      question_option3: "Jupiter",
      question_option4: "Saturn"
    },
    {
      question_id: 3,
      question_content: "What is the boiling point of water?",
      question_option1: "90°C",
      question_option2: "100°C",
      question_option3: "120°C",
      question_option4: "80°C"
    }
  ]
}};

onMounted(() => {
  if (!quizData.value) {
    alert('No quiz data found. Please restart the quiz.');
    return;
  }

  localStorage.setItem('quizData', JSON.stringify(quizData.value)); // Optional fallback

  quizId.value = quizData.value.quiz_id;
  questions.value = quizData.value.questions;
  maxScore.value = quizData.value.max_score;
  timeLeft.value = quizData.value.time_limit;

  startTimer();
});

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
    // const result = await axios.post('/api/evaluate_quiz', payload);
    console.log(payload)
    const result={"data":{"score":50}}
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

