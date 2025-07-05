<template>
  <div class="loan-comparison">
    <h2>Compare Bank Loan Offers</h2>

    <div class="form-layout">
      <!-- Input Column 1 -->
      <div class="input-column">
        <div class="input-group">
          <label>Loan Amount (₹):</label>
          <input type="number" v-model.number="loanAmount" />
        </div>
        <div class="input-group">
          <label>Bank A Interest Rate (% p.a.):</label>
          <input type="number" v-model.number="interestA" />
        </div>
        <div class="input-group">
          <label>Bank A Processing Fee (₹):</label>
          <input type="number" v-model.number="feeA" />
        </div>
      </div>

      <!-- Input Column 2 -->
      <div class="input-column">
        <div class="input-group">
          <label>Repayment Tenure (months):</label>
          <input type="number" v-model.number="tenure" />
        </div>
        <div class="input-group">
          <label>Bank B Interest Rate (% p.a.):</label>
          <input type="number" v-model.number="interestB" />
        </div>
        <div class="input-group">
          <label>Bank B Processing Fee (₹):</label>
          <input type="number" v-model.number="feeB" />
        </div>
      </div>

      <!-- Summary Column -->
      <div class="summary-column">
        <div class="summary">
          <h3>Summary</h3>
          <p>Total repayment (Bank A): ₹{{ totalA.toLocaleString() }}</p>
          <p>Total repayment (Bank B): ₹{{ totalB.toLocaleString() }}</p>
          <p><strong>{{ betterBank }}</strong> is better for this tenure.</p>
          <p v-if="breakEven">Break-even occurs at around {{ breakEven }} months.</p>
        </div>
      </div>
    </div>

    <canvas ref="lineCanvas" height="100" style="margin-top: 20px;"></canvas>

    <button @click="resetZoom" class="reset-button">Reset Zoom</button>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue'
import Chart from 'chart.js/auto'
import zoomPlugin from 'chartjs-plugin-zoom'

Chart.register(zoomPlugin)

const loanAmount = ref(100000)
const tenure = ref(84)
const interestA = ref(7.25)
const interestB = ref(11)
const feeA = ref(5000)
const feeB = ref(0)

const totalA = ref(0)
const totalB = ref(0)
const breakEven = ref(null)
const betterBank = ref('')

const lineCanvas = ref(null)
let lineChart = null

const calculateEMI = (P, annualRate, N) => {
  const r = annualRate / 12 / 100
  return P * r * Math.pow(1 + r, N) / (Math.pow(1 + r, N) - 1)
}

const generateTotalRepaymentTimeline = (emi, fee, N) => {
  const timeline = []
  for (let i = 1; i <= N; i++) {
    timeline.push(Math.round(emi * i + fee))
  }
  return timeline
}

const renderLineChart = (repaymentA, repaymentB) => {
  if (!lineCanvas.value) return

  const labels = Array.from({ length: tenure.value }, (_, i) => `Month ${i + 1}`)

  if (lineChart) lineChart.destroy()

  lineChart = new Chart(lineCanvas.value, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Bank A Total Repayment (₹)',
          data: repaymentA,
          borderColor: '#4e91fc',
          backgroundColor: '#4e91fc33',
          fill: false,
          tension: 0.2
        },
        {
          label: 'Bank B Total Repayment (₹)',
          data: repaymentB,
          borderColor: '#63e6be',
          backgroundColor: '#63e6be33',
          fill: false,
          tension: 0.2
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'top' },
        tooltip: {
          callbacks: {
            label: (context) => `₹${context.raw.toLocaleString()}`
          }
        },
        zoom: {
          zoom: {
            wheel: { enabled: true },
            pinch: { enabled: true },
            mode: 'x'
          },
          pan: {
            enabled: true,
            mode: 'x',
            modifierKey: 'ctrl'
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: value => `₹${value.toLocaleString()}`
          }
        }
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
  totalB.value = Math.round(emiB * N + feeB.value)

  betterBank.value = totalA.value < totalB.value ? 'Bank A' : 'Bank B'

  breakEven.value = null
  for (let t = 6; t <= 360; t += 6) {
    const eA = calculateEMI(P, interestA.value, t)
    const eB = calculateEMI(P, interestB.value, t)
    const TA = eA * t + feeA.value
    const TB = eB * t + feeB.value
    if ((feeA.value > feeB.value && TA <= TB) || (feeB.value > feeA.value && TB <= TA)) {
      breakEven.value = t
      break
    }
  }

  const repaymentTimelineA = generateTotalRepaymentTimeline(emiA, feeA.value, N)
  const repaymentTimelineB = generateTotalRepaymentTimeline(emiB, feeB.value, N)

  await nextTick()
  renderLineChart(repaymentTimelineA, repaymentTimelineB)
}

const resetZoom = () => {
  if (lineChart) lineChart.resetZoom()
}

watch([loanAmount, tenure, interestA, interestB, feeA, feeB], updateComparison)
onMounted(updateComparison)
</script>

<style scoped>
.loan-comparison {
  max-width: 1100px;
  margin: 20px auto;
  padding: 20px;
  background: #eaf6ff;
  border-radius: 10px;
  border: 1px solid #ccc;
}

.form-layout {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.input-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.summary-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: start;
}

.input-group {
  display: flex;
  flex-direction: column;
}

label {
  font-weight: bold;
  margin-bottom: 5px;
}

input[type="number"] {
  padding: 6px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.summary {
  background: #fff5d7;
  padding: 15px;
  border-radius: 8px;
}

.reset-button {
  margin-top: 10px;
  padding: 6px 12px;
  background-color: #4e91fc;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
</style>
