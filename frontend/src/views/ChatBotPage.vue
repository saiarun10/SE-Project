<template>
  <div class="page-container d-flex flex-column bg-light">
    <Navbar />
    <div class="content-wrapper d-flex flex-grow-1">
      <!-- Collapsible Sidebar for History -->
      <div :class="['sidebar bg-white shadow-sm', { 'collapsed': isSidebarCollapsed }]">
        <div class="sidebar-header p-3 d-flex justify-content-between align-items-center">
          <h3 v-if="!isSidebarCollapsed" class="h5 mb-0">Chat History</h3>
          <button @click="toggleSidebar" class="btn btn-sm btn-outline-secondary">
            <i :class="isSidebarCollapsed ? 'fas fa-chevron-right' : 'fas fa-chevron-left'"></i>
          </button>
        </div>
        <div v-if="!isSidebarCollapsed" class="history-filters p-3">
          <select v-model="selectedTimeRange" @change="fetchChatHistory" class="form-select form-select-sm">
            <option value="1h">Last Hour</option>
            <option value="6h">Last 6 Hours</option>
            <option value="1d">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="all">All Time</option>
          </select>
        </div>
        <div v-if="!isSidebarCollapsed" class="history-list list-group list-group-flush flex-grow-1">
           <p v-if="history.length === 0" class="text-muted p-3 small">No history for this period.</p>
           <a href="#" v-else v-for="(item, index) in history" :key="index" class="list-group-item list-group-item-action py-2">
              <div class="d-flex w-100 justify-content-between">
                <strong class="mb-1">{{ item.sender === 'user' ? 'You' : 'Bot' }}</strong>
                <small>{{ item.timestamp }}</small>
              </div>
              <p class="mb-1 small text-muted">{{ item.text.substring(0, 40) }}...</p>
           </a>
        </div>
      </div>

      <!-- Main Chat Content -->
      <main class="chat-main flex-grow-1 d-flex flex-column p-3 p-md-4">
        <div class="chat-container card shadow-sm border-light flex-grow-1">
          <div class="card-header bg-primary text-white p-3 d-flex align-items-center gap-3">
            <i class="fas fa-robot fs-4"></i>
            <h2 class="h5 mb-0 fw-semibold">FinBot Assistant</h2>
          </div>
          <div ref="chatMessages" class="card-body chat-messages p-3">
            <!-- Messages -->
            <div v-for="(message, index) in messages" :key="index" :class="['mb-3 d-flex', message.sender === 'user' ? 'justify-content-end' : 'justify-content-start']">
              <div class="d-flex align-items-end gap-2" style="max-width: 70%;">
                <i v-if="message.sender !== 'user'" class="fas fa-robot text-primary fs-5"></i>
                <div :class="['p-3 rounded-3', message.sender === 'user' ? 'bg-info-subtle text-info-emphasis' : 'bg-white border']">
                  <span class="fw-semibold">{{ message.sender === 'user' ? 'You' : 'Bot' }}: </span>
                  <span v-html="message.text"></span>
                  <div class="text-muted small mt-1 text-end">{{ message.timestamp }}</div>
                </div>
                <i v-if="message.sender === 'user'" class="fas fa-user text-primary fs-5"></i>
              </div>
            </div>
            <!-- Typing Indicator -->
            <div v-if="isTyping" class="d-flex justify-content-start">
              <div class="d-flex align-items-end gap-2">
                <i class="fas fa-robot text-primary fs-5"></i>
                <div class="p-3 rounded-3 bg-white border">Typing...</div>
              </div>
            </div>
          </div>
          <div class="card-footer p-3 bg-white">
            <div class="input-group">
              <input v-model="userInput" @keyup.enter="sendMessage" type="text" class="form-control p-3" placeholder="Ask FinBot a question..." :disabled="isTyping">
              <button @click="sendMessage" class="btn btn-primary text-white px-4" :disabled="!userInput.trim() || isTyping">
                <i class="fas fa-paper-plane me-2"></i>Send
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
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
      history: [],
      isTyping: false,
      isSidebarCollapsed: window.innerWidth < 768, // Collapse by default on smaller screens
      selectedTimeRange: '1h',
    };
  },
  methods: {
    toggleSidebar() {
      this.isSidebarCollapsed = !this.isSidebarCollapsed;
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const chatContainer = this.$refs.chatMessages;
        if (chatContainer) chatContainer.scrollTop = chatContainer.scrollHeight;
      });
    },
    async fetchChatHistory() {
        // This method is now simplified to fetch history for the sidebar.
        // The main chat window will only show the current session's history.
      try {
        const response = await axios.get(`${import.meta.env.VITE_BASE_URL}/api/chatbot/history/${this.selectedTimeRange}`, {
          headers: { Authorization: `Bearer ${this.$store.state.token}` }
        });
        this.history = response.data.history;
      } catch (error) {
        console.error('Failed to fetch chat history:', error);
        this.history = []; // Clear history on error
      }
    },
    async fetchCurrentSessionHistory() {
      // Fetches only the current session's history for the main chat window
      try {
        const response = await axios.get(`${import.meta.env.VITE_BASE_URL}/api/history`, {
          headers: { Authorization: `Bearer ${this.$store.state.token}` }
        });
        this.messages = response.data.history;
        if (this.messages.length === 0) {
           this.messages.push({ 
            sender: 'bot', 
            text: 'Hello! I am FinBot. Ask me about saving or earning money!', 
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          });
        }
        this.scrollToBottom();
      } catch (error) {
        console.error('Failed to fetch current session history:', error);
      }
    },
    async sendMessage() {
      const messageText = this.userInput.trim();
      if (!messageText || this.isTyping) return;

      this.messages.push({
        sender: 'user',
        text: messageText,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      });
      
      this.userInput = '';
      this.isTyping = true;
      this.scrollToBottom();

      try {
        const response = await axios.post(`${import.meta.env.VITE_BASE_URL}/api/send_message`, 
          { message: messageText },
          { headers: { Authorization: `Bearer ${this.$store.state.token}` } }
        );
        this.messages.push(response.data.reply);
      } catch (error) {
        let botErrorMessage = 'Sorry, I am having trouble connecting. Please try again.';
        if (error.response && error.response.status === 403) {
            botErrorMessage = `You've reached your free message limit! <a href="/premium" class="text-primary fw-bold">Upgrade to Premium</a> for unlimited chats.`;
        } else {
            console.error('Failed to send message:', error);
        }
        this.messages.push({
          sender: 'bot',
          text: botErrorMessage,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        });
      } finally {
        this.isTyping = false;
        this.scrollToBottom();
      }
    }
  },
  mounted() {
    this.fetchCurrentSessionHistory(); // Load main chat window
    this.fetchChatHistory(); // Load sidebar history
  }
};
</script>

<style scoped>
.page-container {
  height: 100vh;
  overflow: hidden;
}
.content-wrapper {
  overflow: hidden; /* Prevent this wrapper from scrolling */
}
.sidebar {
  width: 300px;
  flex-shrink: 0;
  transition: width 0.3s ease;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow-y: auto;
}
.sidebar.collapsed {
  width: 60px;
}
.sidebar.collapsed .history-filters,
.sidebar.collapsed .history-list {
  display: none;
}
.history-list {
  overflow-y: auto;
}
.chat-main {
  height: 100%;
  display: flex;
  flex-direction: column;
}
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden; /* Prevent the card itself from scrolling */
}
.chat-messages {
  flex-grow: 1;
  overflow-y: auto;
}
</style>
