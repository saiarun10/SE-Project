<template>
    <div class="quiz-wrapper">
<Navbar />

    <!-- Quiz Starter Strip -->
    <div class="quiz-strip shadow-sm">
      <QuizForm />
    </div>

    <!-- Title and Description -->
    <div class="quiz-content text-center mx-auto">
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
    </div>

    <Footer />
  </div>
</template>

<script setup>
import QuizForm from '@/components/QuizForm.vue';
import Navbar from '@/components/Navbar.vue';
import Footer from '@/components/Footer.vue';
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

