<template>
  <div class="ppa-page">
    <div v-if="loading" class="text-center py-5">
      <div class="ppa-spinner ppa-spinner-sm"></div>
    </div>

    <template v-else-if="drive">
      <div class="section-header">
        <div>
          <h1 class="page-title">{{ drive.job_title }}</h1>
          <p class="page-subtitle">{{ drive.company_name }}<span v-if="drive.location"> &middot; {{ drive.location }}</span></p>
        </div>
        <router-link to="/student/drives" class="btn btn-outline-secondary">Back</router-link>
      </div>

      <div class="row g-4">
        <!-- Left: Job description + skills -->
        <div class="col-lg-7">
          <div class="ppa-card mb-4">
            <div class="card-header">Job Description</div>
            <div class="card-body">
              <p v-if="drive.job_description" style="white-space: pre-wrap;" class="mb-4">{{ drive.job_description }}</p>
              <p v-else class="text-muted mb-4">No description provided.</p>

              <h6 class="fw-bold mb-2">Required Skills</h6>
              <div v-if="drive.required_skills" class="d-flex flex-wrap gap-2">
                <span v-for="skill in drive.required_skills.split(',')" :key="skill" class="skill-tag">{{ skill.trim() }}</span>
              </div>
              <p v-else class="text-muted small mb-0">Not specified</p>
            </div>
          </div>
        </div>

        <!-- Right: Drive info + apply -->
        <div class="col-lg-5">
          <div class="ppa-card mb-4">
            <div class="card-header">Drive Information</div>
            <div class="card-body">
              <table class="table table-sm table-borderless mb-3">
                <tbody>
                  <tr>
                    <td class="text-muted" style="width: 45%">Company</td>
                    <td class="fw-medium">{{ drive.company_name }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Location</td>
                    <td>{{ drive.location || '—' }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Salary / yr</td>
                    <td class="fw-medium">{{ drive.salary || 'Not specified' }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Min CGPA</td>
                    <td>{{ drive.min_cgpa || 'None' }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Eligible Branches</td>
                    <td>{{ formatBranches(drive.eligible_branches) }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Batch</td>
                    <td>{{ drive.eligible_year || 'Any' }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Deadline</td>
                    <td class="fw-medium">{{ new Date(drive.application_deadline).toLocaleDateString() }}</td>
                  </tr>

                </tbody>
              </table>

              <div v-if="drive.applied" class="alert alert-success text-center mb-0 py-2 small">
                You have already applied for this drive.
              </div>
              <div v-else-if="drive.status === 'approved' && isDriveOpen(drive)">
                <button @click="openApplyModal" class="btn btn-primary w-100" :disabled="loadingProfile">
                  <span v-if="loadingProfile" class="spinner-border spinner-border-sm me-2"></span>
                  Apply Now
                </button>
              </div>
              <div v-else class="alert alert-warning text-center mb-0 py-2 small">
                <span v-if="drive.status === 'cancelled'">This drive has been cancelled.</span>
                <span v-else>Applications are closed for this drive.</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <div v-else class="text-center py-5 text-muted">Drive not found.</div>

    <!-- Apply Modal -->
    <div v-if="showModal" class="modal d-block" style="background: rgba(0,0,0,0.5);" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title fw-bold">Confirm Application</h5>
            <button type="button" class="btn-close" @click="showModal = false"></button>
          </div>
          <div class="modal-body">
            <p class="mb-3 text-muted small">Applying for <strong>{{ drive?.job_title }}</strong> at <strong>{{ drive?.company_name }}</strong>. Edits made here will update your profile.</p>

            <div class="row g-3">
              <div class="col-6">
                <label class="form-label small fw-medium">Full Name</label>
                <input type="text" class="form-control form-control-sm" v-model="profileForm.full_name" required>
              </div>
              <div class="col-6">
                <label class="form-label small fw-medium">Email</label>
                <input type="email" class="form-control form-control-sm" v-model="profileForm.email" required>
              </div>
              <div class="col-6">
                <label class="form-label small fw-medium">Phone</label>
                <input type="text" class="form-control form-control-sm" v-model="profileForm.phone">
              </div>
              <div class="col-6">
                <label class="form-label small fw-medium">Branch</label>
                <input type="text" class="form-control form-control-sm" v-model="profileForm.branch">
              </div>
              <div class="col-6">
                <label class="form-label small fw-medium">Grad Year</label>
                <input type="number" class="form-control form-control-sm" v-model="profileForm.year">
              </div>
              <div class="col-6">
                <label class="form-label small fw-medium">CGPA</label>
                <input type="number" step="0.01" class="form-control form-control-sm" v-model="profileForm.cgpa">
              </div>
              <div class="col-12">
                <label class="form-label small fw-medium">Skills</label>
                <input type="text" class="form-control form-control-sm" v-model="profileForm.skills" placeholder="Comma-separated">
              </div>
              <div class="col-12">
                <label class="form-label small fw-medium">Resume Link</label>
                <input type="url" class="form-control form-control-sm" v-model="profileForm.resume_path" placeholder="https://drive.google.com/...">
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-light btn-sm" @click="showModal = false" :disabled="applying">Cancel</button>
            <button type="button" class="btn btn-primary btn-sm" @click="confirmApply" :disabled="applying">
              <span v-if="applying" class="spinner-border spinner-border-sm me-2"></span>
              Submit Application
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, getCurrentInstance } from 'vue';
import { useRoute } from 'vue-router';

export default {
  name: 'DriveDetail',
  setup() {
    const route = useRoute();
    const drive = ref(null);
    const loading = ref(true);
    const applying = ref(false);
    const showModal = ref(false);
    const profileForm = ref({});
    const loadingProfile = ref(false);
    const { proxy } = getCurrentInstance();

    const isDriveOpen = (d) => {
      if (!d || !d.application_deadline) return false;
      return new Date(d.application_deadline) >= new Date();
    };

    const formatBranches = (branches) => {
      if (!branches) return 'All';
      try {
        const arr = typeof branches === 'string' ? JSON.parse(branches) : branches;
        return Array.isArray(arr) ? arr.join(', ') : branches;
      } catch {
        return branches;
      }
    };

    const loadDrive = async () => {
      try {
        const res = await axios.get(`/api/student/drives/${route.params.id}`);
        drive.value = res.data;
      } catch (err) {
        proxy.$toast('Failed to load drive details.', 'error');
      } finally {
        loading.value = false;
      }
    };

    const openApplyModal = async () => {
      loadingProfile.value = true;
      try {
        const res = await axios.get('/api/student/profile');
        profileForm.value = res.data || {};
        showModal.value = true;
      } catch (err) {
        proxy.$toast('Failed to load profile. Please try again.', 'error');
      } finally {
        loadingProfile.value = false;
      }
    };

    const confirmApply = async () => {
      applying.value = true;
      try {
        await axios.put('/api/student/profile', profileForm.value);
        const payload = { drive_id: drive.value.id };
        if (profileForm.value.resume_path) payload.resume_path = profileForm.value.resume_path;
        await axios.post('/api/student/applications', payload);
        proxy.$toast('Applied successfully!', 'success');
        drive.value.applied = true;
        showModal.value = false;
      } catch (err) {
        proxy.$toast(err.response?.data?.message || err.response?.data?.error || 'Failed to apply.', 'error');
      } finally {
        applying.value = false;
      }
    };

    onMounted(loadDrive);

    return { drive, loading, applying, showModal, profileForm, loadingProfile, openApplyModal, confirmApply, formatBranches, isDriveOpen };
  }
}
</script>

<style scoped>
.skill-tag {
  background: rgba(0, 167, 111, 0.1);
  color: var(--ppa-success);
  font-size: 0.75rem;
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
  font-weight: 500;
}
</style>
