<template>
  <div class="quiz-wrapper">
    <Navbar />

    <!-- Quiz Starter Strip -->
    <div class="quiz-strip shadow-sm">
      <QuizForm />
    </div>

    <!-- Conditional Quiz Content -->
    <div class="quiz-content text-center mx-auto">
      <template v-if="!quizData || quizData.length === 0">
        <h2 class="fw-bold text-primary mb-3">
          Hey Richie, let’s evaluate your learning through a simple yet engaging quiz!
        </h2>
        <p class="fs-5 text-muted">
          Choose a lesson, module, and topic for which you want to attempt the quiz.
        </p>
        <p>..</p>
        <p class="fs-6 text-secondary fst-italic">
          Click on <strong class="text-dark">Start Quiz</strong> to begin your quiz journey.
        </p>
      </template>

      <template v-else>
        <h2 class="fw-bold text-primary mb-4">Available Quizzes</h2>
        <div class="row row-cols-1 row-cols-md-2 g-4">
          <div class="col" v-for="quiz in quizData" :key="quiz.quiz_id">
            <div class="card h-100 shadow-sm p-3 text-start">
              <h5 class="card-title text-dark">{{ quiz.quiz_title }}</h5>
              <p class="card-text text-muted mb-1">Duration: {{ quiz.duration_minutes }} minutes</p>
              <button class="btn btn-primary mt-2" @click="startQuiz(quiz)">Start Quiz</button>
            </div>
          </div>
        </div>
      </template>
    </div>

    <Footer />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import QuizForm from '@/components/QuizForm.vue';
import Navbar from '@/components/Navbar.vue';
import Footer from '@/components/Footer.vue';

const route = useRoute();
const router = useRouter();


const quizData = ref(route.state?.quiz ?? []);


const startQuiz = async (quiz) => {
  try {
    const apiUrl = `/module/${quiz.module_id}/topic/${quiz.topic_id}/quizzes/${quiz.quiz_id}/questions`;
    const response = await fetch(apiUrl);

    if (!response.ok) {
      throw new Error(`Error fetching quiz questions: ${response.status}`);
    }

    const questions = await response.json();

    router.push({
      name: 'ExamInterface',
      state: {
        questions,
        duration_minutes: quiz.duration_minutes
      }
    });


  } catch (error) {
    console.error("Failed to load quiz questions:", error);
    alert("Unable to load quiz. Please try again later.");
  }
};
</script>

<style scoped>
.quiz-wrapper {
  font-family: var(--bs-body-font-family);
  background: linear-gradient(145deg, #f3f4f6, #ffffff);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.quiz-strip {
  background-color: #ffffff;
  padding: 1rem 2rem;
  border-bottom: 1px solid #dee2e6;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.quiz-content {
  max-width: 1800px;
  margin-top: 4rem;
  margin-bottom: 3rem;
  background: white;
  padding: 2rem;
  border-radius: 20px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
}

h2 {
  color: #0d6efd;
}

p {
  line-height: 3;
}

@media (max-width: 768px) {
  .quiz-content {
    padding: 1.5rem;
    margin: 2rem 1rem;
  }

  .quiz-strip {
    padding: 1rem;
  }
}
</style>
