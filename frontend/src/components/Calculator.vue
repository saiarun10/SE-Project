<template>
  <div class="calculator">
    <h2>Interest Calculator</h2>

    <div class="input-group">
      <label>Principal: ₹{{ principal.toLocaleString() }}</label>
      <input type="range" v-model="principal" min="100000" max="10000000" step="100000" />
    </div>

    <div class="input-group">
      <label>Interest Rate: {{ rate }}%</label>
      <input type="range" v-model="rate" min="1" max="20" step="0.5" />
    </div>

    <div class="input-group">
      <label>Number of Years: {{ years }}</label>
      <input type="range" v-model="years" min="1" max="30" />
    </div>

    <div class="input-group">
      <label>Compounds per Year: {{ compPerYear }}</label>
      <input type="range" v-model="compPerYear" min="2" max="12" />
    </div>

    <div class="results">
      <h3>Results</h3>
      <p>Simple Interest: ₹{{ simpleInterest.toLocaleString() }}</p>
      <p>Compound Interest: ₹{{ compoundInterest.toLocaleString() }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const principal = ref(1000000)
const rate = ref(5)
const years = ref(5)
const compPerYear = ref(4)

const simpleInterest = computed(() =>
  Math.round((principal.value * rate.value * years.value) / 100)
)

const compoundInterest = computed(() => {
  const p = principal.value
  const r = rate.value / 100
  const n = compPerYear.value
  const t = years.value
  return Math.round(p * Math.pow(1 + r / n, n * t) - p)
})
</script>

<style scoped>
.calculator {
  max-width: 600px;
  margin: 20px auto;
  padding: 20px;
  background: #f6fafd;
  border: 1px solid #ccc;
  border-radius: 12px;
}
.input-group {
  margin: 15px 0;
}
label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}
input[type="range"] {
  width: 100%;
}
.results {
  margin-top: 20px;
  background: #eefaf2;
  padding: 15px;
  border-radius: 8px;
}
</style>

