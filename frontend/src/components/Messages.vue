<template>
  <div class="ppa-page h-100 d-flex flex-column" style="min-height: 80vh;">
    <div class="section-header mb-3">
      <div class="d-flex justify-content-between align-items-center w-100">
        <div>
          <h1 class="page-title">Messages & Support</h1>
          <p class="page-subtitle">Chat with administrators, companies, and resolve issues.</p>
        </div>
        <button class="btn btn-primary" @click="showComposeModal = true">
          <i class="bi bi-pencil-square me-2"></i>New Message
        </button>
      </div>
    </div>

    <div class="row flex-grow-1 gx-4">
      <!-- Threads List -->
      <div class="col-md-4 d-flex flex-column">
        <div class="ppa-card flex-grow-1 d-flex flex-column">
          <div class="card-header border-bottom-0 pb-0">
            <h5 class="fw-bold mb-0">Conversations</h5>
          </div>
          <div class="card-body p-0 d-flex flex-column overflow-auto mt-2" style="max-height: 600px;">
            <div v-if="loadingThreads" class="text-center py-4">
              <span class="ppa-spinner ppa-spinner-sm"></span>
            </div>
            <div v-else-if="threads.length === 0" class="text-center py-4 text-muted small">
              <i class="bi bi-chat-square-text fs-1 d-block mb-2 text-light"></i>
              No conversations yet.
            </div>
            <div v-else class="list-group list-group-flush rounded-0">
              <button 
                v-for="t in threads" :key="t.id"
                class="list-group-item list-group-item-action border-0 border-bottom py-3 px-4"
                :class="{ 'bg-light': activeThread?.id === t.id }"
                @click="selectThread(t)"
              >
                <div class="d-flex w-100 justify-content-between mb-1">
                  <h6 class="mb-0 fw-bold text-truncate" style="max-width: 80%;">{{ t.subject }}</h6>
                  <small class="text-muted" style="font-size: 0.7rem;">{{ $formatDate(t.created_at) }}</small>
                </div>
                <div class="d-flex w-100 justify-content-between align-items-center mt-2">
                  <small class="text-muted text-truncate" style="max-width: 70%;">
                    {{ t.creator_id === user.id ? 'To: ' + (t.recipient_name || t.recipient_group) : 'From: ' + t.creator_name }}
                  </small>
                  <span class="badge rounded-pill" :class="t.status === 'resolved' ? 'bg-success' : 'bg-warning text-dark'">
                    {{ t.status }}
                  </span>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Chat View -->
      <div class="col-md-8 d-flex flex-column h-100">
        <div v-if="!activeThread" class="ppa-card flex-grow-1 d-flex align-items-center justify-content-center text-center text-muted h-100 min-h-400">
          <div>
            <i class="bi bi-chat-dots fs-1 d-block mb-3 text-light"></i>
            Select a conversation to view messages
          </div>
        </div>
        
        <div v-else class="ppa-card flex-grow-1 d-flex flex-column" style="min-height: 600px; max-height: 600px;">
          <!-- Chat Header -->
          <div class="card-header border-bottom bg-white py-3 d-flex justify-content-between align-items-center">
            <div>
              <h5 class="fw-bold mb-1">{{ activeThread.subject }}</h5>
              <div class="small text-muted">
                {{ activeThread.creator_id === user.id ? 'To: ' + (activeThread.recipient_name || activeThread.recipient_group) : 'From: ' + activeThread.creator_name }}
              </div>
            </div>
            <div>
              <button v-if="activeThread.status !== 'resolved' && (activeThread.creator_id === user.id || user.role === 'admin')" 
                      class="btn btn-sm btn-outline-success" 
                      @click="resolveThread">
                <i class="bi bi-check-circle me-1"></i>Mark Resolved
              </button>
              <span v-else-if="activeThread.status === 'resolved'" class="badge bg-success">
                <i class="bi bi-check-circle me-1"></i>Resolved
              </span>
            </div>
          </div>
          
          <!-- Chat Messages -->
          <div class="card-body overflow-auto bg-light p-4 flex-grow-1" ref="messagesContainer">
            <div v-if="loadingMessages" class="text-center py-4">
              <span class="ppa-spinner ppa-spinner-sm"></span>
            </div>
            <div v-else class="d-flex flex-column gap-3">
              <div v-for="reply in replies" :key="reply.id" class="d-flex" :class="reply.sender_id === user.id ? 'justify-content-end' : 'justify-content-start'">
                <div class="d-flex flex-column" :class="reply.sender_id === user.id ? 'align-items-end' : 'align-items-start'" style="max-width: 75%;">
                  <div class="small text-muted mb-1 px-1">{{ reply.sender_name }} ({{ reply.sender_role }})</div>
                  <div class="p-3 rounded-4 shadow-sm" :class="reply.sender_id === user.id ? 'bg-primary text-white rounded-bottom-end-0' : 'bg-white text-dark rounded-bottom-start-0'">
                    <span style="white-space: pre-wrap;">{{ reply.body }}</span>
                  </div>
                  <div class="small text-muted mt-1 px-1" style="font-size: 0.65rem;">{{ $formatDate(reply.created_at) }}</div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Chat Input -->
          <div class="card-footer bg-white border-top p-3">
            <form v-if="activeThread.status !== 'resolved'" @submit.prevent="sendReply" class="d-flex gap-2">
              <textarea 
                class="form-control" 
                rows="1" 
                placeholder="Type your message..." 
                v-model="replyForm.body"
                @keydown.enter.prevent="sendReply"
                style="resize: none;"
              ></textarea>
              <button type="submit" class="btn btn-primary px-4 d-flex align-items-center" :disabled="sendingReply || !replyForm.body.trim()">
                <i v-if="!sendingReply" class="bi bi-send"></i>
                <span v-else class="spinner-border spinner-border-sm"></span>
              </button>
            </form>
            <div v-else class="text-center text-muted small py-2">
              <i class="bi bi-lock-fill me-1"></i> This conversation has been marked as resolved and is closed to new replies.
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Compose Modal -->
    <div class="modal fade" id="composeModal" tabindex="-1" :class="{ 'show d-block': showComposeModal }" style="background: rgba(0,0,0,0.5);" v-if="showComposeModal">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow-lg">
          <div class="modal-header border-bottom-0">
            <h5 class="modal-title fw-bold">New Message</h5>
            <button type="button" class="btn-close" @click="showComposeModal = false"></button>
          </div>
          <div class="modal-body pt-0">
            <form @submit.prevent="createThread">
              <div class="mb-3">
                <label class="form-label text-muted small fw-bold">To</label>
                <select class="form-select" v-model="composeForm.recipient_group" required>
                  <option value="" disabled>Select Recipient Group</option>
                  <option value="admin">Administrators (Support)</option>
                  <option v-if="user.role !== 'student'" value="all_students">Broadcast to All Students</option>
                  <option v-if="user.role === 'admin'" value="all_companies">Broadcast to All Companies</option>
                  <!-- We could fetch active companies for students or applicants for companies, but for now we use groups -->
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label text-muted small fw-bold">Subject</label>
                <input type="text" class="form-control" v-model="composeForm.subject" placeholder="What is this regarding?" required>
              </div>
              <div class="mb-4">
                <label class="form-label text-muted small fw-bold">Message</label>
                <textarea class="form-control" rows="4" v-model="composeForm.body" placeholder="Type your message here..." required></textarea>
              </div>
              <div class="d-flex justify-content-end gap-2">
                <button type="button" class="btn btn-light" @click="showComposeModal = false">Cancel</button>
                <button type="submit" class="btn btn-primary" :disabled="creatingThread">
                  <span v-if="creatingThread" class="spinner-border spinner-border-sm me-2"></span> Send
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import { ref, onMounted, getCurrentInstance, nextTick } from 'vue';

