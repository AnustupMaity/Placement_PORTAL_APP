<template>
  <div class="auth-wrapper">
    <div class="auth-card">
      <div class="text-center mb-4">
        <h3 class="fw-bold">Forgot Username</h3>
        <p class="text-muted">Enter your registered email address to receive your username.</p>
      </div>

      <form @submit.prevent="requestUsername">
        <div class="mb-3">
          <label class="form-label fw-medium">Email Address</label>
          <input type="email" class="form-control" v-model="email" required placeholder="Enter your email" />
        </div>
        <button type="submit" class="btn btn-primary w-100" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span> Send Username
        </button>
      </form>

      <div class="text-center mt-4 pt-3 border-top">
        <p class="text-muted small mb-0">Remembered your username? <router-link to="/login" class="fw-bold text-primary text-decoration-none">Log in</router-link></p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, getCurrentInstance } from 'vue';
import { useRouter } from 'vue-router';

export default {
  name: 'ForgotUsername',
  setup() {
    const router = useRouter();
    const { proxy } = getCurrentInstance();
    const loading = ref(false);
    const email = ref('');

    const requestUsername = async () => {
      loading.value = true;
      try {
        const res = await axios.post('/api/auth/forgot-username', { email: email.value });
        proxy.$toast(res.data.message, 'success');
        router.push('/login');
      } catch (err) {
        proxy.$toast(err.response?.data?.error || 'Failed to request username.', 'error');
      } finally {
        loading.value = false;
      }
    };

    return { loading, email, requestUsername };
  }
}
</script>

<style scoped>
.auth-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--ppa-bg);
  padding: 1rem;
}
.auth-card {
  background: #ffffff;
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.08);
  padding: 2.5rem;
  width: 100%;
  max-width: 420px;
}
</style>
