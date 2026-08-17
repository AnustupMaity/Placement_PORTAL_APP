<template>
  <div class="ppa-page">
    <div class="section-header">
      <div>
        <h1 class="page-title">Create Placement Drive</h1>
        <p class="page-subtitle">Post a new job opportunity for students.</p>
      </div>
      <router-link to="/company/drives" class="btn btn-outline-secondary">Cancel</router-link>
    </div>

    <div class="ppa-card" style="max-width: 800px;">
      <div class="card-body">
        <form @submit.prevent="handleSubmit">
          <div class="mb-3">
            <label class="form-label-dark">Job Title *</label>
            <input type="text" class="form-control" v-model="form.job_title" required>
          </div>

          <div class="mb-3">
            <label class="form-label-dark">Job Description *</label>
            <textarea class="form-control" rows="4" v-model="form.job_description" required></textarea>
          </div>

          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label-dark">Location *</label>
              <input type="text" class="form-control" v-model="form.location" required>
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label-dark">Salary/Stipend *</label>
              <input type="text" class="form-control" v-model="form.salary" required>
            </div>
          </div>

          <div class="mb-3">
            <label class="form-label-dark">Required Skills</label>
            <input type="text" class="form-control" v-model="form.required_skills" placeholder="e.g. Python, VueJS, SQL">
          </div>

          <h5 class="mt-4 mb-3 fw-bold border-bottom pb-2">Eligibility Criteria</h5>

          <div class="row">
            <div class="col-md-4 mb-3">
              <label class="form-label-dark">Eligible Branches</label>
              <input type="text" class="form-control" v-model="form.eligible_branches" placeholder="e.g. CSE, IT">
            </div>
            <div class="col-md-4 mb-3">
              <label class="form-label-dark">Eligible Year</label>
              <input type="number" class="form-control" v-model="form.eligible_year" placeholder="e.g. 2026">
            </div>
            <div class="col-md-4 mb-3">
              <label class="form-label-dark">Minimum CGPA</label>
              <input type="number" step="0.01" class="form-control" v-model="form.min_cgpa" placeholder="e.g. 7.5">
            </div>
          </div>

          <div class="row">
            <div class="col-md-6 mb-4">
              <label class="form-label-dark">Application Deadline *</label>
              <input type="date" class="form-control" v-model="form.application_deadline" required>
            </div>
          </div>

          <button type="submit" class="btn btn-gradient w-100" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            Post Drive
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, getCurrentInstance } from 'vue';
import { useRouter } from 'vue-router';

export default {
  name: 'CreateDrive',
  setup() {
    const { proxy } = getCurrentInstance();
    const router = useRouter();
    const loading = ref(false);
    
    const form = ref({
      job_title: '',
      job_description: '',
      required_skills: '',
      salary: '',
      location: '',
      eligible_branches: '',
      min_cgpa: '',
      eligible_year: '',
      application_deadline: ''
    });

    const handleSubmit = async () => {
      loading.value = true;
      try {
        const payload = { ...form.value };
        
        if (new Date(payload.application_deadline) <= new Date()) {
          proxy.$toast('Application deadline must be a future date.', 'error');
          loading.value = false;
          return;
        }
        if (payload.min_cgpa && (parseFloat(payload.min_cgpa) < 0 || parseFloat(payload.min_cgpa) > 10)) {
          proxy.$toast('Minimum CGPA must be between 0 and 10.', 'error');
          loading.value = false;
          return;
        }
        if (payload.eligible_branches) {
          payload.eligible_branches = payload.eligible_branches.split(',').map(s => s.trim());
        } else {
          payload.eligible_branches = [];
        }
        if (payload.min_cgpa) payload.min_cgpa = parseFloat(payload.min_cgpa);
        if (payload.eligible_year) payload.eligible_year = parseInt(payload.eligible_year);
        
        await axios.post('/api/company/drives', payload);
        proxy.$toast('Drive created successfully!', 'success');
        router.push('/company/drives');
      } catch (err) {
        proxy.$toast(err.response?.data?.error || 'Failed to create drive.', 'error');
      } finally {
        loading.value = false;
      }
    };

    return { form, loading, handleSubmit };
  }
}
</script>
