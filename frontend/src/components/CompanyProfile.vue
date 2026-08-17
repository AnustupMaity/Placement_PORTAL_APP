<template>
  <div class="ppa-page">
    <div class="section-header">
      <div>
        <h1 class="page-title">Company Profile</h1>
        <p class="page-subtitle">Update your organisation and authorization details</p>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="ppa-spinner ppa-spinner-sm"></div>
    </div>

    <div v-else class="ppa-card" style="max-width: 800px;">
      <div class="card-body">
        <form @submit.prevent="handleUpdate">
          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label-dark">Company Name *</label>
              <input type="text" class="form-control" v-model="form.company_name" required>
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label-dark">Industry</label>
              <input type="text" class="form-control" v-model="form.industry">
            </div>
          </div>

          <div class="mb-3">
            <label class="form-label-dark">Description</label>
            <textarea class="form-control" rows="4" v-model="form.description"></textarea>
          </div>

          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label-dark">Website</label>
              <input type="url" class="form-control" v-model="form.website">
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label-dark">Location</label>
              <input type="text" class="form-control" v-model="form.location">
            </div>
          </div>

          <h5 class="mt-4 mb-3 fw-bold border-bottom pb-2">HR Contact Details</h5>

          <div class="row">
            <div class="col-md-4 mb-3">
              <label class="form-label-dark">HR Name</label>
              <input type="text" class="form-control" v-model="form.hr_name">
            </div>
            <div class="col-md-4 mb-3">
              <label class="form-label-dark">HR Email</label>
              <input type="email" class="form-control" v-model="form.hr_email">
            </div>
            <div class="col-md-4 mb-3">
              <label class="form-label-dark">HR Phone</label>
              <input type="text" class="form-control" v-model="form.hr_phone">
            </div>
          </div>

          <!-- Company Authorized Signatory Signature (Optional) -->
          <div class="card mb-4 border bg-light">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label-dark fw-bold mb-0"><i class="bi bi-pen me-2"></i>Authorized Signatory Signature</label>
                <span class="badge bg-secondary bg-opacity-25 text-dark">Optional</span>
              </div>
              <p class="text-muted small mb-3">Upload your authorized HR / Director signature image (PNG, JPG, JPEG). When provided, this signature will be included in the official Offer Letter PDFs sent to selected candidates.</p>

              <div class="d-flex align-items-center gap-3 flex-wrap">
                <div v-if="form.signature_path" class="p-2 border rounded bg-white text-center">
                  <img :src="form.signature_path" alt="Company Signature" style="max-height: 60px; max-width: 200px; object-fit: contain;" />
                  <div class="small text-muted mt-1">Active Offer Signature</div>
                </div>
                <div v-else class="text-muted small italic p-2 border rounded bg-white">
                  No company signature uploaded (Offer letters will display standard digital authorization text).
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
  name: 'CompanyProfile',
  setup() {
    const { proxy } = getCurrentInstance();
    const loading = ref(true);
    const saving = ref(false);
    const uploadingSig = ref(false);
    const form = ref({});

    const loadProfile = async () => {
      try {
        const res = await axios.get('/api/company/profile');
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
        proxy.$toast('Company signature uploaded! Click Update Profile to save.', 'success');
      } catch (err) {
        proxy.$toast(err.response?.data?.error || 'Failed to upload signature.', 'error');
      } finally {
        uploadingSig.value = false;
      }
    };

    const removeSignature = () => {
      form.value.signature_path = null;
      proxy.$toast('Company signature removed. Click Update Profile to save.', 'info');
    };

    const handleUpdate = async () => {
      saving.value = true;
      try {
        await axios.put('/api/company/profile', form.value);
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
