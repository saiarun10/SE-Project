<template>
  <Navbar />
  <div class="pdf-viewer-container">
    <button class="back-btn" @click="$router.go(-1)">
      <i class="fas fa-arrow-left"></i> Back To Module
    </button>

    <h2 class="topic-title">Topic: {{ topicTitle }}</h2>

    <iframe
      v-if="pdfPath"
      :src="pdfPath"
      class="pdf-frame"
      frameborder="0"
    ></iframe>

    <div v-else class="error-message">PDF not available.</div>
  </div>
  <AppFooter />
</template>

<script>
import Navbar from '@/components/Navbar.vue'
import AppFooter from '@/components/Footer.vue'

export default {
  name: 'Topic',
  components: {
    Navbar,
    AppFooter
  }, 
  data() {
    return {
      topicTitle: '',
      pdfPath: ''
    };
  },
  mounted() {
    const { topicId, lessonId } = this.$route.params;

    // Example logic — You can map topicId to filename or URL
    const topicMap = {
      1: { title: 'What is a Stock?', file: 'stock-intro.pdf' },
      2: { title: 'How Stock Market Works', file: 'stock-market-works.pdf' }
    };

    const topic = topicMap[topicId];
    if (topic) {
      this.topicTitle = topic.title;
      this.pdfPath = `/pdfs/${topic.file}`; // Ensure this path is valid and publicly accessible
    }
  }
};
</script>

<style scoped>
.pdf-viewer-container {
  padding: 20px;
  background: #fff;
}
.back-btn {
  margin-bottom: 10px;
}
.topic-title {
  font-size: 24px;
  margin-bottom: 20px;
}
.pdf-frame {
  width: 100%;
  height: 80vh;
  border: 1px solid #ccc;
}

.back-btn {
  background: #52575b;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.3s ease;
}

.back-btn:hover {
  background: #3d4145;
}
</style>
