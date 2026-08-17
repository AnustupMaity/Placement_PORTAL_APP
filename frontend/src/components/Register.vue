<template>
  <div class="ppa-auth-wrapper">
    <div class="ppa-auth-card ppa-auth-card-wide">
      <!-- Show success message if company registration is done -->
      <div v-if="companyRegistrationSuccess" class="text-center py-4">
        <div class="auth-brand-badge bg-success mb-3" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
          <i class="bi bi-check-lg fs-2"></i>
        </div>
        <h2 class="auth-brand mb-2">Company Registration Submitted!</h2>
        <p class="text-muted mb-4">
          Thank you for registering your organization. Your profile has been sent to the placement administrator for approval. You will be able to log in once approved.
        </p>
        <router-link to="/login" class="btn btn-gradient w-100 py-2">Go to Login Page</router-link>
      </div>

      <!-- Otherwise show form -->
      <div v-else>
        <div class="auth-brand-badge">
          <i class="bi bi-person-plus-fill"></i>
        </div>
        <h2 class="auth-brand">Create an Account</h2>
        <p class="auth-subtitle">Join the Campus Placement Management Portal</p>

        <!-- Role Selector -->
        <div class="role-selector mb-4">
          <button type="button" class="role-btn" :class="{active: role === 'student'}" @click="role = 'student'">
            <i class="bi bi-mortarboard d-block fs-3 mb-1"></i> Student Candidate
          </button>
          <button type="button" class="role-btn" :class="{active: role === 'company'}" @click="role = 'company'">
            <i class="bi bi-building d-block fs-3 mb-1"></i> Company Recruiter
          </button>
        </div>

        <form @submit.prevent="handleRegister">
          <div class="row g-3 mb-3">
            <div class="col-md-6">
              <label class="form-label-dark">Username <span class="text-danger">*</span></label>
              <input type="text" class="form-control" v-model="form.username" placeholder="Choose a username" autocomplete="username" required>
            </div>
            <div class="col-md-6">
              <label class="form-label-dark">Email Address <span class="text-danger">*</span></label>
              <input type="email" class="form-control" v-model="form.email" placeholder="name@example.com" autocomplete="email" required>
            </div>
          </div>

          <div class="mb-3">
            <label class="form-label-dark">Password <span class="text-danger">*</span> (min 6 characters)</label>
            <div class="input-group">
              <span class="input-group-text"><i class="bi bi-lock"></i></span>
              <input :type="showPassword ? 'text' : 'password'" class="form-control" v-model="form.password" placeholder="Create a secure password" autocomplete="new-password" required minlength="6">
              <button class="btn btn-outline-secondary" type="button" @click="showPassword = !showPassword" tabindex="-1">
                <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
              </button>
            </div>
          </div>

          <!-- Student Profile Fields -->
          <template v-if="role === 'student'">
            <div class="p-3 bg-light rounded-3 border mb-3">
              <h6 class="fw-bold text-primary mb-3"><i class="bi bi-mortarboard me-2"></i>Academic Details</h6>
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label-dark">Full Name <span class="text-danger">*</span></label>
                  <input type="text" class="form-control" v-model="form.full_name" placeholder="Full legal name" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label-dark">Roll Number (Optional)</label>
                  <input type="text" class="form-control" v-model="form.roll_number" placeholder="e.g. 21CS042">
                </div>
                <div class="col-md-4">
                  <label class="form-label-dark">Branch / Department</label>
                  <input type="text" class="form-control" v-model="form.branch" placeholder="e.g. CSE, ECE">
                </div>
                <div class="col-md-4">
                  <label class="form-label-dark">Graduation Year</label>
                  <input type="number" class="form-control" v-model="form.year" placeholder="e.g. 2026">
                </div>
                <div class="col-md-4">
                  <label class="form-label-dark">CGPA (0 - 10)</label>
                  <input type="number" step="0.01" class="form-control" v-model="form.cgpa" placeholder="e.g. 8.5">
                </div>
                <div class="col-12">
                  <label class="form-label-dark">Resume Link (Google Drive / PDF Link)</label>
                  <input type="url" class="form-control" v-model="form.resume_path" placeholder="https://drive.google.com/file/...">
                  <small class="text-muted">You can also update your resume anytime in your profile.</small>
                </div>
              </div>
            </div>
          </template>

          <!-- Company Profile Fields -->
          <template v-if="role === 'company'">
            <div class="p-3 bg-light rounded-3 border mb-3">
              <h6 class="fw-bold text-primary mb-3"><i class="bi bi-building me-2"></i>Organisation & HR Details</h6>
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label-dark">Company Name <span class="text-danger">*</span></label>
                  <input type="text" class="form-control" v-model="form.company_name" placeholder="Company legal name" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label-dark">Industry</label>
                  <input type="text" class="form-control" v-model="form.industry" placeholder="e.g. Information Technology, FinTech">
                </div>
                <div class="col-md-6">
                  <label class="form-label-dark">Official Website</label>
                  <input type="url" class="form-control" v-model="form.website" placeholder="https://example.com">
                </div>
                <div class="col-md-6">
                  <label class="form-label-dark">Headquarters / Location</label>
                  <input type="text" class="form-control" v-model="form.location" placeholder="e.g. Bangalore, India">
                </div>
                <div class="col-12">
                  <label class="form-label-dark">HR Contact Name</label>
                  <input type="text" class="form-control" v-model="form.hr_name" placeholder="Primary HR / Talent Acquisition contact">
                </div>
                <div class="col-md-6">
                  <label class="form-label-dark">HR Email</label>
                  <input type="email" class="form-control" v-model="form.hr_email" placeholder="hr@company.com">
                </div>
                <div class="col-md-6">
                  <label class="form-label-dark">HR Phone</label>
                  <input type="tel" class="form-control" v-model="form.hr_phone" placeholder="+91 9876543210">
                </div>
              </div>
            </div>
          </template>

          <div v-if="error" class="alert alert-danger p-2 small mb-3 d-flex align-items-center gap-2">
            <i class="bi bi-exclamation-triangle-fill"></i> <span>{{ error }}</span>
          </div>

          <button type="submit" class="btn btn-gradient w-100 py-2 mb-3" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            Complete Registration
          </button>

          <div class="text-center pt-2 border-top">
            <span class="text-muted small">Already have an account?</span>
            <router-link to="/login" class="text-decoration-none ms-1 small fw-bold text-primary">Login here</router-link>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, getCurrentInstance } from 'vue';
