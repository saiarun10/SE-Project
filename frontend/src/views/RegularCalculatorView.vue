<template>
  <div class="calculator-wrapper">
    <iframe
      src="https://www.desmos.com/scientific"
      class="calculator-frame"
    ></iframe>
  </div>
</template>

<style scoped>
.calculator-wrapper {
  max-width: 400px;     /* Restrict width */
  height: 500px;        /* Restrict height */
  margin: auto;         /* Center horizontally */
  border: 1px solid #ccc;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.calculator-frame {
  width: 100%;
  height: 100%;
  border: none;
}
</style>

