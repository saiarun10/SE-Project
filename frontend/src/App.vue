<template>
  <div>
    <nav style="padding: 10px; background-color: #e3f1f2;">
      <button @click="goToDashboard">Go to Dashboard</button>
      <button @click="router.push('/calculator')">Interest Calculator</button>
      <button @click="router.push('/loan-comparison')">Loan Comparison</button>    
    </nav>

    <main style="padding: 20px;">
      <RouterView />
    </main>

    <footer style="text-align: center; padding: 10px; background-color: #e3f1f2;">
      © 2025. All rights reserved.
    </footer>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function goToDashboard() {
  router.push('/user-dashboard')
}
</script>

