<template>
  <div class="page-container">
    <Navbar />

    <main class="chat-main">
      <header class="chat-header p-3 d-flex justify-content-between align-items-center border-bottom bg-white">
        <div class="d-flex align-items-center gap-3">
          <div class="avatar bg-primary text-white">
            <i class="fas fa-robot"></i>
          </div>
          <div>
            <h2 class="h5 mb-0 fw-semibold">FinBot</h2>
            <div class="text-success small">
              <i class="fas fa-circle me-1" style="font-size: 0.6em;"></i> Online
            </div>
          </div>
        </div>
        
        <button @click="startNewChat" class="btn btn-outline-secondary" title="Refresh and start a new chat">
          <i class="fas fa-sync-alt"></i>
          <span class="d-none d-sm-inline ms-2">New Chat</span>
        </button>
      </header>

      <div ref="chatMessages" class="chat-messages flex-grow-1 p-md-4">
        <div v-for="(message, index) in messages" :key="index" :class="['message-group', message.sender === 'user' ? 'user' : 'bot']">
          <div class="message-bubble">
            <div v-if="message.sender === 'bot'" class="fw-bold bot-name">FinBot</div>
            <div v-html="message.text"></div>
            <div class="timestamp">{{ getRelativeTime(message.isoTimestamp) }}</div>
          </div>
        </div>
        <div v-if="isTyping" class="message-group bot">
          <div class="message-bubble typing-indicator">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>

      <footer class="chat-input-area p-2 p-sm-3 bg-white border-top">
        <div class="input-group">
          <input v-model="userInput" @keyup.enter="sendMessage" type="text" class="form-control" placeholder="Ask FinBot..." :disabled="isTyping">
          <button @click="sendMessage" class="btn btn-primary" :disabled="!userInput.trim() || isTyping">
            <i class="fas fa-paper-plane"></i>
          </button>
        </div>
      </footer>
    </main>
    
    <AppFooter />
  </div>
</template>

<script>
import Navbar from '@/components/Navbar.vue';
import AppFooter from '@/components/Footer.vue';
import axios from 'axios';

export default {
  name: 'ChatBotPage',
  components: { Navbar, AppFooter },
  data() {
    return {
      userInput: '',
      messages: [],
      isTyping: false,
    };
  },
  methods: {
    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.chatMessages;
        if (container) {
          container.scrollTop = container.scrollHeight;
        }
      });
    },
    getRelativeTime(isoTimestamp) {
        if (!isoTimestamp) return '';
        const now = new Date();
        const messageTime = new Date(isoTimestamp);

        const diffSeconds = Math.round((now - messageTime) / 1000);
        const diffMinutes = Math.round(diffSeconds / 60);
        const diffHours = Math.round(diffMinutes / 60);

        if (diffSeconds < 10) return "just now";
        if (diffMinutes < 1) return `${diffSeconds} seconds ago`;
        if (diffMinutes < 60) return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`;
        if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;

        return messageTime.toLocaleDateString();
    },
    displayWelcomeMessage() {
      this.messages.push({
          sender: 'bot',
          text: 'Hello! I am FinBot, your personal finance assistant. How can I help you today?',
          isoTimestamp: new Date().toISOString()
      });
    },
    startNewChat() {
      // This action clears the view for a fresh start.
      this.messages = []; 
      this.displayWelcomeMessage();
      this.scrollToBottom();
    },
    async sendMessage() {
      const messageText = this.userInput.trim();
      if (!messageText || this.isTyping) return;

      const userMessage = {
        sender: 'user',
        text: messageText,
        isoTimestamp: new Date().toISOString()
      };
      this.messages.push(userMessage);

      this.userInput = '';
      this.isTyping = true;
      this.scrollToBottom();

      try {
        const response = await axios.post(`${import.meta.env.VITE_BASE_URL}/api/send_message`,
          { message: messageText },
          { headers: { Authorization: `Bearer ${this.$store.state.token}` } }
        );

        const botReply = {
          ...response.data.reply,
          isoTimestamp: new Date().toISOString()
        };
        this.messages.push(botReply);
      } catch (error)
      {
        let botErrorMessage = 'Sorry, an error occurred. Please try again later.';
        if (error.response?.status === 403) {
            botErrorMessage = `You've reached your free message limit! <a href="/buy-premium" class="text-primary fw-bold">Upgrade to Premium</a> for unlimited chats.`;
        } else if (error.response?.data?.message) {
            botErrorMessage = error.response.data.message;
        } else {
            console.error('Failed to send message:', error);
        }
        this.messages.push({
          sender: 'bot',
          text: botErrorMessage,
          isoTimestamp: new Date().toISOString()
        });
      } finally {
        this.isTyping = false;
        this.scrollToBottom();
      }
    }
  },
  mounted() {
    // UPDATED: Always start with a new, clear chat when the page loads.
    this.startNewChat();

    // This interval keeps the "time ago" display accurate.
    setInterval(() => {
        this.messages = [...this.messages];
    }, 60000);
  }
};
</script>

<style scoped>
/* --- Layout & Styles (Unchanged) --- */
.page-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f8f9fa;
}
.chat-main {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.chat-header {
  flex-shrink: 0;
}
.chat-messages {
  flex-grow: 1;
  overflow-y: auto;
  padding: 0.75rem;
  background-color: #f4f7f9;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.chat-input-area {
  flex-shrink: 0;
}
.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}
.message-group {
  display: flex;
  flex-direction: column;
  max-width: 85%;
  width: fit-content;
}
.message-group.bot {
  align-self: flex-start;
  align-items: flex-start;
}
.message-group.user {
  align-self: flex-end;
  align-items: flex-end;
}
.message-bubble {
  padding: 10px 16px;
  border-radius: 20px;
  line-height: 1.5;
  word-wrap: break-word;
  font-size: 0.95rem;
}
.message-group.bot .message-bubble {
  background-color: #e9ecef;
  color: #212529;
  border-bottom-left-radius: 5px;
}
.message-group.user .message-bubble {
  background-color: var(--bs-primary);
  color: white;
  border-bottom-right-radius: 5px;
}
.bot-name {
  font-size: 0.9em;
  color: var(--bs-primary);
  margin-bottom: 4px;
}
.timestamp {
  font-size: 0.7rem;
  color: #6c757d;
  margin-top: 8px;
  text-align: right;
}
.message-group.user .timestamp {
  color: rgba(255, 255, 255, 0.7);
}
.typing-indicator span {
  height: 8px;
  width: 8px;
  background-color: #6c757d;
  border-radius: 50%;
  display: inline-block;
  margin: 0 1px;
  animation: wave 1.3s infinite;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
@keyframes wave {
  0%, 60%, 100% { transform: initial; }
  30% { transform: translateY(-8px); }
}
.chat-input-area .form-control {
  border-right: 0;
  border-radius: 2rem 0 0 2rem;
  padding: 0.5rem 1.25rem;
  box-shadow: none;
  border-color: #ced4da;
}
.chat-input-area .btn {
  border-radius: 0 2rem 2rem 0;
  padding: 0.5rem 1.25rem;
  z-index: 2;
}
@media (min-width: 768px) {
  .chat-messages {
    padding: 1.5rem;
    gap: 1.25rem;
  }
  .message-group {
    max-width: 75%;
  }
  .message-bubble {
    font-size: 1rem;
    padding: 12px 18px;
  }
  .timestamp {
    font-size: 0.75rem;
  }
  .chat-input-area .form-control,
  .chat-input-area .btn {
    padding: 0.75rem 1.5rem;
  }
}
</style>