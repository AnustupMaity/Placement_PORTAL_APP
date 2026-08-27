<template>
  <div class="support-bot-container">
    <!-- Chat Toggle Button -->
    <button 
      @click="toggleChat" 
      class="btn btn-primary rounded-circle shadow-lg d-flex align-items-center justify-content-center support-bot-toggle"
    >
      <i class="bi bi-robot fs-4" v-if="!isOpen"></i>
      <i class="bi bi-x-lg fs-5" v-else></i>
    </button>

    <!-- Chat Window -->
    <div v-if="isOpen" class="card shadow-lg support-bot-window border-0 overflow-hidden">
      <div class="card-header bg-primary text-white d-flex align-items-center justify-content-between p-3 border-0">
        <div class="d-flex align-items-center gap-2">
          <i class="bi bi-robot fs-5"></i>
          <h6 class="mb-0 fw-bold">Portal Assistant</h6>
        </div>
        <button @click="toggleChat" class="btn btn-sm btn-link text-white p-0 text-decoration-none">
          <i class="bi bi-dash-lg"></i>
        </button>
      </div>
      
      <div class="card-body p-0 d-flex flex-column" style="height: 350px;">
        <div class="flex-grow-1 p-3 overflow-auto" ref="chatBox">
          <div v-if="messages.length === 0" class="text-center text-muted small mt-4">
            <i class="bi bi-chat-left-dots fs-3 mb-2 d-block"></i>
            Ask me anything about using the Placement Portal!
          </div>
          
          <div v-for="(msg, index) in messages" :key="index" class="mb-3 d-flex" :class="msg.role === 'user' ? 'justify-content-end' : 'justify-content-start'">
            <div class="chat-bubble shadow-sm" :class="msg.role === 'user' ? 'bg-primary text-white' : 'bg-light text-dark'">
              <span style="white-space: pre-wrap; font-size: 0.9rem;">{{ msg.content }}</span>
            </div>
          </div>
          
          <div v-if="isLoading" class="d-flex justify-content-start mb-3">
            <div class="chat-bubble bg-light text-muted small d-flex align-items-center gap-2">
              <span class="spinner-grow spinner-grow-sm" style="width: 1rem; height: 1rem;"></span>
              Thinking...
            </div>
          </div>
        </div>
        
        <div class="p-2 border-top bg-white">
          <form @submit.prevent="sendMessage" class="d-flex gap-2">
            <input 
              type="text" 
              class="form-control form-control-sm border-0 bg-light" 
              v-model="newMessage" 
              placeholder="Type your question..." 
              required
              :disabled="isLoading"
            >
            <button type="submit" class="btn btn-primary btn-sm rounded-circle px-2" :disabled="isLoading || !newMessage.trim()">
              <i class="bi bi-send-fill"></i>
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, nextTick, getCurrentInstance } from 'vue';

export default {
  name: 'SupportBot',
  setup() {
    const { proxy } = getCurrentInstance();
    const isOpen = ref(false);
    const messages = ref([]);
    const newMessage = ref('');
    const isLoading = ref(false);
    const chatBox = ref(null);

    const toggleChat = () => {
      isOpen.value = !isOpen.value;
      if (isOpen.value && messages.value.length === 0) {
        messages.value.push({ role: 'assistant', content: 'Hi! I am the Portal AI Assistant. How can I help you today?' });
      }
    };

    const scrollToBottom = async () => {
      await nextTick();
      if (chatBox.value) {
        chatBox.value.scrollTop = chatBox.value.scrollHeight;
      }
    };

    const sendMessage = async () => {
      if (!newMessage.value.trim() || isLoading.value) return;
      
      const userMsg = newMessage.value.trim();
      messages.value.push({ role: 'user', content: userMsg });
      newMessage.value = '';
      scrollToBottom();
      
      isLoading.value = true;
      
      try {
        const res = await axios.post('/api/ai/support-bot', {
          message: userMsg,
          history: messages.value.slice(0, -1) // pass all previous context except the one we just added
        });
        
        messages.value.push({ role: 'assistant', content: res.data.reply });
      } catch (err) {
        messages.value.push({ role: 'assistant', content: 'Sorry, I encountered an error connecting to the server.' });
      } finally {
        isLoading.value = false;
        scrollToBottom();
      }
    };

    return { isOpen, toggleChat, messages, newMessage, sendMessage, isLoading, chatBox };
  }
}
</script>

<style scoped>
.support-bot-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1050;
  font-family: 'Plus Jakarta Sans', sans-serif;
}

.support-bot-toggle {
  width: 56px;
  height: 56px;
  transition: transform 0.2s;
}

.support-bot-toggle:hover {
  transform: scale(1.05);
}

.support-bot-window {
  position: absolute;
  bottom: 70px;
  right: 0;
  width: 320px;
  border-radius: 12px;
  animation: slideUp 0.3s ease-out;
}

.chat-bubble {
  max-width: 85%;
  padding: 8px 12px;
  border-radius: 12px;
}

.bg-primary {
  border-top-right-radius: 2px;
}

.bg-light {
  border-top-left-radius: 2px;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 576px) {
  .support-bot-window {
    width: 280px;
  }
}
</style>
