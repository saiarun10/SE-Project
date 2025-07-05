<template>
  <div class="chatbot-page-container">
    <Navbar />
    <main class="chatbot-content">
      <h1 class="page-title">Chat with Us</h1>
      <div class="chatbot-container">
        <div class="card">
          <div class="card-header">
            ChatBot
          </div>
          <div class="card-body">
            <div class="chat-messages mb-3" style="height: 300px; overflow-y: auto;">
              <div class="alert alert-info" role="alert">
                Welcome! How can I assist you today?
              </div>
            </div>
            <div class="input-group">
              <input type="text" class="form-control" placeholder="Type your message..." aria-label="Chat input">
              <button class="btn btn-primary" type="button">Send</button>
            </div>
          </div>
        </div>
      </div>
    </main>
    <AppFooter />
  </div>
</template>

<script>
import Navbar from '@/components/Navbar.vue';
import AppFooter from '@/components/Footer.vue';

export default {
  name: 'ChatBotPage',
  components: {
    Navbar,
    AppFooter,
  },
};
</script>