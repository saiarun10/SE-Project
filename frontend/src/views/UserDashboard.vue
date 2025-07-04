<template>
  <Navbar />
  <div>
    <div class="container py-5">
      <!-- Header -->
      <h1 class="fs-4 fw-bold mb-4">Hey User, Welcome</h1>

      <section class="bg-white py-5 px-4">
        <div class="container-fluid">
          <h3 class="text-center fw-bold fs-2 mb-5">Navigate Through Sections</h3>

          <div class="row text-center g-4">
            <div class="col-12 col-sm-6 col-md-3">
              <router-link to="/login" class="text-decoration-none text-dark d-block transition-hover">
                <img src="@/assets/learn.png" alt="Chart" class="mx-auto d-block mb-3 hover-zoom" style="width: 140px; height: 140px;" />
                <p class="fw-medium fs-6">Learn</p>
              </router-link>
            </div>

            <div class="col-12 col-sm-6 col-md-3">
              <router-link to="/login" class="text-decoration-none text-dark d-block transition-hover">
                <img src="@/assets/quiz_user.png" alt="Quiz" class="mx-auto d-block mb-3 hover-zoom" style="width: 140px; height: 140px;" />
                <p class="fw-medium fs-6">Quiz</p>
              </router-link>
            </div>

            <div class="col-12 col-sm-6 col-md-3">
              <router-link to="/login" class="text-decoration-none text-dark d-block transition-hover">
                <img src="@/assets/record_expenses.png" alt="Investing" class="mx-auto d-block mb-3 hover-zoom" style="width: 140px; height: 140px;" />
                <p class="fw-medium fs-6">Record Expenses</p>
              </router-link>
            </div>

            <div class="col-12 col-sm-6 col-md-3">
              <router-link to="/login" class="text-decoration-none text-dark d-block transition-hover">
                <img src="@/assets/awareness.png" alt="Calculator" class="mx-auto d-block mb-3 hover-zoom" style="width: 140px; height: 140px;" />
                <p class="fw-medium fs-6">Awareness Section</p>
              </router-link>
            </div>
          </div>
        </div>
      </section>

      <section class="bg-white py-5 px-4">
        <div class="container-fluid">
          <div class="row text-center g-4">
            <div class="col-12 col-sm-6 col-md-3">
              <router-link to="/login" class="text-decoration-none text-dark d-block transition-hover">
                <img src="@/assets/Calculate.png" alt="Chart" class="mx-auto d-block mb-3 hover-zoom" style="width: 140px; height: 140px;" />
                <p class="fw-medium fs-6">Calculate it</p>
              </router-link>
            </div>

            <div class="col-12 col-sm-6 col-md-3">
              <router-link to="/login" class="text-decoration-none text-dark d-block transition-hover">
                <img src="@/assets/askaquestion.png" alt="Calculator" class="mx-auto d-block mb-3 hover-zoom" style="width: 140px; height: 140px;" />
                <p class="fw-medium fs-6">Ask A Question !</p>
              </router-link>
            </div>
          </div>
        </div>
      </section>
      
    </div>

    <AppFooter />
  </div>
</template>

<script>
import AppFooter from '../components/Footer.vue'
import Navbar from '../components/Navbar.vue'

import learnImg from '@/assets/images/Learn.png'
import quizImg from '@/assets/images/quiz_user.png'
import expensesImg from '@/assets/images/record_expenses.png'
import awarenessImg from '@/assets/images/awareness.png'
import calculatorImg from '@/assets/images/Calculate.png'
import askImg from '@/assets/images/askaquestion.png'

export default {
  name: 'UserDashboard',
  components: {
    AppFooter,
    Navbar
  },
  data() {
    return {
      learnImg,
      quizImg,
      expensesImg,
      awarenessImg,
      calculatorImg,
      askImg,
    }
  }
}
</script>

<style scoped>
/* Optional hover effect for buttons */
.btn:hover {
  background-color: #e2e6ea;
}
</style>
