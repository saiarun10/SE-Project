<template>
  <section class="bg-white py-5 px-4">
    <div class="container-fluid">
      <h3 class="text-center fw-bold fs-2 mb-5">Features we provide</h3>

      <div class="row text-center g-4">
        <div class="col-12 col-sm-6 col-md-3">
          <router-link to="/login" class="text-decoration-none text-dark d-block transition-hover">
            <img src="@/assets/chart.jpg" alt="Chart" class="mx-auto d-block mb-3 hover-zoom" style="width: 140px; height: 140px;" />
            <p class="fw-medium fs-6">Dashboard to record expenses</p>
          </router-link>
        </div>

        <div class="col-12 col-sm-6 col-md-3">
          <router-link to="/login" class="text-decoration-none text-dark d-block transition-hover">
            <img src="@/assets/quiz.png" alt="Quiz" class="mx-auto d-block mb-3 hover-zoom" style="width: 140px; height: 140px;" />
            <p class="fw-medium fs-6">Learn and Evaluate through Quiz</p>
          </router-link>
        </div>

        <div class="col-12 col-sm-6 col-md-3">
          <router-link to="/login" class="text-decoration-none text-dark d-block transition-hover">
            <img src="@/assets/invest.png" alt="Investing" class="mx-auto d-block mb-3 hover-zoom" style="width: 140px; height: 140px;" />
            <p class="fw-medium fs-6">Awareness about the tempting ways of investing</p>
          </router-link>
        </div>

        <div class="col-12 col-sm-6 col-md-3">
          <router-link to="/login" class="text-decoration-none text-dark d-block transition-hover">
            <img src="@/assets/calculator.png" alt="Calculator" class="mx-auto d-block mb-3 hover-zoom" style="width: 140px; height: 140px;" />
            <p class="fw-medium fs-6">Additional features like Chatbox and calculator</p>
          </router-link>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hover-zoom {
  transition: transform 0.3s ease;
}
.hover-zoom:hover {
  transform: scale(1.07);
}
</style>

<script>
export default {
  name: 'FeatureSection'
}
</script>
