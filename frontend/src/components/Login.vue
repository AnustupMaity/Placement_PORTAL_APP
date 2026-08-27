<template>
  <div class="ppa-auth-wrapper">
    <div class="ppa-auth-card">
      <div class="auth-brand-badge">
        <i class="bi bi-mortarboard-fill"></i>
      </div>
      <h2 class="auth-brand">Welcome Back</h2>
      <p class="auth-subtitle">Sign in to your Placement Portal account</p>
      
      <!-- Google Sign In Button -->
      <div class="mb-3">
        <button type="button" class="btn btn-google w-100 py-2 d-flex align-items-center justify-content-center gap-2" @click="handleGoogleSignIn" :disabled="googleLoading">
          <svg width="18" height="18" viewBox="0 0 18 18" xmlns="http://www.w3.org/2000/svg">
            <path d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.874 2.684-6.616z" fill="#4285F4"/>
            <path d="M9 18c2.43 0 4.467-.806 5.956-2.184l-2.908-2.258c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 0 0 9 18z" fill="#34A853"/>
            <path d="M3.964 10.707c-.18-.54-.282-1.117-.282-1.707 0-.59.102-1.167.282-1.707V4.961H.957A8.996 8.996 0 0 0 0 9c0 1.452.348 2.827.957 4.039l3.007-2.332z" fill="#FBBC05"/>
            <path d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 0 0 .957 4.961L3.964 7.293C4.672 5.166 6.656 3.58 9 3.58z" fill="#EA4335"/>
          </svg>
          <span>{{ googleLoading ? 'Connecting to Google...' : 'Continue with Google' }}</span>
        </button>
      </div>

      <div class="d-flex align-items-center my-3">
        <hr class="flex-grow-1 my-0 text-muted border-secondary opacity-25">
        <span class="px-3 text-muted small fw-semibold">or with username / email</span>
        <hr class="flex-grow-1 my-0 text-muted border-secondary opacity-25">
      </div>

      <form @submit.prevent="handleLogin">
        <div class="mb-3">
          <label class="form-label-dark">Username or Email</label>
          <div class="input-group">
            <span class="input-group-text"><i class="bi bi-person"></i></span>
            <input type="text" class="form-control" v-model="form.username" placeholder="e.g. student_demo or email" autocomplete="username" required>
          </div>
        </div>
        
        <div class="mb-3">
          <label class="form-label-dark">Password</label>
          <div class="input-group">
            <span class="input-group-text"><i class="bi bi-lock"></i></span>
            <input :type="showPassword ? 'text' : 'password'" class="form-control" v-model="form.password" placeholder="Enter password" autocomplete="current-password" required>
            <button class="btn btn-outline-secondary" type="button" @click="showPassword = !showPassword" tabindex="-1">
              <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
            </button>
          </div>
        </div>
        
        <div v-if="error" class="alert alert-danger mb-3 p-2 small d-flex align-items-center gap-2">
          <i class="bi bi-exclamation-triangle-fill"></i> <span>{{ error }}</span>
        </div>
        
        <div class="d-flex justify-content-between align-items-center mb-3">
          <router-link to="/forgot-password" class="small text-decoration-none text-muted">Forgot Password?</router-link>
          <router-link to="/forgot-username" class="small text-decoration-none text-muted">Forgot Username?</router-link>
        </div>

        <button type="submit" class="btn btn-gradient w-100 py-2 mb-3" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          Sign In
        </button>

        <div class="text-center pt-2 border-top">
          <span class="text-muted small">Don't have an account?</span>
          <router-link to="/register" class="text-decoration-none ms-1 small fw-bold text-primary">Register here</router-link>
        </div>
      </form>
    </div>

    <!-- Google First-Time Role Selection Modal -->
    <div class="modal fade" id="googleRoleModal" tabindex="-1" data-bs-backdrop="static">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title fw-bold">Welcome! Choose Your Account Type</h5>
          </div>
          <div class="modal-body">
            <p class="text-muted small mb-3">Since this is your first time logging in with Google (<strong>{{ googleUserData?.email }}</strong>), please select how you would like to use Placement Portal:</p>
            
            <div class="role-selector mb-3">
              <button type="button" class="role-btn" :class="{active: selectedGoogleRole === 'student'}" @click="selectedGoogleRole = 'student'">
                <i class="bi bi-mortarboard d-block fs-3 mb-1"></i> Student Candidate
              </button>
              <button type="button" class="role-btn" :class="{active: selectedGoogleRole === 'company'}" @click="selectedGoogleRole = 'company'">
                <i class="bi bi-building d-block fs-3 mb-1"></i> Company Recruiter
              </button>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-primary w-100" @click="completeGoogleRegistration" :disabled="googleLoading">
              <span v-if="googleLoading" class="spinner-border spinner-border-sm me-2"></span>
              Continue as {{ selectedGoogleRole === 'student' ? 'Student' : 'Company' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, getCurrentInstance } from 'vue';
import { useRouter } from 'vue-router';

export default {
  name: 'Login',
  setup() {
    const router = useRouter();
    const { proxy } = getCurrentInstance();
    const form = ref({ username: '', password: '' });
    const loading = ref(false);
    const googleLoading = ref(false);
    const error = ref('');
    const showPassword = ref(false);

    const googleUserData = ref(null);
    const selectedGoogleRole = ref('student');
    let googleRoleModalInstance = null;

    const handleLogin = async () => {
      loading.value = true;
      error.value = '';
      try {
        const response = await axios.post('/api/auth/login', form.value);
        localStorage.setItem('ppa_token', response.data.token);
        localStorage.setItem('ppa_user', JSON.stringify(response.data.user));
        
        window.dispatchEvent(new Event('user-logged-in'));
        
        const role = response.data.user.role;
        if (role === 'admin') router.push('/admin');
        else if (role === 'company') router.push('/company');
        else router.push('/student');
        
      } catch (err) {
        error.value = err.response?.data?.error || 'Login failed. Please check credentials.';
      } finally {
        loading.value = false;
      }
    };

    const handleGoogleSignIn = () => {
      // Check if Google Client SDK is loaded
      if (window.google && window.google.accounts && window.google.accounts.id) {
        window.google.accounts.id.initialize({
          client_id: '1082498294829-mockclientid.apps.googleusercontent.com',
          callback: handleGoogleCredentialResponse,
          auto_select: false
        });
        window.google.accounts.id.prompt((notification) => {
          if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
            // Fallback prompt for demo Google Auth popup
            triggerGooglePopupFallback();
          }
        });
      } else {
        triggerGooglePopupFallback();
      }
    };

    const triggerGooglePopupFallback = () => {
      const email = prompt("Enter your Google Account email for Google Sign-In:", "student.google@demo.com");
      if (!email) return;
      const name = email.split('@')[0].replace('.', ' ').toUpperCase();
      
      googleUserData.value = { email, name };
      
      // Directly try Google Auth API
      executeGoogleAuth(email, name, selectedGoogleRole.value);
    };

    const handleGoogleCredentialResponse = async (response) => {
      googleLoading.value = true;
      try {
        const res = await axios.post('/api/auth/google', {
          credential: response.credential,
          role: selectedGoogleRole.value
        });
        finishGoogleLogin(res.data);
      } catch (err) {
        error.value = err.response?.data?.error || 'Google Sign-In failed.';
      } finally {
        googleLoading.value = false;
      }
    };

    const executeGoogleAuth = async (email, name, role) => {
      googleLoading.value = true;
      try {
        const res = await axios.post('/api/auth/google', {
          email,
          name,
          role
        });
        finishGoogleLogin(res.data);
      } catch (err) {
        error.value = err.response?.data?.error || 'Google Sign-In failed.';
      } finally {
        googleLoading.value = false;
      }
    };

    const finishGoogleLogin = (data) => {
      localStorage.setItem('ppa_token', data.token);
      localStorage.setItem('ppa_user', JSON.stringify(data.user));
      window.dispatchEvent(new Event('user-logged-in'));
      
      const role = data.user.role;
      if (role === 'admin') router.push('/admin');
      else if (role === 'company') router.push('/company');
      else router.push('/student');
    };

    const completeGoogleRegistration = () => {
      if (googleRoleModalInstance) googleRoleModalInstance.hide();
      if (googleUserData.value) {
        executeGoogleAuth(googleUserData.value.email, googleUserData.value.name, selectedGoogleRole.value);
      }
    };

    return {
      form, loading, googleLoading, error, showPassword,
      handleLogin, handleGoogleSignIn, googleUserData, selectedGoogleRole, completeGoogleRegistration
    };
  }
}
</script>