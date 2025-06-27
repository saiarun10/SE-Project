<template>
  <RouterView />
</template>
<style>
#app {
  margin-top: 60px
}
</style>
<script setup>
import { RouterView } from 'vue-router'
import ChartDataLabels from 'chartjs-plugin-datalabels';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables, ChartDataLabels);

</script>



