<template>
  <Navbar />
  <div class="dashboard-container">
    <header class="header-section">
      <h1 class="header-title">Welcome {{ username }} </h1>
    </header>

    <section class="grid-section">
      <div class="container-fluid">
        <div class="row g-4">
          <div class="col-6" v-for="(item, index) in dashboardItems" :key="index">
            <router-link :to="item.route" class="grid-item">
              <img :src="item.image" :alt="item.alt" class="grid-image" />
              <p class="grid-text">{{ item.text }}</p>
            </router-link>
          </div>
        </div>
      </div>
    </section>
    <AppFooter />
  </div>
</template>

<script>
import AppFooter from '@/components/Footer.vue';
import Navbar from '@/components/Navbar.vue';

import learnImg from '@/assets/Learn.png';
import quizImg from '@/assets/Quiz.png';
import expensesImg from '@/assets/Expenses.png';
import awarenessImg from '@/assets/Awareness.png';
import calculatorImg from '@/assets/Calculator.png';
import askImg from '@/assets/Chatbot.png';

export default {
  name: 'UserDashboard',
  components: {
    AppFooter,
    Navbar,
  },
  computed: {
    username() {
      return this.$store.getters.username || 'User'; // Fallback to 'User' if username is null
    },
  },
  data() {
    return {
      dashboardItems: [
        { route: '/lesson', image: learnImg, text: 'Learn', alt: 'Learn Section' },
        { route: '/quiz', image: quizImg, text: 'Quiz', alt: 'Quiz Section' },
        { route: '/add-expense', image: expensesImg, text: 'Record Expenses', alt: 'Expenses Section' },
        { route: '/awareness', image: awarenessImg, text: 'Awareness', alt: 'Awareness Section' },
        { route: '/calculator', image: calculatorImg, text: 'Calculate', alt: 'Calculator Section' },
        { route: '/chatbot', image: askImg, text: 'Ask a Question', alt: 'Question Section' },
      ],
    };
  },
};
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.header-section {
  padding: 2rem 1rem;
  text-align: center;
}

.header-title {
    align-items: left;
  font-size: clamp(1.5rem, 5vw, 2rem);
  font-weight: 700;
  color: #333;
  margin-bottom: 1.5rem;
}

.section-title {
  font-size: clamp(1.25rem, 4vw, 1.75rem);
  font-weight: 600;
  text-align: center;
  margin-bottom: 2rem;
  color: #333;
}

.grid-section {
  padding: 2rem 1rem;
  width: 100%;
  max-width: 1200px;
}

.grid-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-decoration: none;
  color: #333;
  padding: 1.5rem;
  transition: transform 0.3s ease;
}

.grid-item:hover {
  transform: scale(1.1);
}

.grid-image {
  width: 150px;
  height: auto;
  margin-bottom: 1rem;
  transition: transform 0.3s ease-in-out;
}

.grid-item:hover .grid-image {
  transform: scale(1.15);
}

.grid-text {
  font-size: clamp(0.9rem, 2.5vw, 1rem);
  font-weight: 500;
  text-align: center;
  margin: 0;
}

/* 2x3 Grid Layout */
.grid-section .row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2rem;
}

/* Responsive Design */
@media (max-width: 767px) {
  .grid-section .row {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .grid-image {
    max-width: 120px;
  }
}

@media (max-width: 576px) {
  .grid-image {
    max-width: 100px;
  }

  .grid-text {
    font-size: 0.85rem;
  }
}
</style>