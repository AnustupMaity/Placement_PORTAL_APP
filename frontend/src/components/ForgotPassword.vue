<template>
  <div class="auth-wrapper">
    <div class="auth-card">
      <div class="text-center mb-4">
        <h3 class="fw-bold">Forgot Password</h3>
        <p class="text-muted" v-if="step === 1">Enter your email or username to reset your password.</p>
        <p class="text-muted" v-if="step === 2">Enter the 6-digit OTP sent to your email.</p>
        <p class="text-muted" v-if="step === 3">Create a new password.</p>
      </div>

      <!-- Step 1: Request OTP -->
      <form @submit.prevent="requestOtp" v-if="step === 1">
        <div class="mb-3">
          <label class="form-label fw-medium">Username or Email</label>
          <input type="text" class="form-control" v-model="identifier" required placeholder="Enter username or email" />
        </div>
        <button type="submit" class="btn btn-primary w-100" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span> Send OTP
        </button>
      </form>

      <!-- Step 2: Verify OTP -->
      <form @submit.prevent="verifyOtp" v-if="step === 2">
        <div class="mb-3">
          <label class="form-label fw-medium">6-Digit OTP</label>
          <input type="text" class="form-control" v-model="otp" required placeholder="123456" maxlength="6" />
        </div>
        <button type="submit" class="btn btn-primary w-100" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span> Verify OTP
        </button>
      </form>

      <!-- Step 3: Reset Password -->
      <form @submit.prevent="resetPassword" v-if="step === 3">
        <div class="mb-3">
          <label class="form-label fw-medium">New Password</label>
          <input type="password" class="form-control" v-model="newPassword" required placeholder="••••••••" minlength="6" />
        </div>
        <button type="submit" class="btn btn-success w-100" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span> Reset Password
        </button>
      </form>

      <div class="text-center mt-4 pt-3 border-top">
        <p class="text-muted small mb-0">Remembered your password? <router-link to="/login" class="fw-bold text-primary text-decoration-none">Log in</router-link></p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, getCurrentInstance } from 'vue';
import { useRouter } from 'vue-router';

export default {
  name: 'ForgotPassword',
  setup() {
    const router = useRouter();
    const { proxy } = getCurrentInstance();
    
    const step = ref(1);
    const loading = ref(false);
    
    const identifier = ref('');
    const otp = ref('');
    const newPassword = ref('');
    const resetToken = ref('');

    const requestOtp = async () => {
      loading.value = true;
      try {
        const res = await axios.post('/api/auth/forgot-password', { identifier: identifier.value });
        proxy.$toast(res.data.message, 'success');
        step.value = 2;
      } catch (err) {
        proxy.$toast(err.response?.data?.error || 'Failed to request OTP.', 'error');
      } finally {
        loading.value = false;
      }
    };

    const verifyOtp = async () => {
      loading.value = true;
      try {
        const res = await axios.post('/api/auth/verify-otp', { 
          identifier: identifier.value,
          otp: otp.value 
        });
        resetToken.value = res.data.reset_token;
        proxy.$toast('OTP Verified.', 'success');
        step.value = 3;
      } catch (err) {
        proxy.$toast(err.response?.data?.error || 'Invalid OTP.', 'error');
      } finally {
        loading.value = false;
      }
    };

    const resetPassword = async () => {
      loading.value = true;
      try {
        const res = await axios.post('/api/auth/reset-password', { 
          reset_token: resetToken.value,
          new_password: newPassword.value 
        });
        proxy.$toast('Password reset successfully. You can now log in.', 'success');
        router.push('/login');
      } catch (err) {
        proxy.$toast(err.response?.data?.error || 'Failed to reset password.', 'error');
      } finally {
        loading.value = false;
      }
    };

    return { step, loading, identifier, otp, newPassword, requestOtp, verifyOtp, resetPassword };
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
