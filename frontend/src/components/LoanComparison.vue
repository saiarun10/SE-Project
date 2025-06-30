<template>
  <div class="loan-comparison">
    <h2>Compare Bank Loan Offers</h2>

    <div class="input-group">
      <label>Loan Amount (₹):</label>
      <input type="number" v-model.number="loanAmount" min="100000" max="10000000" step="100000" />
    </div>

    <div class="input-group">
      <label>Repayment Tenure (months):</label>
      <input type="number" v-model.number="tenure" min="12" max="360" step="1" />
    </div>

    <div class="input-group">
      <label>Bank A Interest Rate (% p.a.):</label>
      <input type="number" v-model.number="interestA" step="0.01" />
    </div>

    <div class="input-group">
      <label>Bank A Processing Fee (₹):</label>
      <input type="number" v-model.number="feeA" step="100" />
    </div>

    <div class="input-group">
      <label>Bank B Interest Rate (% p.a.):</label>
      <input type="number" v-model.number="interestB" step="0.01" />
    </div>

    <canvas ref="barCanvas" height="100" style="margin-top: 30px;"></canvas>
    <canvas ref="lineCanvas" height="100" style="margin-top: 30px;"></canvas>

    <div class="summary">
      <h3>Summary</h3>
      <p>Total repayment (Bank A): ₹{{ totalA.toLocaleString() }}</p>
      <p>Total repayment (Bank B): ₹{{ totalB.toLocaleString() }}</p>
      <p><strong>{{ betterBank }}</strong> is better for this tenure.</p>
      <p v-if="breakEven">Break-even occurs at around {{ breakEven }} months.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue'
import Chart from 'chart.js/auto'

const loanAmount = ref(1000000)
const tenure = ref(60)

const interestA = ref(7.65)
const interestB = ref(8.25)
const feeA = ref(5000)

const totalA = ref(0)
const totalB = ref(0)
const breakEven = ref(null)
const betterBank = ref('')

const barCanvas = ref(null)
const lineCanvas = ref(null)
let barChart = null
let lineChart = null

const calculateEMI = (P, annualRate, N) => {
  const r = annualRate / 12 / 100
  return P * r * Math.pow(1 + r, N) / (Math.pow(1 + r, N) - 1)
}

const generateAccruedInterest = (P, rate, N) => {
  const r = rate / 12 / 100
  const emi = calculateEMI(P, rate, N)
  let balance = P
  let interestAccum = 0
  const interestTimeline = []

  for (let i = 1; i <= N; i++) {
    const interest = balance * r
    interestAccum += interest
    interestTimeline.push(Math.round(interestAccum))
    const principal = emi - interest
    balance -= principal
  }

  return interestTimeline
}

const renderBarChart = () => {
  if (!barCanvas.value) return

  const labels = ['Bank A', 'Bank B']
  const data = [totalA.value, totalB.value]

  if (barChart) barChart.destroy()

  barChart = new Chart(barCanvas.value, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Total Repayment (₹)',
        data,
        backgroundColor: ['#4e91fc', '#63e6be']
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false }
      }
    }
  })
}

const renderLineChart = (interestAData, interestBData) => {
  if (!lineCanvas.value) return

  const labels = Array.from({ length: tenure.value }, (_, i) => `Month ${i + 1}`)

  if (lineChart) lineChart.destroy()

  lineChart = new Chart(lineCanvas.value, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Bank A Interest (₹)',
          data: interestAData,
          borderColor: '#4e91fc',
          fill: false
        },
        {
          label: 'Bank B Interest (₹)',
          data: interestBData,
          borderColor: '#63e6be',
          fill: false
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'top' }
      }
    }
  })
}

const updateComparison = async () => {
  const P = loanAmount.value
  const N = tenure.value

  const emiA = calculateEMI(P, interestA.value, N)
  const emiB = calculateEMI(P, interestB.value, N)

  totalA.value = Math.round(emiA * N + feeA.value)
  totalB.value = Math.round(emiB * N)

  betterBank.value = totalA.value < totalB.value ? 'Bank A' : 'Bank B'

  for (let t = 36; t <= 84; t++) {
    const eA = calculateEMI(P, interestA.value, t)
    const eB = calculateEMI(P, interestB.value, t)
    const TA = eA * t + feeA.value
    const TB = eB * t
    if (TA <= TB) {
      breakEven.value = t
      break
    }
  }

  const interestTimelineA = generateAccruedInterest(P, interestA.value, N)
  const interestTimelineB = generateAccruedInterest(P, interestB.value, N)

  await nextTick()
  renderBarChart()
  renderLineChart(interestTimelineA, interestTimelineB)
}

watch([loanAmount, tenure, interestA, interestB, feeA], updateComparison)
onMounted(updateComparison)
</script>

<style scoped>
.loan-comparison {
  max-width: 700px;
  margin: 20px auto;
  padding: 20px;
  background: #f0f9ff;
  border-radius: 10px;
  border: 1px solid #ccc;
}
.input-group {
  margin-bottom: 15px;
}
label {
  font-weight: bold;
  display: block;
  margin-bottom: 5px;
}
input[type="number"] {
  width: 100%;
  padding: 6px;
  border: 1px solid #ccc;
  border-radius: 5px;
}
.summary {
  margin-top: 30px;
  background: #fdfbea;
  padding: 15px;
  border-radius: 8px;
}
</style>
