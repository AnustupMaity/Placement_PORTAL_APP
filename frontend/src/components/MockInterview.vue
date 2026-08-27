<template>
  <div class="ppa-page">
    <div class="section-header">
      <div>
        <h1 class="page-title">AI Mock Interview</h1>
        <p class="page-subtitle">Practice your technical and HR skills with our AI</p>
      </div>
    </div>

    <div class="row">
      <!-- Setup Panel -->
      <div class="col-md-4 mb-4" v-if="!sessionActive">
        <div class="ppa-card">
          <div class="card-header bg-dark text-white border-bottom-0"><i class="bi bi-gear-fill me-2"></i>Interview Setup</div>
          <div class="card-body">
            <form @submit.prevent="startInterview">
              <div class="mb-3">
                <label class="form-label-dark">Interview Type</label>
                <select class="form-select" v-model="setup.type">
                  <option value="HR">HR / Behavioral</option>
                  <option value="Technical">Technical</option>
                  <option value="Managerial">Managerial</option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label-dark">Your Branch / Role</label>
                <input type="text" class="form-control" v-model="setup.branch" placeholder="e.g. Computer Science, Full Stack Developer" required>
              </div>
              <div class="mb-4">
                <label class="form-label-dark">Key Skills</label>
                <input type="text" class="form-control" v-model="setup.skills" placeholder="e.g. Python, React, System Design" required>
              </div>
              
              <div class="alert alert-info small">
                <i class="bi bi-info-circle me-1"></i> The AI will ask you questions one-by-one based on this profile and provide feedback on your answers.
              </div>

              <button type="submit" class="btn btn-primary w-100 fw-bold">
                <i class="bi bi-play-circle-fill me-2"></i>Start Mock Interview
              </button>
            </form>
          </div>
        </div>
      </div>

      <!-- Chat Panel -->
      <div class="col-md-8 mx-auto" :class="{'col-md-12': sessionActive}">
        <div class="ppa-card h-100 d-flex flex-column" v-if="sessionActive" style="height: 70vh !important;">
          <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
            <div>
              <i class="bi bi-robot me-2"></i> {{ setup.type }} Interview ({{ setup.branch }})
            </div>
            <button @click="endInterview" class="btn btn-sm btn-outline-light">End Session</button>
          </div>
          
          <!-- Chat Window -->
          <div class="card-body p-4 flex-grow-1 overflow-auto bg-light" ref="chatWindow">
            <div v-for="(msg, index) in messages" :key="index" class="mb-4 d-flex" :class="msg.role === 'user' ? 'justify-content-end' : 'justify-content-start'">
              <div v-if="msg.role === 'assistant'" class="me-3 mt-1">
                <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center" style="width: 36px; height: 36px;">
                  <i class="bi bi-robot"></i>
                </div>
              </div>
              
              <div class="chat-bubble shadow-sm p-3" :class="msg.role === 'user' ? 'bg-white text-dark border' : 'bg-primary text-white'">
                <div style="white-space: pre-wrap; font-size: 1rem; line-height: 1.5;">{{ msg.content }}</div>
              </div>
            </div>

            <div v-if="isLoading" class="d-flex justify-content-start mb-4">
               <div class="me-3 mt-1">
                <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center" style="width: 36px; height: 36px;">
                  <i class="bi bi-robot"></i>
                </div>
              </div>
              <div class="chat-bubble bg-primary text-white shadow-sm p-3 d-flex align-items-center gap-2">
                <span class="spinner-grow spinner-grow-sm text-white" style="width: 1rem; height: 1rem;"></span>
                Thinking...
              </div>
            </div>
          </div>
          
          <!-- Input Area -->
          <div class="card-footer bg-white p-3">
            <form @submit.prevent="sendMessage" class="d-flex gap-2">
              <textarea 
                class="form-control bg-light" 
                v-model="newMessage" 
                placeholder="Type your answer here..." 
                rows="2"
                required
                :disabled="isLoading"
                @keydown.enter.exact.prevent="sendMessage"
              ></textarea>
              <button type="submit" class="btn btn-primary px-4" :disabled="isLoading || !newMessage.trim()">
                <i class="bi bi-send-fill fs-5"></i>
              </button>
            </form>
            <div class="text-muted small mt-2 text-end">Press Enter to send, Shift+Enter for new line</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, nextTick, getCurrentInstance, onMounted } from 'vue';

export default {
  name: 'MockInterview',
  setup() {
    const { proxy } = getCurrentInstance();
    const sessionActive = ref(false);
    const isLoading = ref(false);
    const messages = ref([]);
    const newMessage = ref('');
    const chatWindow = ref(null);
    
    const setup = ref({
      type: 'HR',
      branch: '',
      skills: ''
    });

    onMounted(async () => {
      // Try to pre-fill from user profile
      try {
        const res = await axios.get('/api/student/profile');
        if (res.data) {
          setup.value.branch = res.data.branch || '';
          setup.value.skills = res.data.skills || '';
        }
      } catch (e) {
        // ignore
      }
    });

    const scrollToBottom = async () => {
      await nextTick();
      if (chatWindow.value) {
        chatWindow.value.scrollTop = chatWindow.value.scrollHeight;
      }
    };

    const startInterview = async () => {
      sessionActive.value = true;
      messages.value = [];
      await sendToAI("Hello, I am ready to begin the interview.");
    };
    
    const endInterview = () => {
      if (confirm("Are you sure you want to end this interview session?")) {
        sessionActive.value = false;
        messages.value = [];
      }
    };

    const sendMessage = async () => {
      if (!newMessage.value.trim() || isLoading.value) return;
      
      const msg = newMessage.value.trim();
      messages.value.push({ role: 'user', content: msg });
      newMessage.value = '';
      scrollToBottom();
      
      await sendToAI(msg);
    };
    
    const sendToAI = async (userMsgText) => {
      isLoading.value = true;
      scrollToBottom();
      
      try {
        const payload = {
          type: setup.value.type,
          branch: setup.value.branch,
          skills: setup.value.skills,
          history: messages.value
        };
        
        // We push the user message to history above if it's a real chat, 
        // but if it's the start trigger, we just use the payload.
        if (userMsgText === "Hello, I am ready to begin the interview.") {
           payload.history = [{ role: 'user', content: userMsgText }];
        }
        
        const res = await axios.post('/api/ai/mock-interview', payload);
        messages.value.push({ role: 'assistant', content: res.data.reply });
      } catch (err) {
        messages.value.push({ role: 'assistant', content: 'An error occurred. Please try again.' });
        proxy.$toast('Failed to get response from AI', 'error');
      } finally {
        isLoading.value = false;
        scrollToBottom();
      }
    };

    return { setup, sessionActive, messages, newMessage, isLoading, chatWindow, startInterview, endInterview, sendMessage };
  }
}
</script>

<style scoped>
.chat-bubble {
  max-width: 80%;
  border-radius: 16px;
}

.chat-bubble.bg-white {
  border-top-right-radius: 4px;
}

.chat-bubble.bg-primary {
  border-top-left-radius: 4px;
}
</style>
