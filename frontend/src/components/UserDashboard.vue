<template>
  <div class="container mt-5" style="font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;">
    <h3 class="mb-4">Hey Richie Track Your Progress</h3>

    <!-- Quiz Section -->
    <div class="border p-3 mb-4 bg-light">
      <h5 class="fw-bold border-bottom pb-2">Quiz Section</h5>
      <p>Number Of Quiz Attempted: <strong>10</strong></p>
      <p>Average Time of Quiz: <strong>15 Minutes</strong></p>
      <p>Average Score: <strong>40</strong></p>
    </div>

    <!-- Learning Section -->
    <div class="border p-3 mb-4 bg-light">
      <h5 class="fw-bold border-bottom pb-2">Learning Section</h5>
      <p>Sections Chosen: <strong>3</strong></p>
      <p>Modules Completed: <strong>8</strong></p>
      <p>Topics Learned: <strong>22</strong></p>
      <p>Total Learning Time: <strong>3 Hours</strong></p>
    </div>

    <!-- Overall Summary -->
    <div class="border p-3 bg-light">
      <h5 class="fw-bold border-bottom pb-2">Overall Summary</h5>
      <p>Your Rank: <strong>343</strong></p>
      <p>Daily Average Time: <strong>20 Minutes</strong></p>
      <p>Streak: <strong>7 days</strong></p>
      <p>Summary:</p>
      <canvas id="summaryChart" height="200"></canvas>
    </div>

    <!-- Button Section -->
    <div class="mt-4 text-center">
      <p><strong>Get Summary On Your Email</strong></p>
      <button class="btn btn-primary">Generate Report</button>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import Chart from 'chart.js/auto'

onMounted(() => {
  const ctx = document.getElementById('summaryChart').getContext('2d')
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Quiz', 'Learning', 'Dashboard'],
      datasets: [{
        data: [25, 50, 25],
        backgroundColor: ['#f87171', '#60a5fa', '#86efac'],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    }
  })
})
</script>

<style scoped>
canvas {
  max-width: 300px;
  margin: 0 auto;
}
</style>