export default {
  name: 'Messages',
  setup() {
    const { proxy } = getCurrentInstance();
    const user = ref(JSON.parse(localStorage.getItem('ppa_user')) || {});
    
    const threads = ref([]);
    const loadingThreads = ref(true);
    
    const activeThread = ref(null);
    const replies = ref([]);
    const loadingMessages = ref(false);
    
    const showComposeModal = ref(false);
    const creatingThread = ref(false);
    const composeForm = ref({
      recipient_group: '',
      subject: '',
      body: ''
    });

    const replyForm = ref({ body: '' });
    const sendingReply = ref(false);
    
    const messagesContainer = ref(null);

    const loadThreads = async () => {
      loadingThreads.value = true;
      try {
        const res = await axios.get('/api/messages');
        threads.value = res.data;
      } catch (err) {
        proxy.$toast('Failed to load conversations', 'error');
      } finally {
        loadingThreads.value = false;
      }
    };

    const selectThread = async (thread) => {
      activeThread.value = thread;
      loadingMessages.value = true;
      try {
        const res = await axios.get(`/api/messages/${thread.id}`);
        replies.value = res.data.replies;
        scrollToBottom();
      } catch (err) {
        proxy.$toast('Failed to load messages', 'error');
      } finally {
        loadingMessages.value = false;
      }
    };

    const scrollToBottom = () => {
      nextTick(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
        }
      });
    };

    const createThread = async () => {
      creatingThread.value = true;
      try {
        const res = await axios.post('/api/messages', composeForm.value);
        proxy.$toast('Message sent successfully', 'success');
        showComposeModal.value = false;
        composeForm.value = { recipient_group: '', subject: '', body: '' };
        await loadThreads();
        selectThread(res.data);
      } catch (err) {
        proxy.$toast(err.response?.data?.error || 'Failed to send message', 'error');
      } finally {
        creatingThread.value = false;
      }
    };

    const sendReply = async () => {
      if (!replyForm.value.body.trim() || !activeThread.value) return;
      
      sendingReply.value = true;
      try {
        const res = await axios.post(`/api/messages/${activeThread.value.id}/reply`, replyForm.value);
        replies.value.push(res.data);
        replyForm.value.body = '';
        scrollToBottom();
      } catch (err) {
        proxy.$toast(err.response?.data?.error || 'Failed to send reply', 'error');
      } finally {
        sendingReply.value = false;
      }
    };

    const resolveThread = async () => {
      if (!confirm('Are you sure you want to mark this issue as resolved? This will close the conversation.')) return;
      
      try {
        await axios.put(`/api/messages/${activeThread.value.id}/resolve`);
        proxy.$toast('Conversation marked as resolved', 'success');
        activeThread.value.status = 'resolved';
        
        // update in list
        const t = threads.value.find(x => x.id === activeThread.value.id);
        if (t) t.status = 'resolved';
      } catch (err) {
        proxy.$toast(err.response?.data?.error || 'Failed to resolve', 'error');
      }
    };

    onMounted(loadThreads);

    return {
      user, threads, loadingThreads,
      activeThread, replies, loadingMessages, selectThread,
      showComposeModal, creatingThread, composeForm, createThread,
      replyForm, sendingReply, sendReply,
      resolveThread, messagesContainer
    };
  }
}
</script>

<style scoped>
.min-h-400 {
  min-height: 400px;
}
</style>
