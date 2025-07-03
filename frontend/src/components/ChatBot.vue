<template>
  <div>
    <!-- Floating Chat Button -->
    <button
      class="chat-button rounded-circle shadow-lg"
      @click="toggleChat"
      aria-label="Toggle chat"
    >
      <i class="bi bi-chat-dots-fill"></i>
    </button>

    <!-- Chat Dialog (Chrome Extension Style) -->
    <div
      v-if="showChat"
      class="chat-dialog shadow-lg"
      role="dialog"
      aria-labelledby="chatDialogLabel"
      ref="chatDialog"
    >
      <div class="chat-content">
        <div class="chat-header">
          <h5 class="chat-title" id="chatDialogLabel">Chat with Us</h5>
          <button
            type="button"
            class="btn-close"
            @click="showChat = false"
            aria-label="Close"
          ></button>
        </div>
        <div class="chat-body">
          <div class="chat-container">
            <div
              v-for="(message, index) in messages"
              :key="index"
              :class="[
                'chat-message',
                message.sender === 'user' ? 'user-message' : 'bot-message',
              ]"
            >
              {{ message.text }}
            </div>
          </div>
          <div class="input-group mt-3">
            <input
              v-model="newMessage"
              type="text"
              class="form-control"
              placeholder="Type your message..."
              @keyup.enter="sendMessage"
            />
            <button
              class="btn send-button"
              type="button"
              @click="sendMessage"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ChatBot',
  data() {
    return {
      showChat: false,
      messages: [
        { sender: 'bot', text: 'Hello! How can I assist you today?' },
      ],
      newMessage: '',
      windowWidth: 0,
    };
  },
  computed: {
    dialogSize() {
      if (this.windowWidth < 576) return 'small';
      if (this.windowWidth < 992) return 'medium';
      return 'large';
    },
  },
  mounted() {
    this.windowWidth = window.innerWidth;
    window.addEventListener('resize', this.handleResize);
    document.addEventListener('click', this.handleOutsideClick);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize);
    document.removeEventListener('click', this.handleOutsideClick);
  },
  methods: {
    toggleChat() {
      this.showChat = !this.showChat;
      if (this.showChat) {
        this.$nextTick(() => this.adjustDialogPosition());
      }
    },
    handleResize() {
      this.windowWidth = window.innerWidth;
      if (this.showChat) {
        this.adjustDialogPosition();
      }
    },
    adjustDialogPosition() {
      const dialog = this.$refs.chatDialog;
      const button = this.$el.querySelector('.chat-button');
      if (!dialog || !button) return;

      const buttonRect = button.getBoundingClientRect();
      const dialogRect = dialog.getBoundingClientRect();
      const viewportHeight = window.innerHeight;
      const viewportWidth = window.innerWidth;

      // Position dialog above and to the left of the chat button
      let top = buttonRect.top - dialogRect.height - 15;
      let left = buttonRect.left - dialogRect.width + buttonRect.width;

      // Ensure dialog stays within viewport
      if (top < 15) top = 15;
      if (left < 15) left = 15;
      if (left + dialogRect.width > viewportWidth - 15) {
        left = viewportWidth - dialogRect.width - 15;
      }

      dialog.style.top = `${top}px`;
      dialog.style.left = `${left}px`;
    },
    handleOutsideClick(event) {
      if (!this.showChat) return;
      const dialog = this.$refs.chatDialog;
      const button = this.$el.querySelector('.chat-button');
      if (
        dialog &&
        !dialog.contains(event.target) &&
        button &&
        !button.contains(event.target)
      ) {
        this.showChat = false;
      }
    },
    sendMessage() {
      if (this.newMessage.trim()) {
        this.messages.push({ sender: 'user', text: this.newMessage });
        // Simulate bot response
        setTimeout(() => {
          this.messages.push({
            sender: 'bot',
            text: `You said: ${this.newMessage}`,
          });
          this.scrollToBottom();
        }, 500);
        this.newMessage = '';
        this.scrollToBottom();
      }
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$el.querySelector('.chat-container');
        container.scrollTop = container.scrollHeight;
      });
    },
  },
};
</script>

<style scoped>
.chat-button {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 65px;
  height: 65px;
  font-size: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  background: linear-gradient(135deg, #007bff, #00d4ff);
  color: white;
  border: none;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.chat-button:hover {
  transform: scale(1.15);
  box-shadow: 0 4px 15px rgba(0, 123, 255, 0.4);
}

.chat-button:active {
  transform: scale(0.95);
}

.chat-dialog {
  position: fixed;
  z-index: 1001;
  background-color: transparent;
  max-width: 450px;
  min-width: 320px;
  min-height: 400px;
}

.chat-content {
  background: linear-gradient(145deg, #ffffff, #f0f4f8);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #ced4da;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: linear-gradient(90deg, #e9ecef, #dee2e6);
  border-bottom: 1px solid #ced4da;
}

.chat-title {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: #343a40;
}

.chat-body {
  padding: 20px;
}

.chat-container {
  max-height: 350px;
  min-height: 250px;
  overflow-y: auto;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 15px;
  scrollbar-width: thin;
  scrollbar-color: #adb5bd #f8f9fa;
}

.chat-container::-webkit-scrollbar {
  width: 8px;
}

.chat-container::-webkit-scrollbar-track {
  background: #f8f9fa;
}

.chat-container::-webkit-scrollbar-thumb {
  background: #adb5bd;
  border-radius: 4px;
}

.chat-message {
  margin-bottom: 12px;
  padding: 10px 14px;
  border-radius: 12px;
  max-width: 85%;
  word-wrap: break-word;
  word-break: break-word;
  line-height: 1.4;
  font-size: 0.95rem;
}

.user-message {
  margin-left: auto;
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  text-align: right;
}

.bot-message {
  margin-right: auto;
  background: linear-gradient(135deg, #e9ecef, #dee2e6);
  color: #212529;
}

.send-button {
  background: linear-gradient(135deg, #28a745, #218838);
  color: white;
  border: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.send-button:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);
}

.send-button:active {
  transform: scale(0.95);
}

/* Responsive adjustments */
@media (max-width: 576px) {
  .chat-button {
    width: 55px;
    height: 55px;
    font-size: 22px;
    bottom: 15px;
    right: 15px;
  }
  .chat-dialog {
    min-width: 280px;
    max-width: 90vw;
    min-height: 350px;
  }
  .chat-container {
    max-height: 300px;
    min-height: 200px;
  }
  .chat-title {
    font-size: 1rem;
  }
}
</style>
