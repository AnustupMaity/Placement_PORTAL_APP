<template>
  <div class="ppa-page">
    <div class="section-header">
      <div>
        <h1 class="page-title">My Profile</h1>
        <p class="page-subtitle">Update your personal, academic, and signature details</p>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="ppa-spinner ppa-spinner-sm"></div>
    </div>

    <div v-else class="ppa-card" style="max-width: 800px;">
      <div class="card-body">
        <form @submit.prevent="handleUpdate">
          <div class="row">
            <div class="col-md-4 mb-3">
              <label class="form-label-dark">Full Name *</label>
              <input type="text" class="form-control" v-model="form.full_name" required>
            </div>
            <div class="col-md-4 mb-3">
              <label class="form-label-dark">Email Address *</label>
              <input type="email" class="form-control" v-model="form.email" required>
            </div>
            <div class="col-md-4 mb-3">
              <label class="form-label-dark">Roll Number</label>
              <input type="text" class="form-control" v-model="form.roll_number">
            </div>
          </div>

          <div class="row">
            <div class="col-md-4 mb-3">
              <label class="form-label-dark">Branch</label>
              <input type="text" class="form-control" v-model="form.branch">
            </div>
            <div class="col-md-4 mb-3">
              <label class="form-label-dark">Graduation Year</label>
              <input type="number" class="form-control" v-model="form.year">
            </div>
            <div class="col-md-4 mb-3">
              <label class="form-label-dark">CGPA</label>
              <input type="number" step="0.01" class="form-control" v-model="form.cgpa">
            </div>
          </div>

          <div class="mb-3">
            <label class="form-label-dark">Skills</label>
            <input type="text" class="form-control" v-model="form.skills" placeholder="Comma-separated skills">
          </div>

          <div class="mb-4">
            <label class="form-label-dark">Phone Number</label>
            <input type="text" class="form-control" v-model="form.phone">
          </div>

          <div class="mb-4">
            <label class="form-label-dark">Resume Link (Google Drive / Public Link)</label>
            <input type="url" class="form-control" v-model="form.resume_path" placeholder="https://drive.google.com/...">
          </div>

          <!-- Digital Signature Section -->
          <div class="card mb-4 border bg-light">
            <div class="card-body">
              <label class="form-label-dark fw-bold mb-1"><i class="bi bi-pen me-2"></i>Default Digital Signature</label>
              <p class="text-muted small mb-3">Upload your signature image (PNG, JPG, JPEG) to be used when accepting offer letters.</p>

              <div class="d-flex align-items-center gap-3 flex-wrap">
                <div v-if="form.signature_path" class="p-2 border rounded bg-white text-center">
                  <img :src="form.signature_path" alt="Current Signature" style="max-height: 60px; max-width: 200px; object-fit: contain;" />
                  <div class="small text-muted mt-1">Active Signature</div>
                </div>
                <div v-else class="text-muted small italic p-2 border rounded bg-white">
                  No default signature uploaded yet.
                </div>

                <div>
                  <label class="btn btn-outline-primary btn-sm mb-0">
                    <span v-if="uploadingSig" class="spinner-border spinner-border-sm me-1"></span>
                    <i v-else class="bi bi-cloud-arrow-up me-1"></i>
                    {{ form.signature_path ? 'Change Signature' : 'Upload Signature' }}
                    <input type="file" accept="image/png, image/jpeg, image/jpg, image/webp" @change="handleSignatureUpload" class="d-none" :disabled="uploadingSig">
                  </label>
                  <button v-if="form.signature_path" type="button" class="btn btn-outline-danger btn-sm ms-2" @click="removeSignature">
                    <i class="bi bi-trash me-1"></i> Remove
                  </button>
                </div>
              </div>
            </div>
          </div>

          <button type="submit" class="btn btn-gradient w-100" :disabled="saving">
            <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
            Update Profile
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, getCurrentInstance } from 'vue';

export default {
  name: 'StudentProfile',
  setup() {
    const { proxy } = getCurrentInstance();
    const loading = ref(true);
    const saving = ref(false);
    const uploadingSig = ref(false);
    const form = ref({});

    const loadProfile = async () => {
      try {
        const res = await axios.get('/api/student/profile');
        form.value = res.data || {};
      } catch (err) {
        proxy.$toast('Failed to load profile.', 'error');
      } finally {
        loading.value = false;
      }
    };

    const handleSignatureUpload = async (e) => {
      const file = e.target.files[0];
      if (!file) return;

      const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp'];
      if (!validTypes.includes(file.type)) {
        proxy.$toast('Please select a valid image (PNG, JPG, JPEG, WEBP).', 'error');
        return;
      }

      uploadingSig.value = true;
      const formData = new FormData();
      formData.append('file', file);

      try {
        const res = await axios.post('/api/upload/signature', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        form.value.signature_path = res.data.file_url;
        proxy.$toast('Signature uploaded! Click Update Profile to save changes.', 'success');
      } catch (err) {
        proxy.$toast(err.response?.data?.error || 'Failed to upload signature.', 'error');
      } finally {
        uploadingSig.value = false;
      }
    };

    const removeSignature = () => {
      form.value.signature_path = null;
      proxy.$toast('Signature removed. Click Update Profile to save.', 'info');
    };

    const handleUpdate = async () => {
      saving.value = true;
      try {
        await axios.put('/api/student/profile', form.value);
        proxy.$toast('Profile updated successfully!', 'success');
      } catch (err) {
        proxy.$toast('Failed to update profile.', 'error');
      } finally {
        saving.value = false;
      }
    };

    onMounted(loadProfile);

    return { form, loading, saving, uploadingSig, handleSignatureUpload, removeSignature, handleUpdate };
  }
}
</script>