import { useRouter } from 'vue-router';

export default {
  name: 'Register',
  setup() {
    const router = useRouter();
    const { proxy } = getCurrentInstance();
    const role = ref('student');
    const showPassword = ref(false);
    const loading = ref(false);
    const error = ref('');
    const companyRegistrationSuccess = ref(false);

    const form = ref({
      username: '',
      email: '',
      password: '',
      full_name: '',
      roll_number: '',
      branch: '',
      year: '',
      cgpa: '',
      resume_path: '',
      company_name: '',
      industry: '',
      website: '',
      location: '',
      description: '',
      hr_name: '',
      hr_email: '',
      hr_phone: '',
    });

    const handleRegister = async () => {
      loading.value = true;
      error.value = '';

      const endpoint = role.value === 'student'
        ? '/api/auth/register/student'
        : '/api/auth/register/company';

      const payload = {
        username: form.value.username,
        email: form.value.email,
        password: form.value.password,
      };

      if (role.value === 'student') {
        payload.full_name = form.value.full_name;
        if (form.value.roll_number) payload.roll_number = form.value.roll_number;
        if (form.value.branch) payload.branch = form.value.branch;
        if (form.value.year) payload.year = parseInt(form.value.year);
        if (form.value.cgpa) payload.cgpa = parseFloat(form.value.cgpa);
        if (form.value.resume_path) payload.resume_path = form.value.resume_path;
      } else {
        payload.company_name = form.value.company_name;
        if (form.value.industry) payload.industry = form.value.industry;
        if (form.value.website) payload.website = form.value.website;
        if (form.value.location) payload.location = form.value.location;
        if (form.value.description) payload.description = form.value.description;
        if (form.value.hr_name) payload.hr_name = form.value.hr_name;
        if (form.value.hr_email) payload.hr_email = form.value.hr_email;
        if (form.value.hr_phone) payload.hr_phone = form.value.hr_phone;
      }

      try {
        const response = await axios.post(endpoint, payload);

        if (role.value === 'company') {
          companyRegistrationSuccess.value = true;
        } else {
          proxy.$toast('Registration successful! Please log in.', 'success');
          router.push('/login');
        }
      } catch (err) {
        error.value = err.response?.data?.error || 'Registration failed. Please check your inputs.';
      } finally {
        loading.value = false;
      }
    };

    return {
      role, form, showPassword, loading, error, companyRegistrationSuccess, handleRegister
    };
  }
}
</script>
