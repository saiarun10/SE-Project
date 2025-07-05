<template>
  <div class="chatbot-page-container min-vh-100 d-flex flex-column bg-info-subtle">
    <Navbar />
    <main class="chatbot-content flex-grow-1 container my-5">
      <h1 class="page-title display-4 fw-bold text-center mb-5 text-primary">Chat with Financial Bot</h1>
      <div class="chatbot-container mx-auto" style="max-width: 800px;">
        <div class="card shadow-lg border-light">
          <div class="card-header bg-primary text-white p-4 d-flex align-items-center gap-3">
            <i class="fas fa-robot fs-4"></i>
            <h2 class="h4 mb-0 fw-semibold">Financial Bot Assistant</h2>
          </div>
          <div class="card-body p-4">
            <div class="chat-messages mb-4" style="height: 500px; overflow-y: auto; background: #f8f9fa;">
              <div v-for="(message, index) in messages" :key="index" :class="['mb-3 d-flex', message.sender === 'user' ? 'justify-content-end' : 'justify-content-start']">
                <div class="d-flex align-items-end gap-2" style="max-width: 70%;">
                  <i v-if="message.sender !== 'user'" class="fas fa-robot text-primary fs-5"></i>
                  <div :class="[
                    'p-3 rounded-3 position-relative',
                    message.sender === 'user' ? 'bg-info-subtle text-info-emphasis rounded-bottom-end-0' : 'bg-light text-dark rounded-bottom-start-0'
                  ]">
                    <span class="fw-semibold">{{ message.sender === 'user' ? 'You' : 'Bot' }}: </span>
                    {{ message.text }}
                    <div class="text-muted small mt-1 text-end">
                      {{ message.timestamp }}
                    </div>
                    <div :class="[
                      'position-absolute w-3 h-3 bottom-0',
                      message.sender === 'user' ? 'end-0 bg-info-subtle clip-right' : 'start-0 bg-light clip-left'
                    ]"></div>
                  </div>
                  <i v-if="message.sender === 'user'" class="fas fa-user text-primary fs-5"></i>
                </div>
              </div>
              <div v-if="isTyping" class="mb-3 d-flex justify-content-start">
                <div class="d-flex align-items-end gap-2" style="max-width: 70%;">
                  <i class="fas fa-robot text-primary fs-5"></i>
                  <div class="p-3 rounded-3 bg-light text-dark rounded-bottom-start-0 position-relative">
                    <span class="fw-semibold">Bot: </span>Typing...
                    <div class="position-absolute w-3 h-3 bottom-0 start-0 bg-light clip-left"></div>
                  </div>
                </div>
              </div>
            </div>
            <div class="input-group">
              <input 
                v-model="userInput" 
                @keyup.enter="sendMessage"
                type="text" 
                class="form-control p-3 rounded-pill border-primary-subtle" 
                placeholder="Type your financial query..." 
                aria-label="Chat input"
              >
              <button 
                @click="sendMessage" 
                class="btn btn-primary text-white px-4 rounded-pill d-flex align-items-center gap-2" 
                :disabled="!userInput.trim()"
              >
                <i class="fas fa-paper-plane"></i>
                Send
              </button>
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
  data() {
    return {
      userInput: '',
      messages: [
        { 
          sender: 'bot', 
          text: 'Hello, I am an AI bot for financial queries. How can I assist you today?', 
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ],
      isTyping: false,
      botReplies: [
        'Great question! Let me break down some financial insights for you...',
        'I can help with budgeting, investments, or loans. What’s on your mind?',
        'Did you know compound interest can be your best friend? Want to explore that?',
        'Let’s talk money! What financial topic are you curious about?',
        'I’m crunching the numbers for you! What do you want to discuss?',
        'Financial planning can be fun! What’s your next money move?'
      ]
    };
  },
  methods: {
    sendMessage() {
      if (!this.userInput.trim()) return;

      // Add user message with timestamp
      this.messages.push({
        sender: 'user',
        text: this.userInput,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      });

      // Clear input
      this.userInput = '';

      // Show typing indicator
      this.isTyping = true;

      // Simulate bot response delay
      setTimeout(() => {
        const randomReply = this.botReplies[Math.floor(Math.random() * this.botReplies.length)];
        this.messages.push({
          sender: 'bot',
          text: randomReply,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        });
        this.isTyping = false;

        // Scroll to bottom of chat
        this.$nextTick(() => {
          const chatContainer = this.$el.querySelector('.chat-messages');
          chatContainer.scrollTop = chatContainer.scrollHeight;
        });
      }, 1000);
    }
  }
};
</script>

<style scoped>
.chatbot-page-container {
  display: flex;
  flex-direction: column;
}

.chat-messages {
  scrollbar-width: thin;
  scrollbar-color: #0dcaf0 #f8f9fa;
}

.chat-messages::-webkit-scrollbar {
  width: 8px;
}

.chat-messages::-webkit-scrollbar-track {
  background: #f8f9fa;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #0dcaf0;
  border-radius: 4px;
}

/* WhatsApp-like message tails */
.clip-right {
  clip-path: polygon(0 0, 100% 0, 100% 100%, 20% 100%);
}

.clip-left {
  clip-path: polygon(0 0, 100% 0, 80% 100%, 0 100%);
}
</style>